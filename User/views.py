from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.template.defaultfilters import register
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError

from . import forms, utilities
from django.contrib.auth.models import User, Group
from User.models import Profile
from .utilities import get_inheritance_roles


def user_login(request):
    error = False

    if request.method == "POST":
        print('\033[96m> Trying to log in\033[m')
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                print('\033[92m> Logging in user [' + username + ']\033[m')
                login(request, user)
                return redirect('dashboard')
            else:
                print('\033[91m> Could not find user [' + username + ']\033[m')
                error = True
    else:
        print('\033[96m> Accessed login page\033[m')
        form = forms.LoginForm()

    return render(request, 'User/login.html', locals())


def index(request, filter=None):
    if not utilities.is_granted(request.user, 'instructor'):
        raise PermissionDenied

    if filter:
        print("\033[96m> Listing [" + filter + "] users\033[m")
        group = Group.objects.get(name=filter)
        users = group.user_set.all().filter(groups__in=get_inheritance_roles(request.user, only_id=True))
    else:
        print("\033[96m> Listing [ALL] users\033[m")
        print(get_inheritance_roles(request.user, only_id=True))
        users = User.objects.filter(groups__in=get_inheritance_roles(request.user, only_id=True))

    return render(request, 'User/index_user.html', locals())


def show(request, user_id=None):
    current_user_id = request.user.id

    # security: student can only access it's own account, instructors and upper can access every
    if (not utilities.is_granted(request.user, 'student')) or \
            user_id is None or \
            ((not utilities.is_granted(request.user, 'instructor')) and user_id != current_user_id):
        raise PermissionDenied

    print('\033[96m> Accessing user ' + str(user_id) + ' details\033[m')

    user = User.objects.get(pk=user_id)

    # template will decide text to display according to this information
    own_account = False
    if user_id == current_user_id:
        own_account = True

    return render(request, 'User/show_user.html', locals())


def create(request):
    if not utilities.is_granted(request.user, 'secretary'):
        raise PermissionDenied

    has_error = False
    if request.method == "POST":
        print('\033[96m> Trying to create user\033[m')
        form = forms.CreateForm(request.POST, request=request)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            driving_license = form['driving'].value()  # unable to get it thanks to .cleaned_data
            role = form.cleaned_data['role']
            if utilities.is_granted(request.user, role, True) and not utilities.find_existing_user(username):
                print('\033[96m> Creating user [' + username + ' (' + email + ')]\033[m')
                print('\033[96m>               [Role ' + role + ' License ' + driving_license + ']\033[m')
                user = User.objects.create_user(username, email, password)  # Create new user, no need to save
                group = Group.objects.get(name=role)  # Get role selected
                user.groups.add(group)  # Add user to group
                profile = Profile(user=user, driving_license=driving_license)  # Create user's profile
                if role is not 'student':
                    profile.time = None
                user.save()
                profile.save()
                return redirect('index')
            else:
                has_error = True
                if not utilities.is_granted(request.user, role, True):
                    error = 'You don\'t have permission to create an ' + role + ' user'
                    print(
                        '\033[1;91m> Logged user [' + request.user.username + '] does not have permission to create ' + \
                        role + ' users')
                elif utilities.find_existing_user(username):
                    error = 'An error has occured: User you\'re trying to create apparently already exists, please try again with an other Username'
                    print('\033[1;91m> User [' + username + '] already excists\033[m')
    else:
        print('\033[96m> Accessed create user page\033[m')
        form = forms.CreateForm(request=request)

    return render(request, 'User/create_user.html', locals())
