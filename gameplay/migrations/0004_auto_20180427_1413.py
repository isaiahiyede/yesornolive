# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0003_dailyjackpot_true_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyjackpot',
            name='true_value',
            field=models.BooleanField(default=False),
        ),
    ]
