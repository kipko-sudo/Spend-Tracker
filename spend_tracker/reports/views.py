from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from .models import Report, ReportCategory
from transactions.models import Transaction

@login_required
def report_list(request):
    reports = Report.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'reports/report_list.html', {'reports': reports})

@login_required
def report_detail(request, pk):
    report = get_object_or_404(Report, pk=pk, user=request.user)
    categories = report.categories.all().order_by('transaction_type', '-amount')
    
    # Prepare data for charts
    income_categories = categories.filter(transaction_type='income')
    expense_categories = categories.filter(transaction_type='expense')
    
    income_data = {
        'labels': [cat.category_name for cat in income_categories],
        'values': [float(cat.amount) for cat in income_categories]
    }
    
    expense_data = {
        'labels': [cat.category_name for cat in expense_categories],
        'values': [float(cat.amount) for cat in expense_categories]
    }
    
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'categories': categories,
        'income_data': income_data,
        'expense_data': expense_data
    })

@login_required
def generate_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
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
        
        return redirect('report_detail', pk=report.pk)
    
    return render(request, 'reports/generate_report.html')