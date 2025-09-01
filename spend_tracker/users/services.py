import requests
from decimal import Decimal

def get_exchange_rate(from_currency, to_currency):
    """
    Get the exchange rate between two currencies.
    In a production environment, you would use a paid API service like:
    - Open Exchange Rates
    - Fixer.io
    - Currency Layer
    
    For this example, we'll use a simplified approach with fixed rates.
    """
    # Sample exchange rates (as of a specific date)
    # In production, these would come from an API
    exchange_rates = {
        'USD': {
            'EUR': Decimal('0.92'),
            'GBP': Decimal('0.79'),
            'JPY': Decimal('149.50'),
            'INR': Decimal('83.12'),
            'KES': Decimal('129.50'),
            'NGN': Decimal('1550.00'),
            'ZAR': Decimal('18.50'),
            'GHS': Decimal('12.80'),
            'EGP': Decimal('46.20'),
            'MAD': Decimal('10.05'),
            'TZS': Decimal('2520.00'),
            'UGX': Decimal('3750.00'),
            'XOF': Decimal('605.00'),
            'XAF': Decimal('605.00'),
        },
        # Add more base currencies as needed
    }
    
    # If we have direct rate
    if from_currency in exchange_rates and to_currency in exchange_rates[from_currency]:
        return exchange_rates[from_currency][to_currency]
    
    # If we need to convert through USD
    if from_currency != 'USD' and to_currency != 'USD':
        # First convert to USD, then to target currency
        if from_currency in exchange_rates['USD']:
            usd_to_from = Decimal('1') / exchange_rates['USD'][from_currency]
            if to_currency in exchange_rates['USD']:
                return usd_to_from * exchange_rates['USD'][to_currency]
    
    # Default fallback (1:1 exchange rate)
    return Decimal('1.0')

def convert_amount(amount, from_currency, to_currency):
    """
    Convert an amount from one currency to another.
    """
    if from_currency == to_currency:
        return amount
    
    rate = get_exchange_rate(from_currency, to_currency)
    return amount * rate

def convert_user_transactions(user, old_currency, new_currency):
    """
    Convert all transactions for a user from old currency to new currency.
    """
    from transactions.models import Transaction
    from budgets.models import Budget, ExpectedIncome
    
    # Get exchange rate
    rate = get_exchange_rate(old_currency, new_currency)
    
    # Convert transactions
    transactions = Transaction.objects.filter(user=user)
    for transaction in transactions:
        transaction.amount = transaction.amount * rate
        transaction.save()
    
    # Convert budgets
    budgets = Budget.objects.filter(user=user)
    for budget in budgets:
        budget.amount = budget.amount * rate
        budget.save()
    
    # Convert expected incomes
    incomes = ExpectedIncome.objects.filter(user=user)
    for income in incomes:
        income.amount = income.amount * rate
        income.save()
    
    return True