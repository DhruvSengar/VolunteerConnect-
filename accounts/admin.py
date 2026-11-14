from django.contrib import admin
from .models import Organization, VolunteerProfile
admin.site.register(VolunteerProfile)
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email')
