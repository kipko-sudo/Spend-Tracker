from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserCreationForm, UserPreferenceForm, UserProfileForm
from .models import UserPreference, Notification
from transactions.models import Transaction
from .services import convert_user_transactions

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user preferences
            UserPreference.objects.create(user=user)
            # Log the user in
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    try:
        preferences = user.preferences
    except UserPreference.DoesNotExist:
        preferences = UserPreference.objects.create(user=user)
    
    if request.method == 'POST':
        if 'update_preferences' in request.POST:
            pref_form = UserPreferenceForm(request.POST, instance=preferences)
            profile_form = UserProfileForm(instance=user)
            if pref_form.is_valid():
                pref_form.save()
                messages.success(request, 'Your preferences have been updated!')
                return redirect('profile')
        else:
            profile_form = UserProfileForm(request.POST, instance=user)
            pref_form = UserPreferenceForm(instance=preferences)
            if profile_form.is_valid():
                old_currency = user.currency
                convert = profile_form.cleaned_data.get('convert_currency')
                
                # Save the user profile
                user = profile_form.save()
                
                # If currency changed and conversion requested
                if old_currency != user.currency and convert:
                    convert_user_transactions(user, old_currency, user.currency)
                    messages.success(request, f'Your profile has been updated and transactions converted to {user.get_currency_display()}!')
                else:
                    messages.success(request, 'Your profile has been updated!')
                return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=user)
        pref_form = UserPreferenceForm(instance=preferences)
    
    # Get user's transaction stats
    # Get current date and date ranges
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
    
    # Get unread notifications count
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    
    return render(request, 'users/profile.html', {
        'user': user,
        'profile_form': profile_form,
        'pref_form': pref_form,
        'month_income': month_income,
        'month_expenses': month_expenses,
        'month_savings': month_savings,
        'total_transactions': total_transactions,
        'unread_notifications': unread_notifications,
        'currency_symbol': user.get_currency_symbol(),
    })

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    
    # Mark all as read if requested
    if 'mark_all_read' in request.GET:
        notifications.update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')
    
    # Mark single notification as read
    notification_id = request.GET.get('mark_read')
    if notification_id:
        try:
            notification = notifications.get(id=notification_id)
            notification.is_read = True
            notification.save()
            messages.success(request, 'Notification marked as read.')
        except Notification.DoesNotExist:
            pass
        return redirect('notifications')
    
    # Delete notification
    notification_id = request.GET.get('delete')
    if notification_id:
        try:
            notification = notifications.get(id=notification_id)
            notification.delete()
            messages.success(request, 'Notification deleted.')
        except Notification.DoesNotExist:
            pass
        return redirect('notifications')
    
    return render(request, 'users/notifications.html', {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
    })