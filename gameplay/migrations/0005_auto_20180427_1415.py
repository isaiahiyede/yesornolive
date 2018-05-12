# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0004_auto_20180427_1413'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailyjackpot',
            name='true_value',
        ),
        migrations.AddField(
            model_name='dailyjackpotentries',
            name='true_value',
            field=models.BooleanField(default=False),
        ),
    ]
