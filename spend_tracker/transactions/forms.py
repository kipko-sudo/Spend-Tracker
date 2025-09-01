from django import forms
from django.db.models import Q
from .models import Transaction, Category

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        # Filter categories to show only user's categories and default ones
        self.fields['category'].queryset = Category.objects.filter(
            Q(user=user) | Q(is_default=True)
        )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type']