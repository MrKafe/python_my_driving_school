from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login', views.user_login, name='login'),
    path('logout', auth_views.logout_then_login, name='logout'),
    path('show/<int:user_id>', views.show, name='show_user'),
    path('edit/<int:user_id>', views.edit, name='edit_user'),
    path('delete/<int:user_id>', views.delete, name='delete_user'),
    path('create', views.create, name='create_user'),
    path('', views.index, name='index'),
    path('<str:filter>', views.index, name='index_filter'),
]