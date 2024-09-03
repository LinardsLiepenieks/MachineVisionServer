from django.contrib import admin
from django.urls import reverse
from .models import Machine
from users.models import Profile
from django.utils.html import format_html
from api.models import MachineApiKey

class MachineApiKeyInline(admin.TabularInline):
    model = MachineApiKey
    extra = 0
    fields = ('name', 'key', 'is_active')
    readonly_fields = ('key',)


class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'machine_id', 'redis_key')
    inlines = [MachineApiKeyInline]

    readonly_fields = ('redis_key',)
    exclude = ('redis_key',)
    readonly_fields = ('redis_key', 'user_list')  # Mark user_list as read-only



    def user_list(self, obj):
        profiles = Profile.objects.filter(machines=obj)
        user_links = [
            format_html('<a href="{}">{}</a>', reverse('admin:users_profile_change', args=[profile.id]), profile.user.username)
            for profile in profiles
        ]
        return format_html("<br/>".join(user_links) or "No users connected")
    user_list.short_description = 'Users'

admin.site.register(Machine, MachineAdmin)