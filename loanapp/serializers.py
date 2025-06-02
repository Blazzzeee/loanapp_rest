from rest_framework import serializers
from .models import Customer

class CustomerRegisterSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(read_only=True)  # ✅ mark this read-only
    monthly_income = serializers.DecimalField(max_digits=10, decimal_places=2, source='monthly_salary')
    approved_limit = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'monthly_income', 'approved_limit', 'phone_number']

    def create(self, validated_data):
        # Calculate approved_limit as 36 * monthly_salary rounded to nearest lakh (100,000)
        monthly_salary = validated_data['monthly_salary']
        approved_limit = round((36 * monthly_salary) / 100000) * 100000
        validated_data['approved_limit'] = approved_limit

        # Set current_debt default 0
        validated_data['current_debt'] = 0.0

        # Create Customer object
        return super().create(validated_data)
