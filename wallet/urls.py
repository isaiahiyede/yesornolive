from django.conf.urls import patterns, include, url
from django.conf import settings
import views


urlpatterns = [
        url(r'^wallet/details/$',views.view_wallet, name="wallet"),
        url(r'^wallet/topup/$',views.main, name="main"),
        url(r'^verify/payment/$',views.verify_payment, name="verify_payment"),
       # url(r'^create/recipient/$',views.create_recipient, name="recipient"),
        url(r'^approve/payment/$', views.approve_bankpay, name="approve_bankpay"),
        url(r'^wallet/resend/otp/$',views.resend_otp, name="resend_otp"),
        url(r'^wallet/cashout/$',views.cash_out, name="cashout"),
        url(r'^wallet/initiate-transfer/$',views.initiate_transfer, name="initiate_transfer"),
        url(r'^wallet/finalize-transfer/$',views.finalize_transfer, name="finalize_transfer"),
        url(r'^pending/payment/(?P<pk>[-\w]+)/$',views.verify_pending, name="verify_pending"),
        url(r'^confirmAccount/$',views.confirm_account, name="confirm_account"),
        
]