from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from . import forms
from django.contrib.auth.models import User, Group
from User.models import Profile
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied

ROLE_HIERARCHY = {
    'student': [],
    'instructor': ['student'],
    'secretary': ['instructor', 'student'],
    'admin': ['secretary', 'instructor', 'student'],
}


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
        print("\033[96m > Listing [" + filter + "] users\033[m")
        group = Group.objects.get(name=filter)
        users = group.user_set.all()
    else:
        print("\033[96m > Listing [ALL] users\033[m")
        users = User.objects.all()

    return render(request, 'User/index_user.html', locals())


def show(request, user_id=None):
    current_user_id = request.user.id

    # security: student can only access it's own account, instructors and upper can access every
    if (not is_granted(request.user, 'student')) or \
            user_id is None or \
            ((not is_granted(request.user, 'instructor')) and user_id != current_user_id):
        raise PermissionDenied

    print('\033[96m> Accessing user ' + str(user_id) + ' details\033[m')

    # template will decide text to display according to this information
    own_account = False
    if user_id == current_user_id:
        own_account = True

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
            if is_granted(request.user, role, True) and not find_existing_user(username):
                print('\033[96m> Creating user [' + username + ' (' + email + ')]\033[m')
                print('\033[96m>               [Role ' + role + ' License ' + driving_license + ']\033[m')
                user = User.objects.create_user(username, email, password)  # Create new user, no need to save
                group = Group.objects.get(name=role)  # Get role selected
                user.groups.add(group)  # Add user to group
                profile = Profile(user=user, driving_license=driving_license)  # Create user's profile
                user.save()
                profile.save()
                return redirect('index')
            else:
                has_error = True
                if not is_granted(request.user, role, True):
                    error = 'You don\'t have permission to create an ' + role + ' user'
                    print('\033[1;91m> Logged user ['+request.user.username+'] does not have permission to create '+ \
                        role+' users')
                elif find_existing_user(username):
                    error = 'An error has occured: User you\'re trying to create apparently already exists, please try again with an other Username'
                    print('\033[1;91m> User [' + username + '] already excists\033[m')
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


def is_granted(user, role, strict=False):
    if user.is_staff:
        print('\033[92m> Staff is always granted\033[m')
        return True

    to_print = '\033[96m> Checking if user ' + user.username + ' is granted [' + role + ']'
    to_print = to_print + ' as Strict inheritance' if strict is True else ''
    print(to_print + '\033[m')
    user_roles = user.groups.all()
    for user_role in user_roles:
        if not strict and user_role.name == role:
            print('\033[92m - User ' + user.username + ' have role [' + role + ']\033[m')
            return True
        elif not strict:
            print('\033[33m - User ' + user.username + ' does not have role [' + role + ']\033[m')

        if user_role.name in ROLE_HIERARCHY.keys():
            print('\033[96m - Role [' + role + '] is known in hierarchy: checking inherit roles\033[m')
            inherit = ROLE_HIERARCHY[user_role.name]
            for allowed in inherit:
                if allowed == role:
                    print('\033[92m   - User ' + user.username + ' have role [' + role + '] by inheritance\033[m')
                    return True
            print('\033[91m   - User ' + user.username + ' does not have role [' + role + '] by inheritance\033[m')
        else:
            print('\033[96m - Role [' + role + '] isn\'t in role hierarchy\033[m')

    return False


# TODO: Add more validations on User on create/edit
def check_user(form):
    return True
