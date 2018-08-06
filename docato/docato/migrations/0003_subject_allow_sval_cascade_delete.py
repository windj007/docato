# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docato', '0002_auto_20150610_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='allow_sval_cascade_delete',
            field=models.BooleanField(default=False, verbose_name='Allow delete slots (with cascade deletion of values)'),
        ),
    ]
