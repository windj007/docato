import navigator.models
from django.conf import settings


def get_unique_model_name(queryset, prefix, name_field = 'name'):
    i  = 1
    while True:
        name = "%s %d" % (prefix, i)
        if not queryset.filter(**{ name_field : name }).exists():
            return name
        i += 1


def iterate_over_slots(frametype):
    for slot in frametype.slots.all():
        if isinstance(slot, navigator.models.ObjectSlot) and slot.embedded:
            for nested in iterate_over_slots(slot.value_type):
                yield [slot] + nested
        else:
            yield [slot]


def iterate_over_frametypes(subject):
    for frametype in subject.types.filter(standalone = True):
        for slots in iterate_over_slots(frametype):
            yield (frametype, slots)


class ValuesTypes:
    NONE = "none"
    REF = "ref"
    SIMPLE = "simple"
    REF_LIST = "ref_list"
    SIMPLE_LIST = "simple_list"


def get_value(frame, slots):
    '''
        Collect values situated at the specified path (slots list) starting from the specified frame.
        Always returns a triplet (value_type, is_list, value).
        value_type is an element of ValuesTypes.
        is_list is True if the third element of the triplet (value) is a list of atomic values
        value can be None, list of elements, the value itself, or a list of tuples <atomic_value, full_text> 
    '''
    for i, slot in enumerate(slots):
        if frame == None:
            return (ValuesTypes.NONE, False, None)
        if slot.is_list_slot:
            slot_values = frame.slots.filter(slot = slot)
            if isinstance(slot, navigator.models.ObjectSlot):
                if slot.embedded:
                    res_value_type = None
                    values = []
                    full_texts = []
                    new_slots = slots[i+1:]
                    if slot_values:
                        for sval in slot_values:
                            value_type, is_list, value = get_value(sval.value, new_slots)
                            res_value_type = value_type
                            if is_list:
                                values.extend(value)
                            else:
                                values.append(value)
                        return (res_value_type, True, values)
                    else:
                        return (ValuesTypes.NONE, True, None)
                else:
                    values = []
                    for sval in slot_values:
                        values.append(sval.value)
                        full_texts.append(sval.full_text)
                    return (ValuesTypes.REF, True, values)
            else:
                values = []
                full_texts = []
                for sval in slot_values:
                    values.append(sval.value)
                    full_texts.append(sval.full_text)
                return (ValuesTypes.SIMPLE, True, zip(values, full_texts))
        else:
            sval = frame.slots.get(slot = slot)
            if isinstance(slot, navigator.models.ObjectSlot):
                if slot.embedded:
                    frame = sval.value
                else:
                    return (ValuesTypes.REF, False, sval.value)
            else:
                return (ValuesTypes.SIMPLE, False, (sval.value, sval.full_text))
    return (ValuesTypes.NONE, False, None)


def iterate_over_slot_values(frame):
    for frametype, slots in iterate_over_frametypes(frame.type.subject):
        if frametype == frame.type:
            result = get_value(frame, slots)
            yield result
        else:
            yield (ValuesTypes.NONE, False, None)


def try_get_reference(frame):
    for ref_sval in frame.references.all():
        if ref_sval.slot.embedded:
            return ref_sval
    return None


def get_sval_color_style(sval):
    return 'background-color-%d border-color-%d' % (sval.color_id,
                                                    sval.frame.color_id)

def get_sval_color_style_for_tree(sval):
    if isinstance(sval, navigator.models.ObjectSlotValue):
        return "" 
    return get_sval_color_style(sval)


def get_frame_color_style_for_tree(frame):
    if not try_get_reference(frame) is None:
        return ""
    return 'border-color-%d' % frame.color_id

