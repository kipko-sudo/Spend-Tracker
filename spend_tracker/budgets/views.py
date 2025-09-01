from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Budget, ExpectedIncome
from .forms import BudgetForm, ExpectedIncomeForm

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budgets/budget_list.html', {'budgets': budgets})

@login_required
def add_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget added successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(request.user)
    
    return render(request, 'budgets/budget_form.html', {'form': form, 'title': 'Add Budget'})

@login_required
def edit_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(request.user, instance=budget)
    
    return render(request, 'budgets/budget_form.html', {
        'form': form,
        'title': 'Edit Budget'
    })

@login_required
def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('budget_list')
    
    return render(request, 'budgets/budget_confirm_delete.html', {'budget': budget})

@login_required
def income_list(request):
    incomes = ExpectedIncome.objects.filter(user=request.user)
    return render(request, 'budgets/income_list.html', {'incomes': incomes})

@login_required
def add_income(request):
    if request.method == 'POST':
        form = ExpectedIncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Expected income added successfully!')
            return redirect('income_list')
    else:
        form = ExpectedIncomeForm()
    
    return render(request, 'budgets/income_form.html', {'form': form, 'title': 'Add Expected Income'})

@login_required
def edit_income(request, pk):
    income = get_object_or_404(ExpectedIncome, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ExpectedIncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expected income updated successfully!')
            return redirect('income_list')
    else:
        form = ExpectedIncomeForm(instance=income)
    
    return render(request, 'budgets/income_form.html', {
        'form': form,
        'title': 'Edit Expected Income'
    })

