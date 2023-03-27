from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from bank_management.models import Transaction,Branch,Account,Loan,Notification
from django.utils import timezone
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