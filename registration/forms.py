# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Registration, ManualPayment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class RegistrationForm(forms.ModelForm):
    base_price = forms.IntegerField(label=_('Base Price KRW'))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['base_price'].widget.attrs['readonly'] = True
        self.fields['option'].widget.attrs['disabled'] = True
        self.helper = FormHelper()
        self.helper.form_id = 'registration-form'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Submit'), disabled='disabled'))

    class Meta:
        model = Registration
        fields = ('email', 'option', 'base_price', 'name', 'top_size', 'company', 'phone_number', 'payment_method')
        labels = {
            'name': _('Name'),
            'option': _('Option'),
            'top_size': _('Top Size'),
            'email': _('E-Mail'),
            'company': _('Company or Organization'),
            'phone_number':  _('Phone Number'),
            'payment_method': _('Payment Method'),
        }


class RegistrationAdditionalPriceForm(RegistrationForm):

    additional_price = forms.IntegerField(min_value=0)

    class Meta:
        model = Registration
        fields = ('email', 'option', 'base_price', 'additional_price', 'name', 'top_size', 'company', 'phone_number', 'payment_method')
        labels = {
            'name': _('Name'),
            'option': _('Option'),
            'top_size': _('Top Size'),
            'additional_price': _('Additional Funding KRW'),
            'email': _('E-Mail'),
            'company': _('Company or Organization'),
            'phone_number':  _('Phone Number'),
            'payment_method': _('Payment Method') 
        }


class ManualPaymentForm(forms.ModelForm):
    email = forms.EmailField()
    base_price = forms.IntegerField(label=_('Base Price KRW'))

    def __init__(self, *args, **kwargs):
        super(ManualPaymentForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['base_price'].widget.attrs['readonly'] = True
        self.fields['payment_method'].widget.attrs['readonly'] = True
        self.helper = FormHelper()
        self.helper.form_id = 'manual-payment-form'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Submit'), disabled='disabled'))

    class Meta:
        model = ManualPayment
        fields = ('title', 'email', 'base_price', 'payment_method')
        labels = {
            'title': _('Title'),
            'email': _('Email'),
            'payment_method': _('Payment Method'),
        }
