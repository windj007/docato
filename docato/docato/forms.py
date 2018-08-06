import logging
from django import forms as djforms
from django.utils.translation import ugettext

import models

logger = logging.getLogger('common')

class NewProjectForm(djforms.ModelForm):
    class Meta:
        model = models.Project
        fields = ['name']


class NewSubjectForm(djforms.ModelForm):
    class Meta:
        model = models.Subject
        fields = ['name', 'project', 'timestamp']
        widgets = {
                   'project': djforms.HiddenInput(),
                   'timestamp': djforms.HiddenInput()
                   }


class AddDocumentForm(djforms.ModelForm):
    def clean(self):
        cleaned_data = super(AddDocumentForm, self).clean()
        if not (cleaned_data['title'] or cleaned_data['source_file']):
            raise djforms.ValidationError(_('You must specify URL or File or both'))
        return cleaned_data 

    class Meta:
        model = models.Document
        fields = ('title', 'url', 'source_file')
        widgets = {
                   'title': djforms.TextInput(attrs = { 'maxlength' : '255' }),
                   'url': djforms.TextInput(attrs = { 'maxlength' : '4000' }),
                   }


class NewFrameForm(djforms.Form):
    #parent_id = djforms.CharField(widget = djforms.HiddenInput)
    type = djforms.TypedChoiceField(coerce = int)
    
    def __init__(self, types, *args, **kwargs):
        super(NewFrameForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = types


# class AddSlotValueForm(djforms.ModelForm):
#     class Meta:
#         model = models.SlotValue
# 
# 
# class FindSlotValueForm(djforms.Form):
#     proj_id = djforms.IntegerField()
#     slot_id = djforms.IntegerField()
#     query = djforms.CharField(required = False)
