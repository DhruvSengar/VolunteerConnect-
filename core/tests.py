from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from accounts.models import Organization
from core.models import Certificate, HourLog, Opportunity, Signup


@override_settings(DEBUG=True)
class SeedDataTests(TestCase):
    def counts(self):
        return [m.objects.count() for m in (Organization, Opportunity, Signup, HourLog, Certificate)]

    def test_seed_is_repeatable(self):
        call_command('seed_data', stdout=StringIO())
        first = self.counts()
        call_command('seed_data', stdout=StringIO())
        self.assertEqual(first, self.counts())
        self.assertTrue(Certificate.objects.filter(volunteer__username='meera', milestone__required_hours=25).exists())
        self.assertTrue(HourLog.objects.filter(status='pending').exists())

    @override_settings(DEBUG=False)
    def test_refuses_without_debug(self):
        with self.assertRaises(CommandError):
            call_command('seed_data', stdout=StringIO())


@override_settings(DEBUG=True)
class PageRenderTests(TestCase):
    """Every page renders for each kind of user on the seeded demo data."""

    @classmethod
    def setUpTestData(cls):
        call_command('seed_data', stdout=StringIO())

    def pages(self):
        from django.contrib.auth.models import User
        from django.urls import reverse
        opp = Opportunity.objects.filter(is_active=True).first()
        signup = Signup.objects.filter(status__in=['confirmed', 'completed']).first()
        cert = Certificate.objects.first()
        log = HourLog.objects.filter(status='pending').first()
        return opp, signup, cert, log, [
            reverse('home'), reverse('opportunity-list'), reverse('opportunity-list') + '?q=zzz', reverse('opportunity-detail', args=[opp.pk]),
            reverse('organization-list'), reverse('certificate-verify', args=[cert.certificate_id]), reverse('credits'),
        ]

    def assert_ok(self, urls):
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_anonymous(self):
        from django.urls import reverse
        *_, urls = self.pages()
        self.assert_ok(urls + [reverse('login'), reverse('register')])

    def test_volunteer_and_coordinator_pages(self):
        from django.contrib.auth.models import User
        from django.urls import reverse
        opp, signup, cert, log, urls = self.pages()
        self.client.force_login(signup.volunteer)
        self.assert_ok(urls + [reverse('dashboard'), reverse('profile'), reverse('certificates'), reverse('report'), reverse('submit-hours', args=[signup.id]), reverse('opportunity-detail', args=[signup.opportunity.pk])])
        coordinator = log.signup.opportunity.organization.coordinators.first()
        self.client.force_login(coordinator)
        page = self.client.get(reverse('dashboard'))
        self.assertContains(page, reverse('verify-hours', args=[log.id]))
        self.assert_ok([reverse('manage-signups', args=[log.signup.opportunity.pk]), reverse('verify-hours', args=[log.id]), reverse('opportunity-create'), reverse('opportunity-edit', args=[log.signup.opportunity.pk])])
        admin = User.objects.create_superuser('root', password='x')
        self.client.force_login(admin)
        self.assert_ok([reverse('organization-approval')])

    def test_search_json(self):
        from django.urls import reverse
        data = self.client.get(reverse('opportunity-search'), {'q': 'a'}).json()
        self.assertTrue(data['results'])
        self.assertEqual(set(data['results'][0]), {'id', 'title', 'location', 'slots'})
        # live results are the list page's own cards, in the same order
        page = self.client.get(reverse('opportunity-list'), {'q': 'a'}).context['opportunities']
        self.assertEqual([r['id'] for r in data['results']], [o.id for o in page])
        self.assertIn('date-badge', data['html'])
        self.assertIn(page[0].organization.name, data['html'])
        empty = self.client.get(reverse('opportunity-search'), {'q': 'zzzz'}).json()
        self.assertEqual(empty['results'], [])
        self.assertIn('No matching opportunities', empty['html'])
