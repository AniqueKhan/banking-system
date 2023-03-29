import django,os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from bank_management.models import Loan
import pandas as pd

loans = Loan.objects.all()
data=[]

for loan in loans:
    user = loan.availed_by
    loan_data = {
        "Loan_ID":loan.id,
        "Gender":user.get_gender_display(),
        "Married":user.get_married_display(),
        "Dependent":user.get_dependents_display(),
        "Education":user.get_education_display(),
        "Self_Employed":user.get_self_employed_display(),
        "Applicant_Income":user.applicant_income,
        "Coapplicant_Income":user.co_applicant_income,
        "Loan_Amount":loan.amount,
        "Loan_Amount_Term":loan.get_loan_amount_term(),
        "Credit_History":loan.get_credit_history(),
        "Property_Area":user.get_property_area_display(),
        "Loan_Status":loan.loan_status,
    }
    data.append(loan_data)

df = pd.DataFrame(data)
df.to_csv("dataset.csv",index=False)
print(df.shape)