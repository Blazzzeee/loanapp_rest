from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerRegisterSerializer, LoanDetailsSerializer
from loanapp.models import Customer, Loan
from datetime import datetime
from .utils import calculate_credit_score, calculate_emi  
import math


class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            response_data = {
                "customer_id": customer.customer_id,
                "name": f"{customer.first_name} {customer.last_name}",
                "age": customer.age,
                "monthly_income": int(customer.monthly_salary),
                "approved_limit": int(customer.approved_limit),
                "phone_number": customer.phone_number,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CheckEligibilityView(APIView):
    def post(self, request):
        data = request.data

        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        loan_amount = float(data['loan_amount'])
        interest_rate = float(data['interest_rate'])
        tenure = int(data['tenure'])

        # If current debt exceeds approved limit, credit score is 0
        if customer.current_debt > customer.approved_limit:
            return Response({
                "customer_id": customer.customer_id,
                "approval": False,
                "interest_rate": interest_rate,
                "corrected_interest_rate": None,
                "tenure": tenure,
                "monthly_installment": None,
                "reason": "Current debt exceeds approved limit"
            }, status=status.HTTP_200_OK)

        # Loan history based credit score
        past_loans = Loan.objects.filter(customer=customer)
        past_loans_count = past_loans.count()
        current_year = datetime.now().year

        paid_on_time = sum(1 for loan in past_loans if loan.end_date and loan.end_date <= loan.tenure_end_date)
        current_year_loans = sum(1 for loan in past_loans if loan.start_date and loan.start_date.year == current_year)
        total_loan_amount = sum(loan.loan_amount for loan in past_loans)

        # Simple credit score calculation out of 100
        score = 0
        score += paid_on_time * 5  # each on-time payment gives 5 points
        score += max(0, 10 - past_loans_count)  # fewer loans, better score
        score += current_year_loans * 2
        score += min(40, (total_loan_amount / customer.approved_limit) * 40)  # normalized to 40

        # Check EMI impact
        monthly_salary = float(customer.monthly_salary)
        existing_emis = sum(self.calculate_emi(loan.loan_amount, loan.interest_rate, loan.tenure) for loan in past_loans)
        new_emi = self.calculate_emi(loan_amount, interest_rate, tenure)

        if existing_emis + new_emi > 0.5 * monthly_salary:
            return Response({
                "customer_id": customer.customer_id,
                "approval": False,
                "interest_rate": interest_rate,
                "corrected_interest_rate": None,
                "tenure": tenure,
                "monthly_installment": new_emi,
                "reason": "Total EMI exceeds 50% of monthly salary"
            }, status=status.HTTP_200_OK)

        # Determine interest rate slab based on score
        if score > 50:
            corrected_interest = interest_rate
            approval = True
        elif 50 >= score > 30:
            corrected_interest = max(interest_rate, 12.0)
            approval = True
        elif 30 >= score > 10:
            corrected_interest = max(interest_rate, 16.0)
            approval = True
        else:
            return Response({
                "customer_id": customer.customer_id,
                "approval": False,
                "interest_rate": interest_rate,
                "corrected_interest_rate": None,
                "tenure": tenure,
                "monthly_installment": None,
                "reason": "Low credit score"
            }, status=status.HTTP_200_OK)

        corrected_emi = self.calculate_emi(loan_amount, corrected_interest, tenure)

        return Response({
            "customer_id": customer.customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest,
            "tenure": tenure,
            "monthly_installment": corrected_emi
        }, status=status.HTTP_200_OK)

    def calculate_emi(self, principal, rate, tenure_months):
        r = rate / (12 * 100)
        emi = principal * r * (math.pow(1 + r, tenure_months)) / (math.pow(1 + r, tenure_months) - 1)
        return round(emi, 2)




class CreateLoanView(APIView):
    def post(self, request):
        data = request.data
        customer_id = data.get('customer_id')
        loan_amount = float(data.get('loan_amount'))
        interest_rate = float(data.get('interest_rate'))
        tenure = int(data.get('tenure'))

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "Customer not found.",
                "monthly_installment": None
            }, status=status.HTTP_404_NOT_FOUND)

        # Run credit score logic (same as check-eligibility)
        credit_score = calculate_credit_score(customer_id)
        approved_limit = customer.approved_limit

        if customer.current_debt > approved_limit:
            reason = "Customer's current debt exceeds approved limit."
            approved = False
        elif credit_score <= 10:
            reason = "Low credit score"
            approved = False
        elif interest_rate < 12 and credit_score <= 50 and credit_score > 30:
            reason = "Interest rate too low for this credit score."
            approved = False
        elif interest_rate < 16 and credit_score <= 30 and credit_score > 10:
            reason = "Interest rate too low for this credit score."
            approved = False
        else:
            monthly_installment = calculate_emi(loan_amount, interest_rate, tenure)
            if monthly_installment * Loan.objects.filter(customer=customer).count() > 0.5 * customer.monthly_salary:
                reason = "EMI exceeds 50% of monthly income"
                approved = False
            else:
                approved = True
                reason = "Loan approved successfully."

        if not approved:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": reason,
                "monthly_installment": None
            }, status=status.HTTP_200_OK)

        # Create Loan
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure,
            monthly_installment=monthly_installment
        )

        # Update customer's current debt
        customer.current_debt += loan_amount
        customer.save()

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer_id,
            "loan_approved": True,
            "message": reason,
            "monthly_installment": monthly_installment
        }, status=status.HTTP_201_CREATED)


class LoanDetailView(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return Response({"detail": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LoanDetailsSerializer(loan)
        return Response(serializer.data)
