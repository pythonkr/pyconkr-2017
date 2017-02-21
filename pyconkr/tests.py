# -*- coding: utf-8 -*-

from django.test import TestCase
from django.http import HttpResponse
from django.test import Client
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django_dynamic_fixture import G

from pyconkr.models import TutorialCheckin, TutorialProposal
from pyconkr.helper import render_io_error
from registration.models import Registration

User = get_user_model()


class HelperFunctionTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_render_io_error(self):
        a = render_io_error("test reason")
        self.assertEqual(a.status_code, 406, "render io error status code must be 406")


class PaymentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testname', 'test@test.com', 'testpassword')
        self.client.login(username='testname', password='testpassword')

    def tearDown(self):
        pass

    def test_view_registration_payment(self):
        url = reverse('registration_payment')
        response = self.client.post(url, {'test': 1})
        self.assertEqual(response['content-type'], 'application/json', 'Result has to be JSON')


class ProfileTest(TestCase):
    def test_profile_is_created_when_user_save(self):
        user = User.objects.create_user('test', 'test@email.com', 'password')
        self.assertNotEqual(user.profile, None)

    def test_redirect_to_profile_edit_page_when_user_has_not_profile(self):
        User.objects.create_user('test', 'test@email.com', 'password')
        client = Client()
        client.login(username='test', password='password')
        response = client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], reverse('profile_edit'))


class ProposeTest(TestCase):
    def test_redirect_to_profile_when_propose_without_profile(self):
        user = User.objects.create_user('test', 'test@email.com', 'password')
        client = Client()
        client.login(username='test', password='password')
        response = client.get(reverse('propose'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], reverse('profile_edit'))

class TutorialTest(TestCase):
    def test_tutorial_detail_attendees(self):
        # set capacity for test waiting flag
        tutorial = G(TutorialProposal, capacity='S')
        first_user = G(User, email='first@email.com')
        second_user = G(User, email='second@email.com')
        G(Registration, user=second_user, payment_status='paid')
        many_users = [G(User, email=str(x)+'@email.com') for x in range(9)]
        first_checkin = G(TutorialCheckin, tutorial=tutorial, user=first_user)
        second_checkin = G(TutorialCheckin, tutorial=tutorial, user=second_user)
        many_checkins = [G(TutorialCheckin, tutorial=tutorial, user=x) for x in
                         many_users]
        response = self.client.get(reverse('tutorial', kwargs={'pk': tutorial.pk}))
        attendees = response.context['attendees']
        self.assertEqual(len(attendees), 11)
        # user email head?
        self.assertEqual(attendees[0]['name'], 'first')
        self.assertEqual(attendees[0]['registered'], False)
        self.assertEqual(attendees[1]['registered'], True)
        # waiting order by pk
        self.assertEqual(attendees[0]['waiting'], False)
        self.assertEqual(attendees[10]['waiting'], True)
