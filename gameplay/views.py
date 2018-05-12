# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from general.models import Event, UserAccount
from general.views import getAllOpenEvent
from django.shortcuts import render, redirect
from wallet.account_standing import account_standing
from django.utils import timezone
from wallet.models import Bank, Betpayments
from wallet.views import generate_purchaseRef, purchase_ref
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from gameplay.models import Gameplay, DailyJackPot, DailyJackpotEntries
from django.core.urlresolvers import reverse
from general.custom_functions import *
from general.models import VendorClient, WalletBalances
import random, datetime


# Create your views here.


def strip_phone_number(value):
    value = value.replace(" ","").replace("+","").replace("-","")
    if value[0] == "0":
        value = list(value)
        value[0] = "234"
        value = ''.join(value)
    return value


@login_required
def betting(request):
    balance = account_standing(request, request.user)
    try:
        useraccount = UserAccount.objects.get(user=request.user)
        if not useraccount.profile_updated:
            messages.warning(request, "Please update your profile before playing")
            return redirect(reverse('general:profile'))
    except Exception as e:
        print "e", e
        messages.warning(request, "Please update your profile before playing")
        return redirect(reverse('general:profile'))
    if request.method == "POST":
        if request.POST.get('bot_catcher') != "":
            return redirect(reverse('general:homepage'))
        # print request.POST
        try:
            amount = float(request.POST.get('amount'))
        except:
            messages.warning(request, "Invalid amount supplied")
            return redirect(request.META['HTTP_REFERER'])
        choice = str(request.POST.get('user-choice'))
        if amount == "" or amount < 200:
            messages.error(request, "Amount added is below minimum amount")
            return redirect(request.META['HTTP_REFERER'])
        if choice == "":
            messages.error(request, "You need to make a choice")
            return redirect(request.META['HTTP_REFERER'])
        if amount > balance:
            messages.error(request, "You do not have sufficient money in your wallet to play this game")
            return redirect(request.META['HTTP_REFERER'])
        else:
            # choice = str(request.POST.get('user-choice'))
            # print 'choice', choice
            event = Event.objects.get(id=request.POST.get('event'))
            if event.end_date <= timezone.now().date():
                if event.end_date == timezone.now().date():
                    today = datetime.datetime.now()  # To get current date and time
                    current_time = today.strftime("%I:%M %p")  # to get current time in string format
                    print "current_time", current_time
                    dt = datetime.datetime.strptime(current_time,"%I:%M %p").time()  # to convert datetime.datetime object to datetime.time object
                    # print "dt", dt
                    # endz_time = datetime.datetime.strptime(event.end_time, "%I:%M %p").time()
                    # print endz_time
                    if event.end_time <= dt:
                        messages.error(request, "This event is closed")
                        return redirect(request.META['HTTP_REFERER'])
                else:
                    mesaages.error(request, "This event is closed")
                    return redirect(request.META['HTTP_REFERER'])
            user = UserAccount.objects.get(user=request.user)
            try:
                gameplay = Gameplay.objects.get(event=event, user=user)
                # print gameplay
                messages.warning(request, "You have already Participated in this Event")
                return redirect(request.META['HTTP_REFERER'])
            except Exception as e:
                print "e", e
            random_ref = purchase_ref()
            gameplay = Gameplay.objects.create(user=user, event=event, amount=amount, choice=choice,
                                               date=timezone.now(), status="OPEN", ref_number=random_ref)
            # gameplay = Gameplay.objects.create(user=user,event=event,amount=amount,choice=choice,date=timezone.now(),status="OPEN")
            gameplay.current_ac_bal = balance
            gameplay.date_played = timezone.now().date()
            gameplay.save()
            event.total_amt += amount
            event.counter += 1
            event.save()
            user.djp_wjp_cat = True
            user.total_cat_games_played += 1
            user.wallet_funded = True
            user.game_played = True
            user.save()
            random_ref = purchase_ref()
            bank_record = Bank.objects.create(user=request.user, txn_type="Remove", amount=amount, ref_no=random_ref,
                                              created_at=timezone.now(), status="Successful", bank="Gameplay",
                                              message="Gameplay for event " + event.event_id)
            bank_record.date_created = timezone.now().date()
            bank_record.save()
            payment = Betpayments.objects.create(user=request.user, amount=amount, game=gameplay, date=timezone.now())
            payment.date_created = timezone.now().date()
            payment.save()
            title = "Prediction Confirmation"
            text = "general/game_confirmation.html"
            mail_user (request, user.user, title, text, pkg=gameplay)
            messages.success(request, 'Congratulations!!!! You have successfully made your prediction!!!.')

            WalletBalances.objects.create(balance_bf=balance,description="Category Games",current_bal=float(balance - amount),amount=amount,user=request.user.useraccount)
            user.wallet_balance = float(balance - amount)
            user.save()

            return redirect(request.META['HTTP_REFERER'])
    return redirect(reverse('general:homepage'))


def weeklyjackpot(request):
    context = {}
    balance = account_standing(request, request.user)
    context['balance'] = balance
    return render(request, 'general/weeklyjackpot.html', context)


def weeklyjackpot2(request):
    context = {}
    balance = account_standing(request, request.user)
    context['balance'] = balance
    return render(request, 'general/weeklyjackpot.html', context)


def dailyjackpot(request):
    # from datetime import datetime
    balance = account_standing(request, request.user)
    if request.method == "POST":
        if not request.user.is_authenticated():
            return redirect(reverse('general:login'))
        try:
            useraccount = UserAccount.objects.get(user=request.user)
            if not useraccount.profile_updated:
                messages.warning(request, "Please update your profile before Answering the Question")
                return redirect(reverse('general:profile'))
        except Exception as e:
            print "e", e
            messages.warning(request, "Please update your profile before you can play")
            return redirect(reverse('general:profile'))

        question = request.POST.get('event')
        choice = request.POST.get('user-choice')
        try:
            no_of_entry = int(request.POST.get('no_of_entries'))
        except:
            messages.error(request, "Amount added is invalid")
            return redirect(request.META['HTTP_REFERER'])
        # print no_of_entry
        entry_amt = float(request.POST.get('entry_amt')) * no_of_entry
        # print "amt", entry_amt
        # if request.method == "POST":
        if request.POST.get('bot_catcher') != "":
            return redirect(reverse('general:homepage'))
        # choice = str(request.POST.get('user-choice'))
        if entry_amt == "" or entry_amt < 25:
            messages.error(request, "Amount added is below minimum amount")
            return redirect(request.META['HTTP_REFERER'])
        if choice == "":
            messages.error(request, "You need to make a choice")
            return redirect(request.META['HTTP_REFERER'])
        if entry_amt > balance:
            messages.error(request, "You do not have sufficient money in your wallet to play the game")
            return redirect(request.META['HTTP_REFERER'])

        # ref = purchase_ref()
        event = DailyJackPot.objects.get(id=question)
        today = datetime.datetime.now()  # To get current date and time
        current_time = today.strftime("%I:%M %p")  # to get current time in string format
        print "current_time", current_time
        dt = datetime.datetime.strptime(current_time,"%I:%M %p").time()  # to convert datetime.datetime object to datetime.time object
        print "dt", dt
        if event.stop_time < dt:
            messages.error(request, "Daily Jackpot for today has ended")
            return redirect(request.META['HTTP_REFERER'])
        user = UserAccount.objects.get(user=request.user)
        counter = 0
        while (counter < no_of_entry):
            ref = purchase_ref()
            entry = DailyJackpotEntries.objects.create(dailyjackpot=event, user_obj=user, choice=choice,
                                                       ticket_no=ref)
            entry.date = timezone.now().date()
            entry.user_email = user.user.email
            entry.user_first_name = user.user.first_name
            entry.user_last_name = user.user.last_name
            entry.telephone_no = user.phone_number
            entry.save()
            user.djp_wjp_cat = True
            user.total_djp_played += 1
            user.wallet_funded = True
            user.game_played = True
            user.save()
            event.total_entries += 1
            event.save()
            bank_record = Bank.objects.create(user=request.user, txn_type="Remove", amount=event.entry_amount,
                                              ref_no=ref,
                                              created_at=timezone.now(), status="Successful", bank="DailyJackPot",
                                              message="DailyJackPot for the day")
            bank_record.date_created = timezone.now().date()
            bank_record.save()
            payment = Betpayments.objects.create(user=request.user, amount=event.entry_amount, djp=event, date=timezone.now())
            payment.date_created = timezone.now().date()
            payment.save()

            counter += 1
            # print "counter", counter

        WalletBalances.objects.create(balance_bf=balance, description="Daily Jackpot", current_bal=float(balance - (event.entry_amount * counter)), amount=float(event.entry_amount * counter), user=request.user.useraccount)
        user.wallet_balance = float(balance - entry_amt)
        user.save()

        messages.success(request, 'Your answer has been successfully submitted!!!.')
        
        return redirect(request.META['HTTP_REFERER'])

    else:
        context = {}
        now = timezone.now()
        today = timezone.now().date()
        events_all = getAllOpenEvent(request)
        categories = []
        for event in events_all:
            if event.category in categories:
                pass
            else:
                categories.append(event.category)
        context['categories'] = categories
        # balance = account_standing(request,request.user)

        context['balance'] = balance

        try:
            event = DailyJackPot.objects.get(created_on_date=today)
            print event
            todays_date = timezone.now().date()
            past_dates = timezone.now() - timezone.timedelta(days=7)
            yesterday = timezone.now() - timezone.timedelta(days=1)
            # print yesterday
            jackpots = DailyJackPot.objects.filter(created_on_date__range=[past_dates, todays_date])
            # print jackpots
            yesterdays_game = DailyJackPot.objects.get(created_on_date=yesterday)
            # print yesterdays_game
            context['event'] = event
            context['jackpots'] = jackpots
            context['yesterday_event'] = yesterdays_game
            print event.stop_time
            # print now
            djp = ""
            if event.end_time >= now:
                djp = True
            else:
                djp = False
            # print djp
            context['djp'] = djp
        except:
            event = []
            todays_date = timezone.now().date()
            past_dates = timezone.now() - timezone.timedelta(days=7)
            yesterday = timezone.now() - timezone.timedelta(days=1)
            # print yesterday
            jackpots = DailyJackPot.objects.filter(created_on_date__range=[past_dates, todays_date])
            # print jackpots
            yesterdays_game = DailyJackPot.objects.get(created_on_date=yesterday)
            # print yesterdays_game
            context['event'] = event
            context['jackpots'] = jackpots
            context['yesterday_event'] = yesterdays_game
            # print event.end_time
            # print now
            djp = ""
            context['djp'] = djp
    return render(request, 'general/dailyjackpot.html', context)


def dailyjackpot2(request):
    # from datetime import datetime
    balance = account_standing(request, request.user)
    if request.method == "POST":
        if not request.user.is_authenticated():
            return redirect(reverse('general:login'))
        try:
            useraccount = UserAccount.objects.get(user=request.user)
            if not useraccount.profile_updated:
                messages.warning(request, "Please update your profile before Answering the Question")
                return redirect(reverse('general:profile'))
        except Exception as e:
            print "e", e
            messages.warning(request, "Please update your profile before you can play")
            return redirect(reverse('general:profile'))

        question = request.POST.get('event')
        choice = request.POST.get('user-choice')
        try:
            no_of_entry = int(request.POST.get('no_of_entries'))
        except:
            messages.error(request, "Amount added is invalid")
            return redirect(request.META['HTTP_REFERER'])
        # print no_of_entry
        entry_amt = float(request.POST.get('entry_amt')) * no_of_entry
        # print "amt", entry_amt
        # if request.method == "POST":
        if request.POST.get('bot_catcher') != "":
            return redirect(reverse('general:homepage'))
        # choice = str(request.POST.get('user-choice'))
        if entry_amt == "" or entry_amt < 25:
            messages.error(request, "Amount added is below minimum amount")
            return redirect(request.META['HTTP_REFERER'])
        if choice == "":
            messages.error(request, "You need to make a choice")
            return redirect(request.META['HTTP_REFERER'])
        if entry_amt > balance:
            messages.error(request, "You do not have sufficient money in your wallet to play the game")
            return redirect(request.META['HTTP_REFERER'])

        # ref = purchase_ref()
        event = DailyJackPot.objects.get(id=question)
        today = datetime.datetime.now()  # To get current date and time
        current_time = today.strftime("%I:%M %p")  # to get current time in string format
        print "current_time", current_time
        dt = datetime.datetime.strptime(current_time,"%I:%M %p").time()  # to convert datetime.datetime object to datetime.time object
        print "dt", dt
        if event.stop_time < dt:
            messages.error(request, "Daily Jackpot for today has ended")
            return redirect(request.META['HTTP_REFERER'])
        user = UserAccount.objects.get(user=request.user)
        counter = 0
        while (counter < no_of_entry):
            ref = purchase_ref()
            entry = DailyJackpotEntries.objects.create(dailyjackpot=event, user_obj=user, choice=choice,
                                                       ticket_no=ref)
            entry.date = timezone.now().date()
            entry.user_email = user.user.email
            entry.user_first_name = user.user.first_name
            entry.user_last_name = user.user.last_name
            entry.telephone_no = user.phone_number 
            entry.save()
            user.djp_wjp_cat = True
            user.total_djp_played += 1
            user.wallet_funded = True
            user.game_played = True
            user.save()
            event.total_entries += 1
            event.save()
            bank_record = Bank.objects.create(user=request.user, txn_type="Remove", amount=event.entry_amount,
                                              ref_no=ref,
                                              created_at=timezone.now(), status="Successful", bank="DailyJackPot",
                                              message="DailyJackPot for the day")
            bank_record.date_created = timezone.now().date()
            bank_record.save()
            payment = Betpayments.objects.create(user=request.user, amount=event.entry_amount, djp=event, date=timezone.now())
            payment.date_created = timezone.now().date()
            payment.save()

            counter += 1
            # print "counter", counter

        WalletBalances.objects.create(balance_bf=balance, description="Daily Jackpot", current_bal=float(balance - (event.entry_amount * counter)), amount=float(event.entry_amount * counter), user=request.user.useraccount)
        user.wallet_balance = float(balance - entry_amt)
        user.save()

        messages.success(request, 'Your answer has been successfully submitted!!!.')
        
        return redirect(request.META['HTTP_REFERER'])

    else:
        context = {}
        now = timezone.now()
        today = timezone.now().date()
        events_all = getAllOpenEvent(request)
        categories = []
        for event in events_all:
            if event.category in categories:
                pass
            else:
                categories.append(event.category)
        context['categories'] = categories
        # balance = account_standing(request,request.user)

        context['balance'] = balance

        try:
            event = DailyJackPot.objects.get(created_on_date=today)
            print event
            todays_date = timezone.now().date()
            past_dates = timezone.now() - timezone.timedelta(days=7)
            yesterday = timezone.now() - timezone.timedelta(days=1)
            # print yesterday
            jackpots = DailyJackPot.objects.filter(created_on_date__range=[past_dates, todays_date])
            # print jackpots
            yesterdays_game = DailyJackPot.objects.get(created_on_date=yesterday)
            # print yesterdays_game
            context['event'] = event
            context['jackpots'] = jackpots
            context['yesterday_event'] = yesterdays_game
            print event.stop_time
            # print now
            djp = ""
            if event.end_time >= now:
                djp = True
            else:
                djp = False
            # print djp
            context['djp'] = djp
        except:
            event = []
            todays_date = timezone.now().date()
            past_dates = timezone.now() - timezone.timedelta(days=7)
            yesterday = timezone.now() - timezone.timedelta(days=1)
            # print yesterday
            jackpots = DailyJackPot.objects.filter(created_on_date__range=[past_dates, todays_date])
            # print jackpots
            yesterdays_game = DailyJackPot.objects.get(created_on_date=yesterday)
            # print yesterdays_game
            context['event'] = event
            context['jackpots'] = jackpots
            context['yesterday_event'] = yesterdays_game
            # print event.end_time
            # print now
            djp = ""
            context['djp'] = djp
    return render(request, 'general/dailyjackpot.html', context)


@login_required
def vendor_game_play(request):
    # print 'rp',request.POST
    balance = account_standing(request, request.user)
    random_ref = purchase_ref()
    try:
        useraccount = UserAccount.objects.get(user=request.user)
        if not useraccount.profile_updated:
            messages.warning(request, "Please update your profile before playing the game")
            return redirect(reverse('general:profile'))
    except Exception as e:
        print "e", e
        messages.warning(request, "Please update your profile before playing the game")
        return redirect(reverse('general:profile'))
    if request.method == "POST":
        if request.POST.get('bot_catcher') != "":
            return redirect(reverse('general:homepage'))
        # print request.POST
        amount = float(request.POST.get('amount'))
        choice = str(request.POST.get('user-choice'))
        if amount == "" or amount < 200:
            messages.error(request, "Amount added is below minimum amount")
            return redirect(request.META['HTTP_REFERER'])
        if choice == "":
            messages.error(request, "You need to make a choice")
            return redirect(request.META['HTTP_REFERER'])
        if amount > balance:
            messages.error(request, "You do not have sufficient money in your wallet to play the game")
            return redirect(request.META['HTTP_REFERER'])
        else:
            # choice = str(request.POST.get('user-choice'))
            print 'choice', choice
            event = Event.objects.get(pk=request.POST.get('event_id'))
            user = UserAccount.objects.get(user=request.user)
            vendorClient, created = VendorClient.objects.get_or_create(useraccount=user,
                                                                       phone_number=request.POST.get('phone'))
            if created:
                vendorClient.client_code = purchase_ref()
                vendorClient.save()
            else:
                pass

            try:
                gameplay = Gameplay.objects.get(user=user, event=event, vendorClientCode=vendorClient.client_code,
                                                tel_no=request.POST.get('phone'), nvp=True)
                # print gameplay
                print 'saw this'
                messages.warning(request, "You have already played a game for this client in this Event")
                return redirect(request.META['HTTP_REFERER'])
            except Exception as e:
                print "e", e

            gameplay = Gameplay.objects.create(user=user, event=event, amount=amount, choice=choice,
                                               date=timezone.now(), status="OPEN",tel_no=request.POST.get('phone'), 
                                               vendorClientCode=vendorClient.client_code, nvp=True,
                                               ref_number=random_ref)
            gameplay.date_played = timezone.now().date()
            gameplay.save()
            event.total_amt += amount
            event.counter += 1
            event.save()
            user.djp_wjp_cat = True
            user.total_cat_games_played += 1
            user.wallet_funded = True
            user.game_played = True
            user.save()
            bank_record = Bank.objects.create(user=request.user, txn_type="Remove", amount=amount, ref_no=random_ref,
                                              created_at=timezone.now(), status="Successful", bank="Gameplay",
                                              message="Gameplay for event " + event.event_id)
            bank_record.date_created = timezone.now().date()
            bank_record.save()
            payment = Betpayments.objects.create(user=request.user, amount=amount, game=gameplay, date=timezone.now())
            payment.date_created = timezone.now().date()
            payment.save()
            title = "Prediction Confirmation"
            text = "general/game_confirmation.html"
            mail_user(request, user.user, title, text, pkg=gameplay)

            WalletBalances.objects.create(balance_bf=balance,description="Category Games",current_bal=float(balance - amount),amount=amount,user=request.user.useraccount)
            user.wallet_balance = float(balance - amount)
            user.save()

            messages.success(request, 'Congratulations!!!! You have successfully made your prediction!!!.')
            return redirect(request.META['HTTP_REFERER'])

    messages.warning(request, "You have already Participated in this Event")
    return redirect(request.META['HTTP_REFERER'])


@login_required
def vendor_dailyjackpot(request):
    # from datetime import datetime
    balance = account_standing(request, request.user)
    if request.method == "POST":
        if not request.user.is_authenticated():
            return redirect(reverse('general:login'))
        try:
            useraccount = UserAccount.objects.get(user=request.user)
            if not useraccount.profile_updated:
                messages.warning(request, "Please update your profile before Playing Daily Jackpot")
                return redirect(reverse('general:profile'))
        except Exception as e:
            print "e", e
            messages.warning(request, "Please update your profile before you can play")
            return redirect(reverse('general:profile'))

        question = request.POST.get('event_id')
        choice = request.POST.get('user-choice')
        no_of_entry = int(request.POST.get('no_of_entries'))
        # print no_of_entry
        phone_number = request.POST.get("phone")

        # 02345678
        # +345 890 6559
        # 2345377973597

        entry_amt = 25 * no_of_entry
        print "amt", entry_amt
        # if request.method == "POST":
        if request.POST.get('bot_catcher') != "":
            messages.error(request, "Invalid input detected")
            return redirect(request.META['HTTP_REFERER'])
        # choice = str(request.POST.get('user-choice'))
        if entry_amt == "" or entry_amt < 25:
            messages.error(request, "Amount added is below minimum amount")
            return redirect(request.META['HTTP_REFERER'])
        if choice == "":
            messages.error(request, "You need to make a choice")
            return redirect(request.META['HTTP_REFERER'])
        if entry_amt > balance:
            messages.error(request, "You do not have sufficient money in your wallet to play this game")
            return redirect(request.META['HTTP_REFERER'])

        # ref = purchase_ref()
        event = DailyJackPot.objects.get(id=question)
        today = datetime.datetime.now()  # To get current date and time
        current_time = today.strftime("%I:%M %p")  # to get current time in string format
        print "current_time", current_time
        dt = datetime.datetime.strptime(current_time,"%I:%M %p").time()  # to convert datetime.datetime object to datetime.time object
        print "dt", dt
        if event.stop_time < dt:
            messages.error(request, "Daily Jackpot for today has ended")
            return redirect(request.META['HTTP_REFERER'])
        user = UserAccount.objects.get(user=request.user)
        counter = 0
        tickets_number_list = []

        while (counter < no_of_entry):
            ref = purchase_ref()
            entry = DailyJackpotEntries.objects.create(
                telephone_no = phone_number,
                dailyjackpot=event, 
                user_obj=user, 
                choice=choice,
                ticket_no=ref)
            entry.date = timezone.now().date()
            entry.user_email = user.user.email
            entry.user_first_name = user.user.first_name
            entry.user_last_name = user.user.last_name
            entry.telephone_no = user.phone_number 
            entry.save()
            user.djp_wjp_cat = True
            user.total_djp_played += 1
            user.wallet_funded = True
            user.game_played = True
            user.save()
            event.total_entries += 1
            event.save()

            bank_record = Bank.objects.create(user=request.user, 
                txn_type="Remove", 
                amount=event.entry_amount,
                ref_no=ref, 
                created_at=timezone.now(), 
                status="Successful", 
                bank="DailyJackPot",
                message="DailyJackPot for the day")

            bank_record.date_created = timezone.now().date()
            bank_record.save()
            payment = Betpayments.objects.create(user=request.user,amount=event.entry_amount, djp=event, date=timezone.now())
            payment.date_created = timezone.now().date()
            payment.save()

            counter += 1
            tickets_number_list.append(entry)
            message = "Tk No: " + entry.ticket_no + ", N25" + ", Date: " + str(entry.date) + ", Choice: " + entry.choice
            
            # send_sms(msg=message, num=strip_phone_number(phone_number))

            # print "counter", counter

        vendorClient, created = VendorClient.objects.get_or_create(useraccount=user,phone_number=request.POST.get('phone'))

        if created:
            vendorClient.client_code = purchase_ref()
            vendorClient.save()
        else:
            pass

        WalletBalances.objects.create(balance_bf=balance, description="Daily Jackpot", current_bal=float(balance - (event.entry_amount * counter)), amount=float(event.entry_amount * counter), user=request.user.useraccount)
        user.wallet_balance = float(balance - entry_amt)
        user.save()

        messages.success(request, 'Your answer has been successfully submitted!!!.')

        # title = "Daily Jackpot"
        # text = "general/djp_confirmation.html"
        # mail_user_djp(request, user.user, title, text, djp=event, pkg=tickets_number_list)
        
        
        return redirect(request.META['HTTP_REFERER'])

    return redirect(request.META['HTTP_REFERER'])

    
@login_required
def user_entries(request):
    context = {}
    try:
        today = timezone.now().date()
        event = DailyJackPot.objects.get(created_on_date=today)
        context['event'] = event
        new_dailyjackpot = DailyJackpotEntries.objects.filter(user_obj=request.user.useraccount)
    except:
        new_dailyjackpot = DailyJackpotEntries.objects.filter(user_obj=request.user.useraccount)
    # print "djp", dailyjackpot
    context['dailyjackpot'] = new_dailyjackpot
    return render(request, 'general/user_daily_jackpot_entries.html', context)
