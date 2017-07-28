# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Option(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=False)
    price = models.IntegerField()
    has_additional_price = models.BooleanField(default=False)
    total = models.IntegerField(default=500)
    is_cancelable = models.BooleanField(default=False)
    cancelable_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ['price']

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
        default=None,
        null=True,
        blank=True,
        choices=(
            ('small', u'S(85)'),
            ('medium', u'M(90)'),
            ('large', u'L(95)'),
            ('xlarge', u'XL(100)'),
            ('2xlarge', u'2XL(105)'),
            ('3xlarge', u'3XL(110)'),
            ('4xlarge', u'4XL(115)'),
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

    def __str__(self):
        return "{} {} {}".format(self.name, self.email, self.option.name)

class ManualPayment(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    price = models.PositiveIntegerField(null=False)
    merchant_uid = models.CharField(max_length=32, db_index=True, blank=True)
    imp_uid = models.CharField(max_length=32, null=True, blank=True)
    transaction_code = models.CharField(max_length=36, blank=True)
    payment_method = models.CharField(
        max_length=20,
        default='card',
        choices=(
            ('card', u'Credit Card'),
        )
    )
    payment_status = models.CharField(
        max_length=10,
        default='ready',
        choices=(
            ('ready', u'Ready'),
            ('paid', u'Paid'),
            ('cancelled', u'Cancelled'),
        )
    )
    payment_message = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    confirmed = models.DateTimeField(null=True, blank=True)
    canceled = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '({}) {} ({})원'.format(self.payment_status.upper(), self.title, self.price)


class IssueTicket(models.Model):
    registration = models.ForeignKey(Registration)
    issuer = models.ForeignKey(User)
    issue_date = models.DateTimeField(default=timezone.now)
