from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('family', 'Family'),
    )
    
    CURRENCY_CHOICES = (
        # Original currency
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('INR', 'Indian Rupee (₹)'),
        # African currencies
        ('KES', 'Kenyan Shilling (KSh)'),
        ('NGN', 'Nigerian Naira (₦)'),
        ('ZAR', 'South African Rand (R)'),
        ('GHS', 'Ghanaian Cedi (GH₵)'),
        ('EGP', 'Egyptian Pound (E£)'),
        ('MAD', 'Moroccan Dirham (MAD)'),
        ('TZS', 'Tanzanian Shilling (TSh)'),
        ('UGX', 'Ugandan Shilling (USh)'),
        ('XOF', 'West African CFA Franc (CFA)'),
        ('XAF', 'Central African CFA Franc (FCFA)'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='individual')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    is_family_head = models.BooleanField(default=False)
    family = models.ForeignKey('Family', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    
    def __str__(self):
        return self.username
    
    def get_currency_symbol(self):
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'INR': '₹',
            'KES': 'KSh',
            'NGN': '₦',
            'ZAR': 'R',
            'GHS': 'GH₵',
            'EGP': 'E£',
            'MAD': 'MAD',
            'TZS': 'TSh',
            'UGX': 'USh',
            'XOF': 'CFA',
            'XAF': 'FCFA',
        }
        return currency_symbols.get(self.currency, '$')

class Family(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class UserPreference(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    receive_weekly_reports = models.BooleanField(default=True)
    receive_budget_alerts = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s preferences"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
