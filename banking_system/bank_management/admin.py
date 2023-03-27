from django.contrib import admin
from bank_management.models import *
# Register your models here.
class LoanAdmin(admin.ModelAdmin):
    list_display = ("availed_by","due_at","paid")
    list_editable=("paid",)

admin.site.register(Loan,LoanAdmin)
# Register your models here.
admin.site.register((Branch,Account,Transaction,Notification))