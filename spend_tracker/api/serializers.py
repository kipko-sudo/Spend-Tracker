from rest_framework import serializers
from django.contrib.auth import get_user_model
from transactions.models import Transaction, Category
from budgets.models import Budget, ExpectedIncome
from reports.models import Report, ReportCategory
from users.models import UserPreference, Family

User = get_user_model()

# User Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'currency']
        read_only_fields = ['id']

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['id', 'user', 'receive_weekly_reports', 'receive_budget_alerts']
        read_only_fields = ['id', 'user']

class FamilySerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Family
        fields = ['id', 'name', 'created_at', 'members']
        read_only_fields = ['id', 'created_at']

# Transaction Serializers
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'user', 'is_default']
        read_only_fields = ['id']
    
    def validate(self, data):
        # Ensure non-admin users can't create default categories
        if data.get('is_default', False) and not self.context['request'].user.is_staff:
            raise serializers.ValidationError("Only administrators can create default categories.")
        return data

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'category', 'category_name', 'category_type', 
                  'description', 'date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

# Budget Serializers
class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'category_name', 'amount', 'period', 
                  'spent', 'remaining', 'percentage', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'spent', 'remaining', 'percentage']
    
    def get_spent(self, obj):
        from django.db.models import Sum
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        if obj.period == 'monthly':
            start_date = today.replace(day=1)
        elif obj.period == 'weekly':
            start_date = today - timedelta(days=today.weekday())
        else:  # daily
            start_date = today
        
        spent = Transaction.objects.filter(
            user=obj.user,
            category=obj.category,
            date__gte=start_date,
            date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return spent
    
    def get_remaining(self, obj):
        spent = self.get_spent(obj)
        return obj.amount - spent
    
    def get_percentage(self, obj):
        spent = self.get_spent(obj)
        if obj.amount > 0:
            return (spent / obj.amount) * 100
        return 0

class ExpectedIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpectedIncome
        fields = ['id', 'user', 'source', 'amount', 'period', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

# Report Serializers
class ReportCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCategory
        fields = ['id', 'report', 'category_name', 'amount', 'transaction_type']
        read_only_fields = ['id', 'report']

class ReportSerializer(serializers.ModelSerializer):
    categories = ReportCategorySerializer(many=True, read_only=True)
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'user', 'report_type', 'start_date', 'end_date', 
                  'total_income', 'total_expense', 'net_amount', 'categories', 'created_at']
        read_only_fields = ['id', 'user', 'created_at', 'total_income', 'total_expense', 'net_amount']