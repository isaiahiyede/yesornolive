# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import datetime
from django.utils import timezone
from gameplay.models import Gameplay, DailyJackPot

# Create your models here.


PAYMENT_TYPE = (
    ('Add', 'Add'),
    ('Remove', 'Remove'),
    ('Refund', 'Refund'),
)


class CustomManager(models.Manager):
    def all_credits(self):
        return super(CustomManager, self).get_queryset().filter(Q(txn_type="Add"), (
                Q(status__icontains="Successful") | Q(status__icontains="Approved") | Q(status__icontains="success")))

    def all_debits(self):
        return super(CustomManager, self).get_queryset().filter((Q(txn_type="Remove") | Q(txn_type="Refund")), (
                Q(status__icontains="Successful") | Q(status__icontains="Approved")))

    def user_add_credit(self, user):
        return super(CustomManager, self).get_queryset().filter(Q(user=user), Q(txn_type="Add"), (
                Q(status__icontains="Successful") | Q(status__icontains="Approved") | Q(status__icontains="success")))

    def user_remove_credit(self, user):
        return super(CustomManager, self).get_queryset().filter(Q(user=user), Q(txn_type="Remove"), (
                Q(status__icontains="Successful") | Q(status__icontains="Approved") | Q(
            status__icontains="Approved") | Q(status__icontains="success")))

    def user_refund_credit(self, user):
        return super(CustomManager, self).get_queryset().filter(Q(user=user), Q(txn_type="Refund"), (
                Q(status__icontains="Successful") | Q(status__icontains="Approved") | Q(status__icontains="success")))


class Bank(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    txn_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    amount = models.FloatField(max_length=15)
    ref_no = models.CharField(max_length=50, null=True, blank=True)
    payment_gateway_tranx_id = models.CharField(max_length=30, null=True, blank=True)
    bank = models.CharField(max_length=50, default="PAYSTACK")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='Pending Approval')
    message = models.CharField(max_length=100, null=True, blank=True)
    transaction_fee = models.PositiveIntegerField(default=0)
    date_created = models.DateField(null=True, blank=True)
    objects = CustomManager()

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return unicode(self.user)


class Betpayments(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    game = models.ForeignKey(Gameplay, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(max_length=15)
    date_created = models.DateField(null=True, blank=True)
    djp = models.ForeignKey(DailyJackPot, null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return unicode(self.user)
