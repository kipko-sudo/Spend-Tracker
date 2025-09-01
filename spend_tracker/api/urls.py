from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'preferences', views.UserPreferenceViewSet, basename='preference')
router.register(r'families', views.FamilyViewSet, basename='family')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'budgets', views.BudgetViewSet, basename='budget')
router.register(r'incomes', views.ExpectedIncomeViewSet, basename='income')
router.register(r'reports', views.ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]