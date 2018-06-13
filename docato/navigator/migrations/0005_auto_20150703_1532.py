# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('navigator', '0004_baseslot_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frametype',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name'),
        ),
        migrations.AlterUniqueTogether(
            name='frametype',
            unique_together=set([('subject', 'name')]),
        ),
    ]
