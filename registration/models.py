# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Option(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=False)
    price = models.IntegerField()
    has_additional_price = models.BooleanField(default=False)
    total = models.IntegerField(default=500)

    @property
    def is_soldout(self):
        return self.total <= Registration.objects.filter(option=self, payment_status__in=['paid', 'ready']).count()

    def __str__(self):
        return self.name


class Registration(models.Model):
    user = models.ForeignKey(User)
    merchant_uid = models.CharField(max_length=32)
    option = models.ForeignKey(Option, null=True)
    name = models.CharField(max_length=100)
    top_size = models.CharField(
        max_length=20,
        default='L',
        choices=(
            ('small', u'S(85)'),
            ('medium', u'M(90)'),
            ('large', u'L(95)'),
            ('xlarge', u'XL(100)'),
            ('2xlarge', u'2XL(105)'),
            ('3xlarge', u'3XL(110)'),
            ('4xlarge', u'3XL(115)'),
        )
    )
    email = models.EmailField(max_length=255)
    company = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20)
    transaction_code = models.CharField(max_length=36, blank=True)
    additional_price = models.IntegerField(default=0)
    payment_method = models.CharField(
        max_length=20,
        default='card',
        choices=(
            ('card', u'Credit Card'),
            #('bank', u'Bank Transfer'),
            ('vbank', u'Virtual Bank Transfer'),
        )
    )
    payment_status = models.CharField(
        max_length=10,
        default='ready',
        choices=(
            ('ready', u'Ready'),
            ('paid', u'Paid'),
            ('deleted', u'Deleted'),
            ('cancelled', u'Cancelled'),
        )
    )
    payment_message = models.CharField(max_length=255, null=True, blank=True)
    vbank_num = models.CharField(max_length=255, null=True, blank=True)
    vbank_name = models.CharField(max_length=20, null=True, blank=True)
    vbank_date = models.CharField(max_length=50, null=True, blank=True)
    vbank_holder = models.CharField(max_length=20, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    confirmed = models.DateTimeField(null=True, blank=True)
    canceled = models.DateTimeField(null=True, blank=True)
