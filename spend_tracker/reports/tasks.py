from celery import shared_task
from django.utils import timezone
from django.db.models import Sum
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from datetime import timedelta
from .models import Report, ReportCategory
from transactions.models import Transaction

User = get_user_model()

@shared_task
def generate_weekly_reports():
    """Generate weekly reports for all users and send email notifications."""
    today = timezone.now().date()
    start_date = today - timedelta(days=7)
    
    # Get all users who want weekly reports
    users = User.objects.filter(preferences__receive_weekly_reports=True)
    
    for user in users:
        # Get transactions for the past week
        transactions = Transaction.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=today
        )
        
        # Calculate totals
        income_total = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense_total = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Create report
        report = Report.objects.create(
            user=user,
            report_type='weekly',
            start_date=start_date,
            end_date=today,
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
        
        # Send email notification
        if user.email:
            context = {
                'user': user,
                'report': report,
                'start_date': start_date,
                'end_date': today,
                'income_total': income_total,
                'expense_total': expense_total,
                'net_amount': income_total - expense_total
            }
            
            html_message = render_to_string('reports/email/weekly_report.html', context)
            
            send_mail(
                subject=f'Your Weekly Spending Report ({start_date} to {today})',
                message=f'Your weekly report is ready. Total Income: {income_total}, Total Expenses: {expense_total}',
                from_email='noreply@spendtracker.com',
                recipient_list=[user.email],
                html_message=html_message
            )
    
    return f"Generated weekly reports for {users.count()} users"

