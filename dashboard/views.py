from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect


def dashboard(request):
    return HttpResponse("""
        <h1>Bienvenue sur RackPourTonPermis !</h1>
        <p>Un permis, oui, mais il faut payer !</p>
    """)


def home(request):
    return HttpResponse("""
        <h1>Bienvenue sur PermisPasCher !</h1>
        <p>Un permis, oui, mais il pas trop cher !</p>
    """)


def id_road(request, id_test):
    response = "<h1>Nombre choisi: {0}</h1>"

    if request.GET.get('text') is None:
        print("No get parameter")
    elif request.GET.get('text') == '404':
        raise Http404  # Raise throws errors
    elif request.GET.get('text') == '404':
        raise Http404  # Raise throws errors
    else:
        # response = response + "\n<p>Additional param text: " + request.GET.get('text') + "</p>"
        response = response + "\n<p>Additional param text: {1}</p>"  # Use + to concatenate strings

    return HttpResponse(response.format(id_test, request.GET.get('text')))


def add(request, nb1, nb2):
    total = nb1 + nb2

    # Retourne nombre1, nombre2 et la somme des deux au tpl
    return render(request, 'dashboard/addition.html', locals())
