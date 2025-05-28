from django.contrib.auth.models import User
from django.db import models

# Пользовательские профили
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_paid_user = models.BooleanField(default=False)
    request_limit = models.IntegerField(default=10)

# Подписки пользователей
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    subscription_type = models.CharField(max_length=50)

# История выполнения кода
class CodeExecution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language_version = models.ForeignKey('LanguageVersion', on_delete=models.SET_NULL, null=True)
    code = models.TextField()
    output = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")
    execution_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)
    docker_name = models.CharField(max_length=50, null=True)
    def __str__(self):
        return self.name

class LanguageVersion(models.Model):
    language = models.ForeignKey(Language, related_name='versions', on_delete=models.CASCADE)
    version = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.language.name} {self.version}"