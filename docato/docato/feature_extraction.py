import lxml.html, re
from django.conf import settings
from django.core.urlresolvers import reverse
from cStringIO import StringIO
from docato.utils import get_sval_color_style


def get_doc_text(doc):
    tree = lxml.html.parse(StringIO(doc.converted_content))
    return ' '.join(tree.xpath('/html/body/div[@id="page-container"]//text()'))


def highlight_features(doc):
    tree = lxml.html.parse(StringIO(doc.converted_content))
    head = tree.xpath('/html/head')[0]
    head.append(head.makeelement('link',
                                 attrib = {
                                           'rel' : 'stylesheet',
                                           'type' : 'text/css',
                                           'href' : settings.STATIC_URL + 'docato/css/converted.css'
                                           }))
    head.append(head.makeelement('link',
                                 attrib = {
                                           'rel' : 'stylesheet',
                                           'type' : 'text/css',
                                           'href' : settings.STATIC_URL + 'docato/css/background-colors.css'
                                           }))
    head.append(head.makeelement('link',
                                 attrib = {
                                           'rel' : 'stylesheet',
                                           'type' : 'text/css',
                                           'href' : settings.STATIC_URL + 'docato/css/border-colors.css'
                                           }))
    head.append(head.makeelement('link',
                                 attrib = {
                                           'rel' : 'stylesheet',
                                           'type' : 'text/css',
                                           'href' : settings.STATIC_URL + 'docato/css/contextMenu.css'
                                           }))
    head.append(head.makeelement('script',
                                 attrib = {
                                           'type' : 'text/javascript',
                                           'src' : settings.STATIC_URL + 'docato/js/jquery-1.9.1.js'
                                           }))
    head.append(head.makeelement('script',
                                 attrib = {
                                           'type' : 'text/javascript',
                                           'src' : settings.STATIC_URL + 'docato/js/contextMenu.min.js'
                                           }))
    head.append(head.makeelement('script',
                                 attrib = {
                                           'type' : 'text/javascript',
                                           'src' : reverse('django.views.i18n.javascript_catalog')
                                           }))
    head.append(head.makeelement('script',
                                 attrib = {
                                           'type' : 'text/javascript',
                                           'src' : settings.STATIC_URL + 'docato/js/converted.js'
                                           }))
    for cue in doc.all_cues:
        for n in tree.xpath('//span[@data-token-id >= %i and @data-token-id <= %i]' % (cue.start, cue.end)):
            n.attrib['class'] = n.attrib['class'] + (' ' if n.attrib['class'] else '') + get_sval_color_style(cue.slot_value)
            n.attrib['data-cue-id'] = str(cue.id)
    return lxml.html.tostring(tree)


def try_parse(regex, text, cast, default):
    parsed = re.search(regex, text)
    if parsed:
        return cast(parsed.group(1))
    return default


INT_RE = re.compile(r'(\d+)')
def try_extract_int(text, default = 0):
    return try_parse(INT_RE, text, int, default)

    
REAL_RE = re.compile(r'(\d+(\.\d*)?)')
def try_extract_real(text, default = 0.0):
    return try_parse(INT_RE, text, float, default)


def extract_features(doc):
    pass
#     words = list(nltk.wordpunct_tokenize(get_doc_text(doc)))
#     fset = doc.feature_sets.create(name = 'Set 1')
#     for feat in Feature.objects.all():
#         for _ in xrange(random.randint(0, 3)):
#             num_words = random.randint(1, min(3, len(words)))
#             first_word = random.randint(0, len(words) - num_words)
#             fset.features.create(feature = feat,
#                                  value_begin = first_word,
#                                  value_end = first_word + num_words,
#                                  value = ' '.join(words[first_word:first_word+num_words]) )
