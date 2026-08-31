from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('expenses/', views.expense_list_view, name='expense_list'),
    path('expenses/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('expenses/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('incomes/', views.income_list_view, name='income_list'),
    path('incomes/delete/<int:pk>/', views.delete_income, name='delete_income'),
    path('add-family-member/', views.add_family_member, name='add_family_member'),
    path('add-meal-plan/', views.add_meal_plan, name='add_meal_plan'),
    path('delete-meal/<int:pk>/', views.delete_meal_plan, name='delete_meal_plan'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-debt/', views.add_debt, name='add_debt'),
    path('delete-debt/<int:pk>/', views.delete_debt, name='delete_debt'),
    path('add-wishlist/', views.add_wishlist, name='add_wishlist'),
    path('delete-wishlist/<int:pk>/', views.delete_wishlist, name='delete_wishlist'),
    path('set-savings-goal/', views.set_savings_goal, name='set_savings_goal'),
    path('backup/', views.backup_data, name='backup_data'),
    path('restore/', views.restore_data, name='restore_data'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/csv/', views.export_csv, name='export_csv'),
]