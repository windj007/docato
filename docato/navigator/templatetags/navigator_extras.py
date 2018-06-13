from django import template

register = template.Library()

_OCC_WRAP_LEFT = '<span class="occurrence"><a name="occ_%s">'
_OCC_WRAP_RIGHT = '</a></span>'

@register.filter
def render_body(sentence):
    result = ''
    prev_end = 0
    for focc in sentence.features.order_by('value_begin', 'value_end'):
        result += sentence.text[prev_end:focc.value_begin] + \
            (_OCC_WRAP_LEFT % focc.id) + \
            sentence.text[focc.value_begin:focc.value_end] + \
            _OCC_WRAP_RIGHT
        prev_end = focc.value_end
    result += sentence.text[prev_end:]
    return result
