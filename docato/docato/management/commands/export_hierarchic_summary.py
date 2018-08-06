import json, os
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings

from docato.models import Subject, SlotValueWithCue, ClassLabelSlot, IntegerSlot, RealSlot, Document
from docato.preprocessing.common import get_tokens_from_str, align_tokens_to_text
from docato.preprocessing.pdf import get_plain_text
from docato.preprocessing import get_preprocessor_by_extension


class Command(BaseCommand):
    help = 'Export summary table of the specified subject to CSV file'

    option_list = BaseCommand.option_list + (
        make_option('--subject_id',
                    type = int,
                    help = 'Which subject to export'),
        make_option('--root_frametype',
                    type = int,
                    help = 'Which object type to start traversal from'),
        make_option('--reprocess',  
                    action = 'store_true',
                    dest = 'reprocess',
                    default = False,
                    help = 'Whether to convert documents from scratch or use stored converted_content')
    )


    def handle(self, *args, **options):
        subject = Subject.objects.get(id = options['subject_id'])
        root_frametype = subject.types.get(id = options['root_frametype'])
        embedded_frames = subject.embedded_frames_ids()
        result = {
                  'docs' : [
                            {
                             'id' : doc.id,
                             'title' : doc.title,
                             'text' : txt,
                             'tokens' : list(align_tokens_to_text(txt, tokens)),
                             'frames' : [
                                         frame_obj
                                         for frame in doc.frames.filter(type = root_frametype)
                                         for frame_obj, filled_slots_number in [self._serialize_frame(frame)]
                                         if not frame.id in embedded_frames and filled_slots_number > 0
                                         ]
                             }
                            for doc in subject.docs.all()
                            if doc.state >= Document.States.ANALYZED
                            for txt, tokens in [[get_plain_text(doc.converted_content) \
                                                 if not options['reprocess'] \
                                                 else get_preprocessor_by_extension(doc.content_type).parse(os.path.join(settings.MEDIA_ROOT,
                                                                                                                         doc.source_file.name),
                                                                                                            1000)[1],
                                                 get_tokens_from_str(doc.converted_content)]]
                            ]
                  }
        print json.dumps(result, indent = 4)

    def _serialize_frame(self, frame):
        slots = {}
        filled_slots_number = 0
        for slot_value in frame.slots.all():
            slot_obj, cur_filled_slots_num = self._serialize_slot_value(slot_value)
            slots[slot_value.slot.name] = slot_obj
            filled_slots_number += cur_filled_slots_num
        return ({
                 'id' : frame.id,
                 'type' : frame.type.name,
                 'name' : frame.name,
                 'slots' : slots
                 },
                filled_slots_number)

    def _serialize_slot_value(self, slot_value):
        if isinstance(slot_value, SlotValueWithCue):
            if slot_value.slot.is_list_slot:
                value = [sval.value for sval
                         in slot_value.frame.slots.filter(slot = slot_value.slot)
                         if sval.full_text or sval.value != sval.slot.default_value]
                val_number = len(value)
                cues = [{ 'text' : c.text, 'start' : c.start, 'end' : c.end }
                        for sv in slot_value.frame.slots.filter(slot = slot_value.slot)
                        for c in sv.cues.all()]
                
            else:
                value = slot_value.value if slot_value.full_text or slot_value.value != slot_value.slot.default_value else None
                val_number = 1 if not value is None else 0
                cues = [{ 'text' : c.text, 'start' : c.start, 'end' : c.end }
                        for c in slot_value.cues.all()]
            default = slot_value.slot.default_value
        else:
            cues = []
            if slot_value.slot.embedded:
                if slot_value.slot.is_list_slot: 
                    value, val_numbers = zip(*[self._serialize_frame(sval.value) for sval
                                               in slot_value.frame.slots.filter(slot = slot_value.slot)])
                    val_number = sum(val_numbers)
                else:
                    value, val_number = self._serialize_frame(slot_value.value)
            else:
                if slot_value.slot.is_list_slot: 
                    value = [sval.value.id for sval
                             in slot_value.frame.slots.filter(slot = slot_value.slot)]
                    val_number = len(value)
                else:
                    if slot_value.value is None:
                        value = None
                        val_number = 0
                    else:
                        value = slot_value.value.id
                        val_number = 1
            default = None
        return ({
                 'type' : self._get_slot_type_name(slot_value),
                 'is_list' : slot_value.slot.is_list_slot,
                 'value' : value,
                 'default' : default,
                 'cues' : cues
                 },
                val_number)

    def _get_slot_type_name(self, slot_value):
        if isinstance(slot_value.slot, ClassLabelSlot):
            return 'str'
        elif isinstance(slot_value.slot, IntegerSlot):
            return 'int'
        elif isinstance(slot_value.slot, RealSlot):
            return 'float'
        elif slot_value.slot.embedded:
            return 'embedded'
        else:
            return 'ref'

