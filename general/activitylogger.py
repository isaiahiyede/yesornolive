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


class ActivityLogger(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    action = models.CharField(max_length=200, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    obj_id = models.IntegerField(default=0)
    obj_model_name = models.CharField(max_length=100, null=True, blank=True)
    obj_description = models.CharField(max_length=1000, null=True)

    def __unicode__(self):
        return '%s' % self.user

    class Meta:
        verbose_name_plural = 'ActivityLogger'
        ordering = ['-created_on']
