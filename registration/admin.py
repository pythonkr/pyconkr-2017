# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.mail import send_mass_mail
from django.shortcuts import render
from constance import config
from django.utils import timezone
from .iamporter import get_access_token, Iamporter, IamporterError

from .models import Registration, Option, ManualPayment, IssueTicket


def send_bankpayment_alert_email(modeladmin, request, queryset):
    messages = []
    subject = u"PyCon Korea 2017 입금확인부탁드립니다. Please Check PyCon Korea 2017 payment"
    body = u"""
    안녕하세요. PyCon Korea 준비위원회입니다.
    현재 입금여부를 확인하였으나 입금이 되지 않았습니다.
    혹시나 다른 이름으로 입금하신분은 support@pycon.kr 로 메일 부탁드립니다.
    입금시한은 구매로부터 일주일입니다.
    감사합니다.
    """
    from_email = "pycon@pycon.kr"
    for obj in queryset:
        email = obj.email
        message = (subject, body, from_email, [email])
        messages.append(message)
    send_mass_mail(messages, fail_silently=False)

send_bankpayment_alert_email.short_description = "Send Bank Payment Email"


def cancel_registration(modeladmin, request, queryset):
    messages = []
    subject = u"PyCon Korea 2017 결제 취소 알림"
    body = u"""
안녕하세요. PyCon Korea 준비위원회입니다.

결제가 취소되었음을 알려드립니다.
결제 대행사 사정에 따라 다소 늦게 카드 취소가 이뤄질 수 있습니다.

다른 문의 사항은 support@pycon.kr 로 메일 부탁드립니다.
감사합니다.
    """
    from_email = "pycon@pycon.kr"

    results = []
    now = timezone.now()
    access_token = get_access_token(config.IMP_API_KEY, config.IMP_API_SECRET)
    imp_client = Iamporter(access_token)

    for obj in queryset:
        if obj.payment_method != 'card':
            obj.cancel_reason = u'카드 결제만 취소 가능'
            results.append(obj)
            continue

        if obj.payment_status != 'paid':
            obj.cancel_reason = u'결제 완료만 취소 가능'
            results.append(obj)
            continue

        if not obj.option.is_cancelable:
            obj.cancel_reason = u'취소 불가능 옵션 (얼리버드 등)'
            results.append(obj)
            continue

        if obj.option.cancelable_date and obj.option.cancelable_date < now:
            obj.cancel_reason = u'취소가능일자가 아니므로 취소 불가능'
            results.append(obj)
            continue

        try:
            imp_params = dict(
                merchant_uid=obj.merchant_uid,
                reason=u'Cancel by admin',
            )
            imp_client.cancel(**imp_params)
        except IOError:
            obj.cancel_status = 'IOError'
            results.append(obj)
            continue
        except IamporterError as e:
            obj.cancel_status = e.code
            obj.cancel_reason = e.message
            results.append(obj)
            continue

        obj.canceled = now
        obj.payment_status = 'cancelled'
        obj.save(update_fields=['payment_status', 'canceled'])

        obj.cancel_status = 'CANCELLED'
        results.append(obj)

        message = (subject, body, from_email, [obj.email])
        messages.append(message)

    send_mass_mail(messages, fail_silently=False)
    return render(request, 'registration/cancellation_result.html', {'results': results})

cancel_registration.short_description = "Cancel registration"


class OptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'price', 'is_cancelable', 'cancelable_date')
    list_editable = ('is_active',)
    ordering = ('id',)
admin.site.register(Option, OptionAdmin)


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'option', 'name', 'email', 'payment_method',
                    'payment_status', 'created', 'confirmed', 'canceled')
    list_editable = ('payment_status',)
    list_filter = ('option', 'payment_method', 'payment_status')
    csv_fields = ['name', 'email', 'company', 'option', ]
    search_fields = ('name', 'email', 'merchant_uid', 'transaction_code', )
    readonly_fields = ('created', 'merchant_uid', 'transaction_code', )
    ordering = ('id',)
    actions = (send_bankpayment_alert_email, cancel_registration)
admin.site.register(Registration, RegistrationAdmin)


class IssueTicketAdmin(admin.ModelAdmin):
    list_display = ('registration', 'issuer', 'issue_date')
    ordering = ('issue_date',)
    search_fields = ('registration__name', 'registration__email', 'issuer__username', )
admin.site.register(IssueTicket, IssueTicketAdmin)

class ManualPaymentAdmin(admin.ModelAdmin):
    list_display = ('title', 'payment_status', 'user', )
    list_filter = ('payment_status', )
    search_fields = ('user__email', 'description', )
    raw_id_fields = ('user', )

    class Meta:
        model = ManualPayment
admin.site.register(ManualPayment, ManualPaymentAdmin)
