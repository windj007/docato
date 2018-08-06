from django.utils.translation import ugettext as _
import django_tables2 as djtab2

class ProjectsTable(djtab2.Table):
    select = djtab2.CheckBoxColumn(accessor = 'id', orderable = False)
    name = djtab2.Column()
    # timestamp = djtab2.Column(verbose_name = _('Creation date'))

    class Meta:
        attrs = { 'id' : 'projects', 'class' : 'interactive_table' }
        fields = ('select', 'name') #, 'timestamp')


class SubjectsTable(djtab2.Table):
    select = djtab2.CheckBoxColumn(accessor = 'id', orderable = False)
    name = djtab2.Column()
    timestamp = djtab2.Column(verbose_name = _('Creation date'))

    class Meta:
        attrs = { 'id' : 'subjects', 'class' : 'interactive_table' }
        fields = ('select', 'name', 'timestamp')


class DocumentsTable(djtab2.Table):
    ANALYZED_TEMPLATE = '''
    {% load staticfiles %}
    {% load i18n %}
    {% if record.state == 1 %}
        <img src="{% static 'docato/img/checked_small.png' %}" alt="{% trans 'Analyzed' %}"/>
    {% else %}
        <img src="{% static 'docato/img/empty.png' %}" alt="{% trans 'Not analyzed' %}"/>
    {% endif %}
    '''
    select = djtab2.CheckBoxColumn(accessor = 'id', orderable = False)
    title = djtab2.Column()
    source_file = djtab2.FileColumn(verbose_name = _('File'))
    
    load_time = djtab2.DateTimeColumn(verbose_name = _('Loaded at'))
    analyzed = djtab2.TemplateColumn(ANALYZED_TEMPLATE, verbose_name = _('Analyzed'))
    
    class Meta:
        attrs = { 'id' : 'documents', 'class' : 'interactive_table' }
        fields = ('select', 'title', 'source_file', 'load_time', 'analyzed')
