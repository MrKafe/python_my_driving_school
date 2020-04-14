from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from . import forms


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
                print('\033[92m> Logging in user ['+username+']\033[m')
                login(request, user)
                return redirect('dashboard')
            else:
                print('\033[91m> Could not find user ['+username+']\033[m')
                error = True
    else:
        print('\033[96m> Accessed login page\033[m')
        form = forms.LoginForm()

    return render(request, 'User/login.html', locals())


def show(request, user_id=None):
    current_user_id = request.user.id
    if user_id is None or user_id != current_user_id:
        return redirect('dashboard')

    return render(request, 'User/show_client.html', locals())
