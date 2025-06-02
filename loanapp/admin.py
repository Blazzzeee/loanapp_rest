from django.contrib import admin
from .models import Customer, Loan

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_salary', 'approved_limit', 'current_debt']

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = [
        'loan_id', 
        'customer', 
        'loan_amount', 
        'tenure', 
        'interest_rate', 
        'monthly_repayment',  # <-- Corrected here
        'emis_paid_on_time', 
        'start_date', 
        'end_date',
        'loan_approved'  # If you added this field
    ]
    list_filter = ['loan_approved', 'start_date', 'end_date']  # only if you have loan_approved field
    search_fields = ['loan_id', 'customer__first_name', 'customer__last_name']
