from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', { 'template_name': 'docato/login.html' }),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^$', views.Projects.as_view(), name = 'projects'),
    url(r'^project/(?P<proj_id>\d+)$', views.ProjectPage.as_view(), name = 'project'),
    url(r'^project/delete$', views.delete_projects, name = 'delete_projects'),
    url(r'^subject/(?P<subj_id>\d+)$', views.SubjectPage.as_view(), name = 'subject_page'),
    url(r'^subject/(?P<subj_id>\d+)/update$', views.update_subject, name = 'update_subject'),
    url(r'^subject/delete$', views.delete_subjects, name = 'delete_subjects'),
    
    url(r'^subject/(?P<subj_id>\d+)/typesystem$', views.TypeSystem.as_view(), name = 'typesystem'),
    url(r'^subject/(?P<subj_id>\d+)/typesystem/frametype/new$', views.NewFrameType.as_view(), name = 'add_frametype'),
    url(r'^subject/(?P<subj_id>\d+)/typesystem/frametype/list_json$', views.list_frametypes_json, name = 'list_frametypes_json'),
    url(r'^subject/(?P<subj_id>\d+)/typesystem/frametype/(?P<frametype_id>\d+)/update$', views.update_frametype, name = 'update_frametype'),
    url(r'^subject/(?P<subj_id>\d+)/typesystem/frametype/(?P<frametype_id>\d+)/delete$', views.delete_frametype, name = 'delete_frametype'),
    url(r'^subject/(?P<subj_id>\d+)/typesystem/frametype/(?P<frametype_id>\d+)/clone$', views.CloneFrameType.as_view(), name = 'clone_frametype'),
    url(r'^subject/(?P<subj_id>\d+)/typesystem/frametype/(?P<frametype_id>\d+)/slot/new$', views.add_slot, name = 'add_slot'),
    url(r'^subject/(?P<subj_id>\d+)/typesystem/frametype/(?P<frametype_id>\d+)/slot/(?P<slot_id>\d+)/update$', views.update_slot, name = 'update_slot'),
    url(r'^subject/(?P<subj_id>\d+)/typesystem/frametype/(?P<frametype_id>\d+)/slot/(?P<slot_id>\d+)/delete$', views.delete_slot, name = 'delete_slot'),
    
    url(r'^subject/(?P<subj_id>\d+)/search$', views.SearchFrameset.as_view(), name = 'search'),
    url(r'^subject/(?P<subj_id>\d+)/search/toolbar$', views.SearchToolbar.as_view(), name = 'search_toolbar'),
    
    url(r'^subject/(?P<subj_id>\d+)/summary', views.Summary.as_view(), name = 'summary'),
    url(r'^subject/(?P<subj_id>\d+)/analysis$', views.Analysis.as_view(), name = 'analysis'),
    
    url(r'^subject/(?P<subj_id>\d+)/document/delete$', views.delete_docs, name = 'delete_doc'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)$', views.Doc.as_view(), name = 'view_doc'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/extracted_data$', views.get_extracted_data, name = 'extracted_data'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/converted$', views.converted_doc, name = 'converted_doc'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/frame/add$', views.add_frame, name = 'add_frame'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/frame/rename$', views.rename_frame, name = 'rename_frame'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/frame/delete$', views.delete_frames, name = 'delete_frames'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/frame/add_cues$', views.add_cues, name = 'add_cues'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/frame/delete_cue$', views.delete_cue, name = 'delete_cue'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/frame/update_sval_value$', views.update_sval_value, name = 'update_sval_value'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/frame/get_value_variants$', views.get_value_variants, name = 'get_value_variants'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/frame/add_list_value$', views.add_list_value, name = 'add_list_value'),
    url(r'^subject/(?P<subj_id>\d+)/document/(?P<doc_id>\d+)/frame/delete_list_value$', views.delete_list_value, name = 'delete_list_value'),
    
    url(r'^search_empty$', views.SearchEmpty.as_view(), name = 'search_empty'),
    url(r'^search/(?P<eng_id>\d+)/(?P<query>.*)$', views.do_search, name = 'do_search'),
)
