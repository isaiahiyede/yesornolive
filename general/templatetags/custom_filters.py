from django import template
from django.template.defaultfilters import stringfilter
from general.models import UserAccount, MessageCenter, Event, Comments
from wallet.account_standing import account_standing_new
from django.contrib.auth.models import User
from gameplay.models import DailyJackpotEntries, Gameplay, Entries, DailyJackPot
# from export.models import *
import datetime
# import time
import pytz
from itertools import chain
from operator import attrgetter
# from datetime import datetime
from datetime import date, time
from django.utils import timezone

register = template.Library()

@register.simple_tag
def current_year():
    return date.today().year


@register.simple_tag
def check_last_comment_admin(request, value):
    get_match_obj = MessageCenter.objects.get(pk=value)
    all_comments = get_match_obj.getComments()
    # print all_comments
    last_comment = all_comments[len(all_comments) - 1]
    if not last_comment.user.is_staff:
        return "New Message"
    else:
        return all_comments.count()


@register.simple_tag
def check_last_comment_user(request, value):
    get_match_obj = MessageCenter.objects.get(pk=value)
    all_comments = get_match_obj.getComments()
    # print all_comments
    last_comment = all_comments[len(all_comments) - 1]
    if last_comment.user.is_staff:
        return "New Message"
    else:
        return all_comments.count()


@register.simple_tag
def djpCount(value):
    return DailyJackPot.objects.get(id=value).entries_count()


@register.simple_tag
def user_account_balance(user_pk):
    account_standing = account_standing_new(User.objects.get(pk=user_pk))
    return account_standing


@register.simple_tag
def getDjpCount(value1, value2):
    from datetime import datetime

    try:
        date = datetime.strptime(value2, "%b. %d, %Y").date()
    except:
        date = datetime.strptime(value2, "%B %d, %Y").date()

    return DailyJackpotEntries.objects.filter(user_obj=value1, date=date).count()


@register.simple_tag
def getCATCount(value1, value2, value3):
    return Gameplay.objects.filter(user=value1, date_played=value2, event__category=value3).count()


@register.simple_tag
def getCategoryCount(value):
    now = datetime.datetime.now()  # To get current date and time
    today = timezone.now().date()
    current_time = now.strftime("%I:%M %p")
    dt = datetime.datetime.strptime(current_time, "%I:%M %p").time()

    live_events = []

    category = Event.objects.filter(
        category=value,
        end_date__lte=today
    )

    for event in category:
        if event.end_date == today:
            if event.end_time < dt:
                live_events.append(event)
            else:
                pass
        else:
            live_events.append(event)

    # print "passed",len(live_events)
    return len(live_events)

# @register.simple_tag
# def getEventDetails(arg1, arg2):
#     event_obj = Event.objects.get(event_id=arg1)
#     # if arg2 == 'total_players':
#     #     value = event_obj.total_players()
#     # elif arg2 == 'total_winners':
#     #     value =  event_obj.total_winners()
#     # elif arg2 == 'total_losers':
#     #     value = event_obj.total_losers()
    return True

@register.simple_tag
def getLiveCategoryCount(value):
    now = datetime.datetime.now()  # To get current date and time
    today = timezone.now().date()
    current_time = now.strftime("%I:%M %p")
    dt = datetime.datetime.strptime(current_time, "%I:%M %p").time()

    live_events = []

    category = Event.objects.filter(
        deleted=False, 
        publish=True, 
        validated=True, 
        closed=False,
        category=value,
        end_date__gte=today
    )

    for event in category:
        if event.end_date == today:
            if event.end_time > dt:
                live_events.append(event)
            else:
                pass
        else:
            live_events.append(event)
    # print "live",len(live_events)
    return len(live_events)


@register.simple_tag
def getPercent(value, pk):
    # print "val",value
    if value == 0:
        percent_value = 0
        # print value
        return percent_value
    else:
        event_total_players = Event.objects.get(pk=pk)
        percent_value = round(((float(value) / float(event_total_players.total_players())) * 100), 2)
        return percent_value


@register.assignment_tag
def check_user_like(request, pk):
    comment_obj = Comments.objects.get(pk=pk)
    user_obj = request.user
    likes_for_comment = comment_obj.get_likes()
    for like in likes_for_comment:
        if like.user == request.user:
            return True
        else:
            return False


@register.filter(expects_localtime=True)
def is_today(value):
    # print "Value",value,type(value)
    if not isinstance(value, datetime.date):
        value = value.date()
    # print value <= date.today(), "is_today"
    return value <= date.today()


@register.filter(expects_localtime=True)
def is_past(value):
    if not isinstance(value, datetime.time):
        value = value.time()
    today = datetime.datetime.now()  # To get current date and time
    current_time = today.strftime("%H:%M:%S")  # to get current time in string format
    # print current_time, 'current time'
    dt = datetime.datetime.strptime(current_time,
                                    "%H:%M:%S").time()  # to convert datetime.datetime object to datetime.time object
    # print "dt", dt, value
    # print value <= dt
    return value <= dt


@register.filter(expects_localtime=True)
def today_date(value):
    # print "Value",value,type(value)
    if not isinstance(value, datetime.date):
        value = value.date()
    # print value <= date.today(), "is_today"
    if value < date.today():
        return False
    elif value == date.today():
        return True
    else:
        return True


@register.simple_tag
def getVendorPlayers(request, game):
    vendor_players = game.get_all_entries().filter(user_obj=request.user.useraccount).count()
    return vendor_players


@register.filter(expects_localtime=True)
def time_past(value):
    if not isinstance(value, datetime.time):
        value = value.time()
    today = datetime.datetime.now()  # To get current date and time
    current_time = today.strftime("%H:%M:%S")  # to get current time in string format
    dt = datetime.datetime.strptime(current_time,
                                    "%H:%M:%S").time()  # to convert datetime.datetime object to datetime.time object
    # print value >= dt
    return value > dt
