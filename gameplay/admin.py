# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import Gameplay, WeeklyJackPot, Entries, DailyJackPot, DailyJackpotEntries


# Register your models here.

class GameplayAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'date', 'amount', 'status')


class WeeklyJackPotAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'grand_prize', 'top_winner',)


class EntriesAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'useracc_obj', 'client_code', 'unique_ref_no', 'winner', 'consolation', 'amount')


class DailyJackPotAdmin(admin.ModelAdmin):
    list_display = ('question', 'grand_prize', 'top_winner', 'consolation_winners', 'created_on_date', 'amount')


class DailyJackpotEntriesAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'user_obj', 'vendor_code', 'choice', 'unique_ref_no', 'ticket_no', 'amount', 'winner', 'consolation')


admin.site.register(Gameplay, GameplayAdmin)
admin.site.register(WeeklyJackPot, WeeklyJackPotAdmin)
admin.site.register(Entries, EntriesAdmin)
admin.site.register(DailyJackPot, DailyJackPotAdmin)
admin.site.register(DailyJackpotEntries, DailyJackpotEntriesAdmin)
