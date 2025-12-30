from django.contrib import admin
from .models import DeliveryZone, Profile, EmailLog

# Register existing models if you haven't
admin.site.register(Profile)
admin.site.register(EmailLog)

@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('state', 'fee', 'estimated_time', 'is_active')
    search_fields = ('state',)