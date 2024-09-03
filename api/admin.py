from django.contrib import admin
from .models import APIKey
from .models import APIKey, AudioRecording,  MachineApiKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'is_active', 'created_at')
    readonly_fields = ('key',)

@admin.register(AudioRecording)
class AudioRecordingAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)

@admin.register(MachineApiKey)
class MachineApiKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'is_active', 'created_at', 'machine')
    search_fields = ('name', 'key', 'machine__name')
    list_filter = ('is_active', 'created_at', 'machine')
    readonly_fields = ('key', 'created_at')


