from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^purchase/$', views.index, name='registration_index'),
    url(r'^status/$', views.status, name='registration_status'),
    url(r'^payment/(\d*)/$', views.payment, name='registration_payment'),
    url(r'^payment/$', views.payment_process, name='registration_payment'),
    url(r'^payment/callback/$', views.payment_callback, name='registration_callback'),
    url(r'^receipt/$',
        login_required(views.RegistrationReceiptDetail.as_view()), name='registration_receipt'),
    url(r'^payment/manual/(\d+)/$', views.manual_registration, name='manual_registration'),
    url(r'^payment/manual/payment/$', views.manual_payment_process, name='manual_payment'),
    url(r'^certificates/$', login_required(views.certificates), name='certificates'),
    url(r'^issue/$', views.issue, name='registration_issue'),
    url(r'^issue/submit/$', views.issue_submit, name='registration_issue_submit'),
    url(r'^issue/print/(?P<registration_id>\d+)/$', views.issue_print, name='registration_issue_print'),
]
