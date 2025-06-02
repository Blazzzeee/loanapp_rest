from rest_framework import serializers
from .models import Customer, Loan

class CustomerRegisterSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(read_only=True)  # mark this read-only
    monthly_income = serializers.DecimalField(max_digits=10, decimal_places=2, source='monthly_salary')
    approved_limit = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'monthly_income', 'approved_limit', 'phone_number']

    def create(self, validated_data):
        # 'monthly_salary' is used because 'monthly_income' is mapped to 'monthly_salary'
        monthly_salary = validated_data.get('monthly_salary')
        # Calculate approved_limit as 36 * monthly_salary rounded to nearest lakh (100,000)
        approved_limit = round((36 * monthly_salary) / 100000) * 100000
        validated_data['approved_limit'] = approved_limit

        # Set current_debt default 0
        validated_data['current_debt'] = 0.0

        # Create and return the Customer object
        return super().create(validated_data)

class CustomerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'phone_number', 'age']

class LoanDetailsSerializer(serializers.ModelSerializer):
    customer = CustomerDetailsSerializer(read_only=True)

    class Meta:
        model = Loan
        fields = [
            'loan_id',
            'customer',
            'loan_approved',
            'loan_amount',
            'interest_rate',
            'monthly_repayment',
            'tenure',
        ]


class LoanSummarySerializer(serializers.ModelSerializer):
    monthly_installment = serializers.DecimalField(
        source='monthly_repayment', max_digits=10, decimal_places=2, read_only=True
    )
    repayments_left = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']

    def get_repayments_left(self, obj):
        return max(0, obj.tenure - obj.emis_paid_on_time)
