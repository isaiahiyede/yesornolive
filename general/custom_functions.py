from django.contrib.auth.models import User
from django.template import Context, RequestContext
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponse
from general.models import Event, UserAccount
from django.utils import timezone
import datetime
from wallet.account_standing import account_standing
from django.db.models import Q
from general.activitylogger import ActivityLogger
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from ynladmin.models import CostSetting
import csv
from wallet.models import Bank
from gameplay.models import Gameplay, DailyJackpotEntries, DailyJackPot
from django.utils.encoding import smart_str
from django.db.models import Q, Sum


# import http.client
import httplib
# httplib is for python 2.7 and http.client is for python 3

# sms sending function takes two parameters, message and destination number
# return data is just text-sending parameters and status and also report data
def send_sms(msg=None, num=None):
    # conn = http.client.HTTPSConnection("api.infobip.com")
    conn = httplib.HTTPSConnection("api.infobip.com")

    payload = '{"from":"YesOrNoLive", "to":"%s", "text":"%s" }' % (num, msg)
    print(payload)

    headers = {
        'authorization': "Basic YmFua2xpbms6OFZRUypWQ1JyYm1UX3ZzSA==",
        'content-type': "application/json",
        'accept': "application/json"
        }

    conn.request("POST", "/sms/1/text/single", payload, headers)

    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    conn.request("GET", "/sms/1/reports?limit=1", headers=headers)
    report = conn.getresponse()
    rep_data = report.read()
    print("")
    print("")
    print(rep_data.decode("utf-8"))
    print("")
    print("")


    return data, rep_data




def mail_user(request, user, title, text, pkg=None, username=None):
    if username:
        name = username
    else:
        name       = user.first_name
    to         =  [user.email]
    from_email = '{} <{}>'.format('YesorNoLive.com', 'info@yesornolive.com')
    subject = title
    msg_text = render_to_string(text)
    ctx  = {
        'username': name,
        'body': get_template(text).render(Context({'request':request})),
        'request':request,
        }
    if not pkg == None:
        ctx['body'] = get_template(text).render(Context({'pkg':pkg, 'request':request}))
    message = get_template('general/base_email.html').render(Context(ctx))
    msg = EmailMessage(subject, message, from_email, to)
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(message)

def mail_user_djp(request, user, title, text, pkg=None, djp=None,username=None):
    if username:
        name = username
    else:
        name       = user.first_name
    to         =  [user.email]
    from_email = '{} <{}>'.format('YesorNoLive.com', 'info@yesornolive.com')
    subject = title
    msg_text = render_to_string(text)
    ctx  = {
        'username': name,
        'body': get_template(text).render(Context({'request':request})),
        'request':request,
        }
    if not pkg == None:
        ctx['body'] = get_template(text).render(Context({'djp':djp,'pkg':pkg, 'request':request}))
    message = get_template('general/base_email.html').render(Context(ctx))
    msg = EmailMessage(subject, message, from_email, to)
    msg.content_subtype = 'html'
    msg.send()
    return HttpResponse(message)

def check_eventTime(request):
    today = timezone.now().date()
    now = datetime.datetime.now()
    # print "now", now
    current_time = now.strftime("%I:%M %p")
    dt=datetime.datetime.strptime(current_time,"%I:%M %p").time()
    # print "dt", dt
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
            if event.end_time<= dt:
                events.append(event)
    return events


def activity_history(user,obj_id,obj_model_name,action,message):
    history_instance = ActivityLogger.objects.create(user=user,obj_id=obj_id,obj_model_name=obj_model_name,action=action,obj_description=message)
    return history_instance


def calculator(request):
    #print "am here"
    today = timezone.now().date()
    if request.method == "GET":
        print request.GET
        choice = request.GET.get("choice")
        amount = request.GET.get("amount")
        event_id = request.GET.get('event_id')
        print choice, amount, event_id

        if choice == "" or amount == "":
            message = 'Please ensure a choice is selected and an amount filled!!!'
            return render(request, 'general_snippets/calculator.html', {'message':message})
        else:
            event = Event.objects.get(pk=event_id)

            est_win = event.estimated_wining
           
            # if event.end_date > today:
            #     if est_win < event.gameplay_total_value():
            #         total_amount = amount + event.gameplay_total_value()
            #     else:
            #         total_amount = amount + est_win

            # elif event.end_date == today:
            #     if event.end_time <= current_time:
            #         if est_win <= event.gameplay_total_value():
            #             total_amount = amount + event.gameplay_total_value()
            #         else:
            #             total_amount = amount + est_win
            #     else:

            if est_win <= event.gameplay_total_value():
                est_win = event.gameplay_total_value()

            amount = float(amount)
            total_amount = float(amount + est_win)
            cost_amt = CostSetting.objects.get(id=1)
            stakeholders_percentage = cost_amt.amount * 0.01

            #win_amt = event.gameplay_set.filter(choice=choice).aggregate(Sum('amount'))['amount__sum']
            # if win_amt == None:
            #     win_amt = 0
            
            #win_amt += amount
          
            game_ratio = event.game_ratio
            print "game_ratio_yes",game_ratio

            game_ratio_split = str(game_ratio).split(':')
            print "game_ratio_split",game_ratio_split
            game_ratio_inta = int(game_ratio_split[0])
            game_ratio_intb = int(game_ratio_split[1])
            print "game ratio int", game_ratio_inta, game_ratio_intb

            game_ratio_float = float(game_ratio_inta / float(game_ratio_inta + game_ratio_intb))
            print "game_ratio_float",game_ratio_float

            if game_ratio_inta < game_ratio_intb:
                if choice == "YES":
                   game_ratio_float = 1 - game_ratio_float

            else:
                if choice == "NO":
                    game_ratio_float = 1 - game_ratio_float

            print "game_ratio_no",game_ratio_float
            print "wins",event.estimated_wining
            print "in db",event.gameplay_total_value()

            # amomut_to_be_shared = stakeholders_percentage * float(event.estimated_wining - (float(game_ratio_float * float(event.estimated_wining))))
            # winning_side_sum = float(game_ratio_float * event.estimated_wining) + float(amount)
            # amount_won = (amount * amomut_to_be_shared)/winning_side_sum
            # amount_won += amount

            win_amt = total_amount * float(game_ratio_float)
            lose_amt = total_amount - win_amt
            print "losers",lose_amt, cost_amt, stakeholders_percentage
            print "winners", win_amt
            
            total_win_amt = win_amt + amount
            stakeholders_amt = lose_amt * stakeholders_percentage
            left_over = lose_amt - stakeholders_amt
            print left_over, stakeholders_amt, lose_amt
            amount_won = round(((amount * left_over)/total_win_amt) + amount,2)
            print "amount_won", amount_won

            return render(request, 'general_snippets/calculator.html', {'data':amount_won})
         
        #half_value = total_amount * 0.5
        #print "half_value",half_value
        # if win_amt >= half_value and lose_amt != 0:
        #     print "winnings greater than 50% of total amount"
        #     stakeholders_amt = lose_amt * stakeholders_percentage
        #     left_over = lose_amt - stakeholders_amt
        #     
        #     percentage_won = math.floor((100 * amount)/win_amt)
        #     amount_won = percentage(percentage_won, left_over) + amount
        #     
        # elif win_amt == total_amount:
        #     amount_won = amount
        # elif win_amt < half_value and win_amt != 0:
        #     print "winnings lesser than 50% of total amount"
        #     left_over = half_value - win_amt
        #     print "left_amt", left_over
        #     gameplay = Gameplay.objects.filter(event=event, choice=event.event_decision)
        #     print "gameplay", gameplay
        #     for game in gameplay:
        #         percentage_won = math.floor((100 * game.amount)/win_amt)
        #         print "%",percentage_won
        #         print game.amount
        #         amount_won = percentage(percentage_won, left_over) + game.amount
        #         # print "amt_won", amount_won
        #         game.decision = "WIN"
        #         game.amount_won = amount_won
        #         game.status = "CLOSED"
        #         game.save()
        #         bank_record, created = Bank.objects.get_or_create(user=game.user.user,txn_type="Add",amount=amount_won, ref_no=purchase_ref(),
        #                     created_at=timezone.now(), message="Amount won for Event" + " " +event.event_id, bank="YNL", status="Successful")
        #         title = "Prediction Results"
        #         text = "general/game_results.html"
        #         mail_user(request, game.user.user, title, text, pkg=game)
        #     event.closed = True
        #     event.save()
        #     lost_game = Gameplay.objects.filter(event=event,status="OPEN")
        #     for game in lost_game:
        #         game.status = "CLOSED"
        #         game.decision = "LOST"
        #         game.save()
        #         title = "Prediction Results"
        #         text = "general/game_lost.html"
        #         mail_user(request, game.user.user, title, text, pkg=game)
        #     messages.success(request, "This Event has been Successfully CLOSED!!!")
        # elif win_amt == 0:
        #     print "Nobody won!!!"
        #     event.closed = True
        #     event.save()
        #     lost_game = Gameplay.objects.filter(event=event,status="OPEN")
        #     for game in lost_game:
        #         game.status = "CLOSED"
        #         game.decision = "LOST"
        #         game.save()
        #         title = "Prediction Results"
        #         text = "general/game_lost.html"
        #         mail_user(request, game.user.user, title, text, pkg=game)
        #     messages.success(request, "This Event has been Successfully CLOSED!!!")
        # else:
        #     print "I rep o"
        
        
def export_csv(request):
    from datetime import datetime
    
    query = request.GET.get('query')
    from_date = request.GET.get('from-date')
    to_date  = request.GET.get('to-date')
    print "from_date",from_date

    if query == "export_users_csv":
        if from_date and to_date :
            start_date = datetime.strptime(from_date, "%m/%d/%Y")
            end_date = datetime.strptime(to_date, "%m/%d/%Y")
            queryset = User.objects.filter(useraccount__isnull=True, is_staff=False, date_joined__range=(start_date, end_date))  #to get the users dat dont have useraccount
        else:
            queryset = User.objects.filter(useraccount__isnull=True, is_staff=False)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=user_profile_not_updated.csv'
    
    elif query ==  "export_fund":
        if from_date and to_date :
            start_date = datetime.strptime(from_date, "%m/%d/%Y")
            end_date = datetime.strptime(to_date, "%m/%d/%Y")
            queryset = User.objects.filter(useraccount__isnull=False, useraccount__profile_updated=True, bank__isnull=True, is_staff=False, date_joined__range=(start_date, end_date)).distinct()  #to get the users dat dont have useraccount
        else:
            queryset = User.objects.filter(useraccount__isnull=False, useraccount__profile_updated=True, bank__isnull=True, is_staff=False).distinct()   #to get the users dat dont have useraccount
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=user_profile_updated_acc_not_funded.csv'
    
    elif query == "export_game":
        if from_date and to_date :
            start_date = datetime.strptime(from_date, "%m/%d/%Y")
            end_date = datetime.strptime(to_date, "%m/%d/%Y")
            # queryset = UserAccount.objects.filter(gameplay__isnull=True,user__bank__isnull=False,validator=False,special_user=False,content_provider=False,decider=False,accounts=False, created_on__range=(start_date, end_date)).distinct() #to get the users dat dont have useraccount
            queryset = []
            users_without_gameplay = UserAccount.objects.filter(profile_updated=True,validator=False,special_user=False,content_provider=False,decider=False,accounts=False, created_on__range=(start_date, end_date)).distinct() #to get the users dat dont have useraccount
            for user in users_without_gameplay:
                if user.get_all_gameplay_count() == 0:
                    added_payments = Bank.objects.user_add_credit(user.user).aggregate(Sum('amount')) 
                    if (added_payments['amount__sum'] != None) and (float(account_standing(request,user.user) > 0.0)):
                        # print "username - the_sum - acc_bal", user.user.username, added_payments['amount__sum'], account_standing(request, user.user)
                        queryset.append(user)
                    else:
                        pass
                else:
                    pass
        else:
            # queryset = UserAccount.objects.filter(gameplay__isnull=True,user__bank__isnull=False,validator=False,special_user=False,content_provider=False,decider=False,accounts=False).distinct()   #to get the users dat dont have useraccount
            queryset = []
            users_without_gameplay = UserAccount.objects.filter(profile_updated=True,validator=False,special_user=False,content_provider=False,decider=False,accounts=False).distinct() #to get the users dat dont have useraccount
            for user in users_without_gameplay:
                if user.get_all_gameplay_count() == 0:
                    added_payments = Bank.objects.user_add_credit(user.user).aggregate(Sum('amount')) 
                    if (added_payments['amount__sum'] != None) and (float(account_standing(request,user.user) > 0.0)):
                        # print "username - the_sum - acc_bal", user.user.username, added_payments['amount__sum'], account_standing(request, user.user)
                        queryset.append(user)
                    else:
                        pass
                else:
                    pass
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=users_acc_funded_and_not_played.csv'
    
    elif query == "export_punters":
        if from_date and to_date :
            start_date = datetime.strptime(from_date, "%m/%d/%Y")
            end_date = datetime.strptime(to_date, "%m/%d/%Y")
            queryset = []
            users_without_gameplay = UserAccount.objects.filter(profile_updated=True,validator=False,special_user=False,content_provider=False,decider=False,accounts=False, created_on__range=(start_date, end_date)).distinct()  #to get the users dat dont have useraccount
            for user in users_without_gameplay:
                if user.get_all_gameplay_count() > 0:
                    queryset.append(user)
                else:
                    pass
        else:
            queryset = []
            users_without_gameplay = UserAccount.objects.filter(profile_updated=True,validator=False,special_user=False,content_provider=False,decider=False,accounts=False).distinct() #to get users that have funded and played a game
            for user in users_without_gameplay:
                if user.get_all_gameplay_count() > 0:
                    queryset.append(user)
                else:
                    pass
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=users_acc_funded_and_played.csv'

    elif query == "won_djp":
        if from_date and to_date :
            start_date = datetime.strptime(from_date, "%m/%d/%Y")
            end_date = datetime.strptime(to_date, "%m/%d/%Y")
            queryset = DailyJackpotEntries.objects.filter((~Q(user_obj=None)),won=True)  #to get the users dat dont have useraccount
        else:
            queryset = DailyJackpotEntries.objects.filter((~Q(user_obj=None)),won=True)   #to get users that have funded and played a game
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=user_djp_played.csv'
    
    elif query == "export_punters_category":
        category = request.GET.get('category')
        print category
        if from_date and to_date :
            start_date = datetime.strptime(from_date, "%m/%d/%Y")
            end_date = datetime.strptime(to_date, "%m/%d/%Y")
            queryset =Gameplay.objects.filter(date__range=(start_date, end_date))
        else:
            queryset =Gameplay.objects.all()   #to get users that have funded and played a game
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=users_played_cat_games_played.csv'
    
    else:
        return redirect(request.META['HTTP_REFERER'])
        
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)

    if query == "export_users_csv":
        writer.writerow([
            smart_str(u"Date Joined"),
            smart_str(u"Username"),
            smart_str(u"Email"),
        ])
        for obj in queryset:
            writer.writerow([
                smart_str(obj.date_joined.date()),
                smart_str(obj.username),
                smart_str(obj.email),
            ])

    elif query == "export_fund":    
        writer.writerow([
            smart_str(u"Date joined"),
            smart_str(u"First Name"),
            smart_str(u"Last Name"),
            smart_str(u"Email"),
            smart_str(u"Phone Number"),
        ])
        for obj in queryset:
                writer.writerow([
                    smart_str(obj.date_joined.date()),
                    smart_str(obj.first_name),
                    smart_str(obj.last_name),
                    smart_str(obj.email),
                    smart_str(obj.useraccount.phone_number),
                ])

    elif query == "won_djp":    
        writer.writerow([
            smart_str(u"Date"),
            smart_str(u"Email"),
            smart_str(u"Phone Number"),
            smart_str(u"Username"),
            smart_str(u"Choice"),
            smart_str(u"Ticket Number"),
            smart_str(u"Amount"),
        ])
        for obj in queryset:
                writer.writerow([
                    smart_str(obj.date),
                    smart_str(obj.user_obj.user.email),
                    smart_str(obj.user_obj.phone_number),
                    smart_str(obj.user_obj.user.username),
                    smart_str(obj.choice),
                    smart_str(obj.ticket_no),
                    smart_str(obj.amount),
            ])

    elif query == "export_punters_category":
        writer.writerow([
            smart_str(u"Category"),
            smart_str(u"First Name"),
            smart_str(u"Last Name"),
            smart_str(u"Email"),
            smart_str(u"Phone Number"),
        ])
        for obj in queryset:
            if obj.event.category == category:
                writer.writerow([
                    smart_str(obj.event.category),
                    smart_str(obj.user.user.first_name),
                    smart_str(obj.user.user.last_name),
                    smart_str(obj.user.user.email),
                    smart_str(obj.user.phone_number),
                ])
    else:
        writer.writerow([
            smart_str(u"Date"),
            smart_str(u"First Name"),
            smart_str(u"Last Name"),
            smart_str(u"Email"),
            smart_str(u"Phone Number"),
            smart_str(u"Amount (N)"),
        ])
        for obj in queryset:
            writer.writerow([
                smart_str(obj.created_on.date()),
                smart_str(obj.user.first_name),
                smart_str(obj.user.last_name),
                smart_str(obj.user.email),
                smart_str(obj.phone_number),
                smart_str(account_standing(request, obj.user)),
            ])
            
    return response
	# export_csv.short_description = u"Export CSV"
    
    
def set_cookie(request, response, key, value, max_age_seconds):
    if not check_cookie(request, key):
        response.set_cookie(key, value, max_age_seconds)
    return response

def check_cookie(request, cookie_key):
    return request.COOKIES.has_key(cookie_key)


def get_user_requested(request, username, email=None):
    user = None
    '''Return user depending on which marketing_member they belong to'''
    if email:
        user = get_object_or_404(User, email = email)
    else:
        user = get_object_or_404(User, username = username)
    return user


def get_the_trader(request):
    user = request.user.username
    if user == 'ovirih4games':
        code = 1
    elif user == 'AbdulwahabAdi':
        code = 2
    elif user == 'YinkaDavies':
        code = 3
    elif user == 'Oyindamola':
        code = 5
    elif user == 'iyede_isaiaih':
        code = 4
    return code

def updateModelValues(event):
    event.event_total_value = event.gameplay_total_value()
    event.event_total_winnings = event.event_winnings()
    event.event_total_profit = event.event_profit()
    event.event_total_stakeholder_amount = event.stakeholder_amount()
    event.event_total_vendor_amount = event.vendor_amount()
    event.event_total_jackpot_amount = event.jackpot_amount()
    event.event_total_users_amount = event.users_amount()
    event.event_total_amount_won = event.total_amount_won()
    event.event_total_players = event.total_players()
    event.event_total_winners = event.total_winners()
    event.event_total_losers = event.total_losers()
    event.event_total_yes_choice = event.total_yes_choice()
    event.event_total_no_choice = event.total_no_choice()
    event.event_total_yes_amount = event.total_yes_choice_played()
    event.event_total_no_amount = event.total_no_choice_played()
    event.event_status = event.game_status()
    event.save()
    return True


