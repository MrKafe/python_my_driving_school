from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login', views.user_login, name='login'),
    path('logout', auth_views.logout_then_login, name='logout'),
    path('show/<int:user_id>', views.show, name='show_user'),
]