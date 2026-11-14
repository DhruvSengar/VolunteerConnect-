import csv
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum
from core.models import HourLog, Signup

@login_required
def report(request):
    hours = HourLog.objects.filter(signup__volunteer=request.user, status='verified').aggregate(total=Sum('hours'))['total'] or 0
    return render(request, 'reports/report.html', {'hours': hours, 'signups': Signup.objects.filter(volunteer=request.user).count()})

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="volunteer-hours.csv"'
    writer = csv.writer(response); writer.writerow(['Opportunity', 'Hours', 'Status', 'Submitted'])
    for log in HourLog.objects.filter(signup__volunteer=request.user).select_related('signup__opportunity'):
        writer.writerow([log.signup.opportunity.title, log.hours, log.status, log.submitted_at.date()])
    return response

@login_required
def pdf_report(request):
    from reportlab.pdfgen import canvas
    hours = HourLog.objects.filter(signup__volunteer=request.user, status='verified').aggregate(total=Sum('hours'))['total'] or 0
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="volunteer-report.pdf"'
    page = canvas.Canvas(response); page.setTitle('VolunteerConnect Service Report')
    page.drawString(72, 750, 'VolunteerConnect Service Report')
    page.drawString(72, 710, f'Volunteer: {request.user.get_full_name() or request.user.username}')
    page.drawString(72, 680, f'Verified service hours: {hours}')
    page.drawString(72, 650, f'Applications: {Signup.objects.filter(volunteer=request.user).count()}')
    y = 600
    for log in HourLog.objects.filter(signup__volunteer=request.user).select_related('signup__opportunity')[:12]:
        page.drawString(72, y, f'{log.signup.opportunity.title[:55]} | {log.hours} hours | {log.status}')
        y -= 22
    page.save(); return response
