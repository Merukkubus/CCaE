from django.shortcuts import render
from django.urls import path, include
from django.contrib import admin

def index(request):
    return render(request, 'index.html')

urlpatterns = [
    path('', index, name='index'),
    path('api/', include('execution.urls')),
    path('admin/', admin.site.urls),
]