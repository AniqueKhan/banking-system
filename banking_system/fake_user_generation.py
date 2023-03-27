from faker import Faker
import django,os,rstr

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from app_authentication.models import User

fake = Faker()

for i in range(10):
    account_name = fake.user_name()
    pan_number = rstr.xeger('^[A-Z]{3}P[A-Z][0-9]{4}K$')
    phone = rstr.xeger('^\+?1?\d{9,15}$')
    address = fake.address()
    self_employed = fake.random_element(elements=('Yes', 'No'))
    married = fake.random_element(elements=('Yes', 'No'))
    gender = fake.random_element(elements=('Male', 'Female'))
    dependents = fake.random_int(min=0, max=4)
    education = fake.random_element(elements=('Graduate', 'Not Graduate'))
    applicant_income = fake.random_int(min=0, max=100000)
    co_applicant_income = fake.random_int(min=0, max=100000)
    property_area = fake.random_element(elements=('Urban', 'Rural'))
    user = User.objects.create_user(account_name=account_name, pan_number=pan_number, phone=phone, address=address, self_employed=self_employed, married=married, gender=gender, dependents=dependents, education=education, applicant_income=applicant_income, co_applicant_income=co_applicant_income, property_area=property_area)
    print(f"Created {user}")