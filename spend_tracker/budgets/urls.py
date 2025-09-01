from django.urls import path
from . import views

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('add/', views.add_budget, name='add_budget'),
    path('edit/<int:pk>/', views.edit_budget, name='edit_budget'),
    path('delete/<int:pk>/', views.delete_budget, name='delete_budget'),
    path('income/', views.income_list, name='income_list'),
    path('income/add/', views.add_income, name='add_income'),
    path('income/edit/<int:pk>/', views.edit_income, name='edit_income'),
]