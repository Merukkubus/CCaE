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
    language = models.CharField(max_length=10)
    code = models.TextField()
    output = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")
    execution_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PythonVersion(models.Model):
    version = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.version
