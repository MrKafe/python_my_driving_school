from datetime import datetime, date, timedelta
from time import time, mktime, strftime, gmtime

from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
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
    # TODO: Not well secured
    if (not utilities.is_granted(request.user, 'student')) or \
            user_id is None or \
            ((not utilities.is_granted(request.user, 'instructor')) and user_id != current_user_id):
        raise PermissionDenied

    print('\033[96m> Accessing user ' + str(user_id) + ' details\033[m')

    user = User.objects.get(pk=user_id)

    # template will decide text to display according to this information
    own_account = False
    has_error = False
    if user_id == current_user_id:
        own_account = True
        if request.method == "POST":
            print('\033[96m> Trying change password\033[m')
            form = forms.EditPasswordForm(request.POST)
            if form.is_valid():
                cur_pdw = form.cleaned_data['password']
                new_pdw = form.cleaned_data['new_password']
                upd_user = authenticate(username=request.user.username, password=cur_pdw)
                has_error = True
                if upd_user:
                    print('\033[92m> Changing [' + upd_user.username + '] password\033[m')
                    upd_user.set_password(new_pdw)
                    upd_user.save()
                    login(request, upd_user)  # don't forget to re-login the user, if not he will be redirected to login
                    error = "Password changed successfully!"
                else:
                    error = "An error has occurred"

        form = forms.EditPasswordForm()
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


def edit(request, user_id):
    print('\033[96m> Accessing user ' + str(user_id) + ' edition\033[m')
    user = get_object_or_404(User, pk=user_id)

    to_edit_role = user.groups.all()[0].name
    if not utilities.is_granted(request.user, 'secretary') or not utilities.is_granted(request.user, to_edit_role, strict=True):
        raise PermissionDenied

    has_error = False
    if request.method == "POST":
        print('\033[96m> Trying to edit user\033[m')
        form = forms.EditForm(request.POST)
        if utilities.has_group(user, 'student'):
            form = forms.EditWithTimeForm(request.POST)
        if form.is_valid():
            print('\033[92m - Edit form is valid\033[m')
            username = form.cleaned_data['username']
            if user.username is username and User.objects.get(username=username):
                has_error = True
                error = "This username ("+username+") is already in use by another student"
                print('\033[91m - New username already attributed\033[m')
            else:
                email = form.cleaned_data['email']
                driving = form.cleaned_data['driving'] or None
                hours = form.cleaned_data['hours'] or 0
                minutes = form.cleaned_data['minutes'] or 0

                if hours is not 0 or minutes is not 0:
                    t1 = timedelta(hours=hours, minutes=minutes)
                    t2 = timedelta(hours=user.profile.time.hour, minutes=user.profile.time.minute)
                    new_time = t1+t2
                    delta_as_time_obj = gmtime(new_time.total_seconds())
                    new_time = strftime('%H:%M', delta_as_time_obj)
                    user.profile.time = new_time

                user.username = username
                user.email = email
                user.profile.driving_license = driving
                user.save()
                user.profile.save()

                return redirect('show_user', user_id=user_id)
        else:
            has_error = True
            print('\033[91m - Edit form is invalid\033[m')
    else:
        data = {
            'username': user.username,
            'email': user.email,
            'driving': user.profile.driving_license,
        }

        form = forms.EditForm(data)
        if utilities.has_group(user, 'student'):
            form = forms.EditWithTimeForm(data)

    return render(request, 'User/edit.html', locals())
