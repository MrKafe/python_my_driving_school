from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('edit/<int:meet_id>', views.edit, name='edit_meet'),
    path('delete/<int:meet_id>', views.delete, name='delete_meet'),
    path('create', views.create, name='create_meet'),
    path('', views.index, name='index_meet'),
    path('<int:filter>', views.index, name='index_meet_filter'),
    # path('<str:filter>', views.index, name='index_meet_filter'),
]