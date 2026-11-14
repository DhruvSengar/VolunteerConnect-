from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from accounts.models import Organization
from .forms import HourLogForm, OpportunityForm, ReviewForm
from .models import Cause, Certificate, HourLog, Milestone, Opportunity, Review, Signup

def opportunity_list(request):
    qs = Opportunity.objects.filter(is_active=True, organization__status='approved').select_related('organization').prefetch_related('causes')
    query = request.GET.get('q', '').strip()
    if query: qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
    return render(request, 'core/opportunity_list.html', {'opportunities': qs.order_by('event_date'), 'causes': Cause.objects.all(), 'query': query})

def opportunity_search(request):
    query = request.GET.get('q', '').strip()
    qs = Opportunity.objects.filter(is_active=True, organization__status='approved').filter(Q(title__icontains=query) | Q(location__icontains=query))[:10]
    return JsonResponse({'results': [{'id': x.id, 'title': x.title, 'location': x.location, 'slots': x.available_slots} for x in qs]})

def opportunity_detail(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    is_organizer = request.user.is_authenticated and opportunity.organization.coordinators.filter(pk=request.user.pk).exists()
    return render(request, 'core/opportunity_detail.html', {'opportunity': opportunity, 'is_organizer': is_organizer})

@login_required
def opportunity_create(request):
    org = Organization.objects.filter(coordinators=request.user, status='approved').first()
    if not org: return render(request, 'message.html', {'message': 'You need an approved organization to create opportunities.'})
    form = OpportunityForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False); obj.organization = org; obj.save(); form.save_m2m(); messages.success(request, 'Opportunity created.'); return redirect('opportunity-detail', obj.pk)
    return render(request, 'core/opportunity_form.html', {'form': form, 'title': 'Create opportunity'})

@login_required
def opportunity_edit(request, pk):
    obj = get_object_or_404(Opportunity, pk=pk, organization__coordinators=request.user)
    form = OpportunityForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid(): form.save(); return redirect('opportunity-detail', pk)
    return render(request, 'core/opportunity_form.html', {'form': form, 'title': 'Edit opportunity'})

@login_required
def opportunity_delete(request, pk):
    obj = get_object_or_404(Opportunity, pk=pk, organization__coordinators=request.user)
    if request.method == 'POST': obj.delete(); messages.success(request, 'Opportunity deleted.')
    return redirect('opportunity-list')

@login_required
def apply(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk, is_active=True)
    if opportunity.organization.coordinators.filter(pk=request.user.pk).exists():
        messages.error(request, 'Organizers cannot apply to their own opportunities.')
        return redirect('opportunity-detail', pk)
    try: Signup.objects.create(volunteer=request.user, opportunity=opportunity)
    except IntegrityError: messages.error(request, 'You have already applied.')
    else: messages.success(request, 'Application submitted.')
    return redirect('opportunity-detail', pk)

@login_required
def manage_signups(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk, organization__coordinators=request.user)
    if request.method == 'POST':
        signup = get_object_or_404(Signup, pk=request.POST.get('signup_id'), opportunity=opportunity)
        decision = request.POST.get('decision')
        with transaction.atomic():
            if decision == 'confirmed' and opportunity.available_slots <= 0: messages.error(request, 'No available capacity.'); return redirect('manage-signups', pk)
            signup.status = decision; signup.save(update_fields=['status', 'updated_at'])
        return redirect('manage-signups', pk)
    return render(request, 'core/manage_signups.html', {'opportunity': opportunity, 'signups': opportunity.signups.select_related('volunteer')})

@login_required
def submit_hours(request, signup_id):
    signup = get_object_or_404(Signup, volunteer=request.user, pk=signup_id, status__in=['confirmed', 'completed'])
    form = HourLogForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        log = form.save(commit=False); log.signup = signup; log.save(); signup.status = 'completed'; signup.save(update_fields=['status']); return redirect('dashboard')
    return render(request, 'core/hour_form.html', {'form': form, 'signup': signup})

@login_required
def verify_hours(request, log_id):
    log = get_object_or_404(HourLog, pk=log_id, signup__opportunity__organization__coordinators=request.user)
    if request.method == 'POST':
        log.status = request.POST.get('decision'); log.verified_by = request.user; log.verified_at = timezone.now(); log.save()
        if log.status == 'verified':
            total = sum(x.hours for x in HourLog.objects.filter(signup__volunteer=log.signup.volunteer, status='verified'))
            for milestone in Milestone.objects.filter(is_active=True, required_hours__lte=total):
                Certificate.objects.get_or_create(volunteer=log.signup.volunteer, milestone=milestone)
        return redirect('dashboard')
    return render(request, 'core/verify_hours.html', {'log': log})

@login_required
def certificates(request):
    return render(request, 'core/certificates.html', {'certificates': Certificate.objects.filter(volunteer=request.user).select_related('milestone')})

def certificate_verify(request, certificate_id):
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    return render(request, 'core/certificate_verify.html', {'certificate': certificate})

@login_required
def certificate_pdf(request, certificate_id):
    from django.http import HttpResponse
    from reportlab.pdfgen import canvas
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, volunteer=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate-{certificate.certificate_id}.pdf"'
    page = canvas.Canvas(response); page.setTitle('VolunteerConnect Certificate')
    page.drawCentredString(300, 700, 'VOLUNTEERCONNECT')
    page.drawCentredString(300, 640, 'Certificate of Service')
    page.drawCentredString(300, 570, f'Awarded to {certificate.volunteer.get_full_name() or certificate.volunteer.username}')
    page.drawCentredString(300, 520, f'For completing {certificate.milestone.required_hours} verified service hours')
    page.drawCentredString(300, 450, f'Certificate ID: {certificate.certificate_id}')
    page.drawCentredString(300, 410, f'Issued: {certificate.issued_at.date()}')
    page.save(); return response

@login_required
def review(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    if not opportunity.signups.filter(volunteer=request.user, status='completed').exists(): raise Http404
    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False); obj.volunteer = request.user; obj.opportunity = opportunity; obj.save(); return redirect('opportunity-detail', pk)
    return render(request, 'core/review_form.html', {'form': form, 'opportunity': opportunity})
