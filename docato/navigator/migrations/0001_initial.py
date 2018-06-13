# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseSlot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('description', models.TextField(default='Some description', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BaseSlotValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClassLabelSlot',
            fields=[
                ('baseslot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.BaseSlot')),
                ('default_value', models.CharField(default=b'-', max_length=200)),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.baseslot',),
        ),
        migrations.CreateModel(
            name='ClassLabelListSlot',
            fields=[
                ('classlabelslot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.ClassLabelSlot')),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.classlabelslot',),
        ),
        migrations.CreateModel(
            name='Cue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('start', models.IntegerField()),
                ('end', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=4000, verbose_name='URL', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('authors', models.CharField(max_length=300, verbose_name='Authors', blank=True)),
                ('content_type', models.CharField(max_length=100, verbose_name='Content type', blank=True)),
                ('source_file', models.FileField(upload_to=b'src', max_length=300, verbose_name='Source file', blank=True)),
                ('converted_content', models.TextField(verbose_name='Content')),
                ('state', models.IntegerField(default=0, verbose_name='State', choices=[(0, 'Not analyzed yet'), (1, 'Analyzed successfully'), (-1, 'Error occurred during analysis')])),
                ('load_time', models.DateTimeField(verbose_name='Load time')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Frame',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('doc', models.ForeignKey(related_name='frames', verbose_name='Document', to='navigator.Document')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FrameType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='Name')),
                ('standalone', models.BooleanField(default=True, verbose_name='Standalone')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IntegerSlot',
            fields=[
                ('baseslot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.BaseSlot')),
                ('default_value', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.baseslot',),
        ),
        migrations.CreateModel(
            name='IntegerListSlot',
            fields=[
                ('integerslot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.IntegerSlot')),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.integerslot',),
        ),
        migrations.CreateModel(
            name='ObjectSlot',
            fields=[
                ('baseslot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.BaseSlot')),
                ('embedded', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.baseslot',),
        ),
        migrations.CreateModel(
            name='ObjectListSlot',
            fields=[
                ('objectslot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.ObjectSlot')),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.objectslot',),
        ),
        migrations.CreateModel(
            name='ObjectSlotValue',
            fields=[
                ('baseslotvalue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.BaseSlotValue')),
                ('value', models.ForeignKey(related_name='references', default=None, to='navigator.Frame', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.baseslotvalue',),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Name')),
                ('desc', models.CharField(max_length=1000, verbose_name='Description', blank=True)),
            ],
            options={
                'permissions': (('can_access', 'Can view project contents'), ('can_add_or_remove_subjects', 'Can add or remove subjects')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RealSlot',
            fields=[
                ('baseslot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.BaseSlot')),
                ('default_value', models.FloatField(default=0.0)),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.baseslot',),
        ),
        migrations.CreateModel(
            name='RealListSlot',
            fields=[
                ('realslot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.RealSlot')),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.realslot',),
        ),
        migrations.CreateModel(
            name='SavedSearch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('query', models.CharField(max_length=300)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SearchEngine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='Name')),
                ('template_name', models.CharField(default=b'redirect.html', max_length=100)),
                ('kwargs', models.CharField(max_length=2000, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SlotValueWithCue',
            fields=[
                ('baseslotvalue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.BaseSlotValue')),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.baseslotvalue',),
        ),
        migrations.CreateModel(
            name='RealSlotValue',
            fields=[
                ('slotvaluewithcue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.SlotValueWithCue')),
                ('value', models.FloatField(default=0.0)),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.slotvaluewithcue',),
        ),
        migrations.CreateModel(
            name='IntegerSlotValue',
            fields=[
                ('slotvaluewithcue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.SlotValueWithCue')),
                ('value', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.slotvaluewithcue',),
        ),
        migrations.CreateModel(
            name='ClassLabelSlotValue',
            fields=[
                ('slotvaluewithcue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='navigator.SlotValueWithCue')),
                ('value', models.CharField(default=b'-', max_length=200)),
            ],
            options={
                'abstract': False,
            },
            bases=('navigator.slotvaluewithcue',),
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('timestamp', models.DateTimeField(verbose_name='Timestamp')),
                ('project', models.ForeignKey(related_name='subjects', to='navigator.Project')),
            ],
            options={
                'permissions': (('can_add_docs', 'Can upload documents'), ('can_edit_docs', 'Can edit documents markup'), ('can_edit_typesystem', 'Can edit typesystem')),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='subject',
            unique_together=set([('name', 'project')]),
        ),
        migrations.AddField(
            model_name='savedsearch',
            name='subject',
            field=models.ForeignKey(related_name='searches', to='navigator.Subject'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='savedsearch',
            name='user',
            field=models.ForeignKey(related_name='searches', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='objectslot',
            name='value_type',
            field=models.ForeignKey(related_name='references', to='navigator.FrameType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='frametype',
            name='subject',
            field=models.ForeignKey(related_name='types', to='navigator.Subject'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='frame',
            name='type',
            field=models.ForeignKey(related_name='instances', to='navigator.FrameType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='subject',
            field=models.ForeignKey(related_name='docs', verbose_name='Subject', to='navigator.Subject'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together=set([('subject', 'title')]),
        ),
        migrations.AddField(
            model_name='cue',
            name='slot_value',
            field=models.ForeignKey(related_name='cues', to='navigator.SlotValueWithCue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='baseslotvalue',
            name='frame',
            field=models.ForeignKey(related_name='slots', to='navigator.Frame'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='baseslotvalue',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_navigator.baseslotvalue_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='baseslotvalue',
            name='slot',
            field=models.ForeignKey(related_name='values', to='navigator.BaseSlot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='baseslot',
            name='frame_type',
            field=models.ForeignKey(related_name='slots', to='navigator.FrameType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='baseslot',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_navigator.baseslot_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='baseslot',
            unique_together=set([('frame_type', 'name')]),
        ),
    ]
