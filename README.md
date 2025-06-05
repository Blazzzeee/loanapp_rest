# loanapp_rest
data_ingestion
python manage.py ingest_data

API 
/register
curl -X POST http://127.0.0.1:8000/api/register/ \
-H "Content-Type: application/json" \
-d '{
  "first_name": "Abbie",
  "last_name": "Rodrigues",
  "age": 35,
  "monthly_income": 75000,
  "phone_number": "9876543210"
}'

{"customer_id":"","name":"Abbie Rodrigues","age":35,"monthly_income":75000,"approved_limit":2700000,"phone_number":"9876543210"}%    

/check-eligbility
 curl -X POST http://127.0.0.1:8000/api/check-eligibility/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": 1,
  "loan_amount": 50000,
  "interest_rate": 10,
  "tenure": 12
}'

/create-loan
curl -X POST http://127.0.0.1:8000/api/create-loan/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": 1,
  "loan_amount": 50000,
  "interest_rate": 14,
  "tenure": 12
}'

/view-loan/{id}
curl -X GET http://localhost:8000/api/view-loan/1/

/view-loans/{id}
curl -X GET http://127.0.0.1:8000/api/view-loans/1/
