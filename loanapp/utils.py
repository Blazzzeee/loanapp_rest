from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from .models import Loan, Customer
from django.db.models import Sum
def calculate_credit_score(customer_id: int) -> int:
    """
    Calculate credit score (out of 100) based on:
    i. Past Loans paid on time
    ii. Number of loans taken in past
    iii. Loan activity in current year
    iv. Loan approved volume
    v. If sum of current loans > approved limit, score = 0
    """
    try:
        customer = Customer.objects.get(pk=customer_id)
    except Customer.DoesNotExist:
        return 0  # or raise error if preferred

    loans = Loan.objects.filter(customer=customer)

    # Past loans paid on time (assume Loan has 'emis_paid_on_time' boolean field)
    on_time_loans = loans.filter(emis_paid_on_time=True).count()

    # Number of loans taken in past
    total_loans = loans.count()

    # Loan activity in current year (loans with start_date in current year)
    current_year = datetime.now().year
    loans_this_year = loans.filter(start_date__year=current_year).count()

    # Loan approved volume (sum of all loan amounts approved)
    total_approved_volume = loans.aggregate(total_amount=Sum('loan_amount'))['total_amount'] or Decimal('0')

    # Sum of current loans (assume 'monthly_repayment' represents ongoing liabilities)
    current_loans_sum = loans.aggregate(total_repayment=Sum('monthly_repayment'))['total_repayment'] or Decimal('0')

    # If current loans sum > approved_limit, credit score = 0
    if current_loans_sum > customer.approved_limit:
        return 0

    # Normalize each component as per some weighting (example weights, can adjust)
    # You can tune these weights as you like
    weight_on_time = 0.4
    weight_loans_taken = 0.2
    weight_activity_year = 0.1
    weight_approved_vol = 0.3

    # Normalize on_time_loans (max 10 for example)
    on_time_score = min(on_time_loans, 10) / 10  # 0 to 1

    # Normalize total loans (max 20)
    loans_taken_score = min(total_loans, 20) / 20

    # Normalize loans this year (max 5)
    activity_score = min(loans_this_year, 5) / 5

    # Normalize approved volume (max 1 million)
    approved_volume_score = float(min(total_approved_volume, Decimal('1000000'))) / 1000000

    # Calculate weighted score out of 100
    credit_score = int(
        (on_time_score * weight_on_time +
         loans_taken_score * weight_loans_taken +
         activity_score * weight_activity_year +
         approved_volume_score * weight_approved_vol) * 100
    )

    return credit_score


def calculate_emi(loan_amount: float, interest_rate: float, tenure: int) -> float:
    """
    Calculate EMI (Equated Monthly Installment) using formula:

    EMI = P * r * (1+r)^n / ((1+r)^n - 1)

    where:
    P = principal loan amount
    r = monthly interest rate (decimal)
    n = tenure (months)

    Return EMI as float rounded to 2 decimals
    """
    P = Decimal(str(loan_amount))
    annual_interest_rate = Decimal(str(interest_rate))
    n = tenure

    # Convert annual interest rate % to monthly decimal rate
    r = (annual_interest_rate / Decimal('12')) / Decimal('100')

    if r == 0:
        # If interest rate is 0, EMI = Principal / tenure
        emi = P / n
    else:
        numerator = P * r * (1 + r) ** n
        denominator = (1 + r) ** n - 1
        emi = numerator / denominator

    # Round EMI to 2 decimals
    emi = emi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return float(emi)
