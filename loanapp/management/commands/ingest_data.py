import pandas as pd
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from loanapp.models import Customer, Loan

class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def handle(self, *args, **kwargs):

        def parse_excel_date(value):
            if pd.isna(value) or value == '':
                return None
            return parse_date(str(value))

        # 1) Ingest customers
        customer_df = pd.read_excel('data/customer_data.xlsx')
        for _, row in customer_df.iterrows():
            Customer.objects.update_or_create(
                customer_id=row['Customer ID'],
                defaults={
                    'first_name':     row['First Name'],
                    'last_name':      row['Last Name'],
                    'phone_number':   str(row['Phone Number']),
                    'monthly_salary': row['Monthly Salary'],
                    'approved_limit': row['Approved Limit'],
                    'current_debt':   0.0,  # assume 0 since Excel lacks it
                }
            )

        # 2) Ingest loans
        loan_df = pd.read_excel('data/loan_data.xlsx')
        for _, row in loan_df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['Customer ID'])
            except Customer.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"Skipping Loan {row['Loan ID']}: Customer ID {row['Customer ID']} not found."
                ))
                continue

            start_date = parse_excel_date(row['Date of Approval'])
            end_date = parse_excel_date(row['End Date'])

            if start_date is None or end_date is None:
                self.stdout.write(self.style.WARNING(
                    f"Skipping Loan {row['Loan ID']} due to missing start or end date."
                ))
                continue

            Loan.objects.update_or_create(
                loan_id=row['Loan ID'],
                defaults={
                    'customer':          customer,
                    'loan_amount':       row['Loan Amount'],
                    'tenure':            row['Tenure'],
                    'interest_rate':     row['Interest Rate'],
                    'monthly_repayment': row['Monthly payment'],
                    'emis_paid_on_time': row['EMIs paid on Time'],
                    'start_date':        start_date,
                    'end_date':          end_date,
                }
            )

        self.stdout.write(self.style.SUCCESS("Data ingestion completed successfully."))
