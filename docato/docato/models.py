import logging, numpy as np, scipy.sparse
from lazy import lazy

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_delete, pre_delete
from django.db import IntegrityError
from django.dispatch import receiver
from django.conf import settings

from polymorphic.models import PolymorphicModel

from docato.utils import get_unique_model_name, try_get_reference, get_value, ValuesTypes

logger = logging.getLogger('common')

###############################################################################
############################### Projects ######################################
###############################################################################
class Project(models.Model):
    name = models.CharField(max_length = 255, verbose_name = _('Name'), unique = True)
    desc = models.CharField(max_length = 1000, verbose_name = _('Description'), blank = True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        permissions = (
                       ('can_access', _('Can view project contents')),
                       ('can_add_or_remove_subjects', _('Can add or remove subjects')),
                       )


class Subject(models.Model):
    project = models.ForeignKey(Project, related_name = 'subjects')
    name = models.CharField(max_length = 255,
                            verbose_name = _('Name'))
    timestamp = models.DateTimeField(verbose_name = _('Timestamp'))
    allow_sval_cascade_delete = models.BooleanField(default = False,
                                                    verbose_name = _('Allow delete slots (with cascade deletion of values)'))

    class Meta:
        unique_together = ('name', 'project')
        permissions = (
                       ('can_add_docs', _('Can upload documents')),
                       ('can_edit_docs', _('Can edit documents markup')),
                       ('can_edit_typesystem', _('Can edit typesystem')),
                       )

    def __unicode__(self):
        return self.name

    def embedded_frames_ids(self):
        return set(v.value.id for v in
                   ObjectSlotValue.objects.filter(frame__doc__subject = self)
                   if isinstance(v.slot, ObjectSlot) and v.slot.embedded and not v.value is None)
    
    def circular_dependency_exists(self):
        types_map = { t.id : idx for idx, t in enumerate(self.types.all()) }
        graph = np.zeros((len(types_map), len(types_map)))
        graph.fill(np.nan)
        for frametype in self.types.all():
            src_idx = types_map[frametype.id]
            for slot in frametype.slots.instance_of(ObjectSlot):
                if slot.embedded:
                    if slot.value_type == frametype:
                        return True
                    graph[src_idx, types_map[slot.value_type.id]] = 1
        paths = scipy.sparse.csgraph.floyd_warshall(graph)
        for i in xrange(len(types_map)):
            for j in xrange(i + 1, len(types_map)):
                if paths[i, j] != np.inf and paths[j, i] != np.inf:
                    return True
        return False


###############################################################################
################################# Search ######################################
###############################################################################
class SearchEngine(models.Model):
    name = models.CharField(max_length = 200, unique = True, verbose_name = _('Name'))
    template_name = models.CharField(max_length = 100, default = 'redirect.html')
    kwargs = models.CharField(max_length = 2000, blank = True)

    def __unicode__(self):
        return self.name


class SavedSearch(models.Model):
    user = models.ForeignKey(User, related_name = 'searches')
    subject = models.ForeignKey(Subject, related_name = 'searches')
    query = models.CharField(max_length = 300)

    def __unicode__(self):
        return self.query


###############################################################################
############################### Documents #####################################
###############################################################################
class Document(models.Model):
    class States:
        NOT_ANALYZED = 0
        ANALYZED = 1
        ERROR = -1
    STATE_CHOICES = (
                     (States.NOT_ANALYZED, _('Not analyzed yet')),
                     (States.ANALYZED, _('Analyzed successfully')),
                     (States.ERROR, _('Error occurred during analysis')),
                     )
    UPLOAD_TO = 'src'

    subject = models.ForeignKey(Subject, related_name = 'docs', verbose_name = _('Subject'))

    url = models.CharField(max_length = 4000, blank = True, verbose_name = _('URL'))
    title = models.CharField(max_length = 255, verbose_name = _('Title'))
    authors = models.CharField(max_length = 300, blank = True, verbose_name = _('Authors'))
    content_type = models.CharField(max_length = 100, blank = True, verbose_name = _('Content type'))

    source_file = models.FileField(upload_to = UPLOAD_TO, max_length = 300, blank = True, verbose_name = _('Source file'))
    converted_content = models.TextField(verbose_name = _('Content'))
    state = models.IntegerField(choices = STATE_CHOICES, default = States.NOT_ANALYZED, verbose_name = _('State'))

    load_time = models.DateTimeField(verbose_name = _('Load time'))

    @property
    def all_cues(self):
        return Cue.objects.filter(slot_value__frame__doc = self)

    def delete(self):
        for frame in self.frames.all():
            frame.delete()
        super(Document, self).delete()

    @property
    def embedded_frames_ids(self):
        return set(v.value.id for v in
                   ObjectSlotValue.objects.filter(frame__doc = self)
                   if isinstance(v.slot, ObjectSlot) and v.slot.embedded and not v.value is None)
    
    @property
    def standalone_frames(self):
        return self.frames.filter(~Q(id__in = self.embedded_frames_ids))

    def __unicode__(self):
        return self.title

    class Meta:
        unique_together = ('subject', 'title')


@receiver(post_delete, sender = Document)
def del_source_file(sender, instance = None, **kwargs):
    try:
        instance.source_file.delete(save = False)
    except Exception as ex:
        logger.error('Could not delete source file %s: %r' % (instance.source_file.url, ex))


###############################################################################
################################# Types #######################################
###############################################################################
class FrameType(models.Model):
    subject = models.ForeignKey(Subject, related_name = 'types')
    name = models.CharField(max_length = 200,
                            verbose_name = _('Name'))
    standalone = models.BooleanField(default = True,
                                     verbose_name = _('Standalone'))

    def can_delete(self):
        return (not self.instances.all().exists()) \
            and (not self.references.all().exists())

    def delete(self):
        for slot in self.slots.all():
            slot.delete()
        super(FrameType, self).delete()

    def clone(self):
        new_name = get_unique_model_name(self.subject.types.all(),
                                         _('Copy of ') + self.name)
        result = self.subject.types.create(name = new_name,
                                           standalone = self.standalone)
        for slot in self.slots.all():
            def_args = {
                        'frame_type' : result,
                        'name' : slot.name,
                        'description' : slot.description
                        }
            if isinstance(slot, ObjectSlot):
                def_args['value_type'] = slot.value_type
                def_args['embedded'] = slot.embedded
            else:
                def_args['default_value'] = slot.default_value
            type(slot).objects.create(**def_args)
        return result
    
    def get_new_slot_order(self):
        greatest_order = self.slots.order_by('-order').values('order').first()
        return 10 if greatest_order is None else (greatest_order['order'] + 10)

    class Meta:
        unique_together = ('subject', 'name')


class BaseSlot(PolymorphicModel):
    frame_type = models.ForeignKey(FrameType,
                                   related_name = 'slots')
    name = models.CharField(max_length = 255,
                            verbose_name = _('Name'))
    description = models.TextField(blank = True,
                                   default = _('Some description'))
    order = models.IntegerField(default = 0,
                                verbose_name = _('Order'))

    @property
    def is_list_slot(self):
        return False

    def ensure_objects_containment(self):
        for frame in self.frame_type.instances.all():
            if not frame.slots.filter(slot = self).exists():
                frame.create_slot_value(self)

    def delete(self, *args, **kwargs):
        if self.values.exists() and not self.frame_type.subject.allow_sval_cascade_delete:
            raise IntegrityError(_('Slot values cascade deletion is not allowed!'))
        for sval in self.values.all():
            sval.delete()
        super(BaseSlot, self).delete()

    def __unicode__(self):
        return '%s.%s' % (self.frame_type.name, self.name)
    
    class Meta:
        unique_together = ('frame_type', 'name')


class ClassLabelSlot(BaseSlot):
    template_name = 'docato/typesystem/slots/class_label.html'
    type_name = _('Class Label')
    
    default_value = models.CharField(max_length = 200,
                                     default = "-")


class ClassLabelListSlot(ClassLabelSlot):
    type_name = _('List of class labels')
    
    @property
    def is_list_slot(self):
        return True


class IntegerSlot(BaseSlot):
    template_name = 'docato/typesystem/slots/integer.html'
    type_name = _('Integer')

    default_value = models.IntegerField(default = 0)


class IntegerListSlot(IntegerSlot):
    type_name = _('List of integers')
    
    @property
    def is_list_slot(self):
        return True


class RealSlot(BaseSlot):
    template_name = 'docato/typesystem/slots/real.html'
    type_name = _('Real')

    default_value = models.FloatField(default = 0.0)


class RealListSlot(RealSlot):
    type_name = _('List of real numbers')
    
    @property
    def is_list_slot(self):
        return True


class ObjectSlot(BaseSlot):
    template_name = 'docato/typesystem/slots/object.html'
    value_type = models.ForeignKey(FrameType,
                                   related_name = 'references')
    embedded = models.BooleanField(default = True)
    type_name = _('Object')


class ObjectListSlot(ObjectSlot):
    type_name = _('List of objects')
    
    @property
    def is_list_slot(self):
        return True


###############################################################################
############################### Objects #######################################
###############################################################################
class Frame(models.Model):
    doc = models.ForeignKey(Document,
                            related_name = 'frames',
                            verbose_name = _('Document'))
    type = models.ForeignKey(FrameType,
                             related_name = 'instances')
    name = models.CharField(max_length = 200)

    def __unicode__(self):
        return "%s #%s" % (self.type, self.id)
    
    def create_slot_values(self):
        for slot_type in self.type.slots.all():
            self.create_slot_value(slot_type)
    
    def create_slot_value(self, slot_type, force = False):
        assert self.type.slots.filter(id = slot_type.id).exists()
        if slot_type.is_list_slot and not force:
            return None
        elif isinstance(slot_type, ClassLabelSlot):
            return ClassLabelSlotValue.objects.create(frame = self,
                                                      slot = slot_type,
                                                      value = slot_type.default_value)
        elif isinstance(slot_type, IntegerSlot):
            return IntegerSlotValue.objects.create(frame = self,
                                                   slot = slot_type,
                                                   value = slot_type.default_value)
        elif isinstance(slot_type, RealSlot):
            return RealSlotValue.objects.create(frame = self,
                                                slot = slot_type,
                                                value = slot_type.default_value)
        elif isinstance(slot_type, ObjectSlot):
            new_slot = ObjectSlotValue.objects.create(frame = self, slot = slot_type)
            if slot_type.embedded:
                new_slot.value = self.doc.frames.create(type = slot_type.value_type)
                new_slot.save()
                new_slot.value.reset_name()
                new_slot.value.create_slot_values()
            return new_slot

    def delete(self):
        for sval in self.slots.all():
            sval.delete()
        super(Frame, self).delete()

    def can_delete(self):
        return not self.references.all().exists()
    
    def is_standalone(self):
        return try_get_reference(self) is None

    def get_default_name(self):
        if not self.id:
            return self.type.name
        return '%s #%d' % (self.type.name, self.id)

    def reset_name(self, save = True):
        if not self.name:
            self.name = self.get_default_name()
            if save:
                self.save()

    @lazy
    def top_reference(self):
        frame, path = self.get_top_reference_path()
        if len(path) > 0:
            return frame, path[-1]
        else:
            return self, None

    def get_top_reference_path(self):
        path = []
        frame = self
        while True:
            ref_sval = try_get_reference(frame)
            if ref_sval is None:
                return frame, path
            path.append(ref_sval)
            frame = ref_sval.frame

    @lazy
    def color_id(self):
        return self.top_reference[0].id % settings.COLORS_NUMBER


class BaseSlotValue(PolymorphicModel):
    frame = models.ForeignKey(Frame,
                              related_name = 'slots')
    slot = models.ForeignKey(BaseSlot, related_name = 'values')
    
    @lazy
    def color_id(self):
        top_ref_sval = self.frame.top_reference[1]
        if top_ref_sval is None:
            return self.slot.id  % settings.COLORS_NUMBER
        else:
            return (self.slot.id ^ top_ref_sval.slot.id) % settings.COLORS_NUMBER


class SlotValueWithCue(BaseSlotValue):
    @property
    def full_text(self):
        return ' '.join(c['text'] for c in self.cues.all().values('text'))


class Cue(models.Model):
    slot_value = models.ForeignKey(SlotValueWithCue,
                                   related_name = 'cues')
    text = models.TextField()                       # cached value
    start = models.IntegerField()                   # serial number of the first token
    end = models.IntegerField()                     # serial number of the last token    


class ClassLabelSlotValue(SlotValueWithCue):
    value = models.CharField(max_length = 200, default = "-")
    
    def get_other_values(self):
        top_frame, sval_path = self.frame.get_top_reference_path()
        sval_path.reverse()
        slot_path = [sval.slot for sval in sval_path]
        slot_path.append(self.slot)
        result = set()
        for frame in top_frame.type.instances.all():
            if not frame.is_standalone():
                continue
            value_type, is_list, value = get_value(frame, slot_path)
            if value_type == ValuesTypes.NONE or value is None:
                continue
            if is_list:
                result.update(v for v, _ in value)
            else:
                result.add(value[0])
        return result


class IntegerSlotValue(SlotValueWithCue):
    value = models.IntegerField(default = 0)


class RealSlotValue(SlotValueWithCue):
    value = models.FloatField(default = 0.0)


class ObjectSlotValue(BaseSlotValue):
    value = models.ForeignKey(Frame,
                              related_name = 'references',
                              null = True,
                              default = None)

    def delete(self):
        if self.value and self.slot.embedded:
            val = self.value
            super(ObjectSlotValue, self).delete()
            val.delete()
        else:
            super(ObjectSlotValue, self).delete()
