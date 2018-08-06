# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def fill_orders(apps, schema_editor):
    FrameType = apps.get_model('docato', 'FrameType')
    for frametype in FrameType.objects.all():
        for i, slot in enumerate(frametype.slots.all().order_by('name')):
            slot.order = (i + 1) * 10
            slot.save()


class Migration(migrations.Migration):

    dependencies = [
        ('docato', '0003_subject_allow_sval_cascade_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseslot',
            name='order',
            field=models.IntegerField(default=0, verbose_name='Order'),
        ),
        migrations.RunPython(fill_orders)
    ]
