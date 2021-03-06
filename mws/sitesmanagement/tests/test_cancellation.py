from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import override_settings, TestCase
from mwsauth.tests import do_test_login
from sitesmanagement.cronjobs import check_subscription, delete_cancelled
from sitesmanagement.models import Site, NetworkConfig, Service, ServerType


@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, CELERY_ALWAYS_EAGER=True, BROKER_BACKEND='memory')
class CancelSiteTest(TestCase):

    def test_scheduled_cancellation(self):
        today = datetime.today()
        do_test_login(self, user="test0001")
        # Create site (300 days ago start date)
        site = Site.objects.create(name="testSite", email='amc203@cam.ac.uk', type=ServerType.objects.get(id=1),
                                   start_date=today-timedelta(days=300))
        netconf = NetworkConfig.objects.create(IPv4='131.111.58.253', IPv6='2001:630:212:8::8c:253', type='ipvxpub',
                                               name="mws-66424.mws3.csx.cam.ac.uk")
        Service.objects.create(site=site, type='production', status="ready", network_configuration=netconf)
        site.users.add(User.objects.get(username="test0001"))

        self.assertFalse(hasattr(site, 'billing'))
        pofile = SimpleUploadedFile("file.pdf", "file_content")
        self.client.post(reverse('billing_management', kwargs={'site_id': site.id}),
                         {'purchase_order_number': 'testOrderNumber', 'group': 'testGroup', 'purchase_order': pofile})
        # Retrieve object
        site = Site.objects.get(pk=site.id)
        self.assertTrue(hasattr(site, 'billing'))

        check_subscription()
        delete_cancelled()
        # Retrieve object
        site = Site.objects.get(pk=site.id)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIsNone(site.end_date)
        self.assertTrue(site.subscription)
        self.assertTrue(site.users.exists())

        asdfasd = self.client.post(reverse('donotrenew', kwargs={'site_id': site.id}), {})
        # Retrieve object
        site = Site.objects.get(pk=site.id)
        self.assertIsNone(site.end_date)
        self.assertFalse(site.subscription)
        self.assertTrue(site.users.exists())

        check_subscription()
        delete_cancelled()
        # Retrieve object
        site = Site.objects.get(pk=site.id)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIsNone(site.end_date)
        self.assertTrue(site.users.exists())

        site.start_date = today - timedelta(days=370)
        site.save()
        check_subscription()
        delete_cancelled()
        # Retrieve object
        site = Site.objects.get(pk=site.id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Your managed web server has been cancelled')
        self.assertEqual(mail.outbox[0].to, [site.email])
        self.assertEqual(site.end_date, today.date())
        self.assertFalse(site.users.exists())

        # After 3 weeks the site should have not been deleted yet
        site.end_date = today - timedelta(days=21)
        site.save()
        check_subscription()
        delete_cancelled()
        # Retrieve object
        site = Site.objects.get(pk=site.id)

        # After 9 weeks the site should have been deleted
        site.end_date = today - timedelta(days=60)
        site.save()
        check_subscription()
        delete_cancelled()
        # Retrieve object
        self.assertFalse(Site.objects.filter(pk=site.id))

    def test_scheduled_deletion_paid_service(self):
        today = datetime.today().date()
        do_test_login(self, user="test0001")
        site = Site.objects.create(name="testSite", email='amc203@cam.ac.uk', type=ServerType.objects.get(id=1),
                                   start_date=today-timedelta(days=300))
        netconf = NetworkConfig.objects.create(IPv4='131.111.58.253', IPv6='2001:630:212:8::8c:253', type='ipvxpub',
                                               name="mws-66424.mws3.csx.cam.ac.uk")
        Service.objects.create(site=site, type='production', status="ready", network_configuration=netconf)
        site.users.add(User.objects.get(username="test0001"))

        self.assertFalse(hasattr(site, 'billing'))
        pofile = SimpleUploadedFile("file.pdf", "file_content")
        self.client.post(reverse('billing_management', kwargs={'site_id': site.id}),
                         {'purchase_order_number': 'testOrderNumber', 'group': 'testGroup', 'purchase_order': pofile})
        # Retrieve object
        site = Site.objects.get(pk=site.id)
        self.assertTrue(hasattr(site, 'billing'))

        site.end_date=today
        site.save()

        delete_cancelled()
        # Retrieve object
        site = Site.objects.get(pk=site.id)
        self.assertEqual(site.end_date, today)

        site.end_date = today-timedelta(days=14) # Two weeks ago
        site.save()
        delete_cancelled()
        # Retrieve object
        site = Site.objects.get(pk=site.id)
        self.assertEqual(site.end_date, today-timedelta(days=14))

        site.end_date = today-timedelta(days=60) # > 8 weeks ago
        site.save()
        delete_cancelled()
        # Retrieve object
        self.assertFalse(Site.objects.filter(pk=site.id))

    def test_scheduled_deletion_unpaid_service(self):
        today = datetime.today().date()
        do_test_login(self, user="test0001")
        site = Site.objects.create(name="testSite", email='amc203@cam.ac.uk', type=ServerType.objects.get(id=1),
                                   start_date=today-timedelta(days=15))
        netconf = NetworkConfig.objects.create(IPv4='131.111.58.253', IPv6='2001:630:212:8::8c:253', type='ipvxpub',
                                               name="mws-66424.mws3.csx.cam.ac.uk")
        Service.objects.create(site=site, type='production', status="ready", network_configuration=netconf)
        site.users.add(User.objects.get(username="test0001"))

        check_subscription()
        delete_cancelled()
        # Retrieve object
        site = Site.objects.get(pk=site.id)
        self.assertIsNone(site.end_date)
        self.assertTrue(site.subscription)
        self.assertTrue(site.users.exists())

        site.start_date = today-timedelta(days=32)
        site.save()
        check_subscription()
        delete_cancelled()
        # Retrieve object
        site = Site.objects.get(pk=site.id)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject,
                         'Your managed web server has been cancelled')
        self.assertEqual(mail.outbox[1].to, [site.email])
        self.assertEqual(site.end_date, today)
        self.assertFalse(site.users.exists())


        site.start_date = today-timedelta(days=62)
        site.end_date = today-timedelta(days=30)
        site.save()
        check_subscription()
        delete_cancelled()
        # Retrieve object
        self.assertFalse(Site.objects.filter(pk=site.id))
