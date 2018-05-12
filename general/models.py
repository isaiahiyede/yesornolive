# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.utils import timezone
from django.conf import settings
import datetime
from django.utils import timezone
from django.template.defaultfilters import slugify
from general.modelchoices import *
from ynladmin.models import CostSetting
import math


# Create your models here.
try:
    costsetting = CostSetting.objects.get(id=1)
except:
    pass



class UserAccount(models.Model):
    """ user details """
    user = models.OneToOneField(User, unique=True, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    bank = models.CharField(max_length=100, null=True, blank=True, choices=BANK)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=50,null=True, blank=True)
    user_image = models.ImageField(upload_to="media/user_image/%Y/%M/%d/", null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDER)
    deleted = models.BooleanField(default=False)
    referred_by = models.ForeignKey('Referral', null=True, blank=True)
    profile_updated = models.BooleanField(default=False)
    validator = models.BooleanField(default=False)
    decider = models.BooleanField(default=False)
    content_provider = models.BooleanField(default=False)
    accounts = models.BooleanField(default=False)
    special_user = models.BooleanField(default=False)
    referal_link = models.CharField(max_length=100, null=True, blank=True)
    trader = models.BooleanField(default=False)
    trading_account = models.BooleanField(default=False)
    data_analyst = models.BooleanField(default=False)
    dev = models.BooleanField(default=False)
    duv = models.BooleanField(default=False)
    vendor = models.BooleanField(default=False)
    vendor_code = models.CharField(max_length=50, null=True, blank=True)
    trader_code = models.PositiveIntegerField(default=0)
    adminRealityTV = models.BooleanField(default=False)
    in_house = models.BooleanField(default=False)
    special_user_test = models.BooleanField(default=False)
    special_user_test_2 = models.BooleanField(default=False)
    total_djp_played = models.PositiveIntegerField(default=0)
    total_djp_won = models.PositiveIntegerField(default=0)
    total_djp_grand_prize_won = models.PositiveIntegerField(default=0)
    total_djp_consolation_prize_won = models.PositiveIntegerField(default=0)
    total_wjp_won = models.PositiveIntegerField(default=0)
    total_wjp_grand_prize_won = models.PositiveIntegerField(default=0)
    total_wjp_consolation_prize_won = models.PositiveIntegerField(default=0)
    total_cat_games_played = models.PositiveIntegerField(default=0)
    djp_wjp_cat = models.BooleanField(default=False)
    duv = models.BooleanField(default=False)
    wallet_balance = models.CharField(max_length=20,null=True,blank=True)
    wallet_funded = models.BooleanField(default=False)
    game_played = models.BooleanField(default=False)


    def __unicode__(self):
        return '%s' % (self.user)

    class Meta:
        verbose_name_plural = 'UserAccount'
        ordering = ['-created_on']

    def get_all_gameplay_count(self):
        gameplay_count = self.total_cat_games_played
        djp_count = self.total_djp_played
        return (gameplay_count + djp_count)

    def game_points(self):
        return self.gameplay_set.all().aggregate(Sum('game_points'))['game_points__sum']

    def referrer_points(self):
        return self.gameplay_set.all().count()



class VendorClient(models.Model):
    useraccount = models.ForeignKey(UserAccount, null=True, blank=True)
    client_code = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __unicode__(self):
        return '%s - %s : %s' % (self.useraccount.user.username, self.client_code, self.phone_number)


class AddressInfo(models.Model):
    user_account = models.ForeignKey(UserAccount, null=True)
    address_line1 = models.CharField(max_length=300, null=True)
    address_line2 = models.CharField(max_length=300, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=20, null=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return unicode(self.user)

    def full_address(self):
        return "%s, %s, %s, %s, %s. %s" % (self.address_line1, self.address_line2, self.city, self.state, self.country)


class Event(models.Model):
    """ events to be created """
    author = models.ForeignKey(User, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True, choices=CATEGORY)
    created_on = models.DateTimeField(auto_now_add=True)
    start_time = models.TimeField(default=timezone.now, auto_now_add=False)
    end_time = models.TimeField(default=timezone.now, auto_now_add=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    publish = models.BooleanField(default=False)
    event_image = models.ImageField(upload_to="media/event/%Y/%M/%d/", null=True, blank=True)
    event_msg_body = models.TextField(null=True, blank=True)
    closed = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    event_id = models.CharField(max_length=50, null=True, blank=True)
    bet_question = models.CharField(max_length=250, null=True, blank=True)
    event_decision = models.CharField(max_length=5, choices=CHOICES, null=True, blank=True)
    validated = models.BooleanField(default=False)
    decided = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True, blank=True)
    counter = models.PositiveIntegerField(default=0)
    total_amt = models.FloatField(max_length=15, default=0.0)
    not_validated_reason = models.TextField(null=True, blank=True)
    estimated_wining = models.PositiveIntegerField(default=0)
    game_ratio = models.CharField(max_length=50, null=True, blank=True, choices=RATIO)
    date_created = models.DateField(blank=True, null=True)
    event_total_value = models.FloatField(max_length=15, default=0.0)
    event_total_winnings = models.FloatField(max_length=15, default=0.0)
    event_total_profit = models.FloatField(max_length=15, default=0.0)
    event_total_stakeholder_amount = models.FloatField(max_length=15, default=0.0)
    event_total_vendor_amount = models.FloatField(max_length=15, default=0.0)
    event_total_jackpot_amount = models.FloatField(max_length=15, default=0.0)
    event_total_users_amount = models.FloatField(max_length=15, default=0.0)
    event_total_amount_won = models.FloatField(max_length=15, default=0.0)
    event_total_players = models.PositiveIntegerField(default=0)
    event_total_winners = models.PositiveIntegerField(default=0)
    event_total_losers = models.PositiveIntegerField(default=0)
    event_total_yes_choice = models.PositiveIntegerField(default=0)
    event_total_no_choice = models.PositiveIntegerField(default=0)
    event_total_yes_amount = models.FloatField(max_length=15, default=0.0)
    event_total_no_amount = models.FloatField(max_length=15, default=0.0)
    event_status = models.BooleanField(default=False)
    realityTV = models.BooleanField(default=False)
    slug = models.SlugField(max_length=500,unique=False,null=True,blank=True)


    def __unicode__(self):
        return '%s' % (self.author)

    class Meta:
        verbose_name_plural = 'Event'
        ordering = ['-created_on']

    def gameplay_total_value(self):
        amount = self.gameplay_set.filter(~Q(status='CANCELLED')).aggregate(Sum('amount'))['amount__sum']
        if not amount:
            return 0.0
        else:
            return amount

    def event_winnings(self):
        amount = self.gameplay_set.filter(choice=self.event_decision).aggregate(Sum('amount'))['amount__sum']
        if not amount:
            return 0.0
        else:
            return amount

    def total_amount_won(self):
        amount = self.gameplay_set.all().aggregate(Sum('amount_won'))['amount_won__sum']
        if not amount:
            return 0.0
        else:
            return amount

    def event_profit(self):
        amount = self.gameplay_set.filter(decision="LOST").aggregate(Sum('amount'))['amount__sum']
        # print "amt", amount
        if not amount:
            return 0.0
        else:
            return amount

    def stakeholder_amount(self):
        try:
            amount = math.floor((costsetting.amount * self.event_profit()) / 100.0)
        except:
            amount = 0.0
        return amount

    def vendor_amount(self):
        try:
            amount = math.floor((costsetting.agent_percentage * self.event_profit()) / 100.0)
        except:
            amount = 0.0
        
        return amount

    def jackpot_amount(self):
        try:
            amount = math.floor((costsetting.referal_percentage * self.event_profit()) / 100.0)
        except:
            amount = 0.0

        return amount

    def users_amount(self):
        try:
            user_percentage = 100 - costsetting.referal_percentage - costsetting.agent_percentage - costsetting.amount
            # print user_percentage
            amount = math.floor((user_percentage * self.event_profit()) / 100.0)
        except:
            amount = 0.0
            
        return amount

    def total_players(self):
        return self.gameplay_set.all().count()

    # def all_event_game_players(self):
    # 	return self.gameplay_set.all()


    def total_winners(self):
        return self.gameplay_set.filter(choice=self.event_decision).count()

    def total_losers(self):
        return self.gameplay_set.filter(~Q(choice=self.event_decision)).count()

    def total_yes_choice(self):
        return self.gameplay_set.filter(choice="YES").count()

    def total_yes_choice_played(self):
        amount = self.gameplay_set.filter(choice="YES").aggregate(Sum('amount'))['amount__sum']
        if not amount:
            return 0.0
        else:
            return amount

    def total_no_choice_played(self):
        amount = self.gameplay_set.filter(choice="NO").aggregate(Sum('amount'))['amount__sum']
        if not amount:
            return 0.0
        else:
            return amount

    def total_no_choice(self):
        return self.gameplay_set.filter(choice="NO").count()

    def get_comments(self):
        return self.comments_set.filter(deleted=False, approved=True)

    def get_comments_count(self):
        return self.get_comments().count()

    def game_status(self):
        game = self.gameplay_set.all()
        if len(game) == 0:
            status = "OPEN"
        else:
            status = game[0].status
        return status

    def event_passed(self):
        today = timezone.now().date()
        # print "type", type(self.end_date)
        # endz_date = datetime.datetime.strptime(self.end_date, '%Y-%m-%d').date()
        if self.end_date < today:
            return True
        elif self.end_date == today:
            now = datetime.datetime.now()
            # print "now", now
            current_time = now.strftime("%H:%M:%S")  # to get current time in string format
            dt = datetime.datetime.strptime(current_time, "%H:%M:%S").time()
            # print "dt", dt
            if self.end_time <= dt:
                return True
            else:
                return False
        else:
            return False


class Comments(models.Model):
    """ comments for individual events """
    user = models.ForeignKey(User, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    text = models.CharField(max_length=1000, null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    email = models.EmailField(blank=True, null=True)
    event = models.ForeignKey(Event, null=True, blank=True)
    approved = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    liked = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s' % (self.username)

    class Meta:
        verbose_name_plural = 'Comment'
        ordering = ['-created_on']

    def get_likes(self):
        return self.likes_set.all()

    def get_likes_count(self):
        return self.get_likes().count()

    def get_all_replies(self):
        return self.replies_set.all()


class Replies(models.Model):
    """ replies to comments for individual events """
    user = models.ForeignKey(User, null=True, blank=True)
    reply = models.TextField()
    comment_obj = models.ForeignKey(Comments, null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=150, null=True, blank=True)
    email = models.CharField(max_length=150, null=True, blank=True)

    def __unicode__(self):
        return '%s' % (self.username)

    class Meta:
        verbose_name_plural = 'Responses'
        ordering = ['-created_on']


class Likes(models.Model):
    """ likes to a comment"""
    user = models.ForeignKey(User, null=True, blank=True)
    like = models.BooleanField(default=False)
    comment_obj = models.ForeignKey(Comments, null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return '%s' % (self.created_on)

    class Meta:
        verbose_name_plural = 'Likes'
        ordering = ['-created_on']


class MessageCenter(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    subject = models.CharField(max_length=150, null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    no_of_comments = models.IntegerField(default=0)
    new = models.BooleanField(default=True)
    replied = models.BooleanField(default=False)
    replied_on = models.DateTimeField(null=True, blank=True)
    archive = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Messages'

    def __unicode__(self):
        return unicode(self.user)

    def getComments(self):
        return self.messagecentercomment_set.all()

    def get_comments_count(self):
        comments_count = self.getComments().count()
        return comments_count


class MessageCenterComment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    message_obj = models.ForeignKey(MessageCenter, null=True, blank=True)
    image_obj = models.ImageField(upload_to="image_obj", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Message Center Comments'

    def __unicode__(self):
        return unicode(self.user)


class Referral(models.Model):
    referrer = models.CharField(max_length=50, null=True, blank=True)
    referal = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Refferer'

    def __unicode__(self):
        return self.referal.username

    def referrer_count(self):
        value = self.useraccount_set.all().count()
        if value == None:
            return 0
        else:
            return value * 2

    def all_users(self):
        return self.useraccount_set.all()


class TradingAccount(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)

    def __unicode__(self):
        return self.user.firstname


class WalletBalances(models.Model):
    date_created = models.DateTimeField(auto_now_add=timezone)
    current_bal = models.FloatField(default=0.0,null=True,blank=True)
    amount = models.FloatField(default=0.0,null=True,blank=True)
    user = models.ForeignKey(UserAccount,null=True,blank=True)
    balance_bf = models.FloatField(default=0.0,null=True,blank=True)
    description = models.CharField(max_length=50,null=True,blank=True)

    class Meta:
        verbose_name_plural = 'Wallet Balance'

    def __unicode__(self):
        return '%s - %s' %(self.user.user.username, self.amount)


class LeaderBoard(models.Model):
    user_obj = models.ForeignKey(UserAccount, blank=True, null=True)
    total_points = models.PositiveIntegerField(default=0)
    start_date =  models.DateTimeField(null=True,blank=True)
    end_date =  models.DateTimeField(null=True,blank=True)
    date =  models.DateTimeField(null=True,blank=True)

    class Meta:
        verbose_name_plural ="Leader Board"
        ordering = ['-total_points','date']

    def __unicode__(self):
        return '%s - %s' %(self.user_obj.user.username, self.total_points)


