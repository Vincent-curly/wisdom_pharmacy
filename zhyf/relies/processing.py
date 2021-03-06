# coding:utf-8
"""
  Time : 2021/1/27 下午3:01
  Author : vincent
  FileName: processing
  Software: PyCharm
  Last Modified by: vincent
  Last Modified time: 2021/1/27 下午3:01
"""
import logging
import time

from management.models import Institution, DecoctCenter
from services.models import Order, Prescription, PresDetails
from relies.handle import md5_creat_password

logger = logging.getLogger('log')


def save_order_data_validation(dict_data):
    try:
        company_num = Institution.objects.get(company_num=dict_data['company_num'])
    except Exception:
        logger.info('公司认证失败')
        return {'resultCode': 2, 'state': 'fail', 'description': '公司认证失败'}
    company_pass = company_num.company_pass
    receive_key = int(dict_data['key'])
    local_key = int(time.time() * 1000)
    delta = local_key - receive_key
    if delta > 60000:
        logger.info('签名过期')
        return {'resultCode': 4, 'state': 'fail', 'description': '签名过期'}
    local_save_order_sign = md5_creat_password("saveOrderInfo" + dict_data['key'] + company_pass)
    if local_save_order_sign != dict_data['sign'].upper():
        logger.info('密码错误')
        return {'resultCode': 3, 'state': 'fail', 'description': '密码错误'}
    necessarys = ['order_time', 'reg_num', 'addr_str', 'consignee', 'con_tel', 'user_name', 'age', 'gender', 'tel',
                  'is_suffering', 'suffering_num', 'amount', 'is_within', 'other_pres_num', 'medicines', 'dose',
                  'goods_num']
    check_items = []
    for necessary in necessarys:
        if not dict_data.get(necessary):
            check_items.append(necessary)
        elif necessary == 'is_suffering' and dict_data['is_suffering'] == 1:
            if dict_data.get('suffering_num') and dict_data.get('suffering_num') > 0:
                continue
            else:
                check_items.append(necessary)
    if check_items:
        logger.info('异常参数:%s' % check_items)
        return {'resultCode': 1, 'state': 'fail', 'description': '参数异常'}
    return makeOrder(dict_data)


def cancel_order_data_validation(dict_data):
    try:
        company = Institution.objects.get(company_num=dict_data['company_num'])
    except Exception:
        return {'resultCode': 2, 'state': 'fail', 'description': '公司认证失败'}
    company_pass = company.company_pass
    receive_key = int(dict_data['key'])
    local_key = int(time.time() * 1000)
    delta = local_key - receive_key
    if delta > 60000:
        return {'resultCode': 4, 'state': 'fail', 'description': '签名过期'}
    local_cancel_order_sign = md5_creat_password("cancelOrder" + dict_data['key'] + company_pass)
    if local_cancel_order_sign != dict_data['sign'].upper():
        return {'resultCode': 3, 'state': 'fail', 'description': '密码错误'}
    return cancel_order(dict_data)


def makeOrder(dict_data):
    if Order.objects.filter(reg_num=dict_data['reg_num']).count() >= 1:
        logger.info('重复提交订单')
        return {'resultCode': 22, 'state': 'fail', 'description': '重复提交订单'}
    else:
        order_all_list = Order.objects.all()
        logger.info(order_all_list)
        logger.info("订单表 tb_order 中原记录条数:%s" % len(order_all_list))
        order_id = 'KM' + time.strftime('%y%m%d', time.localtime()) + format(len(order_all_list) + 1, '0>5')
        logger.info('生成订单号:%s' % order_id)
        order_information = Order(order_id=order_id, source_id=Institution.objects.get(company_num=dict_data['company_num']),
                                  order_time=dict_data['order_time'], treat_card=dict_data.get('treat_card', None),
                                  reg_num=dict_data['reg_num'], addr_str=dict_data['addr_str'],
                                  provinces=dict_data['addr_str'].split(',')[0],
                                  city=dict_data['addr_str'].split(',')[1],
                                  zone=dict_data['addr_str'].split(',')[2],
                                  consignee=dict_data['consignee'], con_tel=dict_data['con_tel'],
                                  send_goods_time=dict_data.get('send_goods_time', ''),
                                  storage_type=DecoctCenter.objects.get(code=10000),
                                  is_hos_addr=dict_data.get('is_hos_addr', 0))
        try:
            order_information.save()
        except Exception as e:
            logger.error(e)
            return {'resultCode': 5, 'description': '失败', 'state': 'fail', 'reg_num': order_information.reg_num,
                    'IsSuccess': 'false', 'message': str(e)}
        prescri_information = Prescription(prescri_id=order_id + '-1', order_id=Order.objects.get(order_id=order_id),
                                           user_name=dict_data['user_name'],
                                           age=dict_data['age'], gender=dict_data['gender'], tel=dict_data['tel'],
                                           is_pregnant=dict_data.get('is_pregnant', 2),
                                           is_hos=dict_data.get('is_hos', 0),
                                           is_suffering=dict_data['is_suffering'], amount=dict_data['amount'],
                                           suffering_num=dict_data['suffering_num'],
                                           ji_fried=dict_data.get('ji_fried', 1),
                                           prescri_type=dict_data.get('prescri_type', 0), is_within=dict_data['is_within'],
                                           other_pres_num=dict_data['other_pres_num'],
                                           special_instru=dict_data.get('special_instru', ''),
                                           bed_num=dict_data.get('bed_num', ''),
                                           hos_depart=dict_data.get('hos_depart', ''),
                                           hospital_num=dict_data.get('hospital_num', ''),
                                           disease_code=dict_data.get('disease_code', ''), doctor=dict_data.get('doctor', ''),
                                           paste_desc_file=dict_data.get('paste_desc_file', ''),
                                           prescript_remark=dict_data.get('prescript_remark', ''),
                                           per_pack_num=dict_data.get('per_pack_num', 0),
                                           per_pack_dose=dict_data.get('per_pack_dose', 150),
                                           medication_methods=dict_data.get('medication_methods', ''),
                                           medication_instruction=dict_data.get('medication_instruction', ''))
        try:
            prescri_information.save()
        except Exception as e:
            logger.error(e)
            return {'resultCode': 5, 'description': '失败', 'state': 'fail', 'reg_num': order_information.reg_num,
                    'IsSuccess': 'false', 'message': str(e)}
        pres_detail_information_list = []
        medicine_count = len(dict_data['medicines'])
        for num in range(medicine_count):
            pres_detail_information = PresDetails(prescription_details_id=order_id + '-1-' + str(num + 1),
                                                  prescri_id=Prescription.objects.get(prescri_id=order_id + '-1'),
                                                  medicines=dict_data['medicines'][num],
                                                  goods_num=dict_data['goods_num'][num], dose=dict_data['dose'][num],
                                                  unit=dict_data['unit'][num], m_usage=dict_data['m_usage'][num],
                                                  goods_norms=dict_data.get('goods_norms', [None] * medicine_count)[
                                                      num],
                                                  goods_orgin=dict_data.get('goods_orgin', [None] * medicine_count)[
                                                      num],
                                                  remark=dict_data.get('remark', [None] * medicine_count)[num],
                                                  dose_that=dict_data.get('dose_that', [None] * medicine_count)[num],
                                                  company_num=dict_data['company_num'],
                                                  unit_price=dict_data.get('unit_price', ['0.00'] * medicine_count)[num],
                                                  MedPerDos=dict_data.get('MedPerDos', [None] * medicine_count)[num],
                                                  MedPerDay=dict_data.get('MedPerDay', [None] * medicine_count)[num])
            pres_detail_information_list.append(pres_detail_information)
        logger.info("开始连接数据库提交数据")
        try:
            logger.info('prescri_details:%s' % pres_detail_information_list)
            PresDetails.objects.bulk_create(pres_detail_information_list)
            logger.info('数据库数据提交成功')
            return {'resultCode': 0, 'description': '成功', 'state': 'success', 'reg_num': order_information.reg_num,
                    'IsSuccess': 'true', 'message': '成功', 'orderid': order_information.order_id,
                    'prescriptionIds': prescri_information.prescri_id
                    }
        except Exception as e:
            logger.error(e)
            return {'resultCode': 5, 'description': '失败', 'state': 'fail', 'reg_num': order_information.reg_num,
                    'IsSuccess': 'false', 'message': str(e)}


def cancel_order(dict_data):
    order = Order.objects.get(order_id=dict_data.get('order_id'))
    if order:
        if order.order_status <= 5:
            order.order_status = 99
            order.reason = dict_data.get('operate_name') + ':' + dict_data.get('reason')
            try:
                order.save()
                return {'status': 'success'}
            except Exception as e:
                logger.error(e)
                return {'status': 'fail', 'message': str(e)}
        else:
            return {'status': 'fail', 'message': '订单已调剂,不能取消！'}
    else:
        return {'status': 'fail', 'message': '无该订单号,请确认！'}


if __name__ == '__main__':
    order_info = {'orderInfo': None, 'head': None, 'company_num': '10426', 'sign': 'ab310c9638f50b64cd8ae1d8f90341ca', 'key': '1582387461673', 'data': None, 'order_time': '2020-02-23 00:04:09', 'reg_num': 'M2020022300041045834', 'addr_str': '四川省,成都市,新津县,新津县林园路58号', 'consignee': '杨绍琼', 'con_tel': '15388103153', 'pay_status': '1', 'callback_url': 'http://yaofang.bailuzy.com/api/kangmei/orderUpdate?param=eyJvcmRlcl9zbiI6Ik0yMDIwMDIyMzAwMDQxMDQ1ODM0Iiwic2lnbiI6IjE5YzBiNDRhMTk1MDI2NzdmZTJmZDZkM2YxY2M4ZGRkIn0=', 'logis_url_callback': 'http://yaofang.bailuzy.com/api/kangmei/expressUpdate?param=eyJvcmRlcl9zbiI6Ik0yMDIwMDIyMzAwMDQxMDQ1ODM0Iiwic2lnbiI6IjE5YzBiNDRhMTk1MDI2NzdmZTJmZDZkM2YxY2M4ZGRkIn0=', 'prescript': None, 'pdetail': None, 'user_name': '杨绍琼', 'age': '62', 'gender': '0', 'tel': '15388103153', 'is_suffering': '0', 'suffering_num': '0', 'ji_fried': '0', 'amount': '3', 'prescri_type': '0', 'wj_type': None, 'is_within': '0', 'other_pres_num': 'KM_M2020022300041045834', 'special_instru': '脾虚湿热证', 'doctor': '白露中医', 'package_dose': None, 'is_invoice': '0', 'medication_instruction': '每日1帖,每贴3次', 'prescript_remark': '用药时间:两餐间服用,注意事项:忌生冷,忌辛辣,忌油腻,忌发物,忌荤腥,忌烟酒,温服30-40℃', 'medication_methods': None, 'per_pack_num': '3', 'medici_xq': None, 'xq': None, 'medicines': ['知母', '玄参', '芦根', '肉桂', '黄连', '仙鹤草', '豆蔻', '薏苡仁', '姜厚朴', '柴胡（北柴胡）', '白芍', '当归', '茯神', '炙甘草', '炮姜', '青皮', '燀苦杏仁', '干石斛', '南沙参', '白术'], 'dose': ['15', '15', '20', '5', '3', '20', '10', '15', '15', '15', '15', '10', '20', '5', '5', '10', '10', '10', '15', '15'], 'unit': ['克', '克', '克', '克', '克', '克', '克', '克', '克', '克', '克', '克', '克', '克', '克', '克', '克', '克', '克', '克'], 'unit_price': ['0.14868', '0.09306', '0.08550', '0.09666', '0.46296', '0.06624', '0.26622', '0.05490', '0.08190', '0.37566', '0.11628', '0.19026', '0.17604', '0.12654', '0.11502', '0.08676', '0.12006', '0.41796', '0.17460', '0.12402'], 'goods_num': ['35', '29', '496', '179', '226', '454', '342', '408', '405', '41', '403', '36', '146', '42', '64', '24', '918', '139', '28', '188'], 'm_usage': [None, None, None, '后下', None, None, '后下', None, None, None, None, None, None, None, None, None, None, None, None, None]}
    save_order_data_validation(order_info)
