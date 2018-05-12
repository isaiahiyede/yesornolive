from __future__ import unicode_literals
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from general.forms import UserForm, UserAccountForm, UserProfileForm, MessageCenterCommentForm, RepliesForm, bankForm, UserForm2
from general.models import UserAccount, Event, MessageCenter, MessageCenterComment, Comments, Likes, Replies, Referral, \
    VendorClient
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.context import RequestContext
from django.db.models import Count
from django import template
import random, datetime
from django.core.urlresolvers import reverse
import json
from django.db.models import Sum, Max
from general.userSearch import searchQuery
from django.utils import timezone
from wallet.account_standing import account_standing, account_standing_new
from wallet.models import Bank
from gameplay.models import Gameplay, DailyJackPot, DailyJackpotEntries
from general.staff_access import *
from django.views.decorators.csrf import csrf_exempt
from general.custom_functions import mail_user, set_cookie, get_user_requested, check_cookie
import csv


# Create your views here.


def random_no():
    # random_code = '1-%d' %random.randint(0, 9)
    # random_code = '%d' %random.randint(0, 9)
    random_code = ''
    # alnum = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for x in range(4):
        random_code += str(random.randint(0, 9))
        # random_code += random.choice(alnum)
    # print random_code
    return random_code

# def remove_non_ascii(text):
#     return unidecode(unicode(text, encoding = "utf-8"))


def paginate_list(request, objects_list, num_per_page):
    paginator = Paginator(objects_list, num_per_page)  # show number of jobs per page
    page = request.GET.get('page')
    try:
        paginated_list = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer, deliver first page
        paginated_list = paginator.page(1)
    except  EmptyPage:
        # if page is out of range(e.g 9999), deliver last page of results
        paginated_list = paginator.page(paginator.num_pages)
    return paginated_list


def getAllOpenEvent(request):
    return Event.objects.filter(deleted=False, publish=True, validated=True, closed=False)


def getLiveCategory(request, value):
    context = {}
    today = timezone.now().date()
    context['today'] = today
    balance = account_standing(request, request.user)
    context['balance'] = balance
    template_name = 'general/events-page.html'
    value_to_upperCase = value.upper()

    now = datetime.datetime.now() # To get current date and time
    current_time = now.strftime("%I:%M %p")
    dt = datetime.datetime.strptime(current_time, "%I:%M %p").time()

    events_all = []

    category = Event.objects.filter(
        deleted=False, 
        publish=True, 
        validated=True, 
        closed=False,
        category=value_to_upperCase,
        end_date__gte=today,
    )

    for event in category:
        if event.end_date == today:
            if event.end_time > dt:
                events_all.append(event)
            else:
                pass
        else:
            events_all.append(event)

    # events_all = Event.objects.filter(deleted=False,
    # publish=True,validated=True,category=value_to_upperCase).order_by('-end_date')
    datalist = getAllOpenEvent(request).values_list('title', flat=True).distinct()
    new_datalist = ",".join([unicode(item) for item in datalist])
    all_events = paginate_list(request, events_all, 16)
    categories = []
    # print new_datalist

    for event in events_all:
        if event.category in categories:
            pass
        else:
            categories.append(event.category)

    context['categories'] = categories
    context['all_events'] = all_events
    context['datalist'] = new_datalist
    return render(request, template_name, context)


def getMarquee(request):
    today = timezone.now().date()
    context = {}
    events_all = getAllOpenEvent(request).filter(end_date__gte=today)

    # random_number = random.randint(0,len(events_all))
    # print events_all

    count = 6

    if len(events_all) + 1 <= count:
        context['trending_events'] = all_events = events_all
    else:
        all_events_list = []
        while count:
            selected = random.choice(events_all)
            if selected in all_events_list:
                pass
            else:
                all_events_list.append(selected)
                count -= 1

        context['trending_events'] = all_events = all_events_list
    
    return all_events


def homepage(request):
    context = {}
    today = timezone.now().date()
    template_name = 'general/homepage.html'
    current_time = timezone.now()
    
    # all_eventz = []

    # for event in events_all:
    #     if event.trending == True:
    #         # print event.bet_question
    #         all_eventz.append(event)

    # if len(all_eventz) >= 4:
    #     all_events = all_eventz[0:5]
    # else:
    #     all_events = paginate_list(request, events_all, 4)
    # print all_events

    # print len(eventz_all)
    
    context['trending_events'] = marquee_events = getMarquee(request)

    balance = account_standing(request, request.user)

    try:
        user = UserAccount.objects.filter(user=request.user).exists()
        useraccount = user
    except:
        useraccount = None

    today = timezone.now().date()


    try:
        djp_event = DailyJackPot.objects.get(created_on_date=today)
        now = timezone.now()
        todays_date = timezone.now().date()
        past_dates = timezone.now() - timezone.timedelta(days=7)
        yesterday = timezone.now() - timezone.timedelta(days=1)
        yesterdays_game = DailyJackPot.objects.get(created_on_date=yesterday)
        # print yesterdays_game
        context['djp_event'] = djp_event
        context['yesterday_event'] = yesterdays_game
        
        # print now
        djp = ""
        if djp_event.end_time >= now:
            djp = True
        else:
            djp = False
        # print djp
        context['djp'] = djp
    except:
        pass

    # clear_all_points = Gameplay.objects.all().update(game_points=0)

    # print useraccount
    # categories = []
    # try:
    #     most_recent = events_all[0]
    #     context['most_recent'] = most_recent
    # except:
    #     pass
    # for event in events_all:
    #     if event.category in categories:
    #         pass
    #     else:
    #         categories.append(event.category)
    #
    # context['trending_events'] = all_events[0:3]

    try:
        context['some_more_events'] = marquee_events[-1]
    except:
        context['some_more_events'] = []

    context['current_time'] = current_time.date()
    context['events'] = marquee_events
    context['balance'] = balance
    context['useraccount'] = useraccount
    context['today'] = today
    context['macquees'] = marquee_events
    

    return render(request, template_name, context)


def comingSoon(request):

    template_name = 'general/realityComingSoon.html'

    return render(request, template_name)


def getCategory(request, value):
    context = {}
    today = timezone.now().date()
    context['today'] = today
    balance = account_standing(request, request.user)
    context['balance'] = balance
    template_name = 'general/events-page.html'
    value_to_upperCase = value.upper()
    # print 'value_to_upperCase',value_to_upperCase
    if value_to_upperCase == 'REALITYTV':
        events_all = Event.objects.filter(realityTV=True, deleted=False, publish=True, validated=True, closed=False).order_by(
            '-end_date')
        template_name = 'general/realityTV.html'
    elif value_to_upperCase == 'ARCHIVES':
        events_all = Event.objects.filter(deleted=False, publish=True, validated=True, closed=True).order_by(
            '-end_date')
    else:
        events_all = Event.objects.filter(deleted=False, publish=True, validated=True, closed=False,
                                          category=value_to_upperCase).order_by('-end_date')
    datalist = getAllOpenEvent(request).values_list('title', flat=True).distinct()
    new_datalist = ",".join([unicode(item) for item in datalist])
    all_events = paginate_list(request, events_all, 16)
    categories = []
    # print 'all', events_all

    for event in events_all:
        if event.get_category_display() in categories:
            pass
        else:
            categories.append(event.get_category_display())

    marquee_events = getMarquee(request)

    if len(categories) > 1:
        category = 'Archives'
    elif len(categories) == 1:
        category = categories[0]
    else:
        category = ''

    context['category'] = category
    context['categories'] = categories
    context['all_events'] = all_events
    context['datalist'] = new_datalist
    context['macquees'] = marquee_events
    return render(request, template_name, context)


def getPassedCategory(request, value):
    context = {}
    today = timezone.now().date()
    context['today'] = today
    balance = account_standing(request, request.user)
    context['balance'] = balance
    template_name = 'general/events-page.html'
    value_to_upperCase = value.upper()

    now = datetime.datetime.now()  # To get current date and time
    current_time = now.strftime("%I:%M %p")
    dt = datetime.datetime.strptime(current_time, "%I:%M %p").time()

    events_all = []

    category = Event.objects.filter(
        category=value_to_upperCase,
        end_date__lte=today
    )

    for event in category:
        if event.end_date == today:
            if event.end_time < dt:
                events_all.append(event)
            else:
                pass
        else:
            events_all.append(event)

    datalist = getAllOpenEvent(request).values_list('title', flat=True).distinct()
    new_datalist = ",".join([unicode(item) for item in datalist])
    all_events = paginate_list(request, events_all, 16)
    categories = []
    # print new_datalist
    marquee_events = getMarquee(request)

    for event in events_all:
        if event.category in categories:
            pass
        else:
            categories.append(event.category)
    context['categories'] = categories
    context['all_events'] = all_events
    context['datalist'] = new_datalist
    context['macquees'] = marquee_events
    return render(request, template_name, context)


def user_login(request):
    # print len(eventz_all)
    if request.method == "POST":

        # print request.POST
        if request.POST.get('bot_catcher') != "":
            return redirect(reverse('general:homepage'))
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            username = User.objects.get(email=username).username
            # print username
        except Exception as e:
            print "e", e
            try:
                username = User.objects.get(username=username).username
                # print username
                username = username
            except Exception as e:
                messages.warning(request, "Invalid login details supplied")
                return render(request, 'general/sign_in.html', {'username': username})
        user = authenticate(username=username, password=password)
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:

                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                # print "I got here"
                # try:
                #     useraccount = request.user.useraccount
                # except:
                #     return redirect(reverse('general:profile'))

                if user.is_staff:

                    if user.useraccount.dev:
                        response = redirect(reverse('ynladmin:admin_pages', args=['statistics']))
                        max_age_seconds = 120
                        set_cookie(request, response, "admin_username", user.username, max_age_seconds)
                        return response
                    else:
                        response = redirect(reverse('ynladmin:admin_pages', args=['statistics']))
                        return response
                else:
                    # print request.session.keys()
                    response = redirect(reverse('general:events'))
                    return response
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            try:
                print "Invalid login details: {0}, {1}".format(username, password)
            except:
                pass
            messages.warning(request, "Invalid login details supplied")
            return redirect(reverse('general:login'))

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'general/sign_in.html', {})


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    if request.user.is_staff:
        response = redirect(reverse('general:login'))
    else:
        response = redirect(reverse('general:homepage'))

    logout(request)

    return response

    # Take the user back to the homepage.


# def register(request):
#     if request.method == "POST":
#         if request.POST.get('bot_catcher') != "":
#             return redirect(reverse('general:home'))
#         form = UserForm(request.POST)
#         rp = request.POST
#         # print rp

#         # print "form", form
#         if User.objects.filter(username=rp.get('username')).exists() and User.objects.filter(
#                 email=rp.get('email')).exists():
#             # print 'username and email exists'
#             return render(request, 'general/registration.html',
#                           {'form': form, 'username_is_taken': True, 'email_taken': True})
#         elif User.objects.filter(username=rp.get('username')).exists():
#             # print 'email exists'
#             return render(request, 'general/registration.html', {'form': form, 'username_is_taken': True})
#         elif User.objects.filter(email=rp.get('email')).exists():
#             # print 'email exists'                
#             return render(request, 'general/registration.html', {'form': form, 'email_taken': True})
#         else:
#             if form.is_valid():
#                 user = form.save(commit=False)
#                 password = rp.get('password')
#                 password1 = rp.get('password1')
#                 if password != password1:
#                     return render(request, 'general/registration.html', {'form': form, 'password_mismatch': True})
#                 if len(password) < 6:
#                     return render(request, 'general/registration.html', {'form': form, 'password_too_short': True})
#                 # if password == rp.get('first_name'):
#                 # 	return render(request, 'general/registration.html',
#                 #           {'form': form,'password_same_as_first_name':True})
#                 # if password.isalpha():
#                 #     return render(request, 'general/registration.html',
#                 #                   {'form': form, 'password_should_be_alphanumeric': True})
#                 # user = User.objects.create(username = rp.get('username'), email = rp.get('email').lower(),
#                 # 	first_name = rp.get('first_name'), last_name = rp.get('last_name'))
#                 user.set_password(user.password)
#                 user.date_joined = timezone.now().date()
#                 user.save()
#                 # print user
#                 username = user.username

#                 user_login = authenticate(username=username, password=password)
#                 # print user_login

#                 if user_login:
#                     # Is the account active? It could have been disabled.
#                     if user_login.is_active:
#                         # If the account is valid and active, we can log the user in.
#                         # We'll send the user back to the homepage.
#                         login(request, user_login)
#                         response = redirect(reverse('general:events'))
#                         title = "Welcome to YES or NO LIVE!!!"
#                         text = 'general/register_email.txt'
#                         mail_user(request, user, title, text, None, user.username)
#                         messages.success(request, "Registration was successful")
#                         return response
#                 else:
#                     return redirect('general:login')
#                 ''' try this '''
#                 # new_user_acc_obj = UserAccount.objects.create(user=user)
#             else:
#                 print form.errors
#     else:
#         if request.user.is_authenticated():
#             return redirect('general:events')
#         else:
#             form = UserForm()
#             if request.GET.has_key('ref'):
#                 request.session['referral'] = request.GET.get('ref')

#     return render(request, 'general/registration.html', {'form': form})


def register(request):
    form2 = bankForm()
    if request.method == "POST":
        if request.POST.get('bot_catcher') != "":
            return redirect(reverse('general:home'))
        form = UserForm2(request.POST)
        form2 = bankForm(request.POST)
        rp = request.POST
        # print rp

        # print "form", form
        if User.objects.filter(username=rp.get('username')).exists() and User.objects.filter(
                email=rp.get('email')).exists():
            # print 'username and email exists'
            return render(request, 'general/registration2.html',
                          {'form': form, 'form2':form2, 'username_is_taken': True, 'email_taken': True})
        elif User.objects.filter(username=rp.get('username')).exists():
            # print 'email exists'
            return render(request, 'general/registration2.html', {'form': form,  'form2':form2, 'username_is_taken': True})
        elif User.objects.filter(email=rp.get('email')).exists():
            # print 'email exists'                
            return render(request, 'general/registration2.html', {'form': form,  'form2':form2, 'email_taken': True})
        else:
            if form.is_valid() and form2.is_valid():
                user = form.save(commit=False)
                user_account = form2.save(commit=False)

                password = rp.get('password')
                password1 = rp.get('password1')

                if password != password1:
                    return render(request, 'general/registration2.html', {'form': form,  'form2':form2, 'password_mismatch': True})
                if len(password) < 6:
                    return render(request, 'general/registration2.html', {'form': form,  'form2':form2, 'password_too_short': True})
                # if password == rp.get('first_name'):
                #   return render(request, 'general/registration2.html',
                #           {'form': form,'password_same_as_first_name':True})
                # if password.isalpha():
                #     return render(request, 'general/registration2.html',
                #                   {'form': form, 'password_should_be_alphanumeric': True})
                # user = User.objects.create(username = rp.get('username'), email = rp.get('email').lower(),
                #   first_name = rp.get('first_name'), last_name = rp.get('last_name'))
                user.set_password(user.password)
                user.date_joined = timezone.now().date()
                user.save()

                user_account.user = user
                user_account.phone_number = rp.get('phone_number')
                user_account.account_number = rp.get('account_number')
                user_account.created_on = timezone.now()
                user_account.profile_updated = True

                user_account.save()

                # print user
                username = user.username
                user_login = authenticate(username=username, password=password)
                # print user_login

                if user_login:
                    # Is the account active? It could have been disabled.
                    if user_login.is_active:
                        # If the account is valid and active, we can log the user in.
                        # We'll send the user back to the homepage.
                        login(request, user_login)
                        response = redirect(reverse('general:events'))
                        title = "Welcome to YES or NO LIVE!!!"
                        text = 'general/register_email.txt'
                        mail_user(request, user, title, text, None, user.username)
                        messages.success(request, "Registration was successful")
                        return response

                else:
                    return redirect('general:login')
                ''' try this '''
                # new_user_acc_obj = UserAccount.objects.create(user=user)
            else:
                print form.errors
                messages.success(request, "Registration was not successful")
                return render(request, 'general/registration2.html',
                          {'form': form, 'form2':form2})
    else:
        if request.user.is_authenticated():
            return redirect('general:events')
        else:
            form = UserForm()
            if request.GET.has_key('ref'):
                request.session['referral'] = request.GET.get('ref')

    return render(request, 'general/registration2.html', {'form': form,  'form2':form2, 'form2':form2})


def get_simillar_values(request):
    events_all = getAllOpenEvent(request)
    datalist = events_all.values_list('title', flat=True).distinct()
    # new_datalist = u",".join([str(item).encode('utf-8').strip() for item in datalist])
    new_datalist = u",".join([unicode(item).encode('utf-8').strip() for item in datalist])
    
    # print new_datalist
    return events_all, new_datalist


def events_page(request):
    # print request.session.keys()
    user = request.session.get('_auth_user_id')

    try:
        user_obj = request.user
        if str(user_obj.date_joined).split(' ')[1] == "23:00:00+00:00":
            pass
        else:
            user_obj.date_joined = timezone.now().date()
            user_obj.save()
    except:
        pass

    # print "user", user
    if request.session.has_key('referral'):
        if request.user.is_authenticated():
            ref = request.session.get('referral')
            # print "ref",ref
            try:
                refree = User.objects.get(id=ref)
                if request.user == refree:
                    refree = None
            except Exception as e:
                refree = None
            if refree != None:
                referral, created = Referral.objects.get_or_create(referal=refree)
                referral.save()
                try:
                    user_account = UserAccount.objects.get(user=request.user, referred_by=referral)
                except:
                    user_account = UserAccount.objects.get(user=request.user)
                    user_account.referred_by = referral
                    user_account.save()
                else:
                    user_account = UserAccount.objects.create(user=request.user)
                    # user_account, created = UserAccount.objects.get_or_create(user=request.user)
                    # print "the user account is %s" % (user_account)
                    # if created:
                    #    user_account[0].referred_by = referral
                    # else:
                    user_account.referred_by = referral
                    user_account.save()
            del request.session['referral']
    context = {}

    balance = account_standing(request, request.user)

    context['balance'] = balance
    today = timezone.now().date()

    current_time = timezone.now()
    events_all, new_datalist = get_simillar_values(request)

    # for events in events_all:
    #     all_players = events.all_event_game_players()
    #     for player in all_players:
    #         print player.user.user.username
    #         print player.choice
    #         print player.amount
    #         print "end"
    
    marquee_events = getMarquee(request)

    all_events = paginate_list(request, events_all, 16)
    context['all_events'] = all_events
    context['datalist'] = new_datalist
    context['current_time'] = current_time
    context['today'] = today
    context['macquees'] = marquee_events

    return render(request, 'general/events-page.html', context)


def event_details(request, pk):
    context = {}
    events_all = getAllOpenEvent(request)
    categories = []
    balance = account_standing(request, request.user)
    for event in events_all:
        if event.category in categories:
            pass
        else:
            categories.append(event.category)
    context['categories'] = categories
    event_obj = Event.objects.get(pk=pk)

    try:
        next_event = Event.get_previous_by_created_on(event_obj)
        if next_event.deleted:
            pass
        else:
            context['next_event'] = next_event
    except:
        pass

    try:
        previous_event = Event.get_next_by_created_on(event_obj)
        if previous_event.deleted:
            pass
        else:
            context['previous_event'] = previous_event
    except:
        pass

    try:
        user = UserAccount.objects.filter(user=request.user).exists()
        useraccount = user
    except:
        useraccount = None

    # print useraccount
    event_pk = event_obj.pk
    today = timezone.now().date()
    most_recent = events_all[0]
    marquee_events = getMarquee(request)
    context['event'] = event_obj
    context['today'] = today
    context['all_events'] = events_all
    context['event_pk'] = event_pk
    context['most_recent'] = most_recent
    context['balance'] = balance
    context['useraccount'] = useraccount
    context['macquees'] = marquee_events

    return render(request, 'general/events-detail-page.html', context)


def event_details_slug(request, slug, pk):
    context = {}
    events_all = getAllOpenEvent(request)
    categories = []
    balance = account_standing(request, request.user)
    for event in events_all:
        if event.category in categories:
            pass
        else:
            categories.append(event.category)
    context['categories'] = categories

    try:
        event_obj = Event.objects.get(pk=pk)
    except:
        pass
        return redirect(request.META['HTTP_REFERER'])

    try:
        next_event = Event.get_previous_by_created_on(event_obj)
        if next_event.deleted:
            pass
        else:
            context['next_event'] = next_event
    except:
        pass

    try:
        previous_event = Event.get_next_by_created_on(event_obj)
        if previous_event.deleted:
            pass
        else:
            context['previous_event'] = previous_event
    except:
        pass

    try:
        user = UserAccount.objects.filter(user=request.user).exists()
        useraccount = user
    except:
        useraccount = None

    # print useraccount
    event_pk = event_obj.pk
    today = timezone.now().date()
    most_recent = events_all[0]
    marquee_events = getMarquee(request)
    context['event'] = event_obj
    context['today'] = today
    context['all_events'] = events_all
    context['event_pk'] = event_pk
    context['most_recent'] = most_recent
    context['balance'] = balance
    context['useraccount'] = useraccount
    context['macquees'] = marquee_events

    return render(request, 'general/events-detail-page.html', context)


@login_required
def user_profile(request):
    context = {}
    try:
        user_account = UserAccount.objects.get(user=request.user)
    except Exception as e:
        # print "e", e
        user_account = None
    if user_account and user_account.profile_updated:
        # print "I exist"
        user = UserAccount.objects.get(user=request.user)
        context['user'] = user
        if request.method == "POST":
            bot_catcher = request.POST.get('bot_catcher')
            if bot_catcher != "":
                return redirect(reverse('general:homepage'))
            if request.POST.get('checkbox2') == "":
                messages.success(request, "Please select the checkbox!!!")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            # print request.POST
            user_form = UserProfileForm(request.POST, instance=request.user)
            user_account_form = UserAccountForm(request.POST, request.FILES, instance=user)
            if user_account_form.is_valid() and user_form.is_valid():
                form1 = user_form.save()
                form1.first_name = request.POST.get('first_name')
                form1.last_name = request.POST.get('last_name')
                form1.save()
                form2 = user_account_form.save(commit=False)
                form2.user = request.user
                form2.created_on = timezone.now()
                form2.save()
                # user =  UserAccount.objects.get(user=request.user)
                messages.success(request, "User Details Updated Succesfully!!!")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                form1 = UserProfileForm(instance=request.user)
                form2 = UserAccountForm(instance=user)
                print user_account_form.errors, user_form.errors
                return render(request, 'general/profile.html', context)
        else:
            form1 = UserProfileForm(instance=request.user)
            form2 = UserAccountForm(instance=user)
            context['form1'] = form1
            context['form2'] = form2
            return render(request, 'general/profile.html', context)
        # print "form1", form1
    else:
        print "I do not exist"
        if request.method == "POST":
            bot_catcher = request.POST.get('bot_catcher')
            if bot_catcher != "":
                return redirect(reverse('general:homepage'))
            form1 = UserProfileForm(request.POST, instance=request.user)
            if user_account:
                user = UserAccount.objects.get(user=request.user)
                form2 = UserAccountForm(request.POST, request.FILES, instance=user)
                # print "I got here too", request.POST
            else:
                form2 = UserAccountForm(request.POST, request.FILES)
            if form1.is_valid() and form2.is_valid():
                user_form = form1.save(commit=False)
                user_form.first_name = request.POST.get('first_name')
                user_form.last_name = request.POST.get('last_name')
                user_form.save()
                user_account_form = form2.save(commit=False)
                # print user_account_form.user
                
                user_account_form.user = request.user
                user_account_form.bank =  request.POST.get('bank_name')
                user_account_form.created_on = timezone.now()
                user_account_form.profile_updated = True
                user_account_form.save()

                messages.success(request, "User Details Updated Succesfully!!!")
                # user =  UserAccount.objects.get(user=request.user)
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                context['user'] = None
                context['form1'] = form1
                context['form2'] = form2
                # print form1.errors, form2.errors
                messages.error(request, 'Please make sure all fields are filled"')
                return render(request, 'general/profile.html', context)
        else:
            form1 = UserProfileForm(instance=request.user)
            form2 = UserAccountForm()
            context['user'] = None
            context['form1'] = form1
            context['form2'] = form2
        return render(request, 'general/profile.html', context)


@login_required
@user_passes_test(staff_check_for_gameplay, login_url='/backend/admin/all/events/', redirect_field_name=None)
def user_account(request):
    try:
        user = UserAccount.objects.get(user=request.user)
        # print user.referrer_count()
    except Exception as e:
        print "e", e
        user = None
    # referral = Referral.objects.get(referrer=request.user.last_name)
    balance = account_standing(request, request.user)
    game = Gameplay.objects.filter(user=user)
    if game:
        game_points = game.aggregate(Sum('game_points'))['game_points__sum']
        print game_points
    else:
        game_points = 0
    game_count = game.count()
    game_won = game.filter(decision="WIN")
    try:
        referral = Referral.objects.get(referal=request.user)
        # print referral.referrer_count()
    except Exception as e:
        print "e", e
        referral = None
    # query = request.GET.get('q')
    # if query:
    #     game = game.filter(
    #        Q(event__title__icontains=query)|
    #        Q(choice__icontains=query)|
    #        Q(status__icontains=query) |
    #        Q(decision__icontains=query)
    #        )
    # print "game-won", game_won
    # print referral.all_users()

    day_of_the_week = datetime.datetime.today().weekday()
    print "day of the week", day_of_the_week
    if day_of_the_week < 6:
        days = day_of_the_week + 1
    else:
        days = 0

    start_date = timezone.now() - timezone.timedelta(days=days)
    end_date = timezone.now() + timezone.timedelta(days=1)
    print start_date, end_date
    weekly_game_points = game.filter(date__range=(start_date, end_date)).aggregate(Sum('game_points'))[
        'game_points__sum']
    print "wgp", weekly_game_points
    return render(request, 'general/user_account.html',
                  {'user': user, 'balance': balance, 'game': game, 'game_won': game_won, 'game_count': game_count,
                   'referral': referral, 'game_points': game_points, 'wgp': weekly_game_points})


def about_us(request):
    return render(request, 'general/about_page.html', {})


def contact(request):
    return render(request, 'general/contact.html', {})


# def account_activation(request):
# 	if UserAccount.objects.filter(user=request.user).exists():
# 		print "I exist"
# 	
# 	return render(request, 'general/profile.html', {})


@login_required
def user_messages(request):
    context = {}
    try:
        user = UserAccount.objects.get(user=request.user)
    except Exception as e:
        print "e", e
        user = None
    if request.method == 'POST':
        rp = request.POST
        # print "rp: ", rp
        message_obj = MessageCenter.objects.create(
            subject=rp.get('subject'),
            message=rp.get('message'),
            user=request.user,
            new=True
        )
        message_obj.save()
        comment_obj = MessageCenterComment.objects.create(
            message=rp.get('message'),
            message_obj=message_obj,
            user=request.user)
        messages.success(request, 'Message sent successfully')
        return redirect(request.META['HTTP_REFERER'])
    else:
        context = {}
        messages = MessageCenter.objects.filter(user=request.user)
        query = request.GET.get('q')
        if query:
            new_messages = messages.filter((Q(subject__icontains=query) | Q(message__icontains=query)), new=True)
            replied_messages = messages.filter((Q(subject__icontains=query) | Q(message__icontains=query)),
                                               replied=True)
            archived_messages = messages.filter((Q(subject__icontains=query) | Q(message__icontains=query)),
                                                archive=True)
            # deleted_messages = messages.filter((Q(subject__icontains=query) | Q(message__icontains=query)), deleted=True)
        else:
            new_messages = messages.filter(new=True)
            replied_messages = messages.filter(replied=True)
            archived_messages = messages.filter(archive=True)
            # deleted_messages = messages.filter(deleted=True)
        comment_form = MessageCenterCommentForm()
        context['comment_form'] = comment_form
        context['new_messages'] = new_messages
        context['replied_messages'] = replied_messages
        context['archived_messages'] = archived_messages
        context['new_count'] = new_messages.count()
        context['replied_count'] = replied_messages.count()
        context['archived_count'] = archived_messages.count()
        context['user'] = user
        template_name = 'general/user_messages.html'
        return render(request, template_name, context)


@login_required
def user_comment(request):
    user_obj = request.user
    rp = request.POST
    print rp
    event_obj = Event.objects.get(pk=rp.get('event_pk'))
    print event_obj
    create_comment = Comments.objects.create(username=user_obj.username, text=rp.get('comment'), email=user_obj.email,
                                             event=event_obj, user=user_obj)
    messages.success(request, 'Message sent successfully')
    return redirect(request.META['HTTP_REFERER'])


@login_required
def view_comment_message(request):
    context = {}
    if request.method == 'POST':
        print 'rp:', request.POST
        message_obj = MessageCenter.objects.get(id=request.POST.get('msg_id'))
        comment_obj = MessageCenterComment.objects.create(
            message=request.POST.get('message'),
            message_obj=message_obj,
            image_obj=request.FILES.get('image_obj'),
            user=request.user)
        messages.success(request, 'Message sent successfully')
        return redirect(request.META['HTTP_REFERER'])

    else:
        print request.GET
        template_name = ""
        if request.GET.get('identifier') == 'comment':
            template_name = 'general_snippets/messageComments.html'
        else:
            template_name = 'general_snippets/viewMessages.html'
        message_id = request.GET.get('message_id')
        message_obj = MessageCenter.objects.get(id=message_id)
        print "msg_obj:", message_obj
        all_comments = message_obj.getComments()
        comment_form = MessageCenterCommentForm()
        context['comment_form'] = comment_form
        context['all_comments'] = all_comments
        context['message_id'] = message_id
        return render(request, template_name, context)


@login_required
def like_comments(request, action, pk):
    user_obj = request.user
    comment_obj = Comments.objects.get(pk=pk)
    likes_for_comment = comment_obj.get_likes()
    likes_for_comment_count = likes_for_comment.count()
    if likes_for_comment_count == 0:
        like_obj = Likes.objects.create(like=True, comment_obj=comment_obj, user=user_obj)
        return redirect(request.META['HTTP_REFERER'])
    else:
        pass
    for like in likes_for_comment:
        if like.user == request.user:
            like.delete()
        else:
            like_obj = Likes.objects.create(like=True, comment_obj=comment_obj, user=user_obj)
        return redirect(request.META['HTTP_REFERER'])
    return redirect(request.META['HTTP_REFERER'])


@csrf_exempt
def reply_comment(request):
    print "I got here"
    print "I got here too"
    reply = request.POST.get('reply')
    print reply
    comment_id = request.POST.get("comment_id")
    print comment_id
    reply_obj = Replies.objects.create(user=request.user, reply=reply)
    reply_obj.comment_obj = Comments.objects.get(id=comment_id)
    reply_obj.save()
    comment = Comments.objects.filter(id=comment_id)
    return render(request, 'general_snippets/reply.html', {'comment': comment})


def user_search(request, action):
    """
    trending filter from most played to least played event
    ending filter soon based on events ending in 24hours time
    newest filter based on events less than 24hrs of start date
    """

    context = {}
    # print action
    today = timezone.now().date()
    balance = account_standing(request, request.user)
    context['balance'] = balance
    current_time = timezone.now()
    if request.method == 'POST':
        # print request.POST
        print "i wanna search"
        events_all, new_datalist = get_simillar_values(request)
        rp = request.POST
        # print 'rp:',rp

        text = rp.get('query')
        category = rp.get('category')
        amount = rp.get('amount')
        try:
            days = int(rp.get('days'))
        except:
            days = rp.get('days')

        if category == "Category":
            category = ""
        if amount == "Amount to be Shared":
            amount = ""

        events_all = searchQuery(events_all, text, category, amount, days)

    else:
        if action == 'trending':
            events_all, new_datalist = get_simillar_values(request)
            # events_all = events_all.filter(counter = events_all.aggregate(Max('counter'))['counter__max'])
            events_all = events_all.filter(deleted=False, closed=False).order_by('-counter')
        elif action == 'ending':
            events_all, new_datalist = get_simillar_values(request)
            plus_24hrs_time = current_time + timezone.timedelta(hours=72)
            event_all = events_all.filter(end_date__range=(current_time, plus_24hrs_time))
            events_all = []
            for event in event_all:
                if event.end_date > today:
                    events_all.append(event)
                else:
                    now = datetime.datetime.now()  # To get current date and time
                    current_time = now.strftime("%I:%M %p")
                    dt = datetime.datetime.strptime(current_time, "%I:%M %p").time()
                    if event.end_time < dt:
                        events_all.append(event)

        elif action == "newest":
            events_all, new_datalist = get_simillar_values(request)
            minus_24hrs_time = current_time - timezone.timedelta(hours=24)
            events_all = events_all.filter(start_date__lt=minus_24hrs_time)
        else:
            events_all, new_datalist = get_simillar_values(request)

    marquee_events = getMarquee(request)

    all_events = paginate_list(request, events_all, 16)
    context['all_events'] = all_events
    context['datalist'] = new_datalist
    context['current_time'] = current_time
    context['today'] = today
    context['macquees'] = marquee_events
    template_name = 'general/events-page.html'
    return render(request, template_name, context)


def check_referrer(request):
    ref_num = request.GET.get('ref_num')
    try:
        user_account = UserAccount.objects.get(phone_number=ref_num)
        user_account = user_account.user.first_name + '' + user_account.user.last_name
        # print user_account
        return True
    except Exception as e:
        user_account = None
        status = "fail"
        return False
    # return JsonResponse({'status':status, 'user':user_account})


def staff_login_access(request):
    if check_cookie(request, 'admin_username'):
        admin_username = request.COOKIES['admin_username']
        request_by_user = get_user_requested(request, admin_username)
        # print "Requested by User :", request_by_user
        # print 'rp',request.POST
        if request_by_user.is_staff:
            if request.method == 'POST':
                query = request.POST.get('username')
                try:
                    if '@' in str(query):
                        u = User.objects.get(email=query)
                    else:
                        u = User.objects.get(username=query)
                except:
                    messages.warning(request, 'User does not exist')
                    return redirect('general:login')

                u = u.username
                # print "U :", u
                try:
                    # print "Got Here"
                    user = get_user_requested(request, u)
                    # print "User :",user
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    # user.backend = 'backends.EmailAuthBackEnd'

                    if user.is_staff:
                        messages.warning(request, "Access Denied!!!")
                        return redirect(reverse('general:login'))
                    else:
                        login(request, user)
                        # return redirect('/')
                        # request.session['admin_username'] = admin_username
                        return redirect(reverse('general:events'))
                except Exception as e:
                    messages.warning(request, "Access Denied!!!")
                    return redirect(reverse('general:login'))
            else:
                messages.warning(request, "Access Denied!!!")
                return redirect(reverse('general:login'))
        else:
            messages.warning(request, "Access Denied!!!")
            return redirect(reverse('general:login'))
    else:
        messages.warning(request, "Access Denied!!!")
        return redirect(reverse('general:login'))


@login_required
def get_play_event(request):
    context = {}
    event = Event.objects.get(pk=request.GET.get('event'))
    datalist = VendorClient.objects.filter(useraccount=request.user.useraccount).values_list('phone_number',
                                                                                             flat=True).distinct()
    new_datalist = ",".join([unicode(item) for item in datalist])
    template_name = 'general/vendorPlay.html'
    context['event'] = event
    context['datalist'] = new_datalist
    return render(request, template_name, context)


@login_required
def get_djp_event(request):
    context = {}
    dailyjackpot = DailyJackPot.objects.get(created_on_date=timezone.now().date())
    datalist = VendorClient.objects.filter(useraccount=request.user.useraccount).values_list('phone_number',
                                                                                             flat=True).distinct()
    new_datalist = ",".join([unicode(item) for item in datalist])
    template_name = 'general/vendorDJPPlay.html'
    context['event'] = dailyjackpot
    context['datalist'] = new_datalist
    return render(request, template_name, context)


@login_required
def tradingDetails(request, useracc_obj):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Trading Accounts.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['Event', 'Title', 'Prediction Date', 'Amount placed', 'choice', 'Status', 'Game Result', 'Amout won',
         'Amount Lost', 'Wallet Balance B/F', 'Wallet Current Balance'])

    games = Gameplay.objects.filter(user=useracc_obj)

    for game in games:
        if not game.status == 'OPEN':
            if game.amount_won == 0:
                amount_lost = game.amount
                game_result = 'Lost'
                amount_won = 0
                wallet_current_bal = float(game.current_ac_bal - game.amount)
            else:
                amount_lost = 0
                game_result = 'Win'
                amount_won = float(game.amount_won - game.amount)
                wallet_current_bal = float(game.current_ac_bal + amount_won)
        else:
            amount_lost = 0
            game_result = 'Ongoing'
            amount_won = 0
            wallet_current_bal = game.current_ac_bal
        balance_bf = float(wallet_current_bal + game.amount)
        writer.writerow(
            [game.event.event_id, game.event.title, game.date, game.amount, game.choice, game.status, game_result,
             amount_won, amount_lost, balance_bf, wallet_current_bal])
    return response


@login_required
def print_ticket(request, game_pk):
    game = Gameplay.objects.get(pk=game_pk)
    return render(request, 'general/ticket.html', {'game': game})


@login_required
@csrf_exempt
def print_selected_tickets(request):
    tickets = request.POST.get('tcket_numbers').split(',')
    dailyjackpot_entry = []
    for entry in tickets:
        dailyjackpot_entry.append(DailyJackpotEntries.objects.get(ticket_no=entry))
    return render(request, 'general/selectedtickets.html', {'game': dailyjackpot_entry})


@login_required
def print_djp_ticket(request, ticket_no):
    game = DailyJackpotEntries.objects.get(ticket_no=ticket_no)
    return render(request, 'general/ticket.html', {'game': game,'djp_vendor':'djp_vendor'})


def faq(request):
    context = {}
    return render(request, 'general/faq.html', context)


def disclaimer(request):
    context = {}
    return render(request, 'general/disclaimer.html', context)


def close_djp_client(request):
    print "I got here"
    event_id = request.GET.get('event_id')
    return redirect(reverse('ynladmin:close_djp', args=[event_id]))
