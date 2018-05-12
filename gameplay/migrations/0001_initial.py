# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyJackPot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=1000, null=True, blank=True)),
                ('grand_prize', models.CharField(max_length=20, null=True, blank=True)),
                ('consolation_prize', models.CharField(max_length=20, null=True, blank=True)),
                ('created_on_date', models.DateField(null=True, blank=True)),
                ('stop_time', models.TimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('closed_by', models.CharField(max_length=20, null=True, blank=True)),
                ('closed', models.BooleanField(default=False)),
                ('all_players', models.BooleanField(default=False)),
                ('dummy_players', models.BooleanField(default=False)),
                ('top_winner', models.PositiveIntegerField(default=1)),
                ('consolation_winners', models.PositiveIntegerField(default=1)),
                ('amount', models.FloatField(default=0, max_length=15)),
                ('entry_amount', models.FloatField(default=25, max_length=15)),
                ('answer', models.CharField(max_length=1500, null=True, blank=True)),
                ('decision', models.CharField(blank=True, max_length=5, null=True, choices=[(b'YES', b'YES'), (b'NO', b'NO')])),
                ('status', models.CharField(blank=True, max_length=10, null=True, choices=[(b'OPEN', b'OPEN'), (b'CLOSED', b'CLOSED'), (b'CANCELLED', b'CANCELLED')])),
                ('total_entries', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['-created_on_date'],
                'verbose_name_plural': 'Daily JackPot',
            },
        ),
        migrations.CreateModel(
            name='DailyJackpotEntries',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(blank=True, max_length=5, null=True, choices=[(b'YES', b'YES'), (b'NO', b'NO')])),
                ('winner', models.BooleanField(default=False)),
                ('consolation', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('amount', models.FloatField(default=0, max_length=15)),
                ('ticket_no', models.CharField(max_length=50, null=True, blank=True)),
                ('unique_ref_no', models.CharField(max_length=50, null=True, blank=True)),
                ('won', models.BooleanField(default=False)),
                ('date', models.DateField(null=True, blank=True)),
                ('telephone_no', models.CharField(max_length=50, null=True, blank=True)),
                ('dailyjackpot', models.ForeignKey(blank=True, to='gameplay.DailyJackPot', null=True)),
                ('user_obj', models.ForeignKey(related_name='useracc_obj', blank=True, to='general.UserAccount', null=True)),
                ('vendor_code', models.ForeignKey(related_name='nvp_client_code', blank=True, to='general.VendorClient', null=True)),
            ],
            options={
                'ordering': ['-created_on'],
                'verbose_name_plural': 'Daily Jackpot Entries',
            },
        ),
        migrations.CreateModel(
            name='Entries',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('winner', models.BooleanField(default=False)),
                ('consolation', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('amount', models.FloatField(default=0, max_length=15)),
                ('won', models.BooleanField(default=False)),
                ('unique_ref_no', models.CharField(max_length=50, null=True, blank=True)),
                ('client_code', models.ForeignKey(related_name='nvp_client', blank=True, to='general.VendorClient', null=True)),
                ('useracc_obj', models.ForeignKey(related_name='user_obj', blank=True, to='general.UserAccount', null=True)),
            ],
            options={
                'ordering': ['-created_on'],
                'verbose_name_plural': 'Entries',
            },
        ),
        migrations.CreateModel(
            name='Gameplay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('amount', models.FloatField(max_length=15)),
                ('choice', models.CharField(blank=True, max_length=5, null=True, choices=[(b'YES', b'YES'), (b'NO', b'NO')])),
                ('status', models.CharField(blank=True, max_length=10, null=True, choices=[(b'OPEN', b'OPEN'), (b'CLOSED', b'CLOSED'), (b'CANCELLED', b'CANCELLED')])),
                ('decision', models.CharField(blank=True, max_length=10, null=True, choices=[(b'WIN', b'WIN'), (b'LOST', b'LOST'), (b'CANCELLED', b'CANCELLED')])),
                ('amount_won', models.FloatField(default=0.0, max_length=15, null=True, blank=True)),
                ('nvp', models.BooleanField(default=False)),
                ('ref_number', models.CharField(max_length=20, null=True, blank=True)),
                ('vendorClientCode', models.CharField(max_length=20, null=True, blank=True)),
                ('tel_no', models.CharField(max_length=20, null=True, blank=True)),
                ('game_points', models.PositiveIntegerField(default=5)),
                ('current_ac_bal', models.FloatField(default=0, max_length=15)),
                ('date_played', models.DateField(null=True, blank=True)),
                ('event', models.ForeignKey(blank=True, to='general.Event', null=True)),
                ('user', models.ForeignKey(blank=True, to='general.UserAccount', null=True)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name_plural': 'All Games Played',
            },
        ),
        migrations.CreateModel(
            name='WeeklyJackPot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weekly_prize', models.CharField(max_length=20, null=True, blank=True)),
                ('grand_prize', models.CharField(max_length=20, null=True, blank=True)),
                ('consolation_prize', models.CharField(max_length=20, null=True, blank=True)),
                ('top_winner', models.PositiveIntegerField(default=1)),
                ('consolation_winners', models.PositiveIntegerField(default=1)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('opened_by', models.CharField(max_length=20, null=True, blank=True)),
                ('closed_by', models.CharField(max_length=20, null=True, blank=True)),
                ('closed', models.BooleanField(default=False)),
                ('status', models.CharField(default='New', max_length=20, null=True, blank=True)),
            ],
            options={
                'ordering': ['-created_on'],
                'verbose_name_plural': 'Weekly JackPot',
            },
        ),
        migrations.AddField(
            model_name='entries',
            name='weeklyjackpot',
            field=models.ForeignKey(blank=True, to='gameplay.WeeklyJackPot', null=True),
        ),
    ]
