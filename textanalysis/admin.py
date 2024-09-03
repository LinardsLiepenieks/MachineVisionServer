from django.contrib import admin
from .models import ObjectKeyword, ActionVerb

@admin.register(ObjectKeyword)
class ObjectKeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'identifier')
    search_fields = ('keyword', 'identifier')

@admin.register(ActionVerb)
class ActionVerbAdmin(admin.ModelAdmin):
    list_display = ('verb', 'identifier', 'display_related_words')
    search_fields = ('verb', 'identifier')

    def display_related_words(self, obj):
        return ", ".join(obj.get_related_words())
    display_related_words.short_description = 'Related Words'
