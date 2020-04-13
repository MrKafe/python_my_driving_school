from django.http import Http404
from django.shortcuts import render, redirect


def show(request, user_id=None):
    if user_id is None:
        return redirect('dashboard')
    return render(request, 'User/show_client.html', locals())
