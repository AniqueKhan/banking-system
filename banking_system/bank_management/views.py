from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from bank_management.models import Transaction,Branch,Account,Loan,Notification
from django.utils import timezone
import joblib
from datetime import timedelta
from app_authentication.models import User
from bank_management.forms import LoanRequestForm
from sklearn.metrics import accuracy_score
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
# Create your views here.

@login_required
def index(request):
    transactions_sent = Transaction.objects.filter(sent_by__hold_by=request.user).order_by("-timestamp")
    transactions_received = Transaction.objects.filter(sent_to__hold_by=request.user).order_by("-timestamp")
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
    transactions = Transaction.objects.filter(branch=branch).order_by("-timestamp")
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
    pending_loans = Loan.objects.filter(due_at__gte=timezone.now(),availed_by=request.user,paid=False,loan_status="Approved").order_by("-created_at")
    due_loans = Loan.objects.filter(due_at__lte=timezone.now(),availed_by=request.user,paid=False,loan_status="Approved").order_by("-created_at")
    for due_loan in due_loans:
        account = Account.objects.filter(hold_by=request.user).first()
        if account.balance > due_loan.amount:
            pay_loan(request,due_loan.pk)
    paid_loans = Loan.objects.filter(availed_by=request.user,paid=True,loan_status="Approved").order_by("-created_at")
    rejected_loans = Loan.objects.filter(availed_by=request.user,loan_status="Rejected",paid=False).order_by("-created_at")
    context={
        "due_loans":due_loans,
        "pending_loans":pending_loans,
        "paid_loans":paid_loans,
        "rejected_loans":rejected_loans,
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
def delete_notification(request,notification_id):
    Notification.objects.filter(id=notification_id,user=request.user).delete()
    return redirect("notifications")

def preprocessdata(Dependent,Applicant_Income,Coapplicant_Income,Loan_Amount,Loan_Amount_Term,
                   Credit_History,Loan_Amount_Log,Gender, Married, Education, Self_Employed, Property_Area):
    
    Gender_Female, Gender_Male = (0, 1) if Gender == "Male" else (1, 0)
    Married_No, Married_Yes = (0, 1) if Married == "Yes" else (1, 0)
    Education_Not_Graduated, Education_Graduated = (0, 1) if Education == "Graduated" else (1, 0)
    Self_Employed_No, Self_Employed_Yes = (0, 1) if Self_Employed == "Yes" else (1, 0)
    Property_Area_Rural, Property_Area_Urban = (0, 1) if Property_Area == "Urban" else (1, 0)

    test_data = [[Dependent, Applicant_Income, Coapplicant_Income, Loan_Amount,
       Loan_Amount_Term, Credit_History, Loan_Amount_Log,
       Gender_Female, Gender_Male, Married_No, Married_Yes,
       Education_Graduated, Education_Not_Graduated, Self_Employed_No,
       Self_Employed_Yes, Property_Area_Rural, Property_Area_Urban]]


    print(Dependent, Applicant_Income, Coapplicant_Income, Loan_Amount,
       Loan_Amount_Term, Credit_History, Loan_Amount_Log,
       Gender_Female, Gender_Male, Married_No, Married_Yes,
       Education_Graduated, Education_Not_Graduated, Self_Employed_No,
       Self_Employed_Yes, Property_Area_Rural, Property_Area_Urban)

    return joblib.load("model.pkl").predict(test_data)


@login_required
def loan_request(request):
    if request.method == "POST":
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            # Getting form variables
            account_name = form.cleaned_data['account_name']
            pan_number = form.cleaned_data['pan_number']
            loan_type = form.cleaned_data['loan_type']

            # Getting the user and his/her account
            user = User.objects.filter(account_name=account_name,pan_number=pan_number)[0]
            account = Account.objects.filter(hold_by=user)[0]

            # User Due Loans For Credit History
            user_due_loans = Loan.objects.filter(due_at__lte=timezone.now(),availed_by=user,paid=False)


            # Getting Model Data
            Gender = user.get_gender_display() 
            Married = user.get_married_display()
            Dependent = user.get_dependents_display()
            Education = user.get_education_display()  
            Self_Employed = user.get_self_employed_display() 
            Applicant_Income = user.applicant_income
            Coapplicant_Income = user.co_applicant_income if user.co_applicant_income else 0
            Loan_Amount = form.cleaned_data['loan_amount']
            Loan_Amount_Log = np.log(Loan_Amount)
            Loan_Amount_Term = form.cleaned_data['loan_amount_term']
            Credit_History = 1 if len(user_due_loans)==0 else 0
            Property_Area = user.get_property_area_display()
            print(Dependent,Applicant_Income,Coapplicant_Income,Loan_Amount,Loan_Amount_Term,
                   Credit_History,Loan_Amount_Log,Gender, Married, Education, Self_Employed, Property_Area)

            prediction = preprocessdata(Dependent=Dependent,Applicant_Income=Applicant_Income,
                        Coapplicant_Income=Coapplicant_Income,Loan_Amount=Loan_Amount,
                        Loan_Amount_Term=Loan_Amount_Term,Credit_History=Credit_History,
                        Loan_Amount_Log=Loan_Amount_Log,Gender=Gender, Married=Married, Education=Education, 
                        Self_Employed=Self_Employed, Property_Area=Property_Area)
            approved = True if prediction == ['Approved'] else False 
            bg_color = "9ff5b6" if approved else "f59f9f"
            
            loan = Loan.objects.create(loan_type=loan_type,amount=Loan_Amount,paid=False,branch=account.branch,availed_by=user,interest_rate=10,loan_status=prediction[0],due_at=timezone.now()+timedelta(days=Loan_Amount_Term))
                        
            return render(request,"loan-request-response.html",{"approved":approved,"loan":loan,"bg_color":bg_color})

    else:
        form = LoanRequestForm()
    # return render(request,"loan-request.html",{"form":form})
    return render(request,"1.html",{"form":form})