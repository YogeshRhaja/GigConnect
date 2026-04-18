#jobs\views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Job, Proposal
from profiles.models import FreelancerSkill
from recommendations.utils import calculate_match
from django.contrib.auth.models import User
from .models import Job, Proposal, ProjectChat, Message
from .models import Job, JobInvite
from payments.models import Wallet
# ----------------- EMPLOYER DASHBOARD -----------------
@login_required
def employer_dashboard(request):
    role = getattr(request.user.account_profile, 'role', None)
    if role != 'employer':
        return HttpResponseForbidden("Access denied")

    jobs = Job.objects.filter(employer=request.user)
    freelancers = FreelancerSkill.objects.select_related('freelancer')
    recommended_freelancers = []

    for job in jobs:
        if not job.skills_required:
            continue
        for fs in freelancers:
            score = calculate_match(fs.skills, job.skills_required)
            if score > 0:
                recommended_freelancers.append({
                    'freelancer': fs.freelancer,
                    'skills': fs.skills,
                    'skills_list': [s.strip() for s in fs.skills.split(',') if s.strip()],
                    'job': job,
                    'score': score,
                    'already_invited': JobInvite.objects.filter(
                        job=job,
                        freelancer=fs.freelancer
                    ).exists(),
                })

    recommended_freelancers = sorted(
        recommended_freelancers,
        key=lambda x: x['score'],
        reverse=True
    )

    submissions = Proposal.objects.filter(
        job__employer=request.user,
        submission__isnull=False
    ).select_related('job', 'freelancer')

    # ✅ ADD THIS
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    return render(request, 'jobs/employer_dashboard.html', {
        'jobs': jobs,
        'recommended_freelancers': recommended_freelancers,
        'submissions': submissions,
        'wallet': wallet,   # ✅ ADD THIS
    })
@login_required
def post_job(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        skills_required = request.POST.get('skills_required')
        budget = request.POST.get('budget')
        deadline = request.POST.get('deadline')

        if not all([title, description, skills_required, budget, deadline]):
            messages.error(request, "All fields are required")
            return redirect('post_job')

        Job.objects.create(
            employer=request.user,
            title=title,
            description=description,
            skills_required=skills_required,
            budget=budget,
            deadline=deadline
        )

        messages.success(request, "Job posted successfully!")
        return redirect('employer:employer_dashboard')

    return render(request, 'jobs/post_job.html')


@login_required
def view_proposals(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # role check
    if request.user.account_profile.role != 'employer':
        return HttpResponseForbidden("Access denied")

    # ownership check
    if job.employer != request.user:
        return HttpResponseForbidden("Not your job")

    proposals = Proposal.objects.filter(job=job)

    return render(
        request,
        'jobs/view_proposals.html',
        {
            'job': job,
            'proposals': proposals
        }
    )
@login_required
def accept_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    if proposal.job.employer != request.user:
        return HttpResponseForbidden("Not your job")
    proposal.status = 'accepted'
    proposal.save()
    job = proposal.job
    job.freelancer = proposal.freelancer
    job.save()
    ProjectChat.objects.get_or_create(job=job)
    messages.success(request, "Proposal accepted and chat opened.")
    return redirect('jobs:view_proposals', job_id=job.id)
@login_required
def reject_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)

    if request.user.account_profile.role != 'employer':
        return HttpResponseForbidden("Access denied")

    if proposal.job.employer != request.user:
        return HttpResponseForbidden("Not your job")

    proposal.status = 'rejected'
    proposal.save()

    messages.info(request, "Proposal rejected.")
    return redirect('jobs:view_proposals', job_id=proposal.job.id)



# ----------------- FREELANCER DASHBOARD (AI RECOMMENDATION) -----------------

# jobs/views.py
# jobs/views.py
@login_required
def freelancer_dashboard(request):
    if request.user.account_profile.role != 'freelancer':
        return HttpResponseForbidden("Access denied")

    jobs = Job.objects.all()

    # Get freelancer skills
    try:
        freelancer_skill = FreelancerSkill.objects.get(freelancer=request.user)
        freelancer_skills_text = freelancer_skill.skills
    except FreelancerSkill.DoesNotExist:
        freelancer_skills_text = ""

    recommended_jobs = []

    for job in jobs:
        if not job.skills_required:
            continue

        match = calculate_match(freelancer_skills_text, job.skills_required)
        if match > 0:
            recommended_jobs.append((job, match))

    recommended_jobs.sort(key=lambda x: x[1], reverse=True)
    recommended_jobs_only = [job for job, score in recommended_jobs]

    # ✅ Pending invites
    invites = JobInvite.objects.filter(
        freelancer=request.user,
        status='pending'
    ).select_related('job', 'employer')

    # ✅ Accepted projects (proposal accepted)
    accepted_proposals = Proposal.objects.filter(
        freelancer=request.user,
        status='accepted'
    ).select_related('job', 'job__employer')

    return render(
        request,
        'jobs/freelancer_dashboard.html',
        {
            'jobs': jobs,
            'recommended_jobs': recommended_jobs_only,
            'invites': invites,
            'accepted_proposals': accepted_proposals  # new
        }
    )

# ----------------- HOME REDIRECT -----------------

def home(request):
    if request.user.is_authenticated:
        role = request.user.account_profile.role
        if role == 'freelancer':
            return redirect('freelancer:freelancer_dashboard')
        return redirect('employer:employer_dashboard')
    return redirect('accounts:login')
@login_required
def apply_job(request, job_id):
    # Only freelancers can apply
    if request.user.account_profile.role != 'freelancer':
        return HttpResponseForbidden("Access denied")

    job = get_object_or_404(Job, id=job_id)

    # Prevent duplicate application
    if Proposal.objects.filter(job=job, freelancer=request.user).exists():
        messages.warning(request, "You already applied.")
        return redirect('freelancer:freelancer_dashboard')

    if request.method == 'POST':
        Proposal.objects.create(
            job=job,
            freelancer=request.user,
            bid_amount=job.budget,          # default value
            cover_letter="Applied via system"
        )

        messages.success(request, "Proposal submitted successfully.")
        return redirect('freelancer:freelancer_dashboard')

    return render(request, 'jobs/apply_job.html', {'job': job})
from .models import JobInvite
@login_required
def invite_freelancer(request, job_id, freelancer_id):

    if request.method != "POST":
        return HttpResponseForbidden("Invalid request")

    if request.user.account_profile.role != 'employer':
        return HttpResponseForbidden("Access denied")

    job = get_object_or_404(Job, id=job_id)

    if job.employer != request.user:
        return HttpResponseForbidden("Not your job")

    freelancer = get_object_or_404(User, id=freelancer_id)

    if JobInvite.objects.filter(job=job, freelancer=freelancer).exists():
        messages.warning(request, f"You already invited {freelancer.username}.")
        return redirect('employer:employer_dashboard')  # ← fixed namespace

    JobInvite.objects.create(
        job=job,
        employer=request.user,
        freelancer=freelancer,
        message="We would like to invite you for this job."
    )

    messages.success(request, f"Invitation sent to {freelancer.username} for '{job.title}'.")
    return redirect('employer:employer_dashboard')  # ← fixed namespace
@login_required
def accept_invite(request, invite_id):
    invite = get_object_or_404(JobInvite, id=invite_id)

    if invite.freelancer != request.user:
        return HttpResponseForbidden("Access denied")

    # Mark invite accepted
    invite.status = 'accepted'
    invite.save()

    job = invite.job

    # Assign freelancer to job
    job.freelancer = request.user
    job.save()

    # Create accepted proposal
    Proposal.objects.create(
        job=job,
        freelancer=request.user,
        bid_amount=job.budget,
        cover_letter="Accepted invitation",
        status='accepted'
    )

    # Create chat
    ProjectChat.objects.get_or_create(job=job)

    messages.success(request, "Invitation accepted. Chat is now open.")
    return redirect('freelancer:freelancer_dashboard')

@login_required
def decline_invite(request, invite_id):
    invite = get_object_or_404(JobInvite, id=invite_id)

    if invite.freelancer != request.user:
        return HttpResponseForbidden("Access denied")

    invite.status = 'declined'
    invite.save()

    messages.info(request, "Invitation declined.")
    return redirect('freelancer:freelancer_dashboard')
@login_required
def mark_project_completed(request, proposal_id):
    # Fetch the proposal
    proposal = get_object_or_404(Proposal, id=proposal_id)

    # Ensure only the assigned freelancer can mark as complete
    if proposal.freelancer != request.user:
        return HttpResponseForbidden("Access denied")

    # Mark proposal as completed
    proposal.status = 'completed'
    proposal.save()

    # Mark job as completed
    job = proposal.job
    job.is_completed = True
    job.save()

    # Deactivate related chat if exists
    if hasattr(job, 'chat') and job.chat:
        job.chat.is_active = False
        job.chat.save()

    # Feedback message
    messages.success(request, f"Project '{job.title}' marked as completed.")
    return redirect('jobs:freelancer_dashboard')

@login_required
def upload_submission(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)

    if proposal.freelancer != request.user:
        return HttpResponseForbidden("Access denied")

    if request.method == 'POST' and request.FILES.get('file'):
        proposal.submission = request.FILES['file']
        proposal.status = 'completed'   # mark submitted
        proposal.save()
        messages.success(request, "Submission uploaded successfully.")
        return redirect('jobs:freelancer_dashboard')

    return render(request, 'jobs/upload_submission.html', {'proposal': proposal})
# --------------------------
# Job chat view
# --------------------------
@login_required
def job_chat(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if not job.freelancer:
        return HttpResponseForbidden("Chat not available.")

    if job.is_completed:
        return HttpResponseForbidden("Project completed. Chat closed.")

    if request.user not in [job.employer, job.freelancer]:
        return HttpResponseForbidden("You are not allowed to access this chat.")

    chat = get_object_or_404(ProjectChat, job=job)
    # Prevent sending message if inactive
    if request.method == 'POST':
        if not chat.is_active:
            return HttpResponseForbidden("Chat is closed.")

        content = request.POST.get('message')
        if content:
            Message.objects.create(
                chat=chat,
                sender=request.user,
                content=content
            )
            return redirect('jobs:job_chat', job_id=job_id)

    messages_list = chat.messages.order_by('timestamp')

    return render(request, 'jobs/job_chat.html', {
        'chat': chat,
        'messages': messages_list
    })

# --------------------------
# Freelancer accepts a proposal
# --------------------------
@login_required
def freelancer_accept_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)

    # Only the freelancer can accept
    if proposal.freelancer != request.user:
        return HttpResponseForbidden("Access denied")

    job = proposal.job  # changed from project to job
    job.freelancer = proposal.freelancer
    job.status = 'accepted'  # make sure 'status' field exists on Job model
    job.save()
    ProjectChat.objects.get_or_create(job=job)
    messages.success(request, f"You accepted the job '{job.title}'.")
    return redirect('jobs:freelancer_dashboard')
def employer_submissions(request):
    proposals = Proposal.objects.filter(
    job__employer=request.user,
    status='completed'
    )
    return render(request, 'jobs/employer_submissions.html', {
            'proposals': proposals
        })
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from payments.models import EscrowTransaction, Wallet
from .models import Proposal

@login_required
def approve_project(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)

    # security check
    if proposal.job.employer != request.user:
        return HttpResponseForbidden()

    # mark approved
    proposal.status = 'approved'
    proposal.save()

    # release escrow
    escrow = EscrowTransaction.objects.filter(job=proposal.job).first()

    if escrow and not escrow.released:
        freelancer_wallet, created = Wallet.objects.get_or_create(
            user=escrow.freelancer
        )

        freelancer_wallet.balance += escrow.amount
        freelancer_wallet.save()

        escrow.released = True
        escrow.save()

    messages.success(request, "Project approved and payment released.")
    return redirect('jobs:employer_submissions')
@login_required
def reject_project(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)

    if proposal.job.employer != request.user:
        return HttpResponseForbidden()

    proposal.status = 'pending'
    proposal.save()

    messages.warning(request, "Project rejected. Ask for revision.")
    return redirect('jobs:employer_submissions')