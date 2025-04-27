from django.contrib import admin
from .models import CodeExecution, Subscription, UserProfile, PythonVersion

admin.site.register(CodeExecution)

admin.site.register(Subscription)

admin.site.register(UserProfile)

@admin.register(PythonVersion)
class PythonVersionAdmin(admin.ModelAdmin):
    list_display = ('version', 'is_active')