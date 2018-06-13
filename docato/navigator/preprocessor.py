import os
from django.conf import settings
import preprocessing


class Preprocessor(object):
    def __call__(self, doc, window_width = 800):
        src_filepath = os.path.join(settings.MEDIA_ROOT, doc.source_file.name)
        preproc = preprocessing.get_preprocessor_by_extension(doc.content_type)
        formatted_html, plain_text = preproc.parse(src_filepath, window_width)
        doc.converted_content = preprocessing.align.align_text(plain_text, formatted_html)
        doc.save()
