from faker import Faker
import django,os,rstr

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from app_authentication.models import User
from bank_management.models import Branch,Account

fake = Faker()

for i in range(18):
    account_name = fake.user_name()
    pan_number = rstr.xeger('^[A-Z]{3}P[A-Z][0-9]{4}K$')
    phone = rstr.xeger('^\+?1?\d{9,15}$')
    address = fake.address()
    self_employed = fake.random_element(elements=('yes', 'no'))
    # self_employed = fake.random_element(elements=('yes',))
    married = fake.random_element(elements=('yes', 'no'))
    gender = fake.random_element(elements=('male', 'female'))
    dependents = fake.random_int(min=0, max=4)
    # dependents = fake.random_int(min=0, max=3)
    education = fake.random_element(elements=('graduated', 'not_graduated'))
    # education = fake.random_element(elements=('graduated',))
    applicant_income = fake.random_int(min=0, max=100000)
    # applicant_income = fake.random_int(min=40000, max=100000)
    co_applicant_income = fake.random_int(min=0, max=100000)
    property_area = fake.random_element(elements=('urban', 'rural'))
    user = User.objects.create_user(account_name=account_name, pan_number=pan_number, phone=phone, address=address, self_employed=self_employed, married=married, gender=gender, dependents=dependents, education=education, applicant_income=applicant_income, co_applicant_income=co_applicant_income, property_area=property_area)
    print(f"Created User : {user}")
    balance = fake.random_int(min=0,max=90000)
    account_type = fake.random_element(elements=("checking",'savings','money_market','cd','credit','loan'))
    branch = Branch.objects.order_by("?").first()
    account = Account.objects.create(branch=branch,hold_by=user,balance=balance,account_type=account_type)
    print(f"Created Account : {account}")