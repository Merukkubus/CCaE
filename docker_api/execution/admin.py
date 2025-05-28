from django.contrib import admin
from .models import CodeExecution, Subscription, UserProfile, LanguageVersion, Language

admin.site.register(CodeExecution)

admin.site.register(Subscription)

admin.site.register(UserProfile)

@admin.register(LanguageVersion)
class LanguageVersionAdmin(admin.ModelAdmin):
    list_display = ('language', 'version', 'is_active')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)