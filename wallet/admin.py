# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import Bank, Betpayments


# Register your models here.


class BankAdmin(admin.ModelAdmin):
    list_display = ('username', 'ref_no', 'status',)
    list_filter = ['status', 'bank', ]
    search_fields = ['ref_no', ]

    def username(self, obj):
        return '%s %s' % (obj.user.first_name, obj.user.last_name)
# username.admin_order_field = 'user__first_name'


admin.site.register(Bank, BankAdmin)
admin.site.register(Betpayments)
