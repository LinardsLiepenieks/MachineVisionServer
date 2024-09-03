from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile
from api.models import APIKey
from machines.models import Machine

class ApiKeyInline(admin.TabularInline):
    model = APIKey
    extra = 0
    fields = ('name', 'key', 'is_active')
    readonly_fields = ('key',)

class MachineInline(admin.TabularInline):
    model = Profile.machines.through
    extra = 0
    fields = ('machine',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_api_key')
    inlines = [ApiKeyInline, MachineInline]
    search_fields = ('user',)
    readonly_fields = ('redis_key',)
    exclude = ('redis_key',)

    def first_api_key(self, obj):
        # Retrieve the first API key related to this profile
        api_key = APIKey.objects.filter(profile=obj).first()
        return api_key.key if api_key else "No API key"
    
    first_api_key.short_description = 'API Key'

# Register the Profile model and its admin class
admin.site.register(Profile, ProfileAdmin)
