from django import forms
from .models import Budget, ExpectedIncome
from transactions.models import Category
from django.db.models import Q

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'period']
    
    def __init__(self, user, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        # Only show expense categories
        self.fields['category'].queryset = Category.objects.filter(
            (Q(user=user) | Q(is_default=True)) & Q(type='expense')
        )

class ExpectedIncomeForm(forms.ModelForm):
    class Meta:
        model = ExpectedIncome
        fields = ['source', 'amount', 'period']

