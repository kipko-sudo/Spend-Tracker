from django.contrib import admin
from .models import Report, ReportCategory

# Register your models here.
admin.site.register(Report)
admin.site.register(ReportCategory)