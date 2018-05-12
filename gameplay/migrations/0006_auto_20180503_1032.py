# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0005_auto_20180427_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyjackpot',
            name='Dtickets',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailyjackpot',
            name='start',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
