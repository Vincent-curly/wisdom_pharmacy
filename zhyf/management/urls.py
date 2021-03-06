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

from management import views

urlpatterns = [
    url(r'^login/', views.login, name='login'),
    url(r'^changeVerifyCode/', views.change_verify_code, name='changeVerifyCode'),
    url(r'^index/', views.index, name='index'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^home/', views.home, name='home'),
    url(r'^menuManage/(?P<type>\w+)/', views.menu_manage, name='menuManage'),
    url(r'^userManage/(?P<type>\w+)/', views.user_manage, name='userManage'),
    url(r'^role/', views.get_role, name='role'),
    url(r'^tableData/(?P<type>\w+)/', views.table_data, name='tableData'),
    url(r'^updatePass/', views.update_pass, name='updatePass'),
    url(r'^roleManage/(?P<type>\w+)/', views.role_manage, name='roleManage'),
    url(r'^goodsManage/(?P<type>\w+)/', views.goods_manage, name='goodsManage'),
    url(r'^goodsDetailsManage/(?P<type>\w+)/', views.goods_details_manage, name='goodsDetailsManage'),
    url(r'^decoctionCenterManage/(?P<type>\w+)/', views.decoction_center_manage, name='decoctionCenterManage'),
    url(r'^companyManage/(?P<type>\w+)', views.company_manage, name='companyManage'),
    url(r'^prescriptionQuery/(?P<type>\w+)', views.prescription_query, name='prescriptionQuery'),
    url(r'^orderAudit/(?P<type>\w+)', views.order_audit, name='orderAudit'),
    url(r'^orderInitial/(?P<type>\w+)', views.order_initial, name='orderInitial'),
    url(r'^Adjust/(?P<type>\w+)', views.prescription_adjust, name='Adjust')

]