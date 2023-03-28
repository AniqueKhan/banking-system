import django,os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from app_authentication.models import User
from faker import Faker
from django.utils import timezone
from bank_management.models import Loan, Branch,Account


fake = Faker()

# Create 10 Loan instances
for i in range(100):
    # Choose a random loan type
    loan_type = fake.random_element(elements=('personal', 'home', 'auto', 'student', 'business', 'line_of_credit'))

    # Generate a random loan amount
    amount = fake.pydecimal(left_digits=5, right_digits=2, positive=True, min_value=100, max_value=10000)

    # Choose a random branch
    branch = Branch.objects.order_by('?').first()

    # Choose a random user to avail the loan
    user = User.objects.order_by('?').first()
    user_due_loans =  Loan.objects.filter(due_at__lte=timezone.now(),availed_by=user,paid=False)
    user_pending_loans =  Loan.objects.filter(due_at__gte=timezone.now(),availed_by=user,paid=False)
    account=Account.objects.filter(hold_by=user).first()
    print(f"Pending Loans :{user_pending_loans.count()}")


    # Generate a random interest rate
    interest_rate = fake.pyint(min_value=0, max_value=45)

    # Generate a random due date
    due_at = fake.date_time_between(start_date='+10d', end_date='+365d', tzinfo=timezone.get_current_timezone())

    # Create the Loan instance
    loan = Loan(
        loan_type=loan_type,
        amount=amount,
        branch=branch,
        availed_by=user,
        interest_rate=interest_rate,
        due_at=due_at
    )

    # Save the Loan instance
    loan.save()
    print(loan)

print(len(Loan.objects.filter(loan_status="Approved")))
print(len(Loan.objects.filter(loan_status="Rejected")))
