from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserPreferenceSerializer, FamilySerializer,
    CategorySerializer, TransactionSerializer,
    BudgetSerializer, ExpectedIncomeSerializer,
    ReportSerializer, ReportCategorySerializer
)
from transactions.models import Transaction, Category
from budgets.models import Budget, ExpectedIncome
from reports.models import Report, ReportCategory
from users.models import UserPreference, Family
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        elif user.is_family_head:
            return User.objects.filter(family=user.family)
        return User.objects.filter(pk=user.pk)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Get month-to-date totals
        month_income = Transaction.objects.filter(
            user=user,
            date__gte=start_of_month,
            date__lte=today,
            category__type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_expenses = Transaction.objects.filter(
            user=user,
            date__gte=start_of_month,
            date__lte=today,
            category__type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate month-to-date savings
        month_savings = month_income - month_expenses
        
        # Get transaction counts
        total_transactions = Transaction.objects.filter(user=user).count()
        
        return Response({
            'month_income': month_income,
            'month_expenses': month_expenses,
            'month_savings': month_savings,
            'total_transactions': total_transactions
        })

class UserPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FamilyViewSet(viewsets.ModelViewSet):
    serializer_class = FamilySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Family.objects.all()
        elif user.family and (user.is_family_head or user.family):
            return Family.objects.filter(pk=user.family.pk)
        return Family.objects.none()
    
    def perform_create(self, serializer):
        family = serializer.save()
        user = self.request.user
        user.family = family
        user.is_family_head = True
        user.save()

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'type']
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user) | Category.objects.filter(is_default=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def income(self, request):
        queryset = self.get_queryset().filter(type='income')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expense(self, request):
        queryset = self.get_queryset().filter(type='expense')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'category__name']
    ordering_fields = ['date', 'amount', 'category__name']
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('type')
        if transaction_type:
            queryset = queryset.filter(category__type=transaction_type)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Get month-to-date totals
        month_income = self.get_queryset().filter(
            date__gte=start_of_month,
            date__lte=today,
            category__type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_expenses = self.get_queryset().filter(
            date__gte=start_of_month,
            date__lte=today,
            category__type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get top expense categories
        top_expenses = self.get_queryset().filter(
            date__gte=start_of_month,
            date__lte=today,
            category__type='expense'
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        return Response({
            'month_income': month_income,
            'month_expenses': month_expenses,
            'month_savings': month_income - month_expenses,
            'top_expenses': top_expenses
        })

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def progress(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ExpectedIncomeViewSet(viewsets.ModelViewSet):
    serializer_class = ExpectedIncomeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return ExpectedIncome.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        report_type = self.request.data.get('report_type', 'monthly')
        days = 7 if report_type == 'weekly' else 30
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get transactions for the period
        transactions = Transaction.objects.filter(
            user=self.request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calculate totals
        income_total = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense_total = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Create report
        report = serializer.save(
            user=self.request.user,
            start_date=start_date,
            end_date=end_date,
            total_income=income_total,
            total_expense=expense_total
        )
        
        # Create report categories
        category_data = transactions.values('category__name', 'category__type').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        for item in category_data:
            if item['category__name']:
                ReportCategory.objects.create(
                    report=report,
                    category_name=item['category__name'],
                    amount=item['total'],
                    transaction_type=item['category__type']
                )
        
        return report
    
    @action(detail=False, methods=['get'])
    def generate(self, request):
        report_type = request.query_params.get('report_type', 'monthly')
        days = 7 if report_type == 'weekly' else 30
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get transactions for the period
        transactions = Transaction.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calculate totals
        income_total = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense_total = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Create report
        report = Report.objects.create(
            user=request.user,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            total_income=income_total,
            total_expense=expense_total
        )
        
        # Create report categories
        category_data = transactions.values('category__name', 'category__type').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        for item in category_data:
            if item['category__name']:
                ReportCategory.objects.create(
                    report=report,
                    category_name=item['category__name'],
                    amount=item['total'],
                    transaction_type=item['category__type']
                )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

