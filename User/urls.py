from django.urls import path
from . import views

urlpatterns = [
    path('login', views.user_login, name='login'),
    path('show/<int:user_id>', views.show, name='show_user'),
]
