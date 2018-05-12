# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0002_auto_20180427_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='special_user_test_2',
            field=models.BooleanField(default=False),
        ),
    ]
