# coding:utf-8
"""
  Time : 2021/1/27 下午3:07
  Author : vincent
  FileName: views
  Software: PyCharm
  Last Modified by: vincent
  Last Modified time: 2021/1/27 下午3:07
"""
import base64
import datetime
import json
import logging
import os
import random
import string
import re
import time
from _md5 import md5
from decimal import Decimal
from io import BytesIO

import pandas as pd
from django.conf import settings
from django.core import serializers
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from management.models import User, Role, Goods, GoodsDetails, DecoctCenter, Institution, Menu, Permission
from relies import generate_code
from relies.authorityControl import get_menu_html
from relies.barCode_QRcode import generateBarcode
from relies.handle import DateEncoder, string_to_list, model2json, makepdf
from relies.prescription_audit import reverse_18, fear_19, usage_match, poisonous_and_dose_match
from services.models import Order, Prescription, PresDetails
from zhyf.settings import BASE_DIR
logger = logging.getLogger('log')


def login_old(request):
    err_msg = {}
    today_str = datetime.date.today().strftime("%Y%m%d")
    verify_code_img_path = os.path.join('static/verify_code_imgs', today_str)
    if not os.path.exists(verify_code_img_path):
        os.makedirs(verify_code_img_path)
        print('创建目录成功')
    print("session:", request.session.session_key)
    # print("session:",request.META.items())
    random_filename = "".join(random.sample(string.ascii_lowercase, 4))
    random_code = generate_code.gene_code(verify_code_img_path, random_filename)
    cache.set(random_filename, random_code, 30)
    # GET 请求,直接显示用户登录界面
    if request.method == 'POST':
        # POST 请求,获取用户输入的用户名和密码
        username = request.POST.get('username')
        password = request.POST.get('password')
        verify_code = request.POST.get('code')
        verify_code_key = request.POST.get('verify_code_key')
        # print('username:', username)
        # print('password:', md5(password.encode('utf-8')).hexdigest())
        # print("verify_code_key:", verify_code_key)
        # print("verify_code:", verify_code)
        # print('cache_code:', cache.get(verify_code_key))

        if cache.get(verify_code_key) == verify_code.upper():
            print("code verification pass!")
            # 从数据库中查询用户名和密码是否正确
            user = User.objects.filter(username=username, password=md5(password.encode('utf-8')).hexdigest())
            print(user)
            if len(user) != 0:
                request.session['username'] = username
                print('用户名密码正确，验证通过')
                login_user = User.objects.get(username=username)
                print(login_user)
                print(type(login_user))
                login_user.login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                login_user.save()
                context = {'name': login_user.name}
                print(context)
                return render(request, 'backstage/index.html', context=context)
            else:
                err_msg["uperror"] = '用户名或密码错误！'
        else:
            err_msg['cerror'] = "验证码错误或已过期！"
    return render(request, 'backstage/mg_login_old.html',
                  {"filename": random_filename, "today_str": today_str, "error": err_msg})


def login(request):
    err_msg = {}
    if request.method == 'POST':
        # POST 请求,获取用户输入的用户名和密码
        username = request.POST.get('username')
        password = request.POST.get('password')
        verify_code = request.POST.get('code')
        if cache.get('verify_code') == verify_code.upper():
            if username != 'whiteadmin':
                user = User.objects.filter(username=username, password=password).first()
                if user:
                    request.session["is_login"] = True
                    request.session['username'] = user.username
                    request.session.set_expiry(0)       # 关闭浏览器就清掉session
                    if user.is_disabled > 0:
                        return redirect(reverse('management:index'))
                    else:
                        err_msg['uperror'] = '该用户已停用,请联系管理员！'
                else:
                    err_msg["uperror"] = '用户名或密码错误！'
            else:
                if password == md5('whiteadmin'.encode('utf-8')).hexdigest():
                    return render(request, 'backstage/white_admin_index.html')
                else:
                    err_msg["uperror"] = '用户名或密码错误！'
        else:
            err_msg['cerror'] = "验证码错误或已过期！"
    return render(request, 'backstage/mg_login.html', err_msg)


def change_verify_code(request):
    im = generate_code.gene_code()
    fp = BytesIO()
    im[0].save(fp, 'png')
    cache.set('verify_code', im[1], 60)
    return HttpResponse(fp.getvalue(), content_type='image/png')


def index(request):
    is_login = request.session.get('is_login')
    username = request.session.get('username')
    if not is_login:
        """如果没有登录则跳转至登录页面"""
        return redirect(reverse('management:login'))
    user = User.objects.get(username=username)
    user.login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user.save()
    permission_item_list = list(user.role.values('permissions__url',
                                                 'permissions__title',
                                                 'permissions__per_id',
                                                 'permissions__menu_id').distinct())
    permission_list = []  # 用户权限url列表
    permission_menu_list = []  # 用户权限url所属菜单列表

    for item in permission_item_list:
        if item['permissions__menu_id']:
            temp = {"title": item['permissions__title'],
                    "url": item["permissions__url"],
                    "menu_id": item["permissions__menu_id"],
                    'per_id': item["permissions__per_id"]}
            permission_list.append(temp)
            if item['permissions__menu_id'] in permission_menu_list:
                continue
            else:
                permission_menu_list.append(item['permissions__menu_id'])
    menu_list = list(Menu.objects.filter(id__in=permission_menu_list).values('id', 'title', 'icon'))
    # 注：session在存储时，会先对数据进行序列化，因此对于Queryset对象写入session， 加list()转为可序列化对象
    # print(permission_list)
    # print(menu_list)
    menu_html = get_menu_html(menu_list, permission_data=permission_list)
    context = {'name': user.name, 'menu_html': menu_html}
    # print(context)
    return render(request, 'backstage/index.html', context)
    # return render(request, 'backstage/index.html')


def logout(request):
    request.session.flush()
    return redirect(reverse('management:login'))


def home(request):
    return render(request, 'backstage/home.html')


@csrf_exempt
def table_data(request, type):
    lis = []
    data_count = 0
    if type == 'menu_table':
        menuname = request.GET.get('menuname')
        menutype = request.GET.get('menutype')
        q1 = Q()
        q1.connector = 'AND'
        if menuname:
            q1.children.append(('title', menuname))
        if menutype:
            q1.children.append(('menu_type', menutype))
        if q1.children:
            menu_datas = Menu.objects.filter(q1)
            data_count += menu_datas.count()
            lis = list(menu_datas.values())
            for i in range(len(lis)):
                if lis[i]['parent_id']:
                    lis[i]['parent_id'] = menu_datas[i].parent.title
                else:
                    lis[i]['parent_id'] = ''
        else:
            menu_datas = Menu.objects.all()
            data_count += menu_datas.count()
            lis = list(menu_datas.order_by('id').values())
            # print(menu_datas)
            # print(lis)
            for i in range(len(lis)):
                if lis[i]['parent_id']:
                    lis[i]['parent_id'] = menu_datas[i].parent.title
                else:
                    lis[i]['parent_id'] = ''
    if type == 'user_table':
        username = request.GET.get('username')
        role = request.GET.get('role')
        last_login_start = request.GET.get('lastLoginStart')
        last_login_end = request.GET.get('lastLoginEnd')
        q1 = Q()
        q1.connector = 'AND'
        if username:
            q1.children.append(('username', username))
        if role:
            q1.children.append(('role', role))
        if last_login_start and last_login_end:
            q1.children.append(('login_time__range', (last_login_start, last_login_end)))
        # print(query_dict)
        if q1.children:
            user_datas = User.objects.filter(q1)
            data_count += user_datas.count()
            lis = list(user_datas.values())
            for i in range(len(lis)):
                lis[i]['role'] = list(user_datas[i].role.all().values('role_name'))[0]['role_name']
        else:
            user_datas = User.objects.all()
            data_count += user_datas.count()  # 数据总数
            lis = list(user_datas.values())
            for i in range(len(lis)):       # 级联数据
                lis[i]['role'] = list(user_datas[i].role.all().values('role_name'))[0]['role_name']
            # print(lis)
    elif type == 'role_table':
        data_count += Role.objects.all().count()  # 数据总数
        lis = list(Role.objects.all().order_by('id').values())
    elif type == 'goods_table':
        key_words = request.GET.get('key_words')
        goods_code = request.GET.get('goods_code')
        q2 = Q()
        q3 = Q()
        q2.connector = 'OR'  # q2对象表示‘OR’关系，也就是说q2下的条件都要满足‘OR’
        q3.connector = 'AND'
        if key_words:
            keys = ['goods_name', 'short_code', 'english_name', 'chinese_name', 'alias1', 'alias2', 'alias3', 'alias4',
                    'alias5', 'alias6', 'alias7', 'alias8', 'alias9', 'alias10']
            for key in keys:
                new_key = key + '__contains'
                q2.children.append((new_key, key_words))
        if goods_code:
            q3.children.append(('goods_code', goods_code))
        if (q2 & q3).children:
            goods_datas = Goods.objects.filter(q2 & q3)
            # print(goods_datas)
            data_count += goods_datas.count()
            lis = list(goods_datas.values())
        else:
            data_count += Goods.objects.all().count()
            lis = list(Goods.objects.all().values())
    elif type == 'goodsDetails_table':
        key_words = request.GET.get('key_words')
        goods_code = request.GET.get('goods_code')
        q1 = Q()
        q1.connector = 'AND'
        if key_words:
            q1.children.append(('goods_name__contains', key_words))
        if goods_code:
            q1.children.append(('goods_code', goods_code))
        if q1.children:
            goods_details = GoodsDetails.objects.filter(q1)
            data_count += goods_details.count()
            lis = list(goods_details.values())
        else:
            data_count += GoodsDetails.objects.all().count()
            lis = list(GoodsDetails.objects.all().values())
    elif type == 'center_table':
        key_words = request.GET.get('key_words')
        q1 = Q()
        q1.connector = 'OR'
        if key_words:
            try:
                key_words = int(key_words)
                q1.children.append(('code', key_words))
            except ValueError:
                q1.children.append(('name__contains', key_words))
        if q1.children:
            center_datas = DecoctCenter.objects.filter(q1)
            data_count += center_datas.count()
            lis = list(center_datas.values())
        else:
            data_count += DecoctCenter.objects.all().count()
            lis = list(DecoctCenter.objects.all().values())
    elif type == 'company_table':
        q1 = Q()
        q1.connector = 'OR'
        q2 = Q()
        q2.connector = 'AND'
        key_words = request.GET.get('keyWords')
        storage_type = request.GET.get('storageType')
        his_grade = request.GET.get('hisGrade')
        ascription = request.GET.get('ascription')
        if key_words:
            q1.children.append(('company_num__contains', key_words))
            q1.children.append(('company_name__contains', key_words))
            q1.children.append(('short_name__contains', key_words))
        if storage_type:
            q2.children.append(('storage_type', storage_type))
        if his_grade:
            q2.children.append(('his_grade', his_grade))
        if ascription:
            q2.children.append(('ascription', ascription))
        if (q1 & q2).children:
            companydatas = Institution.objects.filter(q1 & q2)
            data_count += companydatas.count()
            lis = list(companydatas.values())
            for i in range(len(lis)):
                lis[i]['storage_type'] = companydatas[i].storage_type.name
                lis[i]['oper_id'] = companydatas[i].oper_id.name
        else:
            company_datas = Institution.objects.all()
            data_count += company_datas.count()
            lis = list(company_datas.values())
            for i in range(len(lis)):
                lis[i]['storage_type'] = company_datas[i].storage_type.name
                lis[i]['oper_id'] = company_datas[i].oper_id.name
    elif type == 'order_table':
        order_q1 = Q()
        order_q2 = Q()
        order_q3 = Q()
        order_q1.connector = 'AND'
        order_q2.connector = 'AND'
        order_q3.connector = 'OR'
        consignee = request.GET.get('consignee')
        doctor_name = request.GET.get('doctorName')
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')
        is_hos = request.GET.get('isHos')
        is_hosaddr = request.GET.get('isHosAddr')
        order_status = request.GET.get('orderStatus')
        other_presnum = request.GET.get('otherPresNum')
        prescri_type = request.GET.get('prescrType')
        prescri_id = request.GET.get('prescriId')
        source_id = request.GET.get('sourceId')
        storage_type = request.GET.get('storageType')
        user_name = request.GET.get('userName')
        if start_date and end_date:
            order_q1.children.append(('order_time__range', (start_date, end_date)))
        if source_id:
            order_q1.children.append(('source_id', source_id))
        if storage_type:
            order_q1.children.append(('storage_type', storage_type))
        if consignee:
            order_q1.children.append(('consignee', consignee))
        if is_hosaddr:
            order_q1.children.append(('is_hos_addr', is_hosaddr))
        if order_status:
            order_q1.children.append(('order_status', order_status))
        if doctor_name:
            order_q2.children.append(('doctor', doctor_name))
        if is_hos:
            order_q2.children.append(('is_hos', is_hos))
        if other_presnum:
            order_q2.children.append(('other_pres_num', other_presnum))
        if prescri_type:
            order_q2.children.append(('prescri_type', prescri_type))
        if prescri_id:
            order_q2.children.append(('prescri_id', prescri_id))
        if user_name:
            order_q2.children.append(('user_name', user_name))
        # print(order_q1.children)
        # print(order_q2.children)
        if order_q1.children and order_q2.children:
            prescription_datas = Prescription.objects.filter(order_q2)
            # print(prescription_datas)
            count = prescription_datas.count()
            # print(count)
            if count:
                for num in range(count):
                    order_id = prescription_datas[num].order_id.order_id
                    order_q3.children.append(('order_id', order_id))
                order_datas = Order.objects.filter(order_q1 & order_q3)
            else:
                order_datas = prescription_datas
        elif order_q1.children:
            order_datas = Order.objects.filter(order_q1)
        elif order_q2.children:
            prescription_datas = Prescription.objects.filter(order_q2)
            count = prescription_datas.count()
            if count:
                for num in range(count):
                    order_id = prescription_datas[num].order_id.order_id
                    order_q3.children.append(('order_id', order_id))
                order_datas = Order.objects.filter(order_q3)
            else:
                order_datas = prescription_datas
        else:
            order_datas = Order.objects.all()
        data_count += order_datas.count()
        lis = list(order_datas.values())
        for i in range(len(lis)):
            # print(order_datas[i].prescription_set.all().values('other_pres_num')[0]['other_pres_num'])
            prescript = order_datas[i].prescription_set.all()       # 外键反向查询
            lis[i]['other_pres_num'] = prescript.values('other_pres_num')[0]['other_pres_num']
            lis[i]['prescri_id'] = prescript.values('prescri_id')[0]['prescri_id']
            lis[i]['prescri_type'] = prescript.values('prescri_type')[0]['prescri_type']
            lis[i]['is_suffering'] = prescript.values('is_suffering')[0]['is_suffering']
            lis[i]['user_name'] = prescript.values('user_name')[0]['user_name']
            lis[i]['doctor'] = prescript.values('doctor')[0]['doctor']
            lis[i]['storage_type'] = order_datas[i].storage_type.name
            lis[i]['source_id'] = order_datas[i].source_id.company_name
    elif type == 'drugs_table':
        pres_num = request.GET.get('prescri_id')
        drugs_datas = PresDetails.objects.filter(prescri_id=pres_num)
        data_count += drugs_datas.count()
        lis = list(drugs_datas.values())
        for i in range(len(lis)):
            lis[i]['unit_sum'] = Decimal(Decimal(drugs_datas[i].dose).quantize(Decimal('0.00')) *
                                         Decimal(drugs_datas[i].unit_price).quantize(Decimal('0.00000'))).quantize(
                Decimal('0.00'))
        result = {"code": 0, "msg": "", "count": data_count, "data": lis}
        return HttpResponse(json.dumps(result, cls=DateEncoder, ensure_ascii=False), content_type="application/json")
    elif type == 'orderAudit_table':
        order_q1 = Q()
        order_q2 = Q()
        order_q3 = Q()
        order_q1.connector = 'AND'
        order_q2.connector = 'AND'
        order_q3.connector = 'OR'
        is_hos = request.GET.get('isHos')
        is_hosaddr = request.GET.get('isHosAddr')
        audit_type = request.GET.get('auditType')
        other_presnum = request.GET.get('otherPresNum')
        prescri_type = request.GET.get('prescrType')
        source_id = request.GET.get('sourceId')
        user_name = request.GET.get('userName')
        if source_id:
            order_q1.children.append(('source_id', source_id))
        if is_hosaddr:
            order_q1.children.append(('is_hos_addr', is_hosaddr))
        if audit_type:
            if int(audit_type) == 0:
                order_q1.children.append(('order_status', 5))
            else:
                order_q1.children.append(('order_status__gt', 5))
        if is_hos:
            order_q2.children.append(('is_hos', is_hos))
        if other_presnum:
            order_q2.children.append(('other_pres_num', other_presnum))
        if prescri_type:
            order_q2.children.append(('prescri_type', prescri_type))
        if user_name:
            order_q2.children.append(('user_name', user_name))
        if order_q1.children or order_q2.children:
            if order_q2.children and order_q1.children:
                prescription_datas = Prescription.objects.filter(order_q2)
                count = prescription_datas.count()
                if count:
                    for num in range(count):
                        order_id = prescription_datas[num].order_id.order_id
                        order_q3.children.append(('order_id', order_id))
                    order_datas = Order.objects.filter(order_q1 & order_q3 & Q(order_status=5))
                else:
                    order_datas = prescription_datas
            elif order_q1.children:
                order_datas = Order.objects.filter(order_q1)
            else:
                prescription_datas = Prescription.objects.filter(order_q2)
                count = prescription_datas.count()
                if count:
                    for num in range(count):
                        order_id = prescription_datas[num].order_id.order_id
                        order_q3.children.append(('order_id', order_id))
                    order_datas = Order.objects.filter(order_q3 & Q(order_status=5))
                else:
                    order_datas = prescription_datas
            data_count += order_datas.count()
            lis = list(order_datas.values())
        else:
            order_datas = Order.objects.filter(Q(order_status=5))
            data_count += order_datas.count()
            lis = list(order_datas.values())
        for i in range(len(lis)):
            prescript = order_datas[i].prescription_set.all()       # 外键反向查询
            lis[i]['prescri_id'] = prescript.values('prescri_id')[0]['prescri_id']
            lis[i]['prescri_type'] = prescript.values('prescri_type')[0]['prescri_type']
            lis[i]['is_suffering'] = prescript.values('is_suffering')[0]['is_suffering']
            lis[i]['user_name'] = prescript.values('user_name')[0]['user_name']
            lis[i]['source_id'] = order_datas[i].source_id.company_name
    elif type == 'orderInitial_table':
        order_q1 = Q()
        order_q2 = Q()
        order_q3 = Q()
        order_q1.connector = 'AND'
        order_q2.connector = 'AND'
        order_q3.connector = 'OR'
        source_id = request.GET.get('sourceId')
        key_words = request.GET.get('keyWords')
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')
        if source_id:
            order_q1.children.append(('source_id', source_id))
        if key_words:
            if bool(re.search(r'\d', key_words)):
                order_q1.children.append(('order_id', key_words))
            else:
                order_q2.children.append(('user_name', key_words))
        if start_date and end_date:
            order_q1.children.append(('order_time__range', (start_date, end_date)))
        if order_q1.children or order_q2.children:
            if order_q2.children and order_q1.children:
                prescription_datas = Prescription.objects.filter(order_q2)
                # print(prescription_datas)
                count = prescription_datas.count()
                # print(count)
                if count:
                    for num in range(count):
                        order_id = prescription_datas[num].order_id.order_id
                        order_q3.children.append(('order_id', order_id))
                    order_datas = Order.objects.filter(order_q1 & order_q3)
                else:
                    order_datas = prescription_datas
            elif order_q1.children:
                order_datas = Order.objects.filter(order_q1)
            else:
                prescription_datas = Prescription.objects.filter(order_q2)
                count = prescription_datas.count()
                if count:
                    for num in range(count):
                        order_id = prescription_datas[num].order_id.order_id
                        order_q3.children.append(('order_id', order_id))
                    order_datas = Order.objects.filter(order_q3)
                else:
                    order_datas = prescription_datas
            data_count += order_datas.count()
            lis = list(order_datas.values())
        else:
            order_datas = Order.objects.all()
            data_count += order_datas.count()
            lis = list(order_datas.values())
        for i in range(len(lis)):
            prescript = order_datas[i].prescription_set.all()  # 外键反向查询
            lis[i]['prescri_id'] = prescript.values('prescri_id')[0]['prescri_id']
            lis[i]['user_name'] = prescript.values('user_name')[0]['user_name']
            lis[i]['source_id'] = order_datas[i].source_id.company_name
    elif type == 'prescriptionAdjust_table':
        order_q1 = Q()
        order_q2 = Q()
        order_q3 = Q()
        order_q1.connector = 'AND'
        order_q2.connector = 'AND'
        order_q3.connector = 'OR'
        source_id = request.GET.get('sourceId')
        prescri_type = request.GET.get('prescrType')
        print_status = request.GET.get('printStatus')
        batch = request.GET.get('batch')
        is_hos = request.GET.get('isHos')
        is_hosaddr = request.GET.get('isHosAddr')
        taking_method = request.GET.get('takingMethod')
        # print(taking_method)
        prescri_id = request.GET.get('prescriId')
        if source_id:
            order_q1.children.append(('source_id', source_id))
        if is_hosaddr:
            order_q1.children.append(('is_hos_addr', is_hosaddr))
        if print_status:
            order_q2.children.append(('print_type', print_status))
        if is_hos:
            order_q2.children.append(('is_hos', is_hos))
        if prescri_type:
            order_q2.children.append(('prescri_type', prescri_type))
        if batch:
            order_q1.children.append(('batch', batch))
        if taking_method:
            order_q2.children.append(('is_within', taking_method))
        if prescri_id:
            order_q2.children.append(('prescri_id', prescri_id))
        # print(order_q1.children)
        # print(order_q2.children)
        if order_q1.children or order_q2.children:
            if order_q2.children and order_q1.children:
                prescription_datas = Prescription.objects.filter(order_q2)
                count = prescription_datas.count()
                if count:
                    for num in range(count):
                        order_id = prescription_datas[num].order_id.order_id
                        order_q3.children.append(('order_id', order_id))
                    order_datas = Order.objects.filter(order_q1 & order_q3 & Q(order_status=15))
                else:
                    order_datas = prescription_datas
            elif order_q1.children:
                order_datas = Order.objects.filter(order_q1 & Q(order_status=15))
            else:
                prescription_datas = Prescription.objects.filter(order_q2)
                count = prescription_datas.count()
                if count:
                    for num in range(count):
                        order_id = prescription_datas[num].order_id.order_id
                        order_q3.children.append(('order_id', order_id))
                    order_datas = Order.objects.filter(order_q3 & Q(order_status=15))
                else:
                    order_datas = prescription_datas
            data_count += order_datas.count()
            lis = list(order_datas.values())
        else:
            order_datas = Order.objects.filter(Q(order_status=15))
            data_count += order_datas.count()
            lis = list(order_datas.values())
        for i in range(len(lis)):
            prescript = order_datas[i].prescription_set.all()       # 外键反向查询
            lis[i]['prescri_id'] = prescript.values('prescri_id')[0]['prescri_id']
            lis[i]['prescri_type'] = prescript.values('prescri_type')[0]['prescri_type']
            lis[i]['is_suffering'] = prescript.values('is_suffering')[0]['is_suffering']
            lis[i]['user_name'] = prescript.values('user_name')[0]['user_name']
            lis[i]['is_within'] = prescript.values('is_within')[0]['is_within']
            lis[i]['print_type'] = prescript.values('print_type')[0]['print_type']
            lis[i]['adjust_num'] = prescript.values('adjust_num')[0]['adjust_num']
            lis[i]['source_id'] = order_datas[i].source_id.company_name
    page_index = request.GET.get('page')  # 前台传的值，
    page_size = request.GET.get('limit')  # 前台传的值
    paginator = Paginator(lis, page_size)  # 导入分页模块分页操作，不写前端只展示一页数据，
    contacts = paginator.page(page_index)  # 导入分页模块分页操作，不写前端只展示一页数据，
    res = []
    for contact in contacts:
        res.append(contact)
    result = {"code": 0, "msg": "", "count": data_count, "data": res}
    # print(result)
    return HttpResponse(json.dumps(result, cls=DateEncoder, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def user_manage(request, type):
    if type == 'userAdd':
        context = {}
        if request.method == 'POST':
            user = User()
            user.username = request.POST.get('username')
            # user.password = md5(request.POST.get('password').encode('utf-8')).hexdigest()
            user.password = request.POST.get('password')
            user.name = request.POST.get('uname')
            user.department = request.POST.get('department')
            role = Role.objects.get(id=request.POST.get('role'))
            try:
                user.save()
                user.role.add(role)
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                logger.error(e)
                logger.info(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/systemManage/user/user_add.html')
    if type == 'userEdit':
        context = {}
        if request.method == 'POST':
            user = User.objects.get(username=request.POST.get('username'))
            user.name = request.POST.get('uname')
            user.department = request.POST.get('department')
            user.work_num = request.POST.get('worknum')
            role = Role.objects.get(id=request.POST.get('role'))
            user.role.add(role)
            try:
                user.save()
                context['status'] = 'success'
            except Exception as e:
                logger.error(e)
                context['status'] = 'fail'
                context['message'] = str(e)
                logger.info(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        user = User.objects.get(id=request.GET.get('userId'))
        role_id = list(user.role.all().values('id'))[0]['id']
        return render(request, 'backstage/systemManage/user/user_edit.html', locals())
    if type == 'userDelete':
        context = {}
        # print(request.POST)
        dele_datas = string_to_list(request.POST.get('delData'))
        # print(dele_datas)
        for data in dele_datas:
            try:
                User.objects.get(username=data).delete()
                context['status'] = 'success'
                context['message'] = '成功删除%s条数据' % len(dele_datas)
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                logger.error(e)
        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    if type == 'updateStatus':
        context = {}
        user = User.objects.get(username=request.POST.get('username'))
        status = request.POST.get('status')
        if int(status) > 0:
            user.is_disabled = 0
        else:
            user.is_disabled = 1
        try:
            user.save()
            context['status'] = 'success'
        except Exception as e:
            logger.error(e)
            context['status'] = 'fail'
            context['message'] = str(e)
        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    if type == 'home':
        return render(request, 'backstage/systemManage/user/user_manage.html')


@csrf_exempt
def update_pass(request):
    context = {}
    if request.method == 'POST':
        user = User.objects.get(name=request.POST.get('uName'))
        # print(user.password)
        # print(request.POST.get('prePassword'))
        if user.password == request.POST.get('prePassword'):
            user.password = request.POST.get('newPassword')
            try:
                user.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
        else:
            context['status'] = 'fail'
            context['message'] = '原密码不正确！'
        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    return render(request, 'backstage/systemManage/user/update_pass.html')


@csrf_exempt
def role_manage(request, type):
    if type == 'roleAdd':
        context = {}
        if request.method == 'POST':
            role = Role()
            # print(request.POST.get('rolename'))
            role.role_name = request.POST.get('rolename')
            try:
                role.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/systemManage/user/role_add.html')
    if type == 'roleEdit':
        context = {}
        if request.method == 'POST':
            role = Role.objects.get(id=request.POST.get('roleid'))
            role.role_name = request.POST.get('rolename')
            try:
                role.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/systemManage/user/role_edit.html')
    if type == 'roleDelete':
        context = {}
        try:
            Role.objects.get(id=request.POST.get('delData')).delete()
            context['status'] = 'success'
        except Exception as e:
            context['status'] = 'fail'
            context['message'] = str(e)
        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    if type == 'menuData':
        menu_datalist = list(Menu.objects.all().values())
        # print(menu_datalist)
        # print(len(menu_datalist))
        menu_data = []
        parent_id = []
        for num in range(len(menu_datalist)):
            # print(menu_datalist[num]['parent_id'])
            if menu_datalist[num]['parent_id'] == None:
                del menu_datalist[num]['icon']
                del menu_datalist[num]['parent_id']
                menu_datalist[num]['children'] = []
                menu_data.append(menu_datalist[num])
                parent_id.append(menu_datalist[num]['id'])
                # print(menu_data)
                # print(parent_id)
            else:
                for n in range(len(parent_id)):
                    if menu_datalist[num]['parent_id'] == parent_id[n]:
                        del menu_datalist[num]['icon']
                        del menu_datalist[num]['parent_id']
                        menu_data[n]['children'].append(menu_datalist[num])
                        break
                    else:
                        continue
        context = {'menuData': menu_data}
        role = Role.objects.get(id=request.GET.get('roleId'))
        permissions = list(role.permissions.all().values())
        # print(permissions)
        menu_ids = []
        if permissions:
            for num in range(len(permissions)):
                menu_id = Menu.objects.get(title=permissions[num]['title']).id
                menu_ids.append(menu_id)
        context['checkedId'] = menu_ids
        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    if type == 'authorize':
        context = {}
        if request.method == 'POST':
            role = Role.objects.get(id=request.POST.get('roleId'))
            role.permissions.clear()
            auth_data = json.loads(request.POST.get('data'))
            for num in range(len(auth_data)):
                for n in range(len(auth_data[num]['children'])):
                    title = auth_data[num]['children'][n]['title']
                    auth = Permission.objects.filter(title=title).first()
                    if auth:
                        role.permissions.add(auth)
                        context['status'] = 'success'
                    else:
                        au = Permission()
                        url = ''
                        per_id = ''
                        if title == '订单审核':
                            url += "/management/orderAudit/home"
                            per_id += 'order_audit'
                        elif title == '处方查询':
                            url += "/management/prescriptionQuery/home"
                            per_id += 'prescri_query'
                        elif title == '订单初始化':
                            url += "/management/orderInitial/home"
                            per_id += 'order_initial'
                        elif title == '处方调剂':
                            url += "/management/Adjust/home"
                            per_id += 'prescription_adjust'
                        elif title == '商品管理':
                            url += "/management/goodsManage/home"
                            per_id += 'goods_manage'
                        elif title == '商品详情管理':
                            url += "/management/goodsDetailsManage/home"
                            per_id += 'goods_details_manage'
                        elif title == '品牌管理':
                            url += ""
                            per_id += 'brand_manage'
                        elif title == '分类管理':
                            url += ""
                            per_id += 'category_manage'
                        elif title == '菜单管理':
                            url += "/management/menuManage/home/"
                            per_id += 'menu_manage'
                        elif title == '用户管理':
                            url += "/management/userManage/home/"
                            per_id += 'user_manage'
                        elif title == '角色管理':
                            url += "/management/roleManage/home/"
                            per_id += 'role_manage'
                        elif title == '处方重打':
                            url += "/management/Adjust/rePrintPrescription/"
                            per_id += 're_print_prescription'
                        elif title == '煎煮中心管理':
                            url += "/management/decoctionCenterManage/home/"
                            per_id += 'decoction_center_manage'
                        elif title == '机构来源管理':
                            url += "/management/companyManage/home"
                            per_id += 'company_manage'
                        au.title = title
                        au.url = url
                        au.per_id = per_id
                        au.menu = Menu.objects.get(id=auth_data[num]['id'])
                        try:
                            au.save()
                            role.permissions.add(au)
                            context['status'] = 'success'
                        except Exception as e:
                            context['status'] = 'fail'
                            context['message'] = str(e)
                            print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/systemManage/user/role_authorize.html')
    if type == 'home':
        return render(request, 'backstage/systemManage/user/role_manage.html')


def get_role(request):
    roles = Role.objects.all()
    json_roles = serializers.serialize('json', roles)
    return HttpResponse(json_roles)


@csrf_exempt
def goods_manage(request, type):
    if type == 'addGoods':
        context = {}
        if request.method == 'POST':
            goods = Goods()
            keys = []
            values = []
            # print(request.POST)
            # print(request.POST.get('goodsCode'))
            alias = json.loads(request.POST.get('alias'))
            # print(alias)
            for key_value in alias.items():
                keys.append(key_value[0])
                values.append(key_value[1])
            # print(keys)
            # print(values)
            goods.goods_code = request.POST.get('goodsCode')
            goods.goods_name = request.POST.get('goodsName')
            goods.english_name = request.POST.get('englishName')
            goods.chinese_name = request.POST.get('chineseName')
            goods.unit = request.POST.get('unit')
            goods.short_code = request.POST.get('shortCode')
            goods.price = Decimal(request.POST.get('price')).quantize(Decimal('0.000'))
            if 'alias1' in keys:
                goods.alias1 = values[keys.index('alias1')]
            if 'alias2' in keys:
                goods.alias2 = values[keys.index('alias2')]
            if 'alias3' in keys:
                goods.alias3 = values[keys.index('alias3')]
            if 'alias4' in keys:
                goods.alias4 = values[keys.index('alias4')]
            if 'alias5' in keys:
                goods.alias5 = values[keys.index('alias5')]
            if 'alias6' in keys:
                goods.alias6 = values[keys.index('alias6')]
            if 'alias7' in keys:
                goods.alias7 = values[keys.index('alias7')]
            if 'alias8' in keys:
                goods.alias8 = values[keys.index('alias8')]
            if 'alias9' in keys:
                goods.alias9 = values[keys.index('alias9')]
            if 'alias10' in keys:
                goods.alias10 = values[keys.index('alias10')]
            try:
                goods.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/goods/add_goods.html')
    if type == 'goodsBatchImport':
        context = {}
        if request.method == 'POST':
            file = request.FILES['file']
            file_name = '%s/%s' % (settings.MEDIA_ROOT, file.name)
            # print(file_name)
            try:
                with open(file_name, 'wb') as f:
                    for f_file in file.chunks():
                        f.write(f_file)
                        context['status'] = 'success'
                        df = pd.read_excel(file_name)
                        # print(df)
                        drugs = []
                        count_control = 0
                        for num in range(len(df)):
                            drug = Goods(goods_code=df.loc[num]['商品编号'], goods_name=df.loc[num]['药材名'],
                                         short_code=df.loc[num]['代码'], chinese_name=df.loc[num]['中文名'],
                                         price=df.loc[num]['单价'], unit=df.loc[num]['单位'],
                                         oper_id=User.objects.get(username=request.session['username']).id)
                            if not pd.isna(df.loc[num]['英文名']):
                                drug.english_name = df.loc[num]['英文名']
                            if not pd.isna(df.loc[num]['库存']):
                                drug.stock = df.loc[num]['库存']
                            if df.loc[num]['是否停用'] != '否' or df.loc[num]['是否停用'] != '已停用':
                                drug.status = 1
                            else:
                                drug.status = 0
                            if not pd.isna(df.loc[num]['商品规格']):
                                drug.goods_norms = df.loc[num]['商品规格']
                            if not pd.isna(df.loc[num]['商品产地']):
                                drug.goods_orgin = df.loc[num]['商品产地']
                            if df.loc[num]['商品(药材)类型'] == '中药':
                                drug.goods_type = 0
                            else:
                                drug.goods_type = 1
                            if not pd.isna(df.loc[num]['别名1']):
                                drug.alias1 = df.loc[num]['别名1']
                            if not pd.isna(df.loc[num]['别名2']):
                                drug.alias2 = df.loc[num]['别名2']
                            if not pd.isna(df.loc[num]['别名3']):
                                drug.alias3 = df.loc[num]['别名3']
                            if not pd.isna(df.loc[num]['别名4']):
                                drug.alias4 = df.loc[num]['别名4']
                            if not pd.isna(df.loc[num]['别名5']):
                                drug.alias5 = df.loc[num]['别名5']
                            if not pd.isna(df.loc[num]['别名6']):
                                drug.alias6 = df.loc[num]['别名6']
                            if not pd.isna(df.loc[num]['别名7']):
                                drug.alias7 = df.loc[num]['别名7']
                            if not pd.isna(df.loc[num]['别名8']):
                                drug.alias8 = df.loc[num]['别名8']
                            if not pd.isna(df.loc[num]['别名9']):
                                drug.alias9 = df.loc[num]['别名9']
                            if not pd.isna(df.loc[num]['别名10']):
                                drug.alias10 = df.loc[num]['别名10']
                            count_control += 1
                            drugs.append(drug)
                            if count_control >= 100:  # 每100条数据执行一次插入
                                Goods.objects.bulk_create(drugs)
                                count_control = 0  # 计数归0
                                drugs.clear()  # 清空列表
                        Goods.objects.bulk_create(drugs)
                        context['message'] = '导入成功'
            except Exception as e:
                context['status'] = 'false'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/goods/BatchImportGoods.html')
    if type == 'editGoods':
        context = {}
        if request.method == 'POST':
            alias = json.loads(request.POST.get('alias'))
            goods = Goods.objects.get(goods_code=request.POST.get('goodsCode'))
            goods.alias1 = alias['alias1']
            goods.alias2 = alias['alias2']
            goods.alias3 = alias['alias3']
            goods.alias4 = alias['alias4']
            goods.alias5 = alias['alias5']
            goods.alias6 = alias['alias6']
            goods.alias7 = alias['alias7']
            goods.alias8 = alias['alias8']
            goods.alias9 = alias['alias9']
            goods.alias10 = alias['alias10']
            goods.unit = request.POST.get('unit')
            goods.stock = request.POST.get('stock')
            goods.price = request.POST.get('price')
            goods.short_code = request.POST.get('shortCode')
            try:
                goods.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        goods_code = request.GET.get('goods_code')
        # print(goods_code)
        goods = Goods.objects.get(goods_code=goods_code)
        return render(request, 'backstage/goods/edit_goods.html', locals())
    if type == 'updateStatus':
        context = {}
        status = request.GET.get('status')
        # print(status)
        if status:
            goods = Goods.objects.get(goods_code=request.GET.get('goodsCode'))
            if int(status) > 0:
                goods.status = 0
            else:
                goods.status = 1
            try:
                goods.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    if type == 'home':
        return render(request, 'backstage/goods/goods_manage.html')


@csrf_exempt
def goods_details_manage(request, type):
    if type == 'addGoodsDetails':
        context = {}
        if request.method == 'POST':
            goods_code = request.POST.get('goodsCode')
            goods_name = request.POST.get('goodsName')
            property = request.POST.get('property')
            channels = request.POST.get('channels')
            action = request.POST.get('action')
            usage_dosage = request.POST.get('usageDosage')
            precaution = request.POST.get('precaution')
            print('goodcode:%s\ngoodsname:%s\nproperty:%s\nchannels:%s\naction:%s\nusageDosage:%s\nprecaution:%s\s' %
                  (goods_code, goods_name, property, channels, action, usage_dosage, precaution))
            details = GoodsDetails()
            details.goods_code = goods_code
            details.goods_name = goods_name
            details.property = property
            details.channels = channels
            details.actions = action
            details.usage_dosage = usage_dosage
            details.precaution = precaution
            try:
                details.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/goods/add_goods_details.html')
    if type == 'detailBatchImport':
        return render(request, 'backstage/goods/BatchImportDetails.html')
    if type == 'home':
        return render(request, 'backstage/goods/goods_details_manage.html')


@csrf_exempt
def decoction_center_manage(request, type):
    context = {}
    if type == 'add':
        if request.method == 'POST':
            # print('name:%s\nnote:%s\nprovince:%s\ncity:%s\nzone:%s\naddress:%s' %
            #       (request.POST.get('name'), request.POST.get('note'), request.POST.get('province'),
            #        request.POST.get('city'), request.POST.get('zone'), request.POST.get('address')))
            exist_center = DecoctCenter.objects.all()
            center = DecoctCenter()
            center.name = request.POST.get('name')
            center.note = request.POST.get('note')
            center.province = request.POST.get('province')
            center.city = request.POST.get('city')
            center.zone = request.POST.get('zone')
            center.address = request.POST.get('address')
            if exist_center:
                pass
            else:
                center.code = '10000'
            try:
                center.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/systemManage/decoctionCenter/decoct_center_add.html')
    if type == 'updateStatus':
        status = request.GET.get('status')
        center = DecoctCenter.objects.get(code=request.GET.get('Code'))
        if int(status) > 0:
            center.status = 0
        else:
            center.status = 1
        try:
            center.save()
            context['status'] = 'success'
        except Exception as e:
            context['status'] = 'fail'
            context['message'] = str(e)
            print(context)
        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    if type == 'home':
        return render(request, 'backstage/systemManage/decoctionCenter/decoction_center_manage.html')


@csrf_exempt
def company_manage(request, type):
    context = {}
    if type == 'storagetype':
        centers = DecoctCenter.objects.all()
        json_roles = serializers.serialize('json', centers)
        return HttpResponse(json_roles)
    if type == 'add':
        if request.method == 'POST':
            exist_company = Institution.objects.all()
            company = Institution()
            company.company_name = request.POST.get('companyName')
            company.company_pass = md5(request.POST.get('companyPass').encode('utf-8')).hexdigest()
            storage_code = DecoctCenter.objects.get(code=request.POST.get('storageType'))
            company.storage_type = storage_code
            company.ascription = request.POST.get('ascription')
            company.short_name = request.POST.get('shortName')
            company.salesman = request.POST.get('salesMan')
            company.sales_tel = request.POST.get('salesTel')
            company.his_abutment = request.POST.get('hisAbutment')
            company.his_abutment_tel = request.POST.get('hisAbutmentTel')
            company.his_grade = request.POST.get('hisGrade')
            company.company_type = request.POST.get('companyType')
            company.is_doc_outh = request.POST.get('isDocOuth')
            company.is_send_msg = request.POST.get('isSendMsg')
            company.his_addr = request.POST.get('hosAddr')
            company.default_consignee = request.POST.get('defaultConsignee')
            company.distribution_description = request.POST.get('distributionDescription')
            company.default_tel = request.POST.get('defaultTel')
            company.defalut_addr = request.POST.get('defaultAddr')
            current_user = request.session['username']
            company.oper_id = User.objects.get(username=current_user)
            if exist_company:
                pass
            else:
                company.company_num = '10000'
            try:
                company.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/systemManage/company/add_company.html')
    if type == 'updateStatus':
        status = request.GET.get('status')
        company = Institution.objects.get(company_num=request.GET.get('companyNum'))
        if int(status) > 0:
            company.status = 0
        else:
            company.status = 1
        try:
            company.save()
            context['status'] = 'success'
        except Exception as e:
            context['status'] = 'fail'
            context['message'] = str(e)
            print(context)
        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    if type == 'edit':
        if request.method == 'POST':
            company = Institution.objects.get(company_num=request.POST.get('companyNum'))
            company.company_name = request.POST.get('companyName')
            storage_code = DecoctCenter.objects.get(code=request.POST.get('storageType'))
            company.storage_type = storage_code
            company.ascription = request.POST.get('ascription')
            company.short_name = request.POST.get('shortName')
            company.salesman = request.POST.get('salesMan')
            company.sales_tel = request.POST.get('salesTel')
            company.his_abutment = request.POST.get('hisAbutment')
            company.his_abutment_tel = request.POST.get('hisAbutmentTel')
            company.his_grade = request.POST.get('hisGrade')
            company.company_type = request.POST.get('companyType')
            company.is_doc_outh = request.POST.get('isDocOuth')
            company.is_send_msg = request.POST.get('isSendMsg')
            company.his_addr = request.POST.get('hosAddr')
            company.default_consignee = request.POST.get('defaultConsignee')
            company.distribution_description = request.POST.get('distributionDescription')
            company.default_tel = request.POST.get('defaultTel')
            company.defalut_addr = request.POST.get('defaultAddr')
            current_user = request.session['username']
            company.oper_id = User.objects.get(username=current_user)
            company.defalut_djdj = request.POST.get('defalutDjdj')
            try:
                company.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        company_num = request.GET.get('company_num')
        company = Institution.objects.get(company_num=company_num)
        return render(request, 'backstage/systemManage/company/edit_company.html', locals())
    if type == 'home':
        return render(request, 'backstage/systemManage/company/company_manage.html')


def prescription_query(request, type):
    if type == 'sourceId':
        sources = Institution.objects.all()
        json_sources = serializers.serialize('json', sources)
        return HttpResponse(json_sources)
    if type == 'pdDetail':
        pres_num = request.GET.get('prescri_id')
        pres_info = Prescription.objects.get(prescri_id=pres_num)
        suffering_unit_price = Decimal(pres_info.order_id.source_id.defalut_djdj).quantize(Decimal('0.00'))
        suffering_price = Decimal(int(pres_info.suffering_num) * suffering_unit_price).quantize(Decimal('0.00'))
        return render(request, 'backstage/customerServiceCenter/prescriptionDetail.html', locals())
    if type == 'home':
        return render(request, 'backstage/customerServiceCenter/prescriptionQuery.html')


@csrf_exempt
def order_audit(request, type):
    if type == 'addRemark':
        context = {}
        if request.method == 'POST':
            order_id = request.POST.get('orderId')
            order_remark = request.POST.get('remark')
            order = Order.objects.get(order_id=order_id)
            order.order_remark = order_remark
            try:
                order.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        order_id = request.GET.get('orderId')
        return render(request, 'backstage/customerServiceCenter/addRemark.html', locals())
    if type == 'auditPrescriptionInfo':
        prescri_id = request.GET.get('prescri_id')
        auto_audit_result = []
        drugs = PresDetails.objects.filter(prescri_id=prescri_id).values('medicines', 'dose', 'm_usage')
        reverse_18_and_fear_19 = reverse_18(*drugs) + fear_19(*drugs) + usage_match(*drugs) + poisonous_and_dose_match(*drugs)
        if reverse_18_and_fear_19:
            auto_audit_result = reverse_18_and_fear_19
        else:
            auto_audit_result.append('处方自动审核正常！')
        prescri_info = Prescription.objects.get(prescri_id=prescri_id)
        total_result = ''
        for result in auto_audit_result:
            total_result += result + '|'
        prescri_info.audit_result = total_result
        prescri_info.save()
        suffering_unit_price = Decimal(prescri_info.order_id.source_id.defalut_djdj).quantize(Decimal('0.00'))
        suffering_price = Decimal(int(prescri_info.suffering_num) * suffering_unit_price).quantize(Decimal('0.00'))
        return render(request, 'backstage/customerServiceCenter/audit_prescription_info.html', locals())
    if type == 'giveUpOrder':
        context = {}
        if request.method == 'POST':
            order_id = request.POST.get('orderId')
            give_up_reason = request.POST.get('giveUpReason')
            print(order_id)
            print(give_up_reason)
            order = Order.objects.get(order_id=order_id)
            order.order_status = 98
            order.reason = give_up_reason
            try:
                order.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/customerServiceCenter/give_up_order.html')
    if type == 'changeCenter':
        context = {}
        if request.method == 'POST':
            order_id = request.POST.get('orderId')
            change_reason = request.POST.get('changeReason')
            storage_type = request.POST.get('storageType')
            print(order_id)
            print(change_reason)
            print(storage_type)
            order = Order.objects.get(order_id=order_id)
            # order.storage_type = DecoctCenter.objects.get(code=storage_type)
            order.storage_type_id = storage_type
            order.reason = change_reason
            try:
                order.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        return render(request, 'backstage/customerServiceCenter/change_center.html')
    if type == 'auditOrder':
        context = {}
        order_id = request.GET.get('orderId')
        batch_num = request.GET.get('batchNum')
        order = Order.objects.get(order_id=order_id)
        order.batch = batch_num
        order.audit_id = User.objects.get(username=request.session['username']).id
        order.order_status = 15
        try:
            order.save()
            context['status'] = 'success'
        except Exception as e:
            context['status'] = 'fail'
            context['message'] = str(e)
            print(context)
        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    if type == 'home':
        return render(request, 'backstage/customerServiceCenter/orderAudit.html')


def order_initial(request, type):
    if type == 'initialStatus':
        order_id = request.GET.get('order_id')
        return render(request, 'backstage/customerServiceCenter/initial.html', locals())
    if type == 'initial':
        context = {}
        order_id = request.GET.get('orderId')
        order = Order.objects.get(order_id=order_id)
        prescription = Prescription.objects.get(order_id=order_id)
        order.order_status = 5
        order.audit_id = None
        order.batch = None
        order.order_remark = ''
        order.adjust_id = None
        order.reason = ''
        prescription.adjust_num = ''
        prescription.print_type = 0
        try:
            order.save()
            prescription.save()
            context['status'] = 'success'
        except Exception as e:
            context['status'] = 'fail'
            context['message'] = str(e)
            print(context)
        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    if type == 'home':
        return render(request, 'backstage/customerServiceCenter/orderInitial.html')


def prescription_adjust(request, type):
    if type == 'print':
        if not request.GET.get('order_id'):
            context = {}
            work_num = request.GET.get('workNum')
            user = User.objects.filter(work_num=work_num).first()
            if user and user.username == request.session['username']:
                context['status'] = 'success'
            else:
                context['status'] = 'fail'
                context['message'] = '工号错误，请核对！'
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        else:
            order_id = request.GET.get('order_id')
            prescription_id = request.GET.get('prescri_id')
            work_num = request.GET.get('workNum')
            order = Order.objects.get(order_id=order_id)
            prescription = Prescription.objects.get(prescri_id=prescription_id)
            order.adjust_id = User.objects.get(work_num=work_num).id
            prescription.print_type = 1
            prescription.adjust_num = work_num
            order.save()
            prescription.save()
            return render(request, 'backstage/adjustCenter/print_model.html', locals())
    if type == 'drugs':
        prescription_id = request.GET.get('prescriId')
        prescri_detail = list(PresDetails.objects.filter(prescri_id=prescription_id).values('medicines', 'dose', 'unit',
                                                                                            'm_usage', 'prescri_id__amount'))
        # print(prescri_detail)
        return HttpResponse(json.dumps(prescri_detail, ensure_ascii=False), content_type="application/json")
    if type == 'barcode':
        prescription_id = request.GET.get('prescriId')
        # print(prescription_id)
        code = generateBarcode(prescription_id)
        fp = BytesIO()
        # code.render(fp)
        code.write(fp, {'module_width': 0.5, 'module_height': 25, 'quiet_zone': 3, 'font_size': 45, 'text_distance': 3,
                        'dpi': 400})
        return HttpResponse(fp.getvalue(), content_type='image/png')
    if type == 'rePrintPrescription':
        pres_id = request.GET.get('presId')
        prescri_id = request.GET.get('prescri_id')
        if pres_id:
            context = {}
            prescription = Prescription.objects.filter(prescri_id=pres_id)
            if prescription.count() > 0:
                context['status'] = 'yes'
            else:
                context['status'] = 'no'
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
        if prescri_id:
            print(prescri_id)
            order_id = prescri_id.split('-')[0]
            print(order_id)
            order = Order.objects.get(order_id=order_id)
            prescription = Prescription.objects.get(prescri_id=prescri_id)
            return render(request, 'backstage/adjustCenter/print_model.html', locals())
        return render(request, 'backstage/adjustCenter/re_print_prescription.html')
    if type == 'home':
        return render(request, 'backstage/adjustCenter/prescription_adjust.html')


@csrf_exempt
def menu_manage(request, type):
    if type == 'menuAdd':
        context = {}
        if request.method == 'POST':
            menu = Menu()
            menu.title = request.POST.get('menuname')
            menu.icon = request.POST.get('menuicon')
            menu.menu_type = request.POST.get('menutype')
            menu.parent_id = request.POST.get('parentMenu')
            try:
                menu.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type='application/json')
        return render(request, 'backstage/systemManage/menu/menu_add.html')
    if type == 'parentMenu':
        parent_menu = Menu.objects.exclude(parent_id__gt=1)
        json_menus = serializers.serialize('json', parent_menu)
        return HttpResponse(json_menus)
    if type == 'menuEdit':
        context = {}
        if request.method == 'POST':
            menu = Menu.objects.get(id=request.POST.get('menuid'))
            menu.title = request.POST.get('menuname')
            menu.icon = request.POST.get('menuicon')
            menu.menu_type = request.POST.get('menutype')
            menu.parent_id = request.POST.get('parentMenu')
            try:
                menu.save()
                context['status'] = 'success'
            except Exception as e:
                context['status'] = 'fail'
                context['message'] = str(e)
                print(context)
            return HttpResponse(json.dumps(context, ensure_ascii=False), content_type='application/json')
        return render(request, 'backstage/systemManage/menu/menu_add.html')
    if type == 'menuDelete':
        context = {}
        try:
            Menu.objects.get(id=request.POST.get('delData')).delete()
            context['status'] = 'success'
        except Exception as e:
            context['status'] = 'fail'
            context['message'] = str(e)
        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    if type == 'home':
        return render(request, 'backstage/systemManage/menu/menu_manage.html')
