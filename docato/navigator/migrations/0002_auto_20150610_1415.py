# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def fill_names(apps, schema_editor):
    Frame = apps.get_model('navigator', 'Frame')
    for frame in Frame.objects.all():
        if not frame.name:
            frame.name = '%s #%d' % (frame.type.name, frame.id)
            frame.save()


class Migration(migrations.Migration):

    dependencies = [
        ('navigator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='frame',
            name='name',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='baseslot',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_navigator.baseslot_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AlterField(
            model_name='baseslotvalue',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_navigator.baseslotvalue_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.RunPython(fill_names)
    ]
