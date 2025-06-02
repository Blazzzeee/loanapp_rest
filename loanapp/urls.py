from django.urls import path
from .views import RegisterCustomerView, CheckEligibilityView

urlpatterns = [
    path('register/', RegisterCustomerView.as_view(), name='register_customer'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check-eligibility'),

]
