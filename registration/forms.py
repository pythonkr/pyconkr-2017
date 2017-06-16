# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Registration
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div

class TopSizeForm(forms.Form):
    class Meta:
        model = Registration
        fields = ('top_size')


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
