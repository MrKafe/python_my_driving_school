from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('<int:id_test>', views.id_road, name='test_id'),  # For a string param, replace 'int' by 'str'
    path('add/<int:nb1>/<int:nb2>/', views.add, name='add')
]
