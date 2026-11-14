from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from .forms import OrganizationForm, ProfileForm, RegistrationForm
from .models import Organization, VolunteerProfile

def home(request):
    return render(request, 'home.html')

def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        if form.cleaned_data['role'] == 'volunteer':
            VolunteerProfile.objects.create(user=user)
        login(request, user)
        if form.cleaned_data['role'] == 'coordinator':
            messages.success(request, 'Account created. Register your organization for approval.')
            return redirect('organization-create')
        messages.success(request, 'Welcome to VolunteerConnect.')
        return redirect('dashboard')
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    obj, _ = VolunteerProfile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def organization_create(request):
    form = OrganizationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        org = form.save()
        org.coordinators.add(request.user)
        messages.success(request, 'Organization submitted for approval.')
        return redirect('dashboard')
    return render(request, 'accounts/organization_form.html', {'form': form})

def organization_list(request):
    return render(request, 'accounts/organization_list.html', {'organizations': Organization.objects.filter(status='approved').prefetch_related('opportunities')})

@login_required
def dashboard(request):
    from core.models import HourLog, Opportunity, Signup
    hours = sum(x.hours for x in HourLog.objects.filter(signup__volunteer=request.user, status='verified'))
    organizations = Organization.objects.filter(coordinators=request.user)
    managed = Opportunity.objects.filter(organization__in=organizations).select_related('organization')
    return render(request, 'dashboard.html', {'opportunities': Opportunity.objects.filter(is_active=True).select_related('organization')[:6], 'signups': Signup.objects.filter(volunteer=request.user).select_related('opportunity'), 'verified_hours': hours, 'organizations': organizations, 'managed_opportunities': managed})

@user_passes_test(lambda user: user.is_superuser)
def organization_approval(request):
    if request.method == 'POST':
        org = get_object_or_404(Organization, pk=request.POST.get('org_id'))
        org.status = request.POST.get('decision')
        org.approved_by = request.user
        org.save(update_fields=['status', 'approved_by'])
        return redirect('organization-approval')
    return render(request, 'accounts/organization_approval.html', {'organizations': Organization.objects.filter(status='pending')})
