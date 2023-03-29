import django,os,random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')
django.setup()

from faker import Faker
from bank_management.models import Account, Branch, Transaction, TRANSACTION_TYPES

fake = Faker()

# Get a list of all the accounts and branches
accounts = Account.objects.all()
branches = Branch.objects.all()

# Generate transactions
for i in range(1000):
    # Choose a random transaction type
    transaction_type = random.choice(TRANSACTION_TYPES)[0]

    # Choose a random account to send the money from
    sent_by = random.choice(accounts)

    # Choose a random account to receive the money
    sent_to = random.choice(accounts.exclude(pk=sent_by.pk))

    # Choose a random branch
    branch = random.choice(branches)

    # Generate a random amount
    amount = fake.pydecimal(left_digits=5, right_digits=2, positive=True, min_value=10, max_value=10000)

    if sent_by.balance < amount:
        print(f"Transaction failed Because {sent_by} does not have enough balance")
        continue

    # Generate a random description
    description = fake.sentence() if random.choice([True, False]) else None

    # Create the transaction
    transaction = Transaction(
        amount=amount,
        transaction_type=transaction_type,
        sent_by=sent_by,
        sent_to=sent_to,
        branch=branch,
        description=description,
    )

    # Save the transaction
    transaction.save()

    print(f"{transaction}")
