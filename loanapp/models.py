from django.db import models

class Customer(models.Model):
    customer_id    = models.CharField(max_length=100, unique=True)
    first_name     = models.CharField(max_length=100)
    last_name      = models.CharField(max_length=100)
    age            = models.IntegerField()                                       # ← Added
    phone_number   = models.CharField(max_length=15)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=10, decimal_places=2)
    current_debt   = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Loan(models.Model):
    customer          = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_id           = models.CharField(max_length=100, unique=True)
    loan_amount       = models.DecimalField(max_digits=10, decimal_places=2)
    tenure            = models.IntegerField()
    interest_rate     = models.FloatField()
    monthly_repayment = models.DecimalField(max_digits=10, decimal_places=2)
    emis_paid_on_time = models.IntegerField()
    start_date        = models.DateField()
    end_date          = models.DateField()
    loan_approved     = models.BooleanField(default=False)   # Add this

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer.first_name}"
