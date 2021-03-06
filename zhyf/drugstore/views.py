from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    ip = request.META.get('REMOTE_ADDR')
    print(ip)
    return render(request, 'mall/base_mall_home.html')


def shopholic_index(request):
    ip = request.META.get('REMOTE_ADDR')
    print(ip)
    return render(request, 'mall/base_shopholic_home.html')


def login(request):
    return render(request, 'mall/login.html')


def register(request):
    return render(request, 'mall/register.html')