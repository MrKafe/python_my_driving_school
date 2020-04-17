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
        print('\033[96m> Attempting to log in\033[m')
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                print('\033[92m✓ Logging in user [' + username + ']\033[m')
                login(request, user)
                return redirect('dashboard')
            else:
                print('\033[91m✕ Could not find user [' + username + ']\033[m')
                error = True
    else:
        print('\033[96m> Access to login page\033[m')
        form = forms.LoginForm()

    return render(request, 'User/login.html', locals())


def index(request, filter=None):
    if not utilities.is_granted(request.user, 'instructor'):
        print('\033[1;91m< User have to be granted [instructor] \033[m')
        raise PermissionDenied

    if filter:
        group = Group.objects.get(name=filter)
        users = group.user_set.all().filter(groups__in=get_inheritance_roles(request.user, only_id=True))
        print('\033[92m✓ Listing ['+filter+'] users ('+str(users.count())+')\033[m')
    else:
        users = User.objects.filter(groups__in=get_inheritance_roles(request.user, only_id=True))
        print('\033[92m✓ Listing [ALL] users ('+str(users.count())+')\033[m')

    return render(request, 'User/index_user.html', locals())


def show(request, user_id=None):
    current_user_id = request.user.id

    # security: student can only access it's own account, instructors and upper can access every
    # TODO: Not well secured: do as delete
    if (not utilities.is_granted(request.user, 'student')) or \
            user_id is None or \
            ((not utilities.is_granted(request.user, 'instructor')) and user_id != current_user_id):
        print('\033[1;91m< User have to:\n  - be granted [instructor]\n  - own the account\033[m')
        raise PermissionDenied

    # TODO: get or 404
    user = User.objects.get(pk=user_id)
    print('\033[96m> Access to user [' + str(user.username) + ']\'s details\033[m')

    # template will decide text to display according to this information
    own_account = False
    has_error = False
    if user_id == current_user_id:
        own_account = True
        if request.method == "POST":
            print('\033[96m> Attempting to change [' + str(user.username) + ']\'s password\033[m')
            form = forms.EditPasswordForm(request.POST)
            if form.is_valid():
                cur_pdw = form.cleaned_data['password']
                new_pdw = form.cleaned_data['new_password']
                upd_user = authenticate(username=request.user.username, password=cur_pdw)
                has_error = True
                if upd_user:
                    upd_user.set_password(new_pdw)
                    upd_user.save()
                    login(request, upd_user)  # don't forget to re-login the user, if not he will be redirected to login
                    print('\033[92m✓ Updated user [' + upd_user.username + ']\'s password\033[m')
                    error = "Password changed successfully!"
                else:
                    print('\033[91m✕ Updating user\'s password failed\033[m')
                    error = "An error has occurred, please make sure you filled the right password"

        form = forms.EditPasswordForm()
    return render(request, 'User/show_user.html', locals())


def create(request):
    if not utilities.is_granted(request.user, 'secretary'):
        print('\033[1;91m< User have to be granted [secretary] to create user\033[m')
        raise PermissionDenied

    has_error = False
    if request.method == "POST":
        print('\033[96m> Attempting to create user\033[m')
        form = forms.CreateForm(request.POST, request=request)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            driving_license = form['driving'].value()  # unable to get it thanks to .cleaned_data
            role = form.cleaned_data['role']

            if utilities.is_granted(request.user, role, True) and not utilities.find_existing_user(username):
                user = User.objects.create_user(username, email, password)  # Create new user, no need to save
                group = Group.objects.get(name=role)  # Get selected role
                user.groups.add(group)  # Add user to group
                profile = Profile(user=user, driving_license=driving_license)  # Create user's profile

                if str(role) == 'student':  # casting str role in str: only way to make this if working
                    profile.time = datetime.strptime('00:00:00', '%H:%M:%S')
                else:
                    profile.time = None

                user.save()
                profile.save()

                print('\033[96m> Created user ['+username+' ('+email+')]\n               Role    '+role+
                      '\n               License '+(driving_license or '_')+
                      '\n               Hours   '+('Yes' if profile.time is not None else '_')+'\033[m')

                return redirect('index')

            else:
                has_error = True

                if not utilities.is_granted(request.user, role, True):
                    error = 'You don\'t have permission to create a ' + role + ' user'
                    print('\033[1;91m< User ['+request.user.username+'] is not allowed to create ['+role+'] users'
                        '\033[m')
                elif utilities.find_existing_user(username):
                    error = 'User already exist, please try again with an other Username'
                    print('\033[1;91m< User ['+username+'] already exist\033[m')
    else:
        print('\033[96m> Access to create user\033[m')
        form = forms.CreateForm(request=request)

    return render(request, 'User/create_user.html', locals())


def edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    to_edit_role = user.groups.all()[0].name
    if not utilities.is_granted(request.user, 'secretary') or \
            not utilities.is_granted(request.user, to_edit_role, strict=True):
        print('\033[1;91m< User have to:\n  - be granted [secretary]\n  - inherit user role\033[m')
        raise PermissionDenied

    has_error = False
    if request.method == "POST":
        print('\033[96m> Attempting to edit user\033[m')

        # picking right form: if user is a student it also have hours and driving license
        form = forms.EditForm(request.POST)
        if utilities.has_group(user, 'student'):
            form = forms.EditWithTimeForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            # Checking if username isn't already attributed
            if user.username is username and utilities.find_existing_user(username=username):
                has_error = True
                error = "This username ("+username+") is already in use by another student"
                print('\033[1;91m< User ['+username+'] already exist\033[m')
            else:
                email = form.cleaned_data['email']
                driving = form.cleaned_data['driving'] or None
                hours = form.cleaned_data['hours'] or 0
                minutes = form.cleaned_data['minutes'] or 0

                if hours is not 0 or minutes is not 0:  # Adding or removing hours
                    user.profile.time = strftime(
                        '%H:%M',
                        gmtime(
                            (
                                timedelta(
                                    hours=hours,
                                    minutes=minutes
                                ) +
                                timedelta(
                                    hours=user.profile.time.hour,
                                    minutes=user.profile.time.minute
                                )
                            ).total_seconds()
                        )
                    )  # Ha, just playing with indent

                    # # Old time calcul, just keeping it safe here
                    # add_time_delta = timedelta(hours=hours, minutes=minutes)
                    # remain_time_delta = timedelta(hours=user.profile.time.hour, minutes=user.profile.time.minute)
                    # new_time_delta = add_time_delta+remain_time_delta
                    # new_time_obj = gmtime(new_time_delta.total_seconds())
                    # new_time_str = strftime('%H:%M', new_time_obj)
                    # user.profile.time = new_time_str

                user.username = username
                user.email = email
                user.profile.driving_license = driving
                user.save()
                user.profile.save()

                print('\033[92m✓ Updated user ['+user.username+']\033[m')

                return redirect('show_user', user_id=user_id)
        else:
            has_error = True
            print('\033[91m✕ Updating user failed\033[m')
    else:
        print('\033[96m> Access to user ['+str(user.username)+']\'s edition\033[m')

        data = {
            'username': user.username,
            'email': user.email,
            'driving': user.profile.driving_license,
        }

        form = forms.EditForm(data)
        if utilities.has_group(user, 'student'):
            form = forms.EditWithTimeForm(data)

    return render(request, 'User/edit.html', locals())


def delete(request, user_id):
    user =get_object_or_404(User, pk=user_id)

    if not utilities.is_granted(user=request.user, role='secretary') or\
        not utilities.is_granted(user=request.user, role=utilities.get_highest_role(user=user)):
        print('\033[1;91m< User does not have permission to delete this user\033[m')
        raise PermissionDenied

    username = user.username
    user.delete()
    print('\033[92m✓ User ['+username+'] have been deleted with it\'s profile and appointments\n\033[m')

    return redirect('index')
