# coding:utf-8
"""
  Time : 2021/1/27 下午3:56
  Author : vincent
  FileName: urls
  Software: PyCharm
  Last Modified by: vincent
  Last Modified time: 2021/1/27 下午3:56
"""
from django.conf.urls import url

from drugstore import views

urlpatterns = [
    url(r'^index/', views.index, name='index'),
    url(r'^shopholic/', views.shopholic_index, name='shopholic_index'),
    url(r'^login/', views.login, name='login'),
    url(r'^register/', views.register, name='register'),

]