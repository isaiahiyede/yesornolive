# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.forms.models import model_to_dict
from wallet.models import Bank
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.models import User
from operator import attrgetter
from django.core import serializers
from django.db.models import Q, Sum
from django.contrib import messages
from django.template.context import RequestContext
from django.db.models import Count
from django import template
from itertools import chain
import re
import hashlib
import random, datetime, string
import urllib
import time, math
from django.core.urlresolvers import reverse
import json
from django.db.models import Sum
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMessage
from general.models import *
from general.forms import *
from general.views import paginate_list
from gameplay.models import Gameplay, Entries, WeeklyJackPot, DailyJackPot, DailyJackpotEntries
from wallet.models import Bank, Betpayments
from ynladmin.models import CostSetting
from ynladmin.forms import CostSettingForm, WeeklyJackpotForm, DailyJackPotForm, DailyJackPotEditForm
from wallet.views import purchase_ref, generate_purchaseRef
from general.custom_functions import *
from wallet.account_standing import account_standing
from collections import Counter
from datetime import timedelta, date
from django.template.defaultfilters import slugify
import csv



# Create your views here.
def randomNumber(value):
    allowed_chars = ''.join((string.digits))
    unique_id = ''.join(random.choice(allowed_chars) for _ in range(5))
    while Event.objects.filter(event_id=unique_id):
        unique_id = ''.join(random.choice(allowed_chars) for _ in range(5))
    return '#' + 'EN' + unique_id



@login_required
def data_update(request):
    all_users = UserAccount.objects.filter(profile_updated=True,validator=False,special_user=False, content_provider=False,decider=False,accounts=False).distinct()

    all_users_count = all_users.count()
    print 'count', all_users_count
    funded_and_not_played_list = []
    
    for user in all_users:
        user.wallet_balance = float(account_standing(request, user.user))

        if (Bank.objects.user_add_credit(user.user).aggregate(Sum('amount')) > 0.0 and (user.wallet_balance > 0.0)):
            user.wallet_funded = True
            if user.get_all_gameplay_count() == 0:
                user.game_played = False
                funded_and_not_played_list.append(user)
                user.save()
            else:
                user.game_played = True
                user.save()


    # print funded_and_not_played_list
    # print len(funded_and_not_played_list)

    return redirect(request.META['HTTP_REFERER'])
    

def allWalletsBalance():
    # added_payments = Bank.objects.all_credits().aggregate(Sum('amount'))
    # print "added_payments", added_payments
    # used_payments = Bank.objects.all_debits().aggregate(Sum('amount'))
    # print "used_payments", used_payments
    # total_bet_payments = Betpayments.objects.all().aggregate(Sum('amount'))
    # print total_bet_payments, "total bet payments"
    users_add_funds = Bank.objects.filter(Q(txn_type="Add"), Q(bank="PAYSTACK"), (
            Q(status__icontains="Successful") | Q(status__icontains="Approved") | Q(
        status__icontains="success"))).aggregate(Sum('amount'))['amount__sum']
    users_remove_fund = Bank.objects.filter(Q(txn_type="Remove"), (
            Q(status__icontains="Successful") | Q(status__icontains="Approved") | Q(status__icontains="Approved") | Q(
        status__icontains="success"))).aggregate(Sum('amount'))['amount__sum']
    transaction_fees = Bank.objects.filter(Q(txn_type="Remove"), (
            Q(status__icontains="Successful") | Q(status__icontains="Approved") | Q(status__icontains="Approved") | Q(
        status__icontains="success"))).aggregate(Sum('transaction_fee'))['transaction_fee__sum']
    users_remove_funds = users_remove_fund + transaction_fees
    # print "userremfund", users_remove_funds
    users_refund = Bank.objects.filter(Q(txn_type="Refund"), (
            Q(status__icontains="Successful") | Q(status__icontains="Approved") | Q(
        status__icontains="success"))).aggregate(Sum('amount'))['amount__sum']
    return users_add_funds, users_remove_funds, users_refund


@login_required
def getQueriedObjects(request, query):
    return Event.objects.filter(Q(title__icontains=query) |
                                Q(category__icontains=query) |
                                Q(bet_question__icontains=query) |
                                Q(event_msg_body__icontains=query) |
                                Q(event_id__icontains=query) |
                                Q(author__first_name__icontains=query)
                                ).distinct()


@login_required
def getSimillarContent(request, events, query):
    context = {}
    if query:
        # print "query", query
        events = getQueriedObjects(request, query)
    all_event = events
    template_name = 'ynladmin/events.html'
    event_form = EventForm()
    context['event_form'] = event_form
    context['all_events'] = all_event
    return event_form, all_event, template_name


def daterange(date1, date2):
    dates = []
    for n in range(int((date2 - date1).days) + 1):
        dates.append(date1 + timedelta(n))
    return dates


@login_required(redirect_field_name='next', login_url=None)
def admin_pages(request, page_to):
    from datetime import datetime
    context = {}
    context['page_to'] = page_to
    try:
        query = request.GET.get('q')
    except:
        pass
    try:
        filter_str = str(page_to).split('-')[1]
        if query:
            # print start_date, end_date
            start_date = datetime.strptime(request.GET.get('to-date-daily'), "%m/%d/%Y").date()
            end_date = datetime.strptime(request.GET.get('from-date-daily'), "%m/%d/%Y").date() 

            payment = Bank.objects.filter(status=filter_str, created_at__gte=end_date,
                                          created_at__lte=start_date).values('created_at', 'ref_no','user__pk',
                    'user__first_name', 'user__last_name', 'bank', 'message', 'amount', 'status','pk' )

        
        # payment = Bank.objects.filter(status="Successful")[0]
        # print payment

        else:
            today = timezone.now().date() + timedelta(days=1)
            last_week = today - timedelta(days=2)
            payment = Bank.objects.filter(status=filter_str, created_at__gte=last_week, created_at__lte=today).values('created_at', 'ref_no','user__pk',
                                                                             'user__first_name', 'user__last_name', 'bank', 'message', 'amount', 'status','pk' )
        template_name = 'ynladmin/payment.html'
        context['payments'] = payment
        request.session['page_to'] = page_to
        # print payment
    # event_passed = check_eventTime(request)
    # if event_passed != "":
    #   pkg = event_passed
    #   title = "Event Decision"
    #   text = "general/decision_mail.txt"
    #   useraccount = UserAccount.objects.filter(decider=True)
    #   for user in useraccount:
    #       mail_user(request, user.user, title, text, pkg)
    except:
        page_to = page_to
    
    user_obj = request.user

    try:
        user_acc_obj = UserAccount.objects.get(user=user_obj)
    except:
        return redirect(request.META['HTTP_REFERER'])

    user_acc_obj = UserAccount.objects.get(user=user_obj)

    if user_acc_obj.special_user:
        page_to = page_to
    # elif user_acc_obj.validator and user_acc_obj.decider:
    #   page_to =
    elif user_acc_obj.accounts:
        page_to = "payment"
    elif user_acc_obj.content_provider:
        page_to = "content_provider"
    elif user_acc_obj.data_analyst:
        if page_to == "game":
            page_to = 'game'
        else:
            page_to = "reports"
    elif user_acc_obj.validator and user_acc_obj.decider:
        if page_to == 'statistics':
            page_to = 'to_validate'
        page_to = page_to
    elif user_acc_obj.validator:
        page_to = "to_validate"
    elif user_acc_obj.trader:
        page_to = "trading"
    elif user_acc_obj.vendor:
        if page_to == "vendor":
            page_to = "vendor"
        elif page_to == "gamesVendor":
            page_to = "gamesVendor"
        elif page_to == "djpVendor":
            page_to == "djpVendor"
        elif page_to == "viewDjpGames":
            page_to = "viewDjpGames"
        else:
            page_to = "paymentsVendor"
    elif user_acc_obj.adminRealityTV:
        page_to = "adminRealityTV"
    else:
        page_to = "to_decide"
    context['user_acc_obj'] = user_acc_obj

    # print "I got here", query
    if query:
        # print "query", query
        start_date = datetime.strptime(request.GET.get('to-date-daily'), "%m/%d/%Y").date()
        end_date = datetime.strptime(request.GET.get('from-date-daily'), "%m/%d/%Y").date()

    if page_to == 'events':
        events = Event.objects.filter(deleted=False,closed=False).values('event_id','title','category',
                                'end_date','closed','publish',
                                'validated', 'not_validated_reason',
                                'id','decided','pk','date_created')
        context['news'] = 'news'
        context['all_events'] = events
        template_name = 'ynladmin/events.html'

    if page_to == 'vendor':
        context['all_events'] = events = Event.objects.filter(deleted=False,closed=False)
        context['allVendorClients'] = VendorClient.objects.filter(useraccount=user_acc_obj).count()
        context['game_count'] = Gameplay.objects.filter(user=user_acc_obj, nvp=True).count()
        context['balance'] = account_standing(request, request.user)
        template_name = 'ynladmin/vendorpage.html'

    elif page_to == 'gamesVendor':
        game = Gameplay.objects.filter(user=user_acc_obj, nvp=True)
        game_count = game.count()
        game_won = game.filter(decision="WIN")
        context['game'] = game
        context['game_won'] = game_won
        context['game_count'] = game_count
        template_name = 'ynladmin/vendorgames.html'

    elif page_to == 'viewDjpGames':
        template_name = 'ynlsnippet/vendor_djp_games_view.html'
        djp_winners = DailyJackpotEntries.objects.filter(user_obj=request.user.useraccount).values('telephone_no', 'ticket_no','amount','date', 'won','choice')
        context['djp_winners'] = djp_winners

    elif page_to == 'djpVendor':
        context['allVendorClients'] = VendorClient.objects.filter(useraccount=request.user.useraccount).count()
        today = timezone.now().date()
        game = DailyJackPot.objects.get(created_on_date=today)
        all_vendor_djps = DailyJackPot.objects.all()
        count = 0
        for vendor in all_vendor_djps:
            count += vendor.get_all_entries().filter(user_obj=request.user.useraccount).count()
        context['count'] = count
        allDjpPlayed = game.get_all_entries().filter(user_obj=request.user.useraccount)
        context['amount_played'] = float(allDjpPlayed.count()) * 25
        context['allDjpPlayed'] = allDjpPlayed.count()
        games = DailyJackPot.objects.all().order_by("created_on_date")
        context['games'] = games
        context['balance'] = account_standing(request, request.user)
        context['total_amount_played'] = float(count) * 25
        context['today'] = today
        template_name = 'ynladmin/ygoDailyJackpotPlay.html'

    elif page_to == 'adminRealityTV':
        events = Event.objects.filter(realityTV=True,publish=True,validated=True,deleted=False).values('event_id','title','category',
            'end_date','closed','publish','event_total_value','event_total_winnings',
            'validated', 'not_validated_reason','event_total_profit','event_total_stakeholder_amount',
            'id','decided','pk','date_created','event_total_vendor_amount','event_total_jackpot_amount',
            'event_total_users_amount', 'event_total_amount_won', 'event_total_players','total_amt',
            'event_total_winners','event_total_losers','event_total_yes_choice','event_total_no_choice',
            'event_total_yes_amount', 'event_total_no_amount', 'event_status','counter')

        context['total_bbn_events'] = events.count()
        total_bbn_amount_staked = Gameplay.objects.filter(~Q(decision='CANCELLED'),event__realityTV=True).aggregate(Sum('amount'))['amount__sum']
        gross_bbn_amount = Gameplay.objects.filter(~Q(decision='CANCELLED'),event__realityTV=True, status='CLOSED').aggregate(Sum('amount'))['amount__sum']
        total_bbn_amount_won = Gameplay.objects.filter(~Q(decision='CANCELLED'),event__realityTV=True).aggregate(Sum('amount_won'))['amount_won__sum']
        print "gross_bbn_amount - total_bbn_amount_won", gross_bbn_amount, total_bbn_amount_won

        try:
            total_amount_stakeholder = gross_bbn_amount - total_bbn_amount_won
        except:
            total_amount_stakeholder = 0.0
            
        context['total_bbn_amount_staked'] = total_bbn_amount_staked
        context['total_amount_stakeholder'] = total_amount_stakeholder
      
        context['events'] = events
        template_name = 'ynladmin/adminRealityTV.html'

    elif page_to == 'paymentsVendor':
        payment = Bank.objects.filter(user=request.user)
        context['payments'] = payment
        template_name = 'ynladmin/vendorpayments.html'

    elif page_to == 'trading':
        template_name = 'ynladmin/trader.html'
        get_trader_code = get_the_trader(request)
        all_users = UserAccount.objects.filter(trader_code=get_trader_code)

        useraccount_form = UserAccountForm()
        user_form = UserForm()
        context['useraccount_form'] = useraccount_form
        context['all_users'] = all_users
        context['user_form'] = user_form

    elif page_to == 'to_decide':
        import datetime
        today = timezone.now().date()
        now = datetime.datetime.now()  # To get current date and time
        current_time = now.strftime("%I:%M %p")
        dt = datetime.datetime.strptime(current_time, "%I:%M %p").time()
        events = []
        eventz = Event.objects.filter(
            deleted=False,
            publish=True,
            end_date__lte=today,
            validated=True,
            decided=False,
            closed=False)
        for event in eventz:
            if event.end_date < today:
                events.append(event)
            else:
                if event.end_time <= dt:
                    events.append(event)
        context['decider'] = "decider"
        context['all_events'] = events
        template_name = 'ynladmin/events.html'

    elif page_to == 'to_validate':
        events = Event.objects.filter(deleted=False, validated=False).values('event_id','title',
                            'category',
                            'end_date','closed','publish',
                            'validated', 'not_validated_reason',
                            'id','decided','pk','date_created')
        query = request.GET.get('q')
        context['validator'] = "validator"
        context['all_events'] = events
        template_name = 'ynladmin/events.html'

    elif page_to == 'reports':
        # data = export_csv(request)
        # events = Event.objects.all()
        # for event in events:
        #     try:
        #         event.slug = slugify(event.title)
        #         event.save()
        #     except:
        #         pass

        # all_users = UserAccount.objects.all()
        # for user in all_users:
        #     try:
        #         if user.get_all_gameplay_count() > 0:
        #             user.wallet_funded = True
        #             user.game_played = True
        #             user.save()
        #     except:
        #         pass

        # duplicate_dict = UserAccount.objects.values('phone_number').annotate(Count('id')) .order_by().filter(id__count__gt=1)
        # for dicto in duplicate_dict:
        #     num = dicto['phone_number']
        #     users = UserAccount.objects.filter(phone_number=num)
        #     for user in users:
        #         user.phone_number = None
        #         user.save()
        
        # print(len(duplicate_dict))
        # print(duplicate_dict)

        template_name = 'ynladmin/reports.html'

    elif page_to == 'active_users':
        
        users = UserAccount.objects.select_related('user').filter(user__is_staff=False,in_house=False,trading_account=False,
                        profile_updated=True, trader=False, djp_wjp_cat=True).values('user__username','user__pk',
                        'total_djp_played', 'total_djp_won','total_djp_grand_prize_won','wallet_balance',
                        'total_djp_consolation_prize_won', 'total_wjp_grand_prize_won',
                        'total_wjp_won', 'total_cat_games_played','total_wjp_consolation_prize_won','wallet_balance')

        context['users'] = users
        template_name = 'ynladmin/active_users.html'

    elif page_to == 'statistics':
        # data = export_csv(request)
        # print "data", data
        events = Event.objects.filter(deleted=False, closed=False, decided=True)
        users = User.objects.filter(is_staff=False).count()
        total_amount_staked = Gameplay.objects.filter(~Q(decision='CANCELLED')).aggregate(Sum('amount'))['amount__sum']
        gross_amount = Gameplay.objects.filter(~Q(decision='CANCELLED'), status='CLOSED').aggregate(Sum('amount'))[
            'amount__sum']
        total_amount_won = Gameplay.objects.all().aggregate(Sum('amount_won'))['amount_won__sum']
        total_amount_stakeholder = gross_amount - total_amount_won
        all_events = Event.objects.filter(deleted=False)
        total_events = all_events.count()
        open_events = all_events.filter(closed=False).count()
        closed_events = all_events.filter(closed=True).count()
        # print "game", users, total_amount_staked
        users_add_fund = Bank.objects.filter(Q(txn_type="Add"), (
                Q(status__icontains="Successful") | Q(status__icontains="Approved") | Q(
            status__icontains="success"))).aggregate(Sum('amount'))['amount__sum']
        users_payouts = Bank.objects.filter(Q(txn_type="Remove"), Q(message__icontains="Cash out"), (
                Q(status__icontains="Successful") | Q(status__icontains="Approved") | Q(
            status__icontains="success"))).aggregate(Sum('amount'))['amount__sum']
        context['users_payouts'] = users_payouts
        context['all_events'] = events
        context['users'] = users
        context['total_amount_staked'] = total_amount_staked
        context['total_amount_won'] = total_amount_won
        context['total_amount_stakeholder'] = total_amount_stakeholder
        context['total_events'] = total_events
        context['open_events'] = open_events
        context['closed_events'] = closed_events
        users_add_funds, users_remove_funds, users_refund = allWalletsBalance()
        total_amt_wallet = users_add_fund - (users_remove_funds - users_refund)
        context['users_add_funds'] = users_add_funds
        context['users_remove_funds'] = users_remove_funds
        context['users_refund'] = users_refund
        context['total_amt_wallet'] = total_amt_wallet
        template_name = 'ynladmin/ynl_statistics.html'

    elif page_to == 'decide_validate':
        events = Event.objects.filter(deleted=False, publish=False, validated=False, decided=False)
        query = request.GET.get('q')
        context['event_form'], context['all_events'], template_name = getSimillarContent(request, events, query)

    elif page_to == 'content_provider':
        today = timezone.now().date()
        # yesterday = timezone.now().date() - timedelta(days=1)
        # events = Event.objects.filter(deleted=False,date_created__range=[yesterday,today])
        events = Event.objects.filter(deleted=False,closed=False).values('event_id','title','category',
                                    'end_date','closed','publish',
                                    'validated', 'not_validated_reason',
                                    'id','decided','pk','date_created')
        context['news'] = 'news'
        context['all_events'] = events
        template_name = 'ynladmin/events.html'

    elif page_to == 'users':
        template_name = 'ynladmin/users.html'
        all_users = UserAccount.objects.filter(deleted=False).values('user__first_name','pk',
                                    'user__last_name', 'account_number', 'bank', 'phone_number', 'gender')
        useraccount_form = UserAccountForm()
        user_form = UserForm()
        context['useraccount_form'] = useraccount_form
        context['all_users'] = all_users
        context['user_form'] = user_form

    elif page_to == 'messages':
        template_name = 'ynladmin/messages.html'
        messages = MessageCenter.objects.all()
        comment_form = MessageCenterCommentForm()
        context['comment_form'] = comment_form
        context['new_messages'] = new_messages
        context['replied_messages'] = replied_messages
        context['archived_messages'] = archived_messages
        context['deleted_messages'] = deleted_messages
        context['new_count'] = new_messages.count()
        context['replied_count'] = replied_messages.count()
        context['archived_count'] = archived_messages.count()
        context['deleted_count'] = deleted_messages.count()

    elif page_to == "payment":
        if query:
            # print start_date, end_date
            end_date = end_date + timedelta(days=1)
            payment = Bank.objects.filter(created_at__gte=end_date,
                                          created_at__lte=start_date).values('created_at', 'ref_no',
                    'user__first_name', 'user__last_name', 'bank', 'message', 'amount', 'status','pk' )

        # payment = Bank.objects.filter(status="Successful")[0]
        # print payment

        else:
            today = timezone.now().date() + timedelta(days=1)
            last_week = today - timedelta(days=2)
            payment = Bank.objects.filter((~Q(status="failed")), created_at__gte=last_week, created_at__lte=today).values('created_at', 'ref_no',
                                                                             'user__first_name', 'user__last_name', 'bank', 'message', 'amount', 'status','pk' )
        template_name = 'ynladmin/payment.html'
        context['payments'] = payment


    # yesterday = timezone.now().date() - timedelta(days=1)
    elif page_to == 'game_payments':
        today = timezone.now().date()
        template_name = "ynladmin/game_payments.html"
        # yesterday = timezone.now().date() - timedelta(days=1)
        payment = Betpayments.objects.filter(date_created=today).values('date',
                                'user__first_name',
                                'user__last_name',
                                'user__email','amount','game__event__event_id')
        context['payments'] = payment

    elif page_to == "comment":
        users = UserAccount.objects.filter(deleted=False)
        template_name = 'ynladmin/typeform.html'
        context['users'] = users

    elif page_to == "game":
        template_name = 'ynladmin/gameplay.html'

        events = Event.objects.all().values('event_id','title','category',
            'end_date','closed','publish','event_total_value','event_total_winnings',
            'validated', 'not_validated_reason','event_total_profit','event_total_stakeholder_amount',
            'id','decided','pk','date_created','event_total_vendor_amount','event_total_jackpot_amount',
            'event_total_users_amount', 'event_total_amount_won', 'event_total_players','total_amt',
            'event_total_winners','event_total_losers','event_total_yes_choice','event_total_no_choice',
            'event_total_yes_amount', 'event_total_no_amount', 'event_status', 'counter')

        context['event'] = events

    elif page_to == "event_stats":
        template_name = 'ynladmin/events_stats.html'
        events = Event.objects.filter(closed=True).values('event_id','title','category',
            'end_date','closed','publish','event_total_value','event_total_winnings',
            'validated', 'not_validated_reason','event_total_profit','event_total_stakeholder_amount',
            'id','decided','pk','date_created','event_total_vendor_amount','event_total_jackpot_amount',
             'event_total_users_amount', 'event_total_amount_won', 'event_total_players','total_amt',
             'event_total_winners','event_total_losers','event_total_yes_choice','event_total_no_choice',
             'event_total_yes_amount', 'event_total_no_amount', 'event_status','counter')

        context['events'] = events

    elif page_to == "wjp":
        template_name = 'ynladmin/wjp.html'
        context['weekly_jackpot'] = WeeklyJackPot.objects.all().values(
            'end_date','start_date','weekly_prize','top_winner','consolation_winners',
            'grand_prize','consolation_prize','created_on')

    elif page_to == "djp":
        template_name = 'ynladmin/djp.html'
        djp = DailyJackPot.objects.all().order_by('-created_on_date').values('created_on_date', 'total_entries',
                            'question', 'amount', 'grand_prize', 'consolation_prize', 'id', 'closed', 'end_time')
        context['total_prize'] = djp.aggregate(Sum('amount'))['amount__sum']
        context['form'] = DailyJackPotForm()
        context['daily_jackpot'] = djp
        context['now'] = timezone.now()
        context['entries'] = DailyJackpotEntries.objects.all().count()

    elif page_to == "settings":
        if request.method == "POST":
            try:
                cost = CostSetting.objects.get(id=1)
                form = CostSettingForm(request.POST, instance=cost)
            except:
                form = CostSettingForm(request.POST)
            if form.is_valid():
                form.save()
            # messages.success(request,"Amount Updated Successfully")
            else:
                # print form.errors
                messages.error(request, "Please try again")
        template_name = 'ynladmin/settings.html'
        try:
            cost = CostSetting.objects.get(id=1)
            form = CostSettingForm(instance=cost)
        except:
            form = CostSettingForm()
        context['form'] = form
    return render(request, template_name, context)


@login_required
def create_new_event(request):
    # print "i got here"
    context = {}
    user_obj = request.user
    user_acc_obj = UserAccount.objects.get(user=user_obj)
    event_form = EventForm()
    all_event = paginate_list(request, Event.objects.filter(deleted=False), 12)
    context['event_form'] = event_form
    context['all_events'] = all_event
    context['user_acc_obj'] = user_acc_obj
    template_name = 'ynladmin/events.html'
    if request.method == 'POST':
        rp = request.POST
        # print 'rp:', rp
        if rp.has_key('edit_event'):
            print "i wanna edit"
            event_obj = Event.objects.get(event_id=rp.get('event_track_num'))
            form = EventForm(request.POST, request.FILES, instance=event_obj)
            if form.is_valid():
                print 'The form is valid'
                today = timezone.now().date()
                end_date = rp.get('end_date')
                end_time = rp.get('end_time')
                endz_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                print "end_time", end_time, type(end_time)
                if endz_date < today:
                    messages.warning(request, 'Unsuccessful...End date cannot be in the past')
                    return redirect(request.META['HTTP_REFERER'])
                if endz_date == today:
                    today = datetime.datetime.now()  # To get current date and time
                    current_time = today.strftime("%I:%M %p")  # to get current time in string format
                    print "current_time", current_time
                    dt = datetime.datetime.strptime(current_time,
                                                    "%I:%M %p").time()  # to convert datetime.datetime object to datetime.time object
                    print "dt", dt
                    endz_time = datetime.datetime.strptime(end_time, "%I:%M %p").time()
                    print endz_time
                    if endz_time <= dt:
                        messages.error(request, 'Unsuccessful...End time cannot be less than or equal to current time')
                        return redirect(request.META['HTTP_REFERER'])
                edit_form = form.save(commit=False)
                if edit_form.publish == True:
                    edit_form.start_date = today
                    edit_form.published_date = timezone.now()
                    current_time = today.strftime("%H:%M:%S")
                    edit_form.start_time = datetime.datetime.strptime(current_time, "%H:%M:%S").time()

                edit_form.author = request.user
                edit_form.slug = slugify(edit_form.title)
                edit_form.event_id = rp.get('event_track_num')
                if rp.get('realityTV'):
                    edit_form.realityTV = True
                edit_form.save()
                messages.success(request, 'Event has been successfully updated')

                if edit_form.publish:
                    date = edit_form.published_date.strftime('%Y-%m-%d %H:%M:%S')
                    # print "date", date
                    activity_history(
                        user=request.user,
                        obj_id=edit_form.pk,
                        obj_model_name="Event", action="published",
                        message="Event with number" + ' ' + edit_form.event_id + " was published by " + request.user.username + ' ' + ' on ' + date)
                else:
                    current_time = today.strftime("%I:%M %p")
                    activity_history(
                        user=request.user,
                        obj_id=edit_form.pk,
                        obj_model_name="Event", action="edited",
                        message="Event with number" + ' ' + edit_form.event_id + " was edited by " + request.user.username + ' ' + ' on ' + str(
                            current_time))

                return redirect(reverse('ynladmin:admin_pages', args=['events']))

            else:
                print form.errors
        elif rp.has_key('edit_user'):
            print "i wanna edit this user"
            user_obj = UserAccount.objects.get(id=rp.get('user_id'))
            form = UserAccountForm(request.POST, request.FILES, instance=user_obj)
            if form.is_valid():
                print 'The form is valid'
                form.save()
                return redirect(reverse('ynladmin:admin_pages', args=['users']))
            else:
                print form.errors
        else:
            form = EventForm(request.POST, request.FILES)
            if form.is_valid():
                print 'The form is valid'
                today = timezone.now().date()
                end_date = rp.get('end_date')
                end_time = rp.get('end_time')
                endz_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                if endz_date < today:
                    messages.warning(request, 'Unsuccessful...End date cannot be in the past')
                    return redirect(request.META['HTTP_REFERER'])
                if end_date == today:
                    today = datetime.datetime.now()  # To get current date and time
                    current_time = today.strftime("%I:%M %p")  # to get current time in string format
                    dt = datetime.datetime.strptime(current_time,
                                                    "%I:%M %p").time()  # to convert datetime.datetime object to datetime.time object
                    endz_time = datetime.datetime.strptime(end_time, "%I:%M %p").time()
                    # print value >= dt
                    if endz_time <= dt:
                        messages.error(request, 'Unsuccessful...End time cannot be less than or equal to current time')
                        return redirect(request.META['HTTP_REFERER'])

                create_event_form = form.save(commit=False)
                # create_event_form.event_msg_body = str(re.sub('<[^<]+?>', '', rp.get('event_msg_body'))).replace('&nbsp;','')
                create_event_form.author = request.user
                create_event_form.date_created = timezone.now().date()
                create_event_form.event_id = randomNumber(str(rp.get('category'))[:2])
                create_event_form.slug = slugify(create_event_form.title)
                if rp.get('realityTV'):
                    create_event_form.realityTV = True
                create_event_form.save()
                title = "New Event " + create_event_form.event_id + " Created"
                text = "general/validators_mail.html"
                useraccount = UserAccount.objects.filter(validator=True)
                for user in useraccount:
                    mail_user(request, user.user, title, text, pkg=create_event_form)
                messages.success(request, 'Event has been successfully created')
                current_time = today.strftime("%I:%M %p")
                activity_history(
                    user=request.user,
                    obj_id=create_event_form.pk,
                    obj_model_name="Event", action="created",
                    message="Event with number" + ' ' + create_event_form.event_id + " was created by " + request.user.username + ' ' + ' on ' + str(
                        current_time))
                return redirect(reverse('ynladmin:admin_pages', args=['events']))
            else:
                print form.errors
            return render(request, template_name, context)

        return render(request, template_name, context)
    else:
        return render(request, template_name, context)


@login_required
def delete_event(request, event_id):
    event_obj = Event.objects.get(id=event_id)
    event_obj.deleted = True
    event_obj.save()
    return redirect(reverse('ynladmin:admin_pages', args=['events']))


@login_required
def event_decision(request):
    if request.method == 'GET':
        event_id = request.GET.get('event_id')
        event = Event.objects.get(id=event_id)
        form = DecisionForm(instance=event)
        # event = Event.objects.get(id = event_id)
        return render(request, 'general_snippets/decison_modal.html', {'event': event, 'form': form})
    else:
        # print "i am a post"
        event_id = request.POST.get('event_id')
        event = Event.objects.get(id=event_id)
        form = DecisionForm(request.POST, instance=event)
        form.save(commit=False)
        form.save()
        event.decided = True
        event.save()

        activity_history(user=request.user, obj_id=event.pk, obj_model_name="Event", action="Decided",
                         message='Event ' + event.event_id + ' ' + ' was decided by ' + request.user.username + ' and the decision was ' + event.event_decision)

        return redirect(reverse('ynladmin:admin_pages', args=['to_decide']))


@login_required
def delete_user(request, user_id):
    user_obj = UserAccount.objects.get(id=user_id)
    user_obj.deleted = True
    user_obj.save()
    return redirect(reverse('ynladmin:admin_pages', args=['users']))


@login_required
def view_edit_event(request):
    context = {}
    # print request.GET
    template_name = ""
    if request.GET.has_key('edit'):
        print "editing"
        template_name = 'ynladmin/edit_event.html'
    elif request.GET.has_key('create_event'):
        event_form = EventForm()
        context['event_form'] = event_form
        context['create_event'] = True
        template_name = 'ynladmin/edit_event.html'
        return render(request, template_name, context)
    else:
        template_name = 'ynladmin/view_event.html'
    event_track_num = request.GET.get('event_track_num')
    event_obj = Event.objects.get(event_id=event_track_num)
    event_form = EventForm(instance=event_obj)
    event_validated = event_obj.validated
    context['event_track_num'] = event_track_num
    context['event_form'] = event_form
    context['event_validated'] = event_validated
    return render(request, template_name, context)


@login_required
def edit_user(request):
    context = {}
    print request.GET
    user_id = request.GET.get('user_id')
    useracc_obj = UserAccount.objects.get(id=user_id)
    # useraccount_form = UserAccountForm(instance=useracc_obj)
    context['user_id'] = user_id
    context['useraccount_form'] = useracc_obj
    return render(request, 'ynladmin/user_edit.html', context)


@login_required
def get_user_activity(request):
    context = {}
    # print request.GET
    # print "getting here"
    user_id = request.GET.get('user_id')
    useracc_obj = UserAccount.objects.get(id=user_id)
    request_user = useracc_obj.user
    balance = account_standing(request, request_user)
    game = Gameplay.objects.filter(user=useracc_obj)
    game_count = game.count()
    game_won = game.filter(decision="WIN")
    game_lost = game.filter(decision="LOST")
    # useraccount_form = UserAccountForm(instance=useracc_obj)
    context['user_id'] = user_id
    context['games'] = game
    context['game_count'] = game_count
    context['game_won'] = game_won.count()
    context['game_lost'] = game_lost.count()
    context['balance'] = balance
    context['total_amount_staked'] = game.filter(~Q(decision='CANCELLED')).aggregate(Sum('amount'))['amount__sum']
    context['total_amount_won'] = game.filter(decision="WIN").aggregate(Sum('amount_won'))['amount_won__sum']
    context['total_amount_lost'] = game.filter(decision="LOST").aggregate(Sum('amount'))['amount__sum']
    context['amount_funded'] = \
        Bank.objects.filter(user=request_user, bank="PAYSTACK", status="Successful").aggregate(Sum('amount'))[
            'amount__sum']
    context['useracc_obj'] = useracc_obj.pk

    return render(request, 'ynladmin/traderDetails.html', context)


@login_required
def payment_filter(request, status):
    context = {}
    user_acc_obj = UserAccount.objects.get(user=request.user)
    context['user_acc_obj'] = user_acc_obj
    if status == "successful":
        template_name = 'ynladmin/payment.html'
        payments = paginate_list(request, Bank.objects.filter(status="Successful"), 12)
        context['payments'] = payments
    elif status == "declined":
        template_name = 'ynladmin/payment.html'
        payments = paginate_list(request, Bank.objects.filter(status="Declined"), 12)
        context['payments'] = payments
    else:
        template_name = 'ynladmin/payment.html'
        payments = paginate_list(request, Bank.objects.filter(status="Transfer"), 12)
        context['payments'] = payments
    return render(request, template_name, context)


@login_required
def admin_messages(request):
    context = {}
    if request.method == 'POST':
        rp = request.POST
        # print "rp here: ", rp
        message_obj = MessageCenter.objects.get(
            id=rp.get('msg_id')
        )
        comment_obj = MessageCenterComment.objects.create(
            message=rp.get('message'),
            message_obj=message_obj,
            image_obj=request.FILES.get('image_obj'),
            user=request.user)
        message_obj.replied = True
        message_obj.new = False
        message_obj.save()
        messages.success(request, 'Message sent successfully')
        return redirect(request.META['HTTP_REFERER'])
    else:
        # print request.GET
        template_name = ""
        if request.GET.get('identifier') == 'comment':
            template_name = 'ynladmin/adminmessageComments.html'
        else:
            template_name = 'ynladmin/adminviewMessages.html'
        message_id = request.GET.get('message_id')
        message_obj = MessageCenter.objects.get(id=message_id)
        # print "msg_obj:", message_obj
        all_comments = message_obj.getComments()
        comment_form = MessageCenterCommentForm()
        context['comment_form'] = comment_form
        context['all_comments'] = all_comments
        context['message_id'] = message_id
        return render(request, template_name, context)


@login_required
def delete_message(request, pk):
    get_msg = MessageCenter.objects.get(pk=pk)
    get_msg.archive = False
    get_msg.new = False
    get_msg.deleted = True
    get_msg.replied = False
    get_msg.save()
    return redirect(request.META['HTTP_REFERER'])


@login_required
def archive_message(request, pk):
    get_msg = MessageCenter.objects.get(pk=pk)
    get_msg.archive = True
    get_msg.new = False
    get_msg.deleted = False
    get_msg.replied = False
    get_msg.save()
    return redirect(request.META['HTTP_REFERER'])


def percentage(percent, whole):
    print 'am here'
    answer = math.floor((percent * whole) / 100.0)
    print answer
    return answer


@login_required
def close_event(request, event_id):
    event = Event.objects.get(id=event_id)

    if event.closed == True:
        return redirect(request.META['HTTP_REFERER'])

    cost_amt = CostSetting.objects.get(id=1)
    stakeholders_percentage = cost_amt.amount * 0.01
    # gameplay = Gameplay.objects.filter(event=event)
    total_value = event.gameplay_total_value()

    if total_value == None:
        total_value = 0
    print "Total", total_value
    win_amt = event.event_winnings()

    if win_amt == None:
        win_amt = 0
    lose_amt = total_value - win_amt
    print "losers", lose_amt
    print "winners", win_amt
    half_value = total_value * 0.5
    print "half_value", half_value

    if win_amt >= half_value and lose_amt != 0:
        print "winnings greater than 50% of total amount"
        stakeholders_amt = lose_amt * stakeholders_percentage
        left_over = lose_amt - stakeholders_amt
        # print "left_amt", left_over
        gameplay = Gameplay.objects.filter(event=event, choice=event.event_decision)
        # print "gameplay", gameplay
        for game in gameplay:
            percentage_won = math.floor((100 * game.amount) / win_amt)
            # print "%",percentage_won
            amount_won = percentage(percentage_won, left_over) + game.amount
            exact_amount_won = float(percentage(percentage_won, left_over))
            # print "amt_won", amount_won
            game.decision = "WIN"
            game.amount_won = amount_won
            game.status = "CLOSED"
            game.save()
            bank_record = Bank.objects.create(user=game.user.user, txn_type="Add", amount=amount_won,
                                                              ref_no=purchase_ref(),
                                                              created_at=timezone.now(),
                                                              message="Amount won for Event" + " " + event.event_id,
                                                              bank="YNL", status="Successful")


            balance = account_standing(request,game.user.user)
            WalletBalances.objects.create(balance_bf=balance, description="Category games", current_bal=float(balance + amount_won),amount=amount_won,user=game.user)
            game.user.wallet_balance = float(balance + amount_won)
            game.user.save()
            # if created:
            #     bank_record.date_created = timezone.now().date()
            title = "Prediction Results"
            text = "general/game_results.html"
            mail_user(request, game.user.user, title, text, pkg=game)
        event.closed = True
        event.save()
        lost_game = Gameplay.objects.filter(event=event, status="OPEN")
        for game in lost_game:
            game.status = "CLOSED"
            game.decision = "LOST"
            game.save()
            title = "Prediction Results"
            text = "general/game_lost.html"
            mail_user(request, game.user.user, title, text, pkg=game)
        messages.success(request, "This Event has been Successfully CLOSED!!!")
    elif win_amt == total_value:

        gameplay = Gameplay.objects.filter(event=event, choice=event.event_decision)
        # print "gameplay", gameplay
        for game in gameplay:
            game.decision = "WIN"
            game.amount_won = game.amount
            game.status = "CLOSED"
            game.save()
            bank_record = Bank.objects.create(user=game.user.user, txn_type="Add",
                                                              amount=game.amount_won, ref_no=purchase_ref(),
                                                              created_at=timezone.now(),
                                                              message="Amount won for Event" + " " + event.event_id,
                                                              bank="YNL", status="Successful")

            balance = account_standing(request,game.user.user)
            WalletBalances.objects.create(balance_bf=balance, description="Category games", current_bal=float(balance + game.amount),amount=game.amount,user=game.user)
            game.user.wallet_balance = float(balance + game.amount)
            game.user.save()
            # if created:
            #     bank_record.date_created = timezone.now().date()
            title = "Prediction Results"
            text = "general/game_results.html"
            mail_user(request, game.user.user, title, text, pkg=game)
        event.closed = True
        event.save()
    elif win_amt < half_value and win_amt != 0:
        print "winnings lesser than 50% of total amount"
        left_over = half_value - win_amt
        print "left_amt", left_over
        gameplay = Gameplay.objects.filter(event=event, choice=event.event_decision)
        print "gameplay", gameplay
        for game in gameplay:
            percentage_won = math.floor((100 * game.amount) / win_amt)
            # print "%",percentage_won
            # print game.amount
            amount_won = percentage(percentage_won, left_over) + game.amount
            exact_amount_won = float(percentage(percentage_won, left_over))
            # print "amt_won", amount_won
            game.decision = "WIN"
            game.amount_won = amount_won
            game.status = "CLOSED"
            game.save()
            bank_record = Bank.objects.create(user=game.user.user, txn_type="Add", amount=amount_won,
                                                              ref_no=purchase_ref(),
                                                              created_at=timezone.now(),
                                                              message="Amount won for Event" + " " + event.event_id,
                                                              bank="YNL", status="Successful")

            balance = account_standing(request,game.user.user)
            WalletBalances.objects.create(balance_bf=balance, description="Category games", current_bal=float(balance + amount_won),amount=amount_won,user=game.user)
            game.user.wallet_balance = float(balance + amount_won)
            game.user.save()

            # if created:
            #     bank_record.date_created = timezone.now().date()
            title = "Prediction Results"
            text = "general/game_results.html"
            mail_user(request, game.user.user, title, text, pkg=game)
        event.closed = True
        event.save()
        lost_game = Gameplay.objects.filter(event=event, status="OPEN")
        for game in lost_game:
            game.status = "CLOSED"
            game.decision = "LOST"
            game.save()
            title = "Prediction Results"
            text = "general/game_lost.html"
            mail_user(request, game.user.user, title, text, pkg=game)
        messages.success(request, "This Event has been Successfully CLOSED!!!")
    elif win_amt == 0:
        print "Nobody won!!!"
        event.closed = True
        event.save()
        lost_game = Gameplay.objects.filter(event=event, status="OPEN")
        for game in lost_game:
            game.status = "CLOSED"
            game.decision = "LOST"
            game.save()
            title = "Prediction Results"
            text = "general/game_lost.html"
            mail_user(request, game.user.user, title, text, pkg=game)
        messages.success(request, "This Event has been Successfully CLOSED!!!")
    else:
         print "I rep o"
    now = datetime.datetime.now()  # To get current date and time
    current_time = now.strftime("%I:%M %p")
    updateModelValues(event)
    activity_history(user=request.user, obj_id=event.pk, obj_model_name="Event", action="Closed",
                     message='Event ' + event.event_id + ' was closed by ' + request.user.username + ' at ' + current_time)

    return redirect(request.META['HTTP_REFERER'])


@login_required
def delete_approve_comment(request, action, pk):
    comment_obj = Comments.objects.get(pk=pk)
    if action == "delete":
        comment_obj.deleted = True
    else:
        print "approved"
        comment_obj.approved = True
    comment_obj.save()
    return redirect(request.META['HTTP_REFERER'])


@login_required
def validate_event(request):
    # print request.POST
    context = {}
    val_opt = request.POST.get('reason_value')
    event_obj = Event.objects.get(event_id=request.POST.get('event_num'))
    if val_opt == 'yes':
        event_obj.validated = True
        event_obj.save()
        action = "Validated"
    else:
        event_obj.validated = False
        event_obj.not_validated_reason = request.POST.get("not_validated_reason")
        event_obj.save()
        action = "Not Validated"

    activity_history(user=request.user, obj_id=event_obj.pk, obj_model_name="Event", action=action,
                     message='Event ' + event_obj.event_id + ' ' + action + ' ' + request.user.username)

    return redirect(request.META['HTTP_REFERER'])


@login_required
def ban_event(request, pk):
    event = Event.objects.get(pk=pk)
    event.closed = True
    event.save()
    gameplay = Gameplay.objects.filter(event=event)

    # print gameplay
    for play in gameplay:
        play.amount_won = 0
        play.status = "CANCELLED"
        play.decision = "CANCELLED"
        play.save()
        bank = Bank.objects.create(user=play.user.user, txn_type="Refund", amount=play.amount, ref_no=purchase_ref(),
                                   created_at=timezone.now(),
                                   message="Refund for Cancellation of Event" + " " + event.event_id, bank="YNL",
                                   status="Successful")
        bank.date_created = timezone.now().date()
        bank.save()

        balance = account_standing(request, play.user.user)

        WalletBalances.objects.create(balance_bf=balance, description="Refund", current_bal=float(balance + play.amount),amount=amount,user=play.user)
        play.user.wallet_balance = float(balance + amount)
        play.user.save()

    messages.success(request, 'This Event has been Stopped!!!')
    activity_history(user=request.user, obj_id=event.pk, obj_model_name="Event", action='Shut down',
                     message='Event ' + event.event_id + ' was shut down by ' + request.user.username)

    return redirect(request.META['HTTP_REFERER'])


@login_required
def get_event_players(request):
    context = {}
    event_id = request.GET.get('event_id')
    event = Event.objects.get(event_id=event_id)
    gameplay = Gameplay.objects.filter(event=event)
    context['gameplay'] = gameplay
    context['event'] = event
    activity_history(user=request.user, obj_id=event.pk, obj_model_name="Gameplay", action='view',
                     message='Gameplay details for Event ' + str(event_id) + ' was viewed by ' + str(
                         request.user.username))

    return render(request, 'ynladmin/event_players.html', context)


@login_required
def cummulative_winnings(request):
    context = {}
    rg = request.GET
    get_event = Event.objects.get(pk=rg.get('event_id'))
    context['get_event'] = get_event
    template_name = 'ynladmin/cummulative_winnings.html'
    return render(request, template_name, context)


@login_required
def wjp_amount(request):
    from datetime import datetime
    context = {}
    if request.method == "GET":
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        # print start_date,end_date
        start_date = datetime.strptime(from_date, "%m/%d/%Y")
        end_date = datetime.strptime(to_date, "%m/%d/%Y")
        weekly_events = Event.objects.filter(closed=True, end_date__range=(start_date, end_date))
        # print "weeklyevents", weekly_events
        total_amount = 0
        for events in weekly_events:
            # print events.event_profit()
            total_amount += events.jackpot_amount()
        # print events.jackpot_amount()
        # print total_amount, "tamt"
        context['total_amount'] = total_amount
        return render(request, 'ynlsnippet/wjp_total.html', context)


@login_required
def start_wjp(request):# from django.db.models import Count
    if request.method == "POST":
        form = WeeklyJackpotForm(request.POST)
        if form.is_valid():
            wjp_form = form.save(commit=False)
            wjp_form.opened_by = str(request.user)
            wjp_form.save()
            # users = UserAccount.objects.filter(gameplay__date__range=(wjp_form.start_date, wjp_form.end_date)).distinct()
            weekly_games = Gameplay.objects.filter(~Q(decision="CANCELLED"),
                                                   date__range=(wjp_form.start_date, wjp_form.end_date))

            counter = {}
            for game in weekly_games:
                if game.nvp == True:
                    if not counter.has_key(game.vendorClientCode):
                        counter[game.vendorClientCode] = {
                            'user': game.vendorClientCode,
                            'count': 0,
                            'points': 0
                        }
                    counter[game.vendorClientCode]['count'] += 1
                    counter[game.vendorClientCode]['points'] += 5
                    # points += game.game_points
                    if counter[game.vendorClientCode]['points'] == 20:
                        code_number = VendorClient.objects.get(client_code=game.vendorClientCode)
                        entry = Entries.objects.create(weeklyjackpot=wjp_form, unique_ref_no=str(code_number),
                                                       client_code=code_number)
                        entry.save()
                        counter[game.vendorClientCode]['points'] = 0
                else:
                    if not counter.has_key(game.user.id):
                        counter[game.user.id] = {
                            'user': game.user,
                            'count': 0,
                            'points': 0
                        }
                    counter[game.user.id]['count'] += 1
                    counter[game.user.id]['points'] += 5
                    # points += game.game_points
                    if counter[game.user.id]['points'] == 20:
                        entry = Entries.objects.create(weeklyjackpot=wjp_form, useracc_obj=game.user,
                                                       unique_ref_no=str(game.user.user.username))
                        entry.save()
                        counter[game.user.id]['points'] = 0

            messages.success(request, 'A Jackpot for the week has been successfully initiated!!!')
            return redirect(reverse('ynladmin:admin_pages', args=['wjp']))


@login_required
def close_wjp(request, pk):
    wjp = WeeklyJackPot.objects.get(id=pk)
    all_entries = wjp.get_all_entries()
    # print "entries", all_entries
    top_winner = wjp.top_winner
    consolation_winners = wjp.consolation_winners
    total_selection = top_winner + consolation_winners

    winning_list = []
    while len(winning_list) + 1 <= total_selection:
        new_entry = random.choice(all_entries)
        # print new_entry
        chosen_value = {'user': new_entry.useracc_obj, 'unique_ref_no': new_entry.unique_ref_no, 'pk': new_entry.pk}
        while chosen_value['unique_ref_no'] in [d['unique_ref_no'] for d in winning_list]:
            new_entry = random.choice(all_entries)
            chosen_value = {'user': new_entry.useracc_obj, 'unique_ref_no': new_entry.unique_ref_no, 'pk': new_entry.pk}
        winning_list.append(chosen_value)

    # print "winning_list", winning_list

    grand_prize_winners_list = []
    while len(grand_prize_winners_list) + 1 <= top_winner:
        winner = random.choice(winning_list)
        grand_prize_winners_list.append(winner)
        winning_list.remove(winner)

    # print "winners", grand_prize_winners_list
    # print "consolation prize winners",winning_list
    winners_amount = wjp.grand_prize
    for winner_entry in grand_prize_winners_list:
        winner_entry = Entries.objects.get(pk=winner_entry['pk'])
        winner_entry.winner = True
        winner_entry.won = True
        winner_entry.amount = winners_amount
        winner_entry.save()
        bank_record = Bank.objects.create(user=winner_entry.useracc_obj.user, txn_type="Add", amount=winners_amount,
                                          ref_no=purchase_ref(),
                                          created_at=timezone.now(), status="Successful", bank="Weekly JackPot",
                                          message="Winner of Weekly JackPot")
        UserAcc = UserAccount.objects.get(user=winner_entry.useracc_obj.user)
        UserAcc.total_wjp_won += 1
        UserAcc.total_grand_prize_wjp_won += 1
        UserAcc.save()
        UserAcc.game_played = True
        bank_record.date_created = timezone.now().date()

        balance = account_standing(request, winner_entry.useracc_obj.user)

        WalletBalances.objects.create(balance_bf=balance, description="Weekly Jackpot", current_bal=(float(balance) + float(winners_amount)),amount=winners_amount,user=winner_entry.useracc_obj)
        winner_entry.useracc_obj.wallet_balance = (float(balance) + float(winners_amount))
        winner_entry.useracc_obj.save()

    bank_record.save()

    consolation_amt = wjp.consolation_prize
    for winners in winning_list:
        consolations = Entries.objects.get(pk=winners['pk'])
        consolations.consolation = True
        consolations.won = True
        consolations.amount = consolation_amt
        consolations.save()
        bank_record = Bank.objects.create(user=consolations.useracc_obj.user, txn_type="Add", amount=consolation_amt,
                                          ref_no=purchase_ref(),
                                          created_at=timezone.now(), status="Successful", bank="Weekly JackPot",
                                          message="Consolation Prize of Weekly JackPot")
        bank_record.date_created = timezone.now().date()
        UserAcc.total_wjp_won += 1
        UserAcc.game_played = True
        UserAcc.total_consolation_prize_wjp_won += 1
        UserAcc.save()

        balance = account_standing(request, consolations.useracc_obj.user)

        WalletBalances.objects.create(balance_bf=balance, description="Weekly Jackpot",current_bal=(float(balance) + float(consolation_amt)),amount=consolation_amt,user=consolations.useracc_obj)
        consolations.useracc_obj.wallet_balance = (float(balance) + float(consolation_amt))
        consolations.useracc_obj.save()

    bank_record.save()

    wjp.closed_by = str(request.user)
    wjp.closed = True
    wjp.status = "Closed"
    wjp.save()
    messages.success(request, 'Jackpot for the week has been successfully Closed!!!')
    return redirect(reverse('ynladmin:admin_pages', args=['wjp']))


# def close_wjp(request,pk):
# 	wjp = WeeklyJackPot.objects.get(id=pk)
# 	all_entries = wjp.get_all_entries()
# 	print all_entries
# 	top_winner = wjp.top_winner
# 	consolation_winners = wjp.consolation_winners
# 	total_selection = top_winner + consolation_winners
# 	print total_selection
# 	winners_selection = random.sample(all_entries, total_selection)
# 	for i in winners_selection:
# 		print i.useracc_obj
# 	duplicate = {}
# 	winning_list =[]
# 	for entry in winners_selection:
# 		if entry.useracc_obj != None:
# 			print entry.useracc_obj
# 			if not duplicate.has_key(entry.useracc_obj.id):
# 				duplicate[entry.useracc_obj.id]={
# 					'user': entry.useracc_obj,
# 					'frequency':0,
# 				}
# 				print "duplicate1", duplicate
# 			duplicate[entry.useracc_obj.id]['frequency']+=1
# 			if duplicate[entry.useracc_obj.id]['frequency'] == 1:
# 				winning_list.append(entry)
# 				print "winning_list1", winning_list
# 			else:
# 				new_entry = random.choice(all_entries.filter(client_code=None))
# 				print "new_entry", new_entry.useracc_obj
# 				print new_entry in winning_list
# 				while new_entry in winning_list:
# 					new_entry = random.choice(all_entries.filter(client_code=None))
# 					print "newentry", new_entry	.useracc_obj
# 				winning_list.append(new_entry)
# 				duplicate[new_entry.useracc_obj.id]={
# 					'user': new_entry.useracc_obj,
# 					'frequency':1,
# 					}
# 				print 'duplicate', duplicate
# 				print "winning_list",winning_list
# 		else:
# 			if not duplicate.has_key(entry.client_code.id):
# 				duplicate[entry.client_code.id]={
# 					'user': entry.client_code,
# 					'frequency':0,
# 				}
# 			duplicate[entry.client_code.id]['frequency']+=1
# 			if duplicate[entry.client_code.id]['frequency'] == 1:
# 				winning_list.append(entry)
# 			else:
# 				new_entry = random.choice(all_entries.filter(useracc_obj=None))
# 				print "new_entry", new_entry
# 				while new_entry in winning_list:
# 					new_entry = random.choice(all_entries.filter(useracc_obj=None))
# 					print "newentry", new_entry
# 				winning_list.append(new_entry)
# 				duplicate[new_entry.client_code.id]={
# 					'user': new_entry.client_code,
# 					'frequency':1,
# 					}
# 				print 'duplicate', duplicate
# 	print "winning_list", winning_list
# 	winner = random.choice(winning_list)
# 	print "winner", winners
# 	winning_list.remove(winner)
# 	print "consolation",winning_list
# 	winner_entry = Entries.objects.get(id=winner.id)
# 	winner_entry.winner = True
# 	winner_entry.save()
# 	for winners in winning_list:
# 		consolations = Entries.objects.get(id=winners.id)
# 		consolations.consolation = True
# 		consolations.save()
# 	wjp.closed_by = str(request.user)	
# 	wjp.closed = True
# 	wjp.save()	
# 	messages.success(request, 'Jackpot for the week has been successfully Closed!!!')		
# 	return redirect(reverse('ynladmin:admin_pages', args=['wjp']))


@login_required
def create_djp(request):
    if request.method == "POST":
        form = DailyJackPotForm(request.POST)
        today = timezone.now().date()
        if form.is_valid():
            djp_form = form.save(commit=False)
            djp_form.status = "OPEN"
            djp_form.created_on_date = today
            djp_form.end_time = datetime.datetime.today().replace(hour=19, minute=00)
            djp_form.stop_time = datetime.datetime.today().replace(hour=19, minute=00)
            djp_form.save()
            messages.success(request, 'Daily Jackpot has been successfully Created!!!')
            return redirect(reverse('ynladmin:admin_pages', args=['djp']))


@login_required
def edit_djp(request):
    if request.method == "GET":
        djp_id = request.GET.get('djp_id')
        djp = DailyJackPot.objects.get(pk=djp_id)
        djp_form = DailyJackPotEditForm(instance=djp)
        return render(request, 'ynlsnippet/djp_edit.html', {'form': djp_form, 'djp': djp})
    else:
        djp = DailyJackPot.objects.get(pk=request.POST.get('djp_id'))
        form = DailyJackPotEditForm(request.POST, instance=djp)
        if form.is_valid():
            form.save()
        return redirect(reverse('ynladmin:admin_pages', args=['djp']))


@login_required
def view_djp(request):
    if request.method == "GET":
        if not "vendorPlayDjp" in request.GET:
            djp_id = request.GET.get('djp_id')
            djp = DailyJackPot.objects.get(pk=djp_id)
            djp_winners = djp.get_winners().values('user_obj__user__first_name', 'user_obj__user__last_name','user_obj__user__email','user_obj__phone_number', 'ticket_no','amount', 'true_value','user_last_name','user_first_name','user_email','telephone_no')
            # print djp_winners
            return render(request, 'ynlsnippet/djp_view.html', {'djp_winners': djp_winners})
        else:
            djp_id = request.GET.get('djp_id')
            djp = DailyJackPot.objects.get(pk=djp_id)
            djp_winners = djp.get_winners().filter(user_obj=request.user.useraccount).values('unique_ref_no', 'ticket_no','amount','date', 'won','choice', 'true_value','user_last_name','user_first_name','user_email','telephone_no')
            # print djp_winners
            return render(request, 'ynlsnippet/vendor_djp_view.html', {'djp_winners': djp_winners})
        

# @login_required

''' 
    when the daily jackpot has ended this method serves to
    end the daily jackpot and select winners for the day
'''

def close_djp(request, pk):
    djp = DailyJackPot.objects.get(id=pk)
    # print 'djp',djp
    winning_list = []

    all_entries = djp.get_qualified_entries(djp.decision)
    # for entry in all_entries:
    #     print entry.choice
    top_winner = djp.top_winner
    consolation_winners = djp.consolation_winners
    total_selection = top_winner + consolation_winners
    
    usernames_list = []

    '''
        get unique users lists
    '''
    for entry in all_entries:
        try:
            usernames_list.append(entry.user_obj.user.username)
        except:
            usernames_list.append(entry.vendor_code.useraccount.user.username)

    unique_list = set(usernames_list)

    '''
        end here
    '''

    # print "unique_list", unique_list
    # if len(unique_list) < total_selection:
    # 	total_selection = len(unique_list)
    # else:
    # 	total_selection = total_selection
    # winning_list = []

    '''
        check if all players were selected to win daily jackpot for the day
    '''

    if not djp.all_players:
        previous_winners = DailyJackpotEntries.objects.filter(won=True)
        # print "previous",previous_winners
        for pw in previous_winners:
            try:
                user = pw.user_obj.user.username
            except:
                try:
                    user = pw.vendor_code.useraccount.user.username
                except:
                    user = None
            if user in unique_list:
                unique_list.remove(user)
    '''
        end here
    '''

    # print unique_list

    if len(unique_list) < total_selection:
        total_selection = len(unique_list)
    # print total_selection
    else:
        total_selection = total_selection
    winning_list = random.sample(unique_list, total_selection)
    # print winning_list
    grand_prize_winners_list = []
    winner = random.choice(winning_list)
    grand_prize_winners_list.append(winner)
    winning_list.remove(winner)

    # while len(winning_list) + 1 <= total_selection:
    # 	new_entry = random.choice(all_entries)
    # 	chosen_value = {'user':new_entry.user_obj, 'ticket_no':new_entry.ticket_no,'pk':new_entry.pk}
    # 	while chosen_value['user'] in [d['user'] for d in winning_list]:
    # 		new_entry = random.choice(all_entries)
    # 		chosen_value = {'user':new_entry.user_obj, 'ticket_no':new_entry.ticket_no, 'pk':new_entry.pk}
    # 	winning_list.append(chosen_value)

    # grand_prize_winners_list = []
    # while len(grand_prize_winners_list) + 1 <= top_winner:
    # 	winner = random.choice(winning_list)
    # 	grand_prize_winners_list.append(winner)
    # 	winning_list.remove(winner)

    winners_amount = djp.grand_prize

    for winner_entry in grand_prize_winners_list:
        # print winner_entry, type(str(winner_entry))
        winner_entrys = DailyJackpotEntries.objects.filter(user_obj__user__username=str(winner_entry), dailyjackpot=djp)
        winner_entry = random.choice(winner_entrys)
        winner_entry.winner = True
        winner_entry.won = True
        winner_entry.amount = winners_amount
        winner_entry.save()

        userAcc = winner_entry.user_obj
        userAcc.total_djp_won += 1
        userAcc.game_played = True
        userAcc.total_djp_grand_prize_won += 1
        userAcc.save()

        bank_record = Bank.objects.create(user=winner_entry.user_obj.user, txn_type="Add", amount=winners_amount,
                                          ref_no=purchase_ref(),
                                          created_at=timezone.now(), status="Successful", bank="Daily JackPot",
                                          message="Winner of Daily JackPot")

        bank_record.date_created = timezone.now().date()

        balance = account_standing(request, winner_entry.user_obj.user)

        WalletBalances.objects.create(balance_bf=balance, description="Daily Jackpot", current_bal=(float(balance) + float(winners_amount)),amount=winners_amount,user=winner_entry.user_obj)
        winner_entry.user_obj.wallet_balance = (float(balance) + float(winners_amount))
        winner_entry.user_obj.save()

    bank_record.save()

    consolation_amt = djp.consolation_prize

    for winners in winning_list:
        consolation = DailyJackpotEntries.objects.filter(user_obj__user__username=str(winners), dailyjackpot=djp)
        consolations = random.choice(consolation)
        consolations.consolation = True
        consolations.won = True
        consolations.amount = consolation_amt
        consolations.save()

        userAcc = UserAccount.objects.get(user__username = str(winners))
        userAcc.total_djp_won += 1
        userAcc.total_djp_consolation_prize_won += 1
        userAcc.game_played = True
        userAcc.save()

        bank_record = Bank.objects.create(user=consolations.user_obj.user, txn_type="Add", amount=consolation_amt,
                                          ref_no=purchase_ref(),
                                          created_at=timezone.now(), status="Successful", bank="Daily JackPot",
                                          message="Consolation Prize Winner of Daily JackPot")
        bank_record.date_created = timezone.now().date()

        balance = account_standing(request, consolations.user_obj.user)

        WalletBalances.objects.create(balance_bf=balance, description="Daily Jackpot", current_bal=(float(balance) + float(consolation_amt)),amount=consolation_amt,user=consolations.user_obj)
        consolations.user_obj.wallet_balance = (float(balance) + float(consolation_amt))
        consolations.user_obj.save()

    bank_record.save()

    djp.closed_by = str(request.user)
    djp.closed = True
    djp.status = "CLOSED"
    djp.save()

    messages.success(request, 'DailyJackPot for the DAY has been successfully Closed!!!')
    return redirect(reverse('ynladmin:admin_pages', args=['djp']))


@login_required
def dailyreports(request):
    from datetime import datetime
    context = {}
    rg = request.GET
    # print 'rg',rg
   
    begin_date = datetime.strptime('10/01/2017', "%m/%d/%Y").date()
    start_date = datetime.strptime(rg.get('to-date-daily'), "%m/%d/%Y").date()
    end_date = datetime.strptime(rg.get('from-date-daily'), "%m/%d/%Y").date()
    total_users = []

    for dt in daterange(end_date, start_date):
        user_obj = User.objects.filter(is_staff=False, date_joined__range=[begin_date, dt])
        gameplay_obj = Gameplay.objects.filter(date_played=dt)
        total_users.append({
            'dt': dt,
            'count': user_obj.count(),
            'not_active': user_obj.filter(useraccount__isnull=True).count(),
            'profile_not_updated': user_obj.filter(useraccount__profile_updated=False).count(),
            'profile_updated': user_obj.filter(useraccount__profile_updated=True).count(),
            'wallet_not_funded': user_obj.filter(useraccount__profile_updated=True, useraccount__wallet_funded=False).distinct().count(),
            'wallet_funded': user_obj.filter(useraccount__profile_updated=True, useraccount__wallet_funded=True).distinct().count(),
            'no_gameplay': user_obj.filter(useraccount__profile_updated=True, useraccount__wallet_funded=True, useraccount__game_played=False).distinct().count(),
            'gameplay': user_obj.filter(useraccount__profile_updated=True, useraccount__wallet_funded=True,useraccount__game_played=True).distinct().count(),
            'cat_games_played': gameplay_obj.count(),
            'new_users_cat_games_played': gameplay_obj.filter(user__user__date_joined=dt).count(),
            'old_users_cat_games_played': gameplay_obj.filter(~Q(user__user__date_joined=dt)).count(),
            'djp': DailyJackPot.objects.get(created_on_date=dt).entries_count(),
            'unique_djp_players': user_obj.filter(useraccount__useracc_obj__date=dt).distinct().count(),
            'new_djp_players': user_obj.filter(Q(date_joined=dt), useraccount__useracc_obj__date=dt).distinct().count(),
            'old_djp_players': user_obj.filter(~Q(date_joined=dt), useraccount__useracc_obj__date=dt).distinct().count()
        })
    context['total_users'] = total_users
    template_name = 'ynladmin/dailyreports.html'
    return render(request, template_name, context)


@login_required
def daily_cat_games_count(request):
    from datetime import datetime
    context = {}
    try:
        date = datetime.strptime(request.GET.get('date'), "%b. %d, %Y").date()
    except:
        date = datetime.strptime(request.GET.get('date'), "%B %d, %Y").date()

    if 'all_cat_games' in request.GET:
        context['title'] = 'Games played by all users per category'
        gameplays = Gameplay.objects.filter(date_played=date)
        context['total'] = gameplays.count()
        context['amount'] = gameplays.count() * 200
        context['date'] = date
        context['politics'] = gameplays.filter(event__category="Politics").count()
        context['sports'] = gameplays.filter(event__category="Sports").count()
        context['ent'] = gameplays.filter(event__category="Entertainment-LifeStyle").count()
        context['general'] = gameplays.filter(event__category="General").count()
        context['business'] = gameplays.filter(event__category="Business-Economy").count()
        context['realityTV'] = gameplays.filter(event__category="realityTV").count()

    elif 'new_users_cat_games' in request.GET:
        context['title'] = 'Games played by new users per category'
        gameplays = Gameplay.objects.filter(user__user__date_joined=date, date_played=date)
        context['total'] = gameplays.count()
        context['amount'] = gameplays.count() * 200
        context['date'] = date
        context['politics'] = gameplays.filter(event__category="Politics").count()
        context['sports'] = gameplays.filter(event__category="Sports").count()
        context['ent'] = gameplays.filter(event__category="Entertainment-LifeStyle").count()
        context['general'] = gameplays.filter(event__category="General").count()
        context['business'] = gameplays.filter(event__category="Business-Economy").count()
        context['realityTV'] = gameplays.filter(event__category="realityTV").count()

    else:
        context['title'] = 'Games played by returning users per category'
        gameplays = Gameplay.objects.filter(~Q(user__user__date_joined=date), date_played=date)
        context['total'] = gameplays.count()
        context['amount'] = gameplays.count() * 200
        context['date'] = date
        context['politics'] = gameplays.filter(event__category="Politics").count()
        context['sports'] = gameplays.filter(event__category="Sports").count()
        context['ent'] = gameplays.filter(event__category="Entertainment-LifeStyle").count()
        context['general'] = gameplays.filter(event__category="General").count()
        context['business'] = gameplays.filter(event__category="Business-Economy").count()
        context['realityTV'] = gameplays.filter(event__category="realityTV").count()

    unique_gameplays_list = []
    for game in gameplays:
        if game.user in unique_gameplays_list:
            pass
        else:
            unique_gameplays_list.append(game.user)  # append to list
    template_name = 'ynladmin/categoriesDaily.html'
    context['gameplays'] = unique_gameplays_list

    return render(request, template_name, context)


@login_required
def users_count(request):
    from datetime import datetime
    context = {}
    
    try:
        date = datetime.strptime(request.GET.get('date'), "%b. %d, %Y").date()
    except:
        date = datetime.strptime(request.GET.get('date'), "%B %d, %Y").date()

    context['date'] = request.GET.get('date')

    if 'unique_users' in request.GET:
        context['title'] = 'Daily Jackpot Players'
        context['user_obj'] = User.objects.filter(useraccount__useracc_obj__date=date).distinct()
        template_name = 'ynladmin/userscount.html'

    elif 'new_users' in request.GET:
        context['title'] = 'New Daily Jackpot Players'
        context['user_obj'] = User.objects.filter(date_joined=date, useraccount__useracc_obj__date=date).distinct()
        template_name = 'ynladmin/usersaccountdjpnew.html'

    else:
        context['title'] = 'Returning Daily Jackpot Players'
        context['user_obj'] = User.objects.filter(~Q(date_joined=date), useraccount__useracc_obj__date=date).distinct()
        template_name = 'ynladmin/usersaccountdjpold.html'

    return render(request, template_name, context)


@login_required
def genericSearch(request):
    from datetime import datetime
    context = {}
    rg = request.GET
    start_date = datetime.strptime(rg.get('from-date-daily'), "%m/%d/%Y").date()
    end_date = datetime.strptime(rg.get('to-date-daily'), "%m/%d/%Y").date()
    # print rg, start_date, end_date
    if rg.has_key('events'):
        context['news'] = 'news'
        context['all_events'] = Event.objects.filter(date_created__range=(start_date, end_date))
        template_name = 'ynladmin/events.html'
    elif rg.has_key('payments'):
        context['payments'] = Bank.objects.filter(date_created__range=(start_date, end_date))
        template_name = 'ynladmin/payment.html'
    elif rg.has_key('game_payments'):
        context['payments'] = Betpayments.objects.filter(date_created__range=(start_date, end_date))
        template_name = "ynladmin/game_payments.html"
    return render(request, template_name, context)


@login_required
def crte_djp_wner(request):
    context = {}
    template_name = "ynladmin/add_winner.html"
    if request.POST:
        today = timezone.now().date()
        djp = DailyJackPot.objects.get(created_on_date=today)
        consolation_amt = 5000.0

        print "rp", request.POST

        try:
            winning_list = request.POST.get('usernames').split(',')
        except:
            pass

        try:
            start = int(request.POST.get('start'))
            stop = int(request.POST.get('stop'))
        except:
            pass

        # for winner in winners:
        #     print "the winner", winner
        # return redirect(request.META['HTTP_REFERER'])
        try:   
            for winners in winning_list:
                try:
                    consolation = DailyJackpotEntries.objects.filter(user_obj__user__username=str(winners), dailyjackpot=djp, choice=djp.decision)
                    print consolation
                    if consolation:
                        messages.info(request, "sucessfully created")
                    else:
                        messages.info(request, "Wrong answers provided or no daily jackpot entry found for the day")
                        # return redirect(request.META['HTTP_REFERER'])
                except:
                    messages.info(request, "Usernames do not exist")
                    # return redirect(request.META['HTTP_REFERER'])
                consolations = random.choice(consolation)
                consolations.consolation = True
                consolations.won = True
                consolations.amount = consolation_amt
                consolations.save()

                userAcc = UserAccount.objects.get(user__username = str(winners))
                userAcc.total_djp_won += 1
                userAcc.total_djp_consolation_prize_won += 1
                userAcc.game_played = True
                userAcc.save()

                bank_record = Bank.objects.create(user=consolations.user_obj.user, txn_type="Add", amount=consolation_amt,
                                                  ref_no=purchase_ref(),
                                                  created_at=timezone.now(), status="Successful", bank="Daily JackPot",
                                                  message="Consolation Prize Winner of Daily JackPot")
                bank_record.date_created = timezone.now().date()

                balance = account_standing(request, consolations.user_obj.user)

                WalletBalances.objects.create(balance_bf=balance, description="Daily Jackpot", current_bal=(float(balance) + float(consolation_amt)),amount=consolation_amt,user=consolations.user_obj)
                consolations.user_obj.wallet_balance = (float(balance) + float(consolation_amt))
                consolations.user_obj.save()

            bank_record.save()
        except:
            pass

            # messages.info(request, "Successful")
            # return redirect(request.META['HTTP_REFERER'])

        try:
            with open('names.txt','r') as f:
                for line in f.readlines()[start:stop]:
                    new_line_value = line.split()
                    first_name = new_line_value[0].upper()
                    last_name = new_line_value[1].upper()
                    phone_number = new_line_value[-1]
                    email = new_line_value[0].lower() + new_line_value[1].lower() + "@gmail.com"
                    
                    DailyJackpotEntries.objects.create(dailyjackpot=djp,
                                                       true_value=True,  
                                                       choice=djp.decision,
                                                       ticket_no=purchase_ref(),
                                                       user_email=email,
                                                       user_first_name=first_name,
                                                       user_last_name=last_name,
                                                       telephone_no=phone_number,
                                                       consolation=True,
                                                       amount=consolation_amt,
                                                       won=True)
        except:
            pass


        return redirect(request.META['HTTP_REFERER'])
    return render(request,template_name,context)


