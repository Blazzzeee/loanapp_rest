from django.urls import path
from .views import RegisterCustomerView, CheckEligibilityView,CreateLoanView,LoanDetailView,CustomerLoansView

urlpatterns = [
    path('register/', RegisterCustomerView.as_view(), name='register_customer'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create_loan'),  # Add this line
    path('view-loan/<int:loan_id>/', LoanDetailView.as_view(), name='view_loan'),
    path('view-loans/<str:customer_id>/', CustomerLoansView.as_view(), name='customer-loans'),
]
