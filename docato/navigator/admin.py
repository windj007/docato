from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from models import SearchEngine, Project, Subject

class ProjectAdmin(GuardedModelAdmin):
    model = Project

class SubjectAdmin(GuardedModelAdmin):
    model = Subject
    
class SearchEngineAdmin(admin.ModelAdmin):
    model = SearchEngine

    
admin.site.register(Project, ProjectAdmin)
admin.site.register(Subject, ProjectAdmin)
admin.site.register(SearchEngine, SearchEngineAdmin)
