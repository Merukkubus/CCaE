from django.shortcuts import render, redirect


def index(request):
    return render(request, 'index.html')

def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    print("Попытка открыть:", request.path)
    return render(request, 'register.html')