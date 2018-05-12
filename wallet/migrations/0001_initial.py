# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('txn_type', models.CharField(max_length=20, choices=[('Add', 'Add'), ('Remove', 'Remove'), ('Refund', 'Refund')])),
                ('amount', models.FloatField(max_length=15)),
                ('ref_no', models.CharField(max_length=50, null=True, blank=True)),
                ('payment_gateway_tranx_id', models.CharField(max_length=30, null=True, blank=True)),
                ('bank', models.CharField(default='PAYSTACK', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='Pending Approval', max_length=100)),
                ('message', models.CharField(max_length=100, null=True, blank=True)),
                ('transaction_fee', models.PositiveIntegerField(default=0)),
                ('date_created', models.DateField(null=True, blank=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Betpayments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('amount', models.FloatField(max_length=15)),
                ('date_created', models.DateField(null=True, blank=True)),
                ('djp', models.ForeignKey(blank=True, to='gameplay.DailyJackPot', null=True)),
                ('game', models.ForeignKey(blank=True, to='gameplay.Gameplay', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
