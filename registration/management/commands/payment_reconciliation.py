import datetime
from django.core.management.base import BaseCommand, CommandError
from registration.models import Registration, Option
from registration.iamporter import Iamporter, get_access_token
from constance import config

class Command(BaseCommand):
    help = 'Cross check paid and registration consistency'

    def handle(self, *args, **options):
        eary_bird = Option.objects.get(name='Early Bird')
        paid_registrations = \
        Registration.objects.filter(payment_status='paid').exclude(payment_method='bank', option=eary_bird).values_list('merchant_uid',
                                                                       'email')
        paid_registrations = dict(list(paid_registrations))
        access_token = get_access_token(config.IMP_API_KEY, config.IMP_API_SECRET)
        imp_client = Iamporter(access_token)
        # Use hard coded date only for pycon 2016.
        paid_pg = imp_client.get_paid_list(since=datetime.datetime(2016, 1, 1))
        paid_pg = map(lambda x: (x['merchant_uid'], x['buyer_email']), paid_pg)
        paid_pg = dict(paid_pg)
        print('registered but not paid')
        for registration in paid_registrations:
            if registration not in paid_pg:
                print(registration)
                print(paid_registrations[registration])
        print('paid but not registered')
        for pg in paid_pg:
            if pg not in paid_registrations:
                print(pg)
                print(paid_pg[pg])
