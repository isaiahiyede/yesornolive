# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyjackpotentries',
            name='user_email',
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='dailyjackpotentries',
            name='user_first_name',
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='dailyjackpotentries',
            name='user_last_name',
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
    ]
