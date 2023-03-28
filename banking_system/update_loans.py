import django,os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from datetime import timedelta 
import random
from bank_management.models import Loan

# Get 800 random loans
loans = Loan.objects.filter(done=False).order_by('?')[:100]

# Loop through each loan and update the paid and paid_at fields
for loan in loans:
    loan.done = True
    loan.paid_at = loan.created_at + timedelta(days=random.randint(1, 365))
    
# Bulk update the loans
Loan.objects.bulk_update(loans, ['done', 'paid_at'])

print(Loan.objects.filter(done=False).count())
print(Loan.objects.filter(done=True).count())