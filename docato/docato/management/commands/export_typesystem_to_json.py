import json

from django.core.management.base import BaseCommand

from docato.models import Subject, ClassLabelSlot, \
    IntegerSlot, RealSlot, ObjectSlot


def get_slot_type_str(slot):
    if isinstance(slot, ClassLabelSlot):
        return 'str'
    elif isinstance(slot, IntegerSlot):
        return 'int'
    elif isinstance(slot, RealSlot):
        return 'float'
    else:
        if slot.embedded:
            return 'embedded'
        else:
            return 'ref'



def get_slot_json(slot):
    result = dict(id = slot.id,
                  name = slot.name,
                  description = slot.description,
                  order = slot.order,
                  is_list = slot.is_list_slot,
                  type = get_slot_type_str(slot))
    if hasattr(slot, 'default_value'):
        result['default_value'] = slot.default_value
    if hasattr(slot, 'value_type'):
        result['value_type_name'] = slot.value_type.name if slot.value_type else None
    return result
                

def get_frametype_json(ft):
    return dict(id = ft.id,
                name = ft.name,
                standalone = ft.standalone,
                slots = map(get_slot_json, ft.slots.all()))


class Command(BaseCommand):
    args = 'subject'
    help = 'Export typesystem to portable JSON file'

    def handle(self, *args, **options):
        subject = Subject.objects.get(id = args[0])
        types = [get_frametype_json(f) for f in subject.types.all()]
        print json.dumps({ 'types' : types }, indent = 4)
