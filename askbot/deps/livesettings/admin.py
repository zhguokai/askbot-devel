from django.contrib import admin
from livesettings.models import Setting, LongSetting

class SettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'site', 'group', 'key', 'value')
    list_filter = ('site',)
    search_fields = ('group', 'key', 'value')
admin.site.register(Setting, SettingAdmin)
admin.site.register(LongSetting, SettingAdmin)
