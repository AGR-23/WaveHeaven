from django.contrib import admin
from .models import UserPreferences, Device, AudioAdjustmentRecord, ExposureReport, HearingRiskNotification

class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'ideal_volume', 'microphone_active', 'sound_category')
    search_fields = ('user__username',)
    list_filter = ('sound_category', 'microphone_active')

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'version', 'headphone_compatibility')
    search_fields = ('user__username', 'type', 'version')
    list_filter = ('headphone_compatibility',)

class AudioAdjustmentRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommended_volume', 'detected_noise', 'timestamp')
    search_fields = ('user__username',)
    list_filter = ('timestamp',)

class ExposureReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_exposure_time', 'trends')
    search_fields = ('user__username',)
    list_filter = ('total_exposure_time',)

class HearingRiskNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'warning_type', 'date_and_time', 'exposure_threshold')
    search_fields = ('user__username', 'warning_type')
    list_filter = ('date_and_time', 'warning_type')

admin.site.register(UserPreferences, UserPreferencesAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(AudioAdjustmentRecord, AudioAdjustmentRecordAdmin)
admin.site.register(ExposureReport, ExposureReportAdmin)
admin.site.register(HearingRiskNotification, HearingRiskNotificationAdmin)