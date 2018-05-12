# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from general.models import Event, UserAccount, VendorClient
from general.modelchoices import CHOICES, DECISION, GAME_STATUS

# Create your models here.


class Gameplay(models.Model):
    user = models.ForeignKey(UserAccount, null=True, blank=True)
    event = models.ForeignKey(Event, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(max_length=15)
    choice = models.CharField(choices=CHOICES, max_length=5, null=True, blank=True)
    status = models.CharField(choices=GAME_STATUS, max_length=10, null=True, blank=True)
    decision = models.CharField(choices=DECISION, max_length=10, null=True, blank=True)
    amount_won = models.FloatField(max_length=15, default=0.0, null=True, blank=True)
    nvp = models.BooleanField(default=False)
    ref_number = models.CharField(max_length=20, null=True, blank=True)
    vendorClientCode = models.CharField(max_length=20, null=True, blank=True)
    tel_no = models.CharField(max_length=20, null=True, blank=True)
    game_points = models.PositiveIntegerField(default=5)
    current_ac_bal = models.FloatField(max_length=15, default=0)
    date_played = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'All Games Played'

    def __unicode__(self):
        return unicode(self.user)


class WeeklyJackPot(models.Model):
    weekly_prize = models.CharField(max_length=20, null=True, blank=True)
    grand_prize = models.CharField(max_length=20, null=True, blank=True)
    consolation_prize = models.CharField(max_length=20, null=True, blank=True)
    top_winner = models.PositiveIntegerField(default=1)
    consolation_winners = models.PositiveIntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    opened_by = models.CharField(max_length=20, null=True, blank=True)
    closed_by = models.CharField(max_length=20, null=True, blank=True)
    closed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, null=True, blank=True, default="New")

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Weekly JackPot'

    def __unicode__(self):
        return unicode(self.start_date)

    def get_all_entries(self):
        return self.entries_set.all()


class DailyJackPot(models.Model):
    question = models.CharField(max_length=1000, null=True, blank=True)
    grand_prize = models.CharField(max_length=20, null=True, blank=True)
    consolation_prize = models.CharField(max_length=20, null=True, blank=True)
    created_on_date = models.DateField(null=True, blank=True)
    stop_time = models.TimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    closed_by = models.CharField(max_length=20, null=True, blank=True)
    closed = models.BooleanField(default=False)
    all_players = models.BooleanField(default=False)
    dummy_players = models.BooleanField(default=False)
    top_winner = models.PositiveIntegerField(default=1)
    consolation_winners = models.PositiveIntegerField(default=1)
    amount = models.FloatField(max_length=15, default=0)
    entry_amount = models.FloatField(max_length=15, default=25)
    answer = models.CharField(max_length=1500, null=True, blank=True)
    decision = models.CharField(choices=CHOICES, max_length=5, null=True, blank=True)
    status = models.CharField(choices=GAME_STATUS, max_length=10, null=True, blank=True)
    total_entries = models.PositiveIntegerField(default=0)
    Dtickets = models.PositiveIntegerField(default=0)
    start = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_on_date']
        verbose_name_plural = 'Daily JackPot'

    def __unicode__(self):
        return unicode(self.question)

    def get_all_entries(self):
        return self.dailyjackpotentries_set.filter(true_value=False)

    def entries_count(self):
        return self.dailyjackpotentries_set.filter(true_value=False).count()

    def get_qualified_entries(self, decision):
        return self.dailyjackpotentries_set.filter(choice=self.decision, user_obj__in_house=False, true_value=False)

    def get_winners(self):
        return self.dailyjackpotentries_set.filter(won=True)


class DailyJackpotEntries(models.Model):
    dailyjackpot = models.ForeignKey(DailyJackPot, null=True, blank=True)
    vendor_code = models.ForeignKey(VendorClient, null=True, blank=True, related_name='nvp_client_code')
    user_obj = models.ForeignKey(UserAccount, null=True, blank=True, related_name = 'useracc_obj')
    choice = models.CharField(choices=CHOICES, max_length=5, null=True, blank=True)
    winner = models.BooleanField(default=False)
    consolation = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(max_length=15, default=0)
    ticket_no = models.CharField(max_length=50, null=True, blank=True)
    unique_ref_no = models.CharField(max_length=50, null=True, blank=True)
    won = models.BooleanField(default=False)
    date = models.DateField(blank=True, null=True)
    telephone_no = models.CharField(max_length=50, null=True, blank=True)
    user_email = models.CharField(max_length=150, null=True, blank=True)
    user_first_name = models.CharField(max_length=150, null=True, blank=True)
    user_last_name = models.CharField(max_length=150, null=True, blank=True)
    true_value = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Daily Jackpot Entries'

    def __unicode__(self):
        return unicode(self.ticket_no)


class Entries(models.Model):
    weeklyjackpot = models.ForeignKey(WeeklyJackPot, null=True, blank=True)
    client_code = models.ForeignKey(VendorClient, null=True, blank=True, related_name='nvp_client')
    useracc_obj = models.ForeignKey(UserAccount, null=True, blank=True, related_name='user_obj')
    winner = models.BooleanField(default=False)
    consolation = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    created_on = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    amount = models.FloatField(max_length=15, default=0)
    won = models.BooleanField(default=False)
    unique_ref_no = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Entries'

    def __unicode__(self):
        return unicode(self.unique_ref_no)
