# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0002_auto_20180427_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyjackpot',
            name='true_value',
            field=models.BooleanField(default=True),
        ),
    ]
