from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, UserPreference

class CustomUserCreationForm(UserCreationForm):
    CURRENCY_CHOICES = CustomUser.CURRENCY_CHOICES
    
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'currency', 'user_type')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ('receive_weekly_reports', 'receive_budget_alerts')

class UserProfileForm(forms.ModelForm):
    convert_currency = forms.BooleanField(required=False, label="Convert existing amounts to new currency")
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'currency')
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-select'}),
        }