from django.views.generic.edit import BaseFormView, BaseCreateView, CreateView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404,\
    render_to_response
from django.template.context import RequestContext
from django.db import IntegrityError
from django.db.models import Q
from guardian.shortcuts import get_objects_for_user, get_perms, assign_perm
import os, json, traceback, itertools
import tables
import forms
import tasks

from models import *
from django.views.generic.base import TemplateView
from feature_extraction import highlight_features, try_extract_int, try_extract_real
from docato.utils import iterate_over_slot_values, iterate_over_frametypes, \
    get_frame_color_style_for_tree, get_sval_color_style, get_sval_color_style_for_tree


logger = logging.getLogger('common')


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


###############################################################################
################################## Projects ###################################
###############################################################################
class Projects(LoginRequiredMixin, BaseCreateView, tables.djtab2.SingleTableView):
    template_name = 'docato/projects.html'
    model = Project
    table_class = tables.ProjectsTable
    form_class = forms.NewProjectForm
    success_url = reverse_lazy('projects')

    def get_queryset(self):
        return get_objects_for_user(self.request.user,
                                    ('can_access', ),
                                    Project)

    def get_table(self, **kwargs):
        table = super(Projects, self).get_table(**kwargs)
        table.paginate(page = self.request.GET.get('page', 1), per_page = 30)
        return table

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(Projects, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Projects, self).get_context_data(**kwargs)
        context['form'] = self.get_form(self.get_form_class())
        return context
    
    def form_valid(self, form):
        result = super(Projects, self).form_valid(form)
        assign_perm('docato.change_project', self.request.user, self.object)
        assign_perm('docato.delete_project', self.request.user, self.object)
        assign_perm('docato.can_add_or_remove_subjects', self.request.user, self.object)
        return result


def get_project(request, proj_id = None, perms = ('can_access',), **kwargs):
    return get_object_or_404(get_objects_for_user(request.user,
                                                  ('can_access',),
                                                  Project.objects),
                             id = proj_id)


class ProjectPage(LoginRequiredMixin, BaseCreateView, tables.djtab2.SingleTableView):
    template_name = 'docato/project.html'
    model = Subject
    table_class = tables.SubjectsTable
    form_class = forms.NewSubjectForm

    def get_object(self, queryset = None):
        if not hasattr(self, 'project'):
            self.project = get_project(self.request,
                                       **self.kwargs)
        return self.project
        

    def get_queryset(self):
        return get_objects_for_user(self.request.user,
                                    ('change_subject', ),
                                    self.get_object().subjects)

    def get_table(self, **kwargs):
        table = super(ProjectPage, self).get_table(**kwargs)
        table.paginate(page = self.request.GET.get('page', 1), per_page = 30)
        return table

    def get_initial(self):
        result = super(ProjectPage, self).get_initial()
        result['project'] = int(self.kwargs.get('proj_id'))
        result['timestamp'] = timezone.now()
        return result

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(ProjectPage, self).post(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(ProjectPage, self).get_context_data(**kwargs)
        context['form'] = self.get_form(self.get_form_class())
        context['project'] = self.project
        return context

    def get_success_url(self):
        return reverse('project',
                       kwargs = { 'proj_id' : self.project.id })
    
    def form_valid(self, form):
        result = super(ProjectPage, self).form_valid(form)
        assign_perm('docato.change_subject', self.request.user, self.object)
        assign_perm('docato.delete_subject', self.request.user, self.object)
        assign_perm('docato.can_add_docs', self.request.user, self.object)
        assign_perm('docato.can_edit_docs', self.request.user, self.object)
        assign_perm('docato.can_edit_typesystem', self.request.user, self.object)
        return result


@login_required
@require_POST
def delete_projects(request):
    ids = request.POST.getlist('ids[]')
    get_objects_for_user(request.user,
                         ('docato.delete_project', ),
                         Project.objects.filter(id__in = ids)).delete()
    return HttpResponse('')

###############################################################################
################################## Subjects ###################################
###############################################################################
def get_subject(request, subj_id = None, **kwargs):
    return get_object_or_404(get_objects_for_user(request.user,
                                                  ('change_subject',),
                                                  Subject.objects),
                             id = subj_id)

class SubjectMixin(object):
    def get_subject(self):
        if hasattr(self, 'subject'):
            return self.subject
        self.subject = get_subject(self.request, **self.kwargs)
        return self.subject

    def get_context_data(self, **kwargs):
        context = super(SubjectMixin, self).get_context_data(**kwargs)
        context['subject'] = self.get_subject()
        context['subject_perms'] = get_perms(self.request.user, context['subject'])
        return context


@login_required
@require_POST
def delete_subjects(request):
    ids = request.POST.getlist('ids[]')
    get_objects_for_user(request.user,
                         ('delete_subject',),
                         Subject.objects).filter(id__in = ids).delete()
    return HttpResponse('')


class SubjectPage(LoginRequiredMixin, SubjectMixin, BaseFormView, tables.djtab2.SingleTableView):
    template_name = 'docato/subject.html'
    model = Document
    table_class = tables.DocumentsTable
    form_class = forms.AddDocumentForm
    
    def get_queryset(self):
        return self.get_subject().docs.all()

    def get_table(self, **kwargs):
        table = super(SubjectPage, self).get_table(**kwargs)
        table.paginate(page = self.request.GET.get('page', 1), per_page = 30)
        return table

    def get_context_data(self, **kwargs):
        context = super(SubjectPage, self).get_context_data(**kwargs)
        context['form'] = self.get_form(self.get_form_class())
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(SubjectPage, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            new_doc = self.get_subject().docs.create(load_time = timezone.now(),
                                                     **form.cleaned_data)
            tasks.process_doc.delay(new_doc.id)
            return redirect('subject_page', subj_id = self.subject.id)
        except Exception as ex:
            logger.error('Could not schedule an uploaded document for processing: %r\n%s' % (ex, traceback.format_exc()))
            open_dialog = True
            add_doc_err = _('The document with the same name has been already uploaded within this subject')
            return self.render_to_response(self.get_context_data(open_dialog = open_dialog,
                                                                 add_doc_err = add_doc_err))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(open_dialog = True))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SubjectPage, self).dispatch(*args, **kwargs)


@login_required
@require_POST
def update_subject(request, *args, **kwargs):
    subject = get_subject(request, **kwargs)
    if not 'can_edit_typesystem' in get_perms(request.user, subject):
        raise PermissionDenied()

    field_name = request.POST.get('name', None)
    value = request.POST.get('value', None)
    if field_name == 'allow_sval_cascade_delete':
        subject.allow_sval_cascade_delete = value == '1'
        subject.save()
    else:
        raise SuspiciousOperation()
    return HttpResponse()


###############################################################################
################################ Type system ##################################
###############################################################################
def get_frametype(request, frametype_id = None, **kwargs):
    return get_object_or_404(get_subject(request, **kwargs).types,
                             id = frametype_id)

class FrameTypeMixin(object):
    def get_frametype(self):
        if hasattr(self, 'frametype'):
            return self.frametype
        self.frametype = get_frametype(self.request, **self.kwargs)
        return self.frametype

    def get_context_data(self, **kwargs):
        context = super(SubjectMixin, self).get_context_data(**kwargs)
        context['frametype'] = self.get_frametype()
        return context


class TypeSystem(LoginRequiredMixin, SubjectMixin, TemplateView):
    template_name = 'docato/typesystem/typesystem.html'


class NewFrameType(LoginRequiredMixin, SubjectMixin, TemplateView):
    template_name = 'docato/typesystem/frame_type.html'

    def get_context_data(self, **kwargs):
        context = super(NewFrameType, self).get_context_data(**kwargs)
        if not 'can_edit_typesystem' in get_perms(self.request.user, self.get_subject()):
            raise PermissionDenied()
        new_name = get_unique_model_name(self.get_subject().types.all(),
                                         _('Frame Type'))
        context['frametype'] = self.get_subject().types.create(name = new_name)
        return context


@login_required
def list_frametypes_json(request, *args, **kwargs):
    subject = get_subject(request, **kwargs)
    return HttpResponse(json.dumps({ t.id : t.name for t in subject.types.all() }),
                        content_type = 'application/json')


@login_required
@require_POST
def update_frametype(request, *args, **kwargs):
    frametype = get_frametype(request, **kwargs)
    if not 'can_edit_typesystem' in get_perms(request.user, frametype.subject):
        raise PermissionDenied()

    field_name = request.POST.get('name', None)
    value = request.POST.get('value', None)
    if field_name == 'name':
        try:
            frametype.name = value
            frametype.save()
        except IntegrityError:
            return HttpResponse(_('Type name must be unique and cannot be empty'),
                                status = 400)
    elif field_name == 'standalone':
        frametype.standalone = value == '1'
        frametype.save()
    else:
        raise SuspiciousOperation()
    return HttpResponse()


@login_required
def delete_frametype(request, *args, **kwargs):
    frametype = get_frametype(request, **kwargs)
    if not 'can_edit_typesystem' in get_perms(request.user, frametype.subject):
        raise PermissionDenied()
    if frametype.can_delete():
        frametype.delete()
        return HttpResponse()
    else:
        return HttpResponse(_('Please remove references to this type first'),
                            status = 400)


class CloneFrameType(LoginRequiredMixin, SubjectMixin, TemplateView):
    template_name = 'docato/typesystem/frame_type.html'

    def get_context_data(self, **kwargs):
        context = super(CloneFrameType, self).get_context_data(**kwargs)
        if not 'can_edit_typesystem' in get_perms(self.request.user, self.get_subject()):
            raise PermissionDenied()
        frametype = get_frametype(self.request, **self.kwargs)
        context['frametype'] = frametype.clone()
        return context


@login_required
def add_slot(request, *args, **kwargs):
    frametype = get_frametype(request, **kwargs)
    if not 'can_edit_typesystem' in get_perms(request.user, frametype.subject):
        raise PermissionDenied()
    new_name = get_unique_model_name(frametype.slots.all(), _('Slot'))
    slot_type = request.POST.get('slot_type', 'class_label')
    new_order = frametype.get_new_slot_order()
    if slot_type == 'class_label':
        new_slot = ClassLabelSlot.objects.create(frame_type = frametype,
                                                 name = new_name,
                                                 order = new_order)
    elif slot_type == 'integer':
        new_slot = IntegerSlot.objects.create(frame_type = frametype,
                                              name = new_name,
                                              order = new_order)
    elif slot_type == 'real':
        new_slot = RealSlot.objects.create(frame_type = frametype,
                                           name = new_name,
                                           order = new_order)
    elif slot_type == 'object':
        new_slot = ObjectSlot.objects.create(frame_type = frametype,
                                             name = new_name,
                                             value_type = frametype.subject.types.all().first(),
                                             order = new_order)
        for other_frametype in frametype.subject.types.all():
            new_slot.value_type = other_frametype
            new_slot.save()
            if not frametype.subject.circular_dependency_exists():
                break
    elif slot_type == 'class_label_list':
        new_slot = ClassLabelListSlot.objects.create(frame_type = frametype,
                                                     name = new_name,
                                                     order = new_order)
    elif slot_type == 'integer_list':
        new_slot = IntegerListSlot.objects.create(frame_type = frametype,
                                                  name = new_name,
                                                  order = new_order)
    elif slot_type == 'real_list':
        new_slot = RealListSlot.objects.create(frame_type = frametype,
                                               name = new_name,
                                               order = new_order)
    elif slot_type == 'object_list':
        new_slot = ObjectListSlot.objects.create(frame_type = frametype,
                                                 name = new_name,
                                                 value_type = frametype.subject.types.all().first(),
                                                 order = new_order)
        for other_frametype in frametype.subject.types.all():
            new_slot.value_type = other_frametype
            new_slot.save()
            if not frametype.subject.circular_dependency_exists():
                break
    else:
        raise SuspiciousOperation()
    frametype.slots.add(new_slot)
    new_slot.ensure_objects_containment()
    return render_to_response(new_slot.template_name,
                              {
                               'subject_perms' : get_perms(request.user, frametype.subject),
                               'subject' : frametype.subject,
                               'frametype' : frametype,
                               'slot' : new_slot
                               },
                              context_instance = RequestContext(request))


def get_slot(request, slot_id = None, **kwargs):
    return get_object_or_404(get_frametype(request, **kwargs).slots,
                             id = slot_id)


@login_required
@require_POST
def update_slot(request, *args, **kwargs):
    slot = get_slot(request, **kwargs)
    if not 'can_edit_typesystem' in get_perms(request.user, slot.frame_type.subject):
        raise PermissionDenied()
    
    field_name = request.POST.get('name', None)
    value = request.POST.get('value', None)
    if field_name == 'name':
        try:
            slot.name = value
            slot.save()
        except IntegrityError:
            return HttpResponse(_('Slot name must be unique within the type and cannot be empty'),
                                status = 400)
    elif field_name == 'description':
        slot.description = value
        slot.save()
    elif field_name == 'order':
        try:
            slot.order = int(value)
            slot.save()
        except ValueError:
            return HttpResponse(_('Please enter a valid integer'),
                                status = 400)
    elif field_name == 'default_value':
        if isinstance(slot, ClassLabelSlot) or isinstance(slot, ClassLabelListSlot):
            slot.default_value = value
            slot.save()
        elif isinstance(slot, IntegerSlot) or isinstance(slot, IntegerListSlot):
            try:
                slot.default_value = int(value)
                slot.save()
            except ValueError:
                return HttpResponse(_('Please enter a valid integer'),
                                    status = 400)
        elif isinstance(slot, RealSlot) or isinstance(slot, RealListSlot):
            try:
                slot.default_value = float(value)
                slot.save()
            except ValueError:
                return HttpResponse(_('Please enter a valid real number'),
                                    status = 400)
        else:
            raise SuspiciousOperation()
    elif isinstance(slot, ObjectSlot) or isinstance(slot, ObjectListSlot):
        if ObjectSlotValue.objects.filter(Q(slot = slot),
                                          ~Q(value = None)).exists():
            return HttpResponse(_('Please delete all the frames using this slot first'),
                                status = 400)
        if field_name == 'value_type':
            old_value = slot.value_type
            slot.value_type = get_object_or_404(slot.frame_type.subject.types,
                                                id = value)
            slot.save()
            if slot.embedded and slot.frame_type.subject.circular_dependency_exists():
                slot.value_type = old_value
                slot.save()
                return HttpResponse(_('This change leads to circular dependency between types'),
                                    status = 400)
        elif field_name == 'embedded':
            slot.embedded = value == '1'
            slot.save()
            if slot.embedded and slot.frame_type.subject.circular_dependency_exists():
                slot.embedded = False
                slot.save()
                return HttpResponse(_('This change leads to circular dependency between types'),
                                    status = 400)
        else:
            raise SuspiciousOperation()
    else:
        raise SuspiciousOperation()
    return HttpResponse()


@login_required
def delete_slot(request, *args, **kwargs):
    slot = get_slot(request, **kwargs)
    if not 'can_edit_typesystem' in get_perms(request.user, slot.frame_type.subject):
        raise PermissionDenied()
    try:
        slot.delete()
        return HttpResponse()
    except IntegrityError as ex:
        return HttpResponse(unicode(ex), status = 400)


###############################################################################
################################# Documents ###################################
###############################################################################
def get_doc(request, doc_id = None, **kwargs):
    return get_object_or_404(get_subject(request, **kwargs).docs,
                             id = doc_id)


def get_frame(request, frame_id = None, **kwargs):
    return get_object_or_404(get_doc(request, **kwargs).frames,
                             id = frame_id)


class DocMixin(object):
    def get_doc(self):
        if hasattr(self, 'doc'):
            return self.doc
        self.doc = get_doc(self.request, **self.kwargs)
        return self.doc

    def get_context_data(self, **kwargs):
        context = super(DocMixin, self).get_context_data(**kwargs)
        context['doc'] = self.get_doc()
        return context


class Doc(LoginRequiredMixin, SubjectMixin, DocMixin, TemplateView):
    template_name = 'docato/doc.html'
    model = BaseSlotValue

    def get_context_data(self, **kwargs):
        context = super(Doc, self).get_context_data(**kwargs)
        context['doc'].source_file.basename = os.path.basename(context['doc'].source_file.name)
        context['new_frame_form'] = forms.NewFrameForm((ft.id, ft.name) for ft in self.get_doc().subject.types.all())
        return context


def get_json_for_cue(cue):
    return {
            'id' : 'cue_%d' % cue.id,
            'text' : cue.text,
            'type' : 'cue',
            'data' : {
                      'id' : cue.id,
                      'start' : cue.start,
                      'end' : cue.end,
                      'classes' : get_sval_color_style(cue.slot_value)
                      },
            'children' : []
            }


def get_ref_node_name(sval):
    return '%s: %s' % (sval.slot.name,
                       (_('ref to ') + sval.value.name) if not sval.value is None else _('not set'))


def get_json_for_slot_value(sval):
    if isinstance(sval, SlotValueWithCue):
        return {
                'id' : 'sval_%d' % sval.id,
                'text' : '%s: %s' % (sval.slot.name, sval.value),
                'type' : 'simple',
                'data' : {
                          'sval_id' : sval.id,
                          'value' : sval.value,
                          'can_delete' : sval.slot.is_list_slot
                          },
                'a_attr' : {
                            'class' : get_sval_color_style_for_tree(sval)
                            },
                'children' : [ get_json_for_cue(cue) for cue in sval.cues.all() ]
                }
    else:
        if sval.slot.embedded:
            return get_json_for_frame(sval.value, sval = sval)
        else:
            return {
                    'id' : 'sval_%d' % sval.id,
                    'text' : get_ref_node_name(sval),
                    'type' : 'reference',
                    'data' : {
                              'sval_id' : sval.id,
                              'target' : sval.value.id if not sval.value is None else None,
                              'can_delete' : sval.slot.is_list_slot,
                              'sval_name' : sval.slot.name
                              },
                    'a_attr' : {
                                'class' : get_sval_color_style_for_tree(sval)
                                },
                    'li_attr' : {
                                 'class' : ('ref_to_%d' % sval.value.id) if not sval.value is None else ''
                                 },
                    'children' : []
                    }


def get_json_for_frame_slot(frame, slot):
    if slot.is_list_slot:
        return {
                'id' : 'frame_%d_list_%d' % (frame.id, slot.id),
                'text' : '%s (%s)' % (slot.name, slot.type_name),
                'type' : 'list',
                'data' : {
                          'slot' : slot.id,
                          'frame' : frame.id
                          },
                'children' : [ get_json_for_slot_value(sval) for sval in frame.slots.filter(slot = slot) ]
                }
    else:
        return get_json_for_slot_value(frame.slots.get(slot = slot))


def get_name_for_frame_node(frame, sval = None):
    return (('%s: ' % sval.slot.name) if sval else '') + frame.name


def get_json_for_frame(frame, sval = None):
    return {
            'id' : 'frame_%d' % frame.id,
            'text' : get_name_for_frame_node(frame, sval),
            'type' : 'frame' if sval is None else 'embedded_frame',
            'state' : {
                       'opened' : sval is None,
                       'disabled' : False,
                       'selected' : False
                       },
            'a_attr' : {
                        'class' : get_frame_color_style_for_tree(frame)
                        },
            'data' : {
                      'id' : frame.id,
                      'sval_id' : sval.id if not sval is None else None,
                      'can_delete' : sval.slot.is_list_slot if not sval is None else True,
                      'name' : frame.name 
                      },
            'children' : [ get_json_for_frame_slot(frame, slot) for slot in frame.type.slots.all().order_by('order') ]
            }


@login_required
def get_extracted_data(request, *args, **kwargs):
    doc = get_doc(request, **kwargs)
    element_id = request.GET['id']
    if element_id == '#':
        embedded_frames = doc.embedded_frames_ids
        result = [
                  {
                   'id' : 'type_%d' % frametype.id,
                   'text' : frametype.name,
                   'type' : 'frametype',
                   'state' : {
                              'opened' : True,
                              'disabled' : False,
                              'selected' : False
                              },
                   'data' : {
                             'id' : frametype.id
                             },
                   'children' : [get_json_for_frame(frame)
                                 for frame in doc.frames.filter(type = frametype)
                                 if not frame.id in embedded_frames]
                  }
                  for frametype in doc.subject.types.all()
                  if frametype.standalone
                  ]
    elif element_id == 'document':
        embedded_frames = frozenset(v.value.id for v in
                                    ObjectSlotValue.objects.filter(frame__doc = doc)
                                    if v.slot is ObjectSlot and v.slot.embedded)
        result = [get_json_for_frame(frame)
                  for frame in doc.frames.all()
                  if not frame.id in embedded_frames]
    else:
        obj_type, obj_id = element_id.split('_')
        if obj_type == 'frame':
            frame = get_object_or_404(doc.frames, id = obj_id)
            result = [ get_json_for_slot_value(slot) for slot in frame.slots.all() ]
        else:
            result = []
    return HttpResponse(json.dumps(result),
                        content_type = 'application/json')
        

@login_required
@require_POST
def delete_docs(request, subj_id):
    ids = request.POST.getlist('ids[]')
    for doc in Document.objects.filter(id__in = ids):
        doc.delete()
    return HttpResponse('')


@login_required
def converted_doc(request, **kwargs):
    return HttpResponse(highlight_features(get_doc(request,
                                                   **kwargs)),
                        content_type = 'text/html; charset=UTF-8')


@login_required
@require_POST
def add_frame(request, **kwargs):
    doc = get_doc(request, **kwargs)
    new_frame = doc.frames.create(type = doc.subject.types.get(id = request.POST['type']))
    new_frame.reset_name() 
    new_frame.create_slot_values()
    return HttpResponse(json.dumps(get_json_for_frame(new_frame)),
                        content_type = 'application/json')


@login_required
@require_POST
def rename_frame(request, **kwargs):
    doc = get_doc(request, **kwargs)
    frame = get_object_or_404(Frame.objects,
                              doc = doc,
                              id = request.POST['id'])
    sval_id = request.POST.get('sval', None)
    if sval_id:
        sval = get_object_or_404(BaseSlotValue.objects,
                                 frame__doc = doc,
                                 id = sval_id)
    else:
        sval = None
    if request.POST['name'].strip():
        frame.name = request.POST['name']
        frame.save()
    return HttpResponse(json.dumps({
                                    'name' : frame.name,
                                    'node_title' : get_name_for_frame_node(frame, sval),
                                    'refs' : { sval.id : get_ref_node_name(sval)
                                              for sval in frame.references.all()
                                              if not sval.slot.embedded }
                                    }),
                        content_type = 'application/json')


@login_required
@require_POST
def delete_frames(request, **kwargs):
    ids = request.POST.getlist('ids[]')
    for frame_id in ids:
        frame = get_doc(request, **kwargs).frames.get(id = frame_id)
        if frame.can_delete():
            frame.delete()
        else:
            return HttpResponse(_('Please remove references to the frame first'),
                                status = 400)
    return HttpResponse('')


@login_required
@require_POST
def update_sval_value(request, **kwargs):
    doc = get_doc(request, **kwargs)
    sval = get_object_or_404(BaseSlotValue.objects,
                             frame__doc = doc,
                             id = request.POST['sval'])
    value = request.POST['value']
    if isinstance(sval, ClassLabelSlotValue):
        sval.value = value
        sval.save()
        return HttpResponse(json.dumps({ 'name' : '%s: %s' % (sval.slot.name, sval.value) }),
                            content_type = 'application/json')
    elif isinstance(sval, IntegerSlotValue):
        try:
            sval.value = int(value)
            sval.save()
            return HttpResponse(json.dumps({ 'name' : '%s: %s' % (sval.slot.name, sval.value) }),
                                content_type = 'application/json')
        except ValueError:
            return HttpResponse(_('Please enter a valid integer'),
                                status = 400)
    elif isinstance(sval, RealSlotValue):
        try:
            sval.value = float(value)
            sval.save()
            return HttpResponse(json.dumps({ 'name' : '%s: %s' % (sval.slot.name, sval.value) }),
                                content_type = 'application/json')
        except ValueError:
            return HttpResponse(_('Please enter a valid real number'),
                                status = 400)
    elif isinstance(sval, ObjectSlotValue) and not sval.slot.embedded:
        try:
            value = int(value)
            sval.value = doc.frames.get(id = value) if value >= 0 else None 
            sval.save()
            return HttpResponse(json.dumps({
                                            'name' : get_ref_node_name(sval),
                                            'classes' : ('ref_to_%d' % sval.value.id) if not sval.value is None else ''
                                            }),
                                content_type = 'application/json')
        except Frame.DoesNotExist:
            return HttpResponse(_('Target frame does not exist!'),
                                status = 400)
    return HttpResponse(status = 400)

@login_required
@require_POST
def get_value_variants(request, **kwargs):
    doc = get_doc(request, **kwargs)
    sval = get_object_or_404(BaseSlotValue.objects,
                             frame__doc = doc,
                             id = request.POST['sval'])
    if isinstance(sval, ClassLabelSlotValue):
        other_values = sval.get_other_values()
        return render_to_response('docato/typesystem/slot_values/select.html',
                                  {
                                   'value' : sval.value,
                                   'possible_values' : zip(other_values, other_values)
                                   },
                                  RequestContext(request))
    elif isinstance(sval, IntegerSlotValue):
        return render_to_response('docato/typesystem/slot_values/simple.html',
                                  {
                                   'value' : try_extract_int(sval.full_text, sval.value)
                                   },
                                  RequestContext(request))
    elif isinstance(sval, RealSlotValue):
        return render_to_response('docato/typesystem/slot_values/simple.html',
                                  {
                                   'value' : try_extract_real(sval.full_text, sval.value)
                                   },
                                  RequestContext(request))
    elif isinstance(sval, ObjectSlotValue) and not sval.slot.embedded:
        embedded_frames = doc.embedded_frames_ids
        possible_values = [(frame.id, frame.name) for frame in
                           doc.frames.filter(type = sval.slot.value_type)
                           if not frame.id in embedded_frames]
        return render_to_response('docato/typesystem/slot_values/select.html',
                                  {
                                   'possible_values' : possible_values,
                                   'value' : sval.value
                                   },
                                  RequestContext(request))
    raise SuspiciousOperation()


@login_required
@require_POST
def add_cues(request, **kwargs):
    doc = get_doc(request, **kwargs)
    sval = get_object_or_404(SlotValueWithCue.objects,
                             frame__doc = doc,
                             id = request.POST['sval'])
    result = [
              get_json_for_cue(sval.cues.create(text = d['text'],
                                                start = d['start'],
                                                end = d['end']))
              for d in json.loads(request.POST['cues'])
              ]
    return HttpResponse(json.dumps(result),
                        content_type = 'application/json')


@login_required
@require_POST
def delete_cue(request, **kwargs):
    doc = get_doc(request, **kwargs)
    get_object_or_404(Cue.objects,
                      slot_value__frame__doc = doc,
                      id = request.POST['cue']).delete()
    return HttpResponse('')


@login_required
@require_POST
def add_list_value(request, **kwargs):
    doc = get_doc(request, **kwargs)
    frame = get_object_or_404(doc.frames, id = int(request.POST['frame']))
    slot = get_object_or_404(frame.type.slots, id = int(request.POST['slot']))
    new_sval = frame.create_slot_value(slot, force = True)
    return HttpResponse(json.dumps(get_json_for_slot_value(new_sval)),
                        content_type = 'application/json')


@login_required
@require_POST
def delete_list_value(request, **kwargs):
    doc = get_doc(request, **kwargs)
    sval = get_object_or_404(BaseSlotValue,
                             frame__doc = doc,
                             id = request.POST['id'])
    if sval.slot.is_list_slot:
        sval.delete()
        return HttpResponse('')
    else:
        raise SuspiciousOperation()


###############################################################################
################################## Search #####################################
###############################################################################
class SearchFrameset(LoginRequiredMixin, TemplateView):
    template_name = 'docato/search_frameset.html'


class SearchToolbar(LoginRequiredMixin, SubjectMixin, CreateView):
    template_name = 'docato/search_toolbar.html'
    model = Document
    form_class = forms.AddDocumentForm

    def get_context_data(self, add_doc_cls = None, add_doc_msg = None, **kwargs):
        context = super(SearchToolbar, self).get_context_data(**kwargs)
        context['search_engines'] = SearchEngine.objects.all()
        context['hide_footer'] = True
        context['form'] = self.get_form(self.get_form_class())
        if add_doc_msg:
            context['add_doc_cls'] = add_doc_cls
            context['add_doc_msg'] = add_doc_msg
        return context

    def form_valid(self, form):
        try:
            new_doc = self.get_subject().docs.create(load_time = timezone.now(),
                                                     **form.cleaned_data)
            tasks.process_doc.delay(new_doc)
            add_doc_cls = 'success'
            add_doc_msg = _('The document has been successfully submitted')
        except IntegrityError as ex:
            logger.error('Could not schedule an uploaded document for processing: %r\n%s' % (ex, traceback.format_exc()))
            add_doc_cls = 'danger'
            add_doc_msg = _('The document with the same name has been already uploaded within this subject')
        return self.render_to_response(self.get_context_data(add_doc_cls = add_doc_cls,
                                                             add_doc_msg = add_doc_msg))


class SearchEmpty(LoginRequiredMixin, TemplateView):
    template_name = 'docato/search_empty.html'


def do_search(request, eng_id, query):
    engine = get_object_or_404(SearchEngine, id = eng_id)
    args = json.loads(engine.kwargs) if engine.kwargs else {}
    args['query'] = escape(query)
    return render_to_response('docato/engines/%s' % engine.template_name, args)


###############################################################################
################################## Summary ###################################
###############################################################################
class Summary(LoginRequiredMixin, SubjectMixin, TemplateView):
    template_name = 'docato/summary.html'

    def get_context_data(self, **kwargs):
        context = super(Summary, self).get_context_data(**kwargs)
        context['header_iterator'] = ('%s / %s' % (ftype.name, ' / '.join(s.name for s in slots))
                                      for ftype, slots in iterate_over_frametypes(self.get_subject()))
        embedded_frames = set(itertools.chain.from_iterable(doc.embedded_frames_ids
                                                            for doc in self.get_subject().docs.all()))
        context['rows'] = ((doc,
                            ((frame,
                              iterate_over_slot_values(frame))
                             for frame in doc.frames.all()
                             if not frame.id in embedded_frames))
                           for doc in self.get_subject().docs.all())
        return context


class Analysis(LoginRequiredMixin, SubjectMixin, TemplateView):
    template_name = 'docato/analysis.html'
