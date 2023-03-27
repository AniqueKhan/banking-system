from django.db import models
from app_authentication.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError

# Create your models here.
class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name_plural = 'Branches'

    def __str__(self):
        return self.name

LOAN_TYPES = (('personal', 'Personal Loan'),('home', 'Home Loan'),('auto', 'Auto Loan'),('student', 'Student Loan'),('business', 'Business Loan'),('line_of_credit', 'Line of Credit'),)
LOAN_STATUS = (('pending', 'Pending'),('approved', 'Approved'),('rejected', 'Rejected'),)

class Loan(models.Model):
    loan_type = models.CharField(max_length=15, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    availed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    interest_rate = models.PositiveIntegerField(default=0,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    paid_at = models.DateTimeField(blank=True,null=True)
    loan_status = models.CharField(max_length=15, choices=LOAN_STATUS,default=LOAN_STATUS[0])


    def get_loan_amount_term(self):
        if self.paid_at:
            return self.created_at - self.paid_at
        return None

    def get_pay_loan_button(self):
        account = Account.objects.filter(hold_by=self.availed_by).first()
        total_amount = self.amount + (self.amount * self.interest_rate / 100)

        if not self.paid and account:
            return account.balance >= total_amount
        
        return False



ACCOUNT_TYPES = (('checking', 'Checking'),('savings', 'Savings'),('money_market', 'Money Market'),('cd', 'Certificate of Deposit'),('credit', 'Credit Card'),('loan', 'Loan'),)

class Account(models.Model):
    account_type = models.CharField(max_length=15, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    hold_by = models.ForeignKey(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.hold_by}"

TRANSACTION_TYPES = (('DEPOSIT', 'Deposit'),('WITHDRAWAL', 'Withdrawal'),('TRANSFER', 'Transfer'))

class Transaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    sent_by = models.ForeignKey(Account, on_delete=models.CASCADE)
    sent_to = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_transactions')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    description = models.CharField(max_length=255,blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sent_by.hold_by.account_name} sent {self.amount} to {self.sent_to.hold_by.account_name} from {self.branch.name}'

    def save(self,*args,**kwargs):
        if self.sent_by.balance < self.amount:
            raise ValidationError(f"Insufficient Balance in {self.sent_by} account")
        self.sent_by.balance-=self.amount
        self.sent_to.balance+=self.amount
        self.sent_by.save()
        self.sent_to.save()
        super().save(*args,**kwargs)


class Notification(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE,blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=90,blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user}"


def create_notification_on_loan_creation(sender, instance, created, **kwargs):
    if created:
        loan = instance
        user = loan.availed_by
        message = f"You took a loan of amount ${loan.amount} from {loan.branch}. The due date is {loan.due_at.date()}."
        Notification.objects.create(loan=loan, user=user, message=message)
post_save.connect(create_notification_on_loan_creation, sender=Loan)

def create_notification_on_loan_payment(sender,instance,created,**kwargs):
    loan = instance
    if not created and loan.paid:
        user = loan.availed_by
        message = f"Your loan of ${loan.amount} from {loan.branch} has been paid off!"
        Notification.objects.create(loan=loan,user=user,message=message)
post_save.connect(create_notification_on_loan_payment, sender=Loan)