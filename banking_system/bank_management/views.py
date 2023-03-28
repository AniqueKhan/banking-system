from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from bank_management.models import Transaction,Branch,Account,Loan,Notification
from django.utils import timezone
import joblib
from app_authentication.models import User
from bank_management.forms import LoanRequestForm
# Create your views here.

@login_required
def index(request):
    transactions_sent = Transaction.objects.filter(sent_by__hold_by=request.user)
    transactions_received = Transaction.objects.filter(sent_to__hold_by=request.user)
    context ={
        "transactions_sent":transactions_sent,
        "transactions_received":transactions_received,
    }
    return render(request, "index.html",context)

def branches(request):
    branches = Branch.objects.all()
    context = {
        "branches":branches
    }
    return render(request, "branches.html",context)



def branch_detail(request,pk):
    branch=Branch.objects.get(pk=pk)
    transactions = Transaction.objects.filter(branch=branch)
    context = {
        "branch":branch,
        "transactions":transactions,
    }
    return render(request, "branch-detail.html",context)

@login_required
def my_profile(request):
    profile = request.user
    account = Account.objects.filter(hold_by=profile).first()
    context = {
        "account":account,
        "profile":profile,
    }
    return render(request,"my-profile.html",context)

def add_balance(request):
    if request.method == 'POST':
        account = Account.objects.filter(hold_by=request.user).first()
        amount = request.POST.get('amount')
        account.balance += int(amount)
        account.save()
    return redirect('my-profile')

@login_required
def pay_loan(request,loan_pk):
    loan = Loan.objects.get(pk=loan_pk)
    account = Account.objects.filter(hold_by=loan.availed_by).first()
    account.balance -= loan.amount
    account.save()
    loan.paid = True
    loan.paid_at = timezone.now()
    loan.save()
    return redirect("loans")

@login_required
def loans(request):
    pending_loans = Loan.objects.filter(due_at__gte=timezone.now(),availed_by=request.user,paid=False)
    due_loans = Loan.objects.filter(due_at__lte=timezone.now(),availed_by=request.user,paid=False)
    for due_loan in due_loans:
        account = Account.objects.filter(hold_by=request.user).first()
        if account.balance > due_loan.amount:
            pay_loan(request,due_loan.pk)
    paid_loans = Loan.objects.filter(availed_by=request.user,paid=True)
    context={
        "due_loans":due_loans,
        "pending_loans":pending_loans,
        "paid_loans":paid_loans,
    }
    return render(request,"loans.html",context=context)

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-date')
    notifications.update(is_seen=True)
    context = {
        "notifications":notifications,
    }
    return render(request,"notifications.html",context=context)

@login_required
def count_notifications(request):
    count_notifications = Notification.objects.filter(user=request.user,is_seen=False).count()
    return {"count_notifications":count_notifications}

@login_required
def delete_notification(request,notification_id):
    Notification.objects.filter(id=notification_id,user=request.user).delete()
    return redirect("notifications")

def preprocessdata(Gender, Married,Dependent, Education, Self_Employed, Applicant_Income,
       Coapplicant_Income, Loan_Amount, Loan_Amount_Term, Credit_History,
       Property_Area):
    test_data = [[Gender, Married,Dependent, Education, Self_Employed, Applicant_Income,
       Coapplicant_Income, Loan_Amount, Loan_Amount_Term, Credit_History,
       Property_Area]]  
    trained_model = joblib.load("model2.pkl") 
    prediction = trained_model.predict(test_data) 

    return prediction 


@login_required
def loan_request(request):
    if request.method == "POST":
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            # Getting form variables
            account_name = form.cleaned_data['account_name']
            pan_number = form.cleaned_data['pan_number']

            # Getting the user and his/her account
            user = User.objects.filter(account_name=account_name,pan_number=pan_number)[0]
            account = Account.objects.filter(hold_by=user)[0]

            # User Due Loans For Credit History
            user_due_loans = Loan.objects.filter(due_at__lte=timezone.now(),availed_by=user,paid=False)


            # Getting Model Data
            Gender = 1 if user.get_gender_display() == "Male" else 0
            Married = 1 if user.get_married_display() == "Yes" else 0
            Dependent = user.get_dependents_display()
            Education = 1 if user.get_education_display() == "Not Graduated" else 0 
            Self_Employed = 1 if user.get_self_employed_display() == "Yes" else 0
            Applicant_Income = 1#user.applicant_income
            Coapplicant_Income = 1#user.co_applicant_income
            Loan_Amount = form.cleaned_data['loan_amount']
            Loan_Amount_Term = form.cleaned_data['loan_amount_term']
            Credit_History = 1 if len(user_due_loans)==0 else 0
            Property_Area = 1 if user.get_property_area_display() == "Urban" else 0
            print(Gender, Married, Dependent, Education, Self_Employed, Applicant_Income, Coapplicant_Income, Loan_Amount, Loan_Amount_Term, Credit_History, Property_Area)

            prediction = preprocessdata(Gender, Married, Dependent, Education, Self_Employed, Applicant_Income, Coapplicant_Income, Loan_Amount, Loan_Amount_Term, Credit_History, Property_Area)
            prediction = "Approved" if prediction == 1 else "Rejected"
            return render(request,"loan-request-response.html",{"prediction":prediction})

    else:
        form = LoanRequestForm()
    return render(request,"loan-request.html",{"form":form})