from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from transactions.models import Transaction, Category
from budgets.models import Budget

@login_required
def dashboard(request):
    # Get current date and date ranges
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    last_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
    last_month_end = start_of_month - timedelta(days=1)
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date')[:5]
    
    # Get month-to-date totals
    month_income = Transaction.objects.filter(
        user=request.user,
        date__gte=start_of_month,
        date__lte=today,
        category__type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    month_expenses = Transaction.objects.filter(
        user=request.user,
        date__gte=start_of_month,
        date__lte=today,
        category__type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get last month totals for comparison
    last_month_income = Transaction.objects.filter(
        user=request.user,
        date__gte=last_month_start,
        date__lte=last_month_end,
        category__type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    last_month_expenses = Transaction.objects.filter(
        user=request.user,
        date__gte=last_month_start,
        date__lte=last_month_end,
        category__type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate month-to-date savings
    month_savings = month_income - month_expenses
    last_month_savings = last_month_income - last_month_expenses
    
    # Calculate percentage changes
    income_change = ((month_income - last_month_income) / last_month_income * 100) if last_month_income > 0 else 0
    expense_change = ((month_expenses - last_month_expenses) / last_month_expenses * 100) if last_month_expenses > 0 else 0
    savings_change = ((month_savings - last_month_savings) / last_month_savings * 100) if last_month_savings > 0 else 0
    
    # Get top expense categories for the current month
    top_expenses = Transaction.objects.filter(
        user=request.user,
        date__gte=start_of_month,
        date__lte=today,
        category__type='expense'
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]
    
    # Get budget progress
    budgets = Budget.objects.filter(user=request.user)
    
    for budget in budgets:
        if budget.period == 'monthly':
            start_date = start_of_month
        elif budget.period == 'weekly':
            # Get the start of the current week (Monday)
            start_date = today - timedelta(days=today.weekday())
        else:  # daily
            start_date = today
        
        # Calculate spent amount for this budget period
        spent = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            date__gte=start_date,
            date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate percentage and remaining
        budget.spent = spent
        budget.percentage = (spent / budget.amount) * 100 if budget.amount > 0 else 0
        budget.remaining = budget.amount - spent
    
    context = {
        'recent_transactions': recent_transactions,
        'month_income': month_income,
        'month_expenses': month_expenses,
        'month_savings': month_savings,
        'income_change': income_change,
        'expense_change': expense_change,
        'savings_change': savings_change,
        'top_expenses': top_expenses,
        'budgets': budgets,
    }
    
    return render(request, 'dashboard/dashboard.html', context)