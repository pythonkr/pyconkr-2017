# -*- coding: utf-8 -*-
import datetime

from unittest import mock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from constance.test import override_config
from django_dynamic_fixture import G

from .models import Option, Registration

User = get_user_model()


@override_config(REGISTRATION_OPEN=datetime.date.today()-datetime.timedelta(days=1), REGISTRATION_CLOSE=datetime.date.today()+datetime.timedelta(days=1))
class RegistrationTest(TestCase):
    def test_patron_has_additional_price(self):
        option = Option.objects.create(name='patron', price=1000, has_additional_price=True, is_active=True)
        user = User.objects.create_user('testname', 'test@test.com', 'testpassword')
        self.client.login(username='testname', password='testpassword')
        response = self.client.get(reverse('registration_payment', args=[option.id]))
        self.assertIn('additional_price', response.context['form'].fields)

    def test_transaction_id_is_not_required(self):
        registration = G(Registration, transaction_code='')
        self.assertNotEqual(registration.id, None)

    @mock.patch('registration.views.get_access_token')
    @mock.patch('registration.views.Iamporter')
    def test_vbank_status_update_via_iamport_callback(self, Iamporter, get_access_token):
        get_access_token.return_value = 'test token'
        iamporter = Iamporter.return_value
        # make registration object for test
        registration = G(Registration, payment_method='vbank', payment_status='ready')
        iamporter.find_by_merchant_uid.return_value = dict(
                merchant_uid=registration.merchant_uid,
                status='paid' # yes i wanna make status to paid
                )
        # WOW it's so easy. I love ddf.
        # let's make a callback parameter
        callback_param = dict(
                merchant_uid=registration.merchant_uid,
                imp_uid='whatever... we dont care.',
                status='ready' # acctually i wanna make status to paid
        )

        response = self.client.post(reverse('registration_callback'), callback_param)
        self.assertEqual(response.status_code, 200)
        registration = Registration.objects.get(id=registration.id)
        self.assertEqual(registration.payment_status, 'paid') 
