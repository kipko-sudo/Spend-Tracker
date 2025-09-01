from django.db import models
from django.conf import settings

class Report(models.Model):
    REPORT_TYPES = (
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_income = models.DecimalField(max_digits=10, decimal_places=2)
    total_expense = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.report_type} Report ({self.start_date} to {self.end_date})"
    
    @property
    def net_amount(self):
        return self.total_income - self.total_expense

class ReportCategory(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='categories')
    category_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10)  # 'income' or 'expense'
    
    def __str__(self):
        return f"{self.report.user.username} - {self.category_name} - {self.amount}"

