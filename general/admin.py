# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import UserAccount, LeaderBoard, Event, Comments, MessageCenter, MessageCenterComment, Likes, Referral, VendorClient, \
    AddressInfo, TradingAccount, WalletBalances
from activitylogger import ActivityLogger


# Register your models here.


# Register your models here.
class EventAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'publish', 'validated', 'category', 'trending', 'event_id',)
    search_fields = ['author__email', 'title', 'publish', 'validated', 'category', 'trending', 'event_id' ]


class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'referred_by', 'created_on')
    search_fields = ['user__email',]


class ActivityLoggerAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'created_on', 'obj_id', 'obj_model_name', 'obj_description')
    search_fields = ['user__email', 'action', 'obj_id', 'obj_description', ]


class WalletBalancesAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_created','description','balance_bf','amount','current_bal',)
    search_fields = ['user', 'amount', ]


class LeaderBoardAdmin(admin.ModelAdmin):
    list_display = ('user_obj', 'start_date','end_date', 'total_points',)
    search_fields = ['user_obj', 'start_date','end_date', 'total_points']


admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Comments)
admin.site.register(MessageCenterComment)
admin.site.register(MessageCenter)
admin.site.register(Likes)
admin.site.register(LeaderBoard, LeaderBoardAdmin)
admin.site.register(Referral)
admin.site.register(ActivityLogger, ActivityLoggerAdmin)
admin.site.register(VendorClient)
admin.site.register(AddressInfo)
admin.site.register(TradingAccount)
admin.site.register(WalletBalances, WalletBalancesAdmin)
