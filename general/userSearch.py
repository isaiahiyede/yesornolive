from django.http import HttpResponse
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.forms.models import model_to_dict
from general.models import UserAccount, Event
from django.contrib.auth.models import User
from operator import attrgetter
from django.core import serializers
from django.db.models import Q
from django.template.context import RequestContext
from django.db.models import Count
from django import template
from itertools import chain
import re
import hashlib
import random, datetime
import urllib
import time
import json
from django.utils import timezone
from django.db.models import Sum, Max



def searchQuery(events_all,text,category,amount,days):
    
    """ not very efficient but adaptable
    for now and subject to review """
    
    # print 'text,category,amount,days', text,category,amount,days
    if text != "" and category == "" and amount == "" and days == "":
        print "case a"
        events_all = events_all.filter(Q(title__icontains=text) | Q(bet_question__icontains=text))
        
    elif text != "" and category != "" and amount == "" and days == "":
        print "case b"
        events_all = events_all.filter((Q(title__icontains=text) | Q(bet_question__icontains=text)),
            category=category)
         
    elif text != "" and category != "" and amount != "" and days == "":
        print "case c"
        amount = str(amount).replace(',','').replace(' ','').split('-')
        events_all = events_all.filter((Q(title__icontains=text) | Q(bet_question__icontains=text)),
            category=category,total_amt__range=(amount[0],amount[1]))

    elif text != "" and category != "" and amount == "" and days != "":
        print "case d"
        current_time = timezone.now()
        in_x_days= current_time + timezone.timedelta(hours=(24*days))
        events_all = events_all.filter((Q(title__icontains=text) | Q(bet_question__icontains=text)),
            category=category, end_date__range=(current_time,in_x_days))

    elif text != "" and category == "" and amount == "" and days != "":
        print "case e"
        current_time = timezone.now()
        in_x_days= current_time + timezone.timedelta(hours=(24*days))
        events_all = events_all.filter((Q(title__icontains=text) | Q(bet_question__icontains=text)),
            end_date__range=(current_time,in_x_days))

    elif text != "" and category == "" and amount != "" and days != "":
        print "case f"
        amount = str(amount).replace(',','').replace(' ','').split('-')
        current_time = timezone.now()
        in_x_days= current_time + timezone.timedelta(hours=(24*days))
        events_all = events_all.filter((Q(title__icontains=text) | Q(bet_question__icontains=text)),
            total_amt__range=(amount[0],amount[1]), end_date__range=(current_time,in_x_days))

    elif text != "" and category != "" and amount == "" and days != "":
        print "case g"
        current_time = timezone.now()
        in_x_days= current_time + timezone.timedelta(hours=(24*days))
        events_all = events_all.filter((Q(title__icontains=text) | Q(bet_question__icontains=text)),
            category=category, end_date__range=(current_time,in_x_days))

    elif text != "" and category == "" and amount != "" and days == "":
        print "case h"
        amount = str(amount).replace(',','').replace(' ','').split('-')
        events_all = events_all.filter((Q(title__icontains=text) | Q(bet_question__icontains=text)),
            total_amt__range=(amount[0],amount[1]))

    elif text == "" and category != "" and amount == "" and days == "":
        print "case i"
        events_all = events_all.filter(category=category)

    elif text == "" and category != "" and amount != "" and days == "":
        print "case j"
        amount = str(amount).replace(',','').replace(' ','').split('-')
        events_all = events_all.filter(category=category, total_amt__range=(amount[0],amount[1]))
        
    elif text == "" and category != "" and amount == "" and days != "":
        print "case k"
        current_time = timezone.now()
        in_x_days= current_time + timezone.timedelta(hours=(24*days))
        events_all = events_all.filter(category=category, end_date__range=(current_time,in_x_days))

    elif text == "" and category == "" and amount != "" and days == "":
        print "case l"
        amount = str(amount).replace(',','').replace(' ','').split('-')
        events_all = events_all.filter(total_amt__range=(amount[0],amount[1]))
        
    elif text == "" and category != "" and amount != "" and days == "":
        print "case m"
        amount = str(amount).replace(',','').replace(' ','').split('-')
        events_all = events_all.filter(total_amt__range=(amount[0],amount[1]), category=category)
        
    elif text == "" and category == "" and amount != "" and days != "":
        print "case n"
        amount = str(amount).replace(',','').replace(' ','').split('-')
        current_time = timezone.now()
        in_x_days= current_time + timezone.timedelta(hours=(24*days))
        events_all = events_all.filter(total_amt__range=(amount[0],amount[1]),
                                       end_date__range=(current_time,in_x_days))

    elif text == "" and category == "" and amount == "" and days != "":
        print "case o" 
        current_time = timezone.now()
        # print current_time
        in_x_days= current_time + timezone.timedelta(hours=(24*days))
        # print in_x_days
        events_all = events_all.filter(end_date__range=(current_time,in_x_days))
        
    elif text == "" and category != "" and amount == "" and days != "":
        print "case p"
        current_time = timezone.now()
        in_x_days= current_time + timezone.timedelta(hours=(24*days))
        events_all = events_all.filter(category=category,end_date__range=(current_time,in_x_days))
     
    elif text == "" and category != "" and amount != "" and days != "":
        print "case q"
        amount = str(amount).replace(',','').replace(' ','').split('-')
        current_time = timezone.now()
        in_x_days= current_time + timezone.timedelta(hours=(24*days))
        events_all = events_all.filter(category=category,total_amt__range=(amount[0],amount[1]),
                                       end_date__range=(current_time,in_x_days))   
    else:
        print "case r"
        amount = str(amount).replace(',','').replace(' ','').split('-')
        current_time = timezone.now()
        in_x_days= current_time + timezone.timedelta(hours=(24*days))
        events_all = events_all.filter((Q(title__icontains=text) | Q(bet_question__icontains=text)),
            category=category,total_amt__range=(amount[0],amount[1]),
            end_date__range=(current_time,in_x_days))
           
    return events_all

  

    
    