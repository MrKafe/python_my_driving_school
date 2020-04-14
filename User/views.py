from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from . import forms
from django.contrib.auth.models import User, Group
from User.models import Profile
from django.db import IntegrityError


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
    if filter:
        print("\033[96m > Listing ["+filter+"] users\033[m")
        group = Group.objects.get(name=filter)
        users = group.user_set.all()
    else:
        print("\033[96m > Listing [ALL] users\033[m")
        users = User.objects.all()

    return render(request, 'User/index_user.html', locals())


def show(request, user_id=None):
    current_user_id = request.user.id
    if user_id is None or user_id != current_user_id:
        return redirect('dashboard')

    return render(request, 'User/show_user.html', locals())


def create(request):
    has_error = False

    if request.method == "POST":
        print('\033[96m> Trying to create user\033[m')
        form = forms.CreateForm(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            driving_license = form['driving'].value()  # unable to get it thanks to .cleaned_data
            role = form.cleaned_data['role']
            if not find_existing_user(username):
                print('\033[96m> Creating user [' + username + ' (' + email + ')]\033[m')
                print('\033[96m>               [Role '+role+' License ' + driving_license + ']\033[m')
                user = User.objects.create_user(username, email, password)  # Create new user, no need to save
                group = Group.objects.get(name=role)  # Get role selected
                # TODO: Secure groups with permissions
                user.groups.add(group)  # Add user to group
                profile = Profile(user=user, driving_license=driving_license)  # Create user's profile
                user.save()
                profile.save()
                return redirect('dashboard')
            else:
                has_error = True
                error = 'An error has occured: User you\'re trying to create apparently already exists, please try ' \
                        'again with an other Username'
                print('\033[1;91m> User ['+username+'] already excists\033[m')
    else:
        print('\033[96m> Accessed create user page\033[m')
        form = forms.CreateForm()

    return render(request, 'User/create_user.html', locals())


def find_existing_user(username):
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    return True


# TODO: Add more validations on User on create/edit
def check_user(form):
    return True
