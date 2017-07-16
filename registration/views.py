# -*- coding: utf-8 -*-
import logging
import datetime
from uuid import uuid4

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.views.decorators.csrf import csrf_exempt
from constance import config

from pyconkr.helper import render_io_error
from .forms import RegistrationForm, RegistrationAdditionalPriceForm, ManualPaymentForm
from .models import Option, Registration, ManualPayment
from .iamporter import get_access_token, Iamporter, IamporterError

logger = logging.getLogger(__name__)
payment_logger = logging.getLogger('payment')


def _is_ticket_open():
    open_datetime = datetime.datetime.combine(config.REGISTRATION_OPEN, config.REGISTRATION_OPEN_TIME)
    close_datetime = datetime.datetime.combine(config.REGISTRATION_CLOSE, config.REGISTRATION_CLOSE_TIME)
    return True if open_datetime <= datetime.datetime.now() <= close_datetime else False


def index(request):
    if request.user.is_authenticated():
        is_registered = Registration.objects.filter(
            user=request.user,
            payment_status__in=['paid', 'ready']
        ).exists()
    else:
        is_registered = False
    options = Option.objects.filter(is_active=True)
    return render(request, 'registration/info.html',
                  {'is_ticket_open': _is_ticket_open,
                   'options': options,
                   'is_registered': is_registered})


@login_required
def status(request):
    registration = Registration.objects.filter(user=request.user)
    if registration:
        registration = registration.latest('created')
    context = {
        'registration': registration,
        'title': _("Registration Status"),
    }
    return render(request, 'registration/status.html', context)


@login_required
def payment(request, option_id):
    if not _is_ticket_open():
        return redirect('registration_index')

    product = Option.objects.get(id=option_id)
    is_registered = Registration.objects.filter(
        user=request.user,
        payment_status__in=['paid', 'ready']
    ).exists()

    if is_registered:
        return redirect('registration_status')

    uid = str(uuid4()).replace('-', '')
    if product.has_additional_price:
        form = RegistrationAdditionalPriceForm(initial={'email': request.user.email,
                                                        'option': product,
                                                        'base_price': product.price})
    else:
        form = RegistrationForm(initial={'email': request.user.email,
                                         'option': product,
                                         'base_price': product.price})
    return render(request, 'registration/payment.html', {
        'title': _('Registration'),
        'form': form,
        'uid': uid,
        'product_name': product.name,
        'amount': product.price,
        'vat': 0,
    })


@login_required
def payment_process(request):
    if request.method == 'GET':
        return redirect('registration_index')

    # alreay registered
    if Registration.objects.filter(user=request.user, payment_status__in=['paid','ready']).exists():
        return redirect('registration_status')

    payment_logger.debug(request.POST)
    form = RegistrationAdditionalPriceForm(request.POST)

    # TODO : more form validation
    # eg) merchant_uid
    if not form.is_valid():
        form_errors_string = "\n".join(('%s:%s' % (k, v[0]) for k, v in form.errors.items()))
        return JsonResponse({
            'success': False,
            'message': form_errors_string,  # TODO : ...
        })

    remain_ticket_count = (config.TOTAL_TICKET - Registration.objects.filter(payment_status__in=['paid', 'ready']).count())

    # sold out
    if remain_ticket_count <= 0:
        return JsonResponse({
            'success': False,
            'message': u'티켓이 매진 되었습니다',
        })

    if form.cleaned_data.get('additional_price', 0) < 0:
        return JsonResponse({
            'success': False,
            'message': u'후원 금액은 0원 이상이어야 합니다.',
        })

    registration = Registration(
            user=request.user,
            name = form.cleaned_data.get('name'),
            email = request.user.email,
            additional_price = form.cleaned_data.get('additional_price', 0),
            company = form.cleaned_data.get('company', ''),
            top_size = form.cleaned_data.get('top_size', ''),
            phone_number = form.cleaned_data.get('phone_number', ''),
            merchant_uid = request.POST.get('merchant_uid'),
            option = form.cleaned_data.get('option'),
            payment_method = form.cleaned_data.get('payment_method')
        )

    # sold out
    if registration.option.is_soldout:
        return JsonResponse({
            'success': False,
            'message': u'{name} 티켓이 매진 되었습니다'.format(name=registration.option.name),
        })

    try:
        product = registration.option

        if registration.payment_method == 'card':
            access_token = get_access_token(config.IMP_API_KEY, config.IMP_API_SECRET)
            imp_client = Iamporter(access_token)
            # TODO : use validated and cleaned data
            imp_params = dict(
                token=request.POST.get('token'),
                merchant_uid=request.POST.get('merchant_uid'),
                amount=product.price + registration.additional_price,
                card_number=request.POST.get('card_number'),
                expiry=request.POST.get('expiry'),
                birth=request.POST.get('birth'),
                pwd_2digit=request.POST.get('pwd_2digit'),
                customer_uid=form.cleaned_data.get('email'),
                name=product.name,
                buyer_name=request.POST.get('name'),
                buyer_email=request.POST.get('email'),
                buyer_tel=request.POST.get('phone_number')

            )
            if request.POST.get('birth') == '':
                # foreign payment
                imp_client.foreign(**imp_params)
            else:
                imp_client.foreign(**imp_params)
                # imp_client.onetime(**imp_params)
            confirm = imp_client.find_by_merchant_uid(request.POST.get('merchant_uid'))

            if confirm['amount'] != product.price + registration.additional_price:
                # TODO : cancel
                return render_io_error("amount is not same as product.price. it will be canceled")

            registration.transaction_code = confirm.get('pg_tid')
            registration.payment_method = confirm.get('pay_method')
            registration.payment_status = confirm.get('status')
            registration.payment_message = confirm.get('fail_reason')
            registration.vbank_name = confirm.get('vbank_name', None)
            registration.vbank_num = confirm.get('vbank_num', None)
            registration.vbank_date = confirm.get('vbank_date', None)
            registration.vbank_holder = confirm.get('vbank_holder', None)
            registration.save()
        elif registration.payment_method == 'vbank':
            registration.transaction_code = request.POST.get('pg_tid')
            registration.payment_method = request.POST.get('pay_method')
            registration.payment_status = request.POST.get('status')
            registration.payment_message = request.POST.get('fail_reason')
            registration.vbank_name = request.POST.get('vbank_name', None)
            registration.vbank_num = request.POST.get('vbank_num', None)
            registration.vbank_date = request.POST.get('vbank_date', None)
            registration.vbank_holder = request.POST.get('vbank_holder', None)
            registration.save()
        else:
            raise Exception('Unknown payment method')

    except IamporterError as e:
        # TODO : other status code
        return JsonResponse({
            'success': False,
            'code': e.code,
            'message': e.message,
        })
    else:
        return JsonResponse({
            'success': True,
        })


@csrf_exempt
def payment_callback(request):
    merchant_uid = request.POST.get('merchant_uid')
    registration = Registration.objects.filter(merchant_uid=merchant_uid)
    if not registration.exists():
        return HttpResponse(status_code=404)
    access_token = get_access_token(config.IMP_API_KEY, config.IMP_API_SECRET)
    imp_client = Iamporter(access_token)
    result = imp_client.find_by_merchant_uid(merchant_uid)
    registration = registration.first()
    if result['status'] == 'paid':
        registration.confirmed = datetime.datetime.now()
    elif result['status'] == 'cancelled':
        registration.canceled = datetime.datetime.now()
    registration.payment_status = result['status']
    registration.save()
    return HttpResponse()


@login_required
def manual_registration(request, manual_payment_id):
    mp = get_object_or_404(ManualPayment, pk=manual_payment_id, user=request.user)
    uid = str(uuid4()).replace('-', '')
    form = ManualPaymentForm(initial={
        'title': mp.title,
        'base_price': mp.price,
        'email': request.user.email,
    })

    return render(request, 'registration/manual_payment.html', {
        'title': _('Registration'),
        'manual_payment_id': manual_payment_id,
        'form': form,
        'uid': uid,
        'product_name': mp.title,
        'amount': mp.price,
        'vat': 0,
        'payment_status': mp.payment_status,
    })


@login_required
def manual_payment_process(request):
    if request.method == 'GET':
        return redirect('registration_index')

    payment_logger.debug(request.POST)
    form = ManualPaymentForm(request.POST)

    if not form.is_valid():
        form_errors_string = "\n".join(('%s:%s' % (k, v[0]) for k, v in form.errors.items()))
        return JsonResponse({
            'success': False,
            'message': form_errors_string,  # TODO : ...
        })

    # check already payment
    try:
        mp = ManualPayment.objects.get(pk=request.POST.get('manual_payment_id'))
    except ManualPayment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '결제할 내역이 존재하지 않습니다. 다시 한번 확인해 주시기 바랍니다.',
        })

    if mp.payment_status == 'paid':
        return JsonResponse({
            'success': False,
            'message': '이미 지불되었습니다. 문의사항은 support@pycon.kr 로 문의주시기 바랍니다.',
        })

    # Only card
    try:
        access_token = get_access_token(config.IMP_API_KEY, config.IMP_API_SECRET)
        imp_client = Iamporter(access_token)

        imp_params = dict(
            token=request.POST.get('token'),
            merchant_uid=request.POST.get('merchant_uid'),
            amount=mp.price,
            card_number=request.POST.get('card_number'),
            expiry=request.POST.get('expiry'),
            birth=request.POST.get('birth'),
            pwd_2digit=request.POST.get('pwd_2digit'),
            customer_uid=form.cleaned_data.get('email'),
            name=mp.title,
            buyer_name=request.POST.get('name', ''),
            buyer_email=request.POST.get('email'),
            buyer_tel=request.POST.get('phone_number', '')
        )

        imp_client.foreign(**imp_params)
        confirm = imp_client.find_by_merchant_uid(request.POST.get('merchant_uid'))

        if confirm['amount'] != mp.price:
            return render_io_error("amount is not same as product.price. it will be canceled")

        mp.transaction_code = confirm.get('pg_tid')
        mp.imp_uid = confirm.get('imp_uid')
        mp.merchant_uid = confirm.get('merchant_uid')
        mp.payment_method = confirm.get('pay_method')
        mp.payment_status = confirm.get('status')
        mp.payment_message = confirm.get('fail_reason')
        mp.confirmed = timezone.now()
        mp.save()
    except IamporterError as e:
        return JsonResponse({
            'success': False,
            'code': e.code,
            'message': e.message,
        })
    else:
        return JsonResponse({
            'success': True,
        })


class RegistrationReceiptDetail(DetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(Registration, payment_status='paid', user_id=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super(RegistrationReceiptDetail, self).get_context_data(**kwargs)
        context['title'] = _("Registration Receipt")
        return context
