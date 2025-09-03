from django.contrib import admin
from .models import Budget, ExpectedIncome

# Register your models here.
admin.site.register(Budget)
admin.site.register(ExpectedIncome)
