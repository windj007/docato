import os, unidecode
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify

class SlugifiedFileSystemStorage(FileSystemStorage):
    def get_valid_name(self, name):
        fname, ext = os.path.splitext(name)
        encoded_name = u'%s.%s' % (self.recode_str(fname), self.recode_str(ext))
        return super(SlugifiedFileSystemStorage, self).get_valid_name(encoded_name)

    def recode_str(self, s):
        return slugify(unidecode.unidecode(s))
