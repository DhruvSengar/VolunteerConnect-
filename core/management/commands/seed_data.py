from datetime import time, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import Organization, VolunteerProfile
from core.models import Cause, Certificate, HourLog, Milestone, Opportunity, Review, Signup

DEMO_PASSWORD = 'demo-pass-2026'

CAUSES = [
    ('Environment', 'environment', 'Clean-ups, tree planting and waste drives.'),
    ('Education', 'education', 'Tutoring, reading sessions and exam help.'),
    ('Health', 'health', 'Blood drives, health camps and first aid.'),
    ('Food security', 'food-security', 'Meal packing and community kitchens.'),
    ('Animal welfare', 'animal-welfare', 'Shelter care and adoption days.'),
]

ORGANIZATIONS = [
    ('Green Sector Collective', 'approved', 'Neighbourhood clean-ups and tree planting across Noida sectors.', 'Sector 62, Noida'),
    ('Padhai Saathi', 'approved', 'Weekend tutoring for school students in Classes 6 to 10.', 'Sector 18, Noida'),
    ('Annapurna Food Bank', 'approved', 'Collects surplus food and packs meal kits for families.', 'Laxmi Nagar, Delhi'),
    ('Paws Shelter Trust', 'pending', 'Rescue, care and adoption for stray dogs and cats.', 'Indirapuram, Ghaziabad'),
]

# (organization, title, causes, location, days from today, start hour, end hour, capacity, requirements)
OPPORTUNITIES = [
    ('Green Sector Collective', 'Okhla Bird Sanctuary clean-up', ['environment'], 'Okhla Bird Sanctuary, Noida', 6, 7, 11, 30, 'Closed shoes, a water bottle and a cap.'),
    ('Green Sector Collective', 'Monsoon tree planting drive', ['environment'], 'Sector 62 park, Noida', 13, 8, 12, 40, 'Gloves are provided.'),
    ('Green Sector Collective', 'E-waste collection day', ['environment'], 'Sector 18 market, Noida', 20, 10, 16, 15, ''),
    ('Padhai Saathi', 'Maths tutoring for Class 8', ['education'], 'Community hall, Sector 18, Noida', 4, 15, 17, 12, 'Comfortable with Class 8 maths. Two Saturdays a month.'),
    ('Padhai Saathi', 'Reading hour at the library', ['education'], 'Public library, Sector 15, Noida', 9, 11, 13, 10, ''),
    ('Annapurna Food Bank', 'Weekend meal kit packing', ['food-security'], 'Warehouse, Laxmi Nagar, Delhi', 3, 9, 13, 25, 'Hair covered and hands washed on arrival.'),
    ('Annapurna Food Bank', 'Community kitchen evening shift', ['food-security', 'health'], 'Shakarpur, Delhi', 11, 17, 21, 8, ''),
    ('Annapurna Food Bank', 'Blood donation camp support', ['health'], 'Laxmi Nagar metro station, Delhi', 17, 9, 15, 20, 'Help with registration and refreshments.'),
]

VOLUNTEERS = [
    ('aarav', 'Aarav', 'Mehta', 'Environment and teaching', 'Engineering student who likes weekend drives.'),
    ('meera', 'Meera', 'Iyer', 'Food security', 'Works in Noida and volunteers on Sundays.'),
    ('kabir', 'Kabir', 'Singh', 'Education', ''),
]

COORDINATORS = [
    ('ritu', 'Ritu', 'Sharma', ['Green Sector Collective', 'Padhai Saathi']),
    ('dev', 'Dev', 'Malhotra', ['Annapurna Food Bank']),
    ('sana', 'Sana', 'Qureshi', ['Paws Shelter Trust']),
]


class Command(BaseCommand):
    help = 'Fill the database with demo organizations, opportunities, volunteers and hours. Safe to run more than once.'

    def handle(self, *args, **options):
        # The demo accounts share one known password, so never create them on a production database.
        if not settings.DEBUG:
            raise CommandError('seed_data only runs with DEBUG = True.')
        if not Milestone.objects.exists():
            raise CommandError('No milestones found. Run "python manage.py migrate" first.')
        with transaction.atomic():
            self.seed()
        self.stdout.write(self.style.SUCCESS('Demo data ready.'))
        self.stdout.write(f'Volunteers: {", ".join(v[0] for v in VOLUNTEERS)}. Coordinators: {", ".join(c[0] for c in COORDINATORS)}.')
        self.stdout.write(f'Password for every demo account: {DEMO_PASSWORD}')

    def user(self, username, first, last):
        user, created = User.objects.get_or_create(username=username, defaults={'first_name': first, 'last_name': last, 'email': f'{username}@volunteerconnect.example'})
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        return user

    def seed(self):
        causes = {slug: Cause.objects.get_or_create(slug=slug, defaults={'name': name, 'description': text})[0] for name, slug, text in CAUSES}

        orgs = {}
        for name, status, text, address in ORGANIZATIONS:
            slug = name.lower().replace(' ', '')
            orgs[name], _ = Organization.objects.get_or_create(name=name, defaults={'status': status, 'description': text, 'address': address, 'email': f'hello@{slug}.example'})
        for username, first, last, org_names in COORDINATORS:
            user = self.user(username, first, last)
            for org_name in org_names:
                orgs[org_name].coordinators.add(user)

        volunteers = {}
        for username, first, last, interests, bio in VOLUNTEERS:
            volunteers[username] = self.user(username, first, last)
            VolunteerProfile.objects.get_or_create(user=volunteers[username], defaults={'interests': interests, 'bio': bio})

        today = timezone.localdate()
        opps = {}
        for org_name, title, slugs, location, days, start, end, capacity, requirements in OPPORTUNITIES:
            opp, _ = Opportunity.objects.get_or_create(organization=orgs[org_name], title=title, defaults={
                'description': f'{title} with {org_name}. Volunteers work in small teams with a coordinator on site.',
                'location': location, 'event_date': today + timedelta(days=days), 'start_time': time(start), 'end_time': time(end),
                'capacity': capacity, 'requirements': requirements})
            opp.causes.set(causes[s] for s in slugs)
            opps[title] = opp

        # A past event, so the volunteers have completed work, verified hours and a certificate to show.
        past, _ = Opportunity.objects.get_or_create(organization=orgs['Annapurna Food Bank'], title='Diwali meal drive', defaults={
            'description': 'Packed and delivered festival meal kits to 400 families.', 'location': 'Laxmi Nagar, Delhi',
            'event_date': today - timedelta(days=21), 'start_time': time(8), 'end_time': time(18), 'capacity': 20, 'is_active': False})
        past.causes.set([causes['food-security']])

        dev = User.objects.get(username='dev')
        for username, hours in (('meera', '26.5'), ('aarav', '8')):
            signup, _ = Signup.objects.get_or_create(volunteer=volunteers[username], opportunity=past, defaults={'status': 'completed'})
            HourLog.objects.get_or_create(signup=signup, status='verified', defaults={'hours': Decimal(hours), 'notes': 'Packing and delivery shifts.', 'verified_by': dev, 'verified_at': timezone.now()})
        Review.objects.get_or_create(volunteer=volunteers['meera'], opportunity=past, defaults={'rating': 5, 'comment': 'Well organised, clear shifts.'})

        signups = [('aarav', 'Okhla Bird Sanctuary clean-up', 'confirmed'), ('aarav', 'Maths tutoring for Class 8', 'pending'),
                   ('meera', 'Weekend meal kit packing', 'confirmed'), ('kabir', 'Maths tutoring for Class 8', 'pending'),
                   ('kabir', 'Reading hour at the library', 'confirmed')]
        for username, title, status in signups:
            Signup.objects.get_or_create(volunteer=volunteers[username], opportunity=opps[title], defaults={'status': status})

        # A submitted log waiting for the coordinator, so the verify step has something in it.
        pending = Signup.objects.get(volunteer=volunteers['aarav'], opportunity=past)
        if not pending.hour_logs.filter(status='pending').exists():
            HourLog.objects.create(signup=pending, hours=Decimal('3'), notes='Extra delivery run on the second day.')

        for volunteer in volunteers.values():
            total = sum(x.hours for x in HourLog.objects.filter(signup__volunteer=volunteer, status='verified'))
            for milestone in Milestone.objects.filter(is_active=True, required_hours__lte=total):
                Certificate.objects.get_or_create(volunteer=volunteer, milestone=milestone)
