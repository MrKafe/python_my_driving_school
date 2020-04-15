from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # path('edit/<int:meet_id>', views.edit, name='edit_meet'),
    path('create', views.create, name='create_meet'),
    path('', views.index, name='index_meet'),
    # path('<str:filter>', views.index, name='index_meet_filter'),
]