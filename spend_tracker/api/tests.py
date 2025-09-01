from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from transactions.models import Category, Transaction
from budgets.models import Budget, ExpectedIncome
from reports.models import Report
from users.models import UserPreference, Family
from decimal import Decimal
from datetime import date

User = get_user_model()

class APITestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            user_type='individual',
            currency='USD'
        )
        
        # Create user preferences
        self.preferences = UserPreference.objects.create(
            user=self.user,
            receive_weekly_reports=True,
            receive_budget_alerts=True
        )
        
        # Create categories
        self.income_category = Category.objects.create(
            name='Salary',
            type='income',
            user=self.user
        )
        
        self.expense_category = Category.objects.create(
            name='Groceries',
            type='expense',
            user=self.user
        )
        
        # Create transactions
        self.income_transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            category=self.income_category,
            description='Monthly salary',
            date=date.today()
        )
        
        self.expense_transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            category=self.expense_category,
            description='Weekly groceries',
            date=date.today()
        )
        
        # Create budget
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('200.00'),
            period='monthly'
        )
        
        # Create expected income
        self.income = ExpectedIncome.objects.create(
            user=self.user,
            source='Salary',
            amount=Decimal('1000.00'),
            period='monthly'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)

    def test_user_profile(self):
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['user_type'], 'individual')
        self.assertEqual(response.data['currency'], 'USD')

    def test_user_stats(self):
        url = reverse('user-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['month_income'], Decimal('1000.00'))
        self.assertEqual(response.data['month_expenses'], Decimal('50.00'))
        self.assertEqual(response.data['month_savings'], Decimal('950.00'))
        self.assertEqual(response.data['total_transactions'], 2)

    def test_list_categories(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_category(self):
        url = reverse('category-list')
        data = {
            'name': 'Entertainment',
            'type': 'expense'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Category.objects.get(name='Entertainment').type, 'expense')

    def test_list_transactions(self):
        url = reverse('transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_transaction(self):
        url = reverse('transaction-list')
        data = {
            'amount': '75.00',
            'category': self.expense_category.id,
            'description': 'Dining out',
            'date': date.today().isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 3)
        self.assertEqual(Transaction.objects.get(description='Dining out').amount, Decimal('75.00'))

    def test_transaction_summary(self):
        url = reverse('transaction-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['month_income'], Decimal('1000.00'))
        self.assertEqual(response.data['month_expenses'], Decimal('50.00'))
        self.assertEqual(response.data['month_savings'], Decimal('950.00'))

    def test_list_budgets(self):
        url = reverse('budget-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '200.00')

    def test_create_budget(self):
        url = reverse('budget-list')
        data = {
            'category': self.expense_category.id,
            'amount': '300.00',
            'period': 'weekly'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Budget.objects.count(), 2)
        self.assertEqual(Budget.objects.get(period='weekly').amount, Decimal('300.00'))

    def test_budget_progress(self):
        url = reverse('budget-progress')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['spent'], '50.00')
        self.assertEqual(response.data[0]['remaining'], '150.00')
        self.assertEqual(response.data[0]['percentage'], 25.0)

    def test_list_incomes(self):
        url = reverse('income-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['source'], 'Salary')

    def test_create_income(self):
        url = reverse('income-list')
        data = {
            'source': 'Freelance',
            'amount': '500.00',
            'period': 'monthly'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExpectedIncome.objects.count(), 2)
        self.assertEqual(ExpectedIncome.objects.get(source='Freelance').amount, Decimal('500.00'))

    def test_generate_report(self):
        url = reverse('report-generate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)
        report = Report.objects.first()
        self.assertEqual(report.total_income, Decimal('1000.00'))
        self.assertEqual(report.total_expense, Decimal('50.00'))
        self.assertEqual(report.categories.count(), 2)