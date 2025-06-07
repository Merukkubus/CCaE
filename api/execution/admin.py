from django.contrib import admin
from .models import UserFacingLogs, Subscription, UserProfile, LanguageVersion, Language, SystemLog

admin.site.register(UserFacingLogs)

admin.site.register(Subscription)

admin.site.register(UserProfile)

@admin.register(LanguageVersion)
class LanguageVersionAdmin(admin.ModelAdmin):
    list_display = ('language', 'version', 'is_active')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'level', 'action')
    list_filter = ('level', 'action', 'timestamp')
    search_fields = ('message',)