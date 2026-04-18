from django.shortcuts import get_object_or_404, redirect
from payments.models import Wallet, EscrowTransaction
from jobs.models import Job
from django.http import HttpResponseForbidden


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from jobs.models import Job
from .models import Wallet, EscrowTransaction

def fund_escrow(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    employer_wallet, created = Wallet.objects.get_or_create(
        user=request.user
    )

    amount = job.budget

    if employer_wallet.balance < amount:
        messages.error(request, "Insufficient wallet balance")
        return redirect('employer:employer_dashboard')

    employer_wallet.balance -= amount
    employer_wallet.save()

    EscrowTransaction.objects.create(
        job=job,
        employer=request.user,
        freelancer=job.freelancer,
        amount=amount
    )

    messages.success(request, "Escrow funded successfully")
    return redirect('employer:employer_dashboard')
def release_payment(request, job_id):
    escrow = get_object_or_404(EscrowTransaction, job_id=job_id)

    if escrow.released:
        return HttpResponse("Already released")

    freelancer_wallet = Wallet.objects.get(user=escrow.freelancer)

    freelancer_wallet.balance += escrow.amount
    freelancer_wallet.save()

    escrow.released = True
    escrow.save()

    return redirect('jobs:employer_dashboard')
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Wallet

@login_required
def deposit_money(request):
    if request.method == "POST":
        amount = float(request.POST.get("amount"))

        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += amount
        wallet.save()

        messages.success(request, f"${amount} added to your wallet")
        return redirect('employer:employer_dashboard')

    return render(request, "payments/deposit.html")