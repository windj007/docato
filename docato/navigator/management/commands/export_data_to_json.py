import json, base64, traceback, os
from optparse import make_option 

from django.core.management.base import BaseCommand
from django.conf import settings

from navigator.models import Subject, SlotValueWithCue, Document
from navigator.preprocessing.common import get_tokens_from_str, align_tokens_to_text
from navigator.preprocessing.pdf import get_plain_text
from navigator.preprocessing import get_preprocessor_by_extension


class Command(BaseCommand):
    args = ''
    help = 'Export summary table of the specified subject to CSV file'

    option_list = BaseCommand.option_list + (
        make_option('--subject_id',
                    type = int,
                    help = 'Which subject to export'),
        make_option('--out_file',
                    type = str,
                    help = 'Name or prefix of file to store data into'),
        make_option('--reprocess',
                    action = 'store_true',
                    dest = 'reprocess',
                    default = False,
                    help = 'Whether to convert documents from scratch or use stored converted_content'),
        make_option('--separate_files',
                    action = 'store_true',
                    dest = 'separate_files',
                    default = False,
                    help = 'Whether to store each document info a separate JSON-file or join them into a big one')
    )

    def handle(self, *args, **options):
        subject = Subject.objects.get(id = options['subject_id'])
        doc_gen = ({
                    'id' : doc.id,
                    'url' : doc.url.encode('utf8'),
                    'title' : doc.title.encode('utf8'),
                    'authors' : doc.authors.encode('utf8'),
                    'plain_text' : txt.encode('utf8'),
                    'source_file' : self._get_doc_content(doc),
                    'converted_content' : self._get_formatted_html(doc),
                    'content_type' : doc.content_type,
                    'state' : doc.state,
                    'load_time' : doc.load_time.isoformat(),
                    'tokens' : list(align_tokens_to_text(txt, tokens)),
                    'frames' : self._export_doc_frames(doc)
                    }
                   for doc in subject.docs.all()
                   if doc.state >= Document.States.ANALYZED
                   for txt, tokens in [[get_plain_text(doc.converted_content) \
                                        if not options['reprocess'] \
                                        else get_preprocessor_by_extension(doc.content_type).parse(os.path.join(settings.MEDIA_ROOT,
                                                                                                                doc.source_file.name),
                                                                                                   1000)[1],
                                        get_tokens_from_str(doc.converted_content)]])
        if options['separate_files']:
            for doc in doc_gen:
                with open(options['out_file'] + str(doc['id']) + '.js', 'w') as f:
                    json.dump(dict(docs = [doc]), f, encoding = 'utf8', indent = 4)
        else:
            with open(options['out_file'], 'w') as f:
                json.dump(dict(docs = list(doc_gen)), f, encoding = 'utf8', indent = 4)


    def _get_doc_content(self, doc):
        try:
            with doc.source_file as f:
                return {
                        'name' : doc.source_file.name,
                        'content' : base64.encodestring(f.read())
                        }
        except:
            traceback.print_exc()
            return None

    def _get_formatted_html(self, doc):
        return base64.encodestring(doc.converted_content)

    def _export_doc_frames(self, doc):
        return map(self._serialize_frame, doc.frames.all())

    def _serialize_frame(self, frame):
        return {
                'id' : frame.id,
                'type' : frame.type.name,
                'name' : frame.name,
                'slots' : map(self._serialize_slot_value, frame.slots.all())
                }

    def _serialize_slot_value(self, slot_value):
        if isinstance(slot_value, SlotValueWithCue):
            norm_value = slot_value.value
        else:
            norm_value = slot_value.value.id if slot_value.value else None
        return {
                'name' : slot_value.slot.name,
                'value' : norm_value,
                'cues' : [{ 'start' : cue.start, 'end' : cue.end }
                          for cue in slot_value.cues.all()] if hasattr(slot_value, 'cues') else []
                }
