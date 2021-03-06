# coding:utf-8
"""
  Time : 2021/1/27 下午2:57
  Author : vincent
  FileName: views
  Software: PyCharm
  Last Modified by: vincent
  Last Modified time: 2021/1/27 下午2:57
"""
import json
import logging
import base64
from spyne import Application, rpc, ServiceBase
from spyne import String, Integer
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from django.views.decorators.csrf import csrf_exempt
from relies.handle import XmlEnvelopeTree
from relies.processing import save_order_data_validation, cancel_order_data_validation

logger = logging.getLogger('log')


class OrderServices(ServiceBase):
    """声明服务的类，类的方法，就是客户端访问的服务，业务逻辑，操作都在这里面"""

    @rpc(String, _returns=String)
    def saveOrderInfo(self, request):
        """
        保存订单接口
        :param request: 接收的请求
        :return: 订单保存结果
        """
        logger.info('接收到请求:%s' % request)
        rq_decode = base64.b64decode(request.encode('utf-8')).decode()
        logger.info('请求参数:%s' % rq_decode)
        env_tree = XmlEnvelopeTree(rq_decode)
        dict_data = env_tree.xml_to_dict()
        logger.info('请求体字典数据:%s' % dict_data)
        result = save_order_data_validation(dict_data)
        xml_tree = XmlEnvelopeTree(result)
        logger.info('响应数据：%s' % xml_tree.envelope_encode())
        return base64.b64encode(xml_tree.envelope_encode().encode('utf-8')).decode()

    @rpc(String, _returns=String)
    def acceptUserAddrInfo(self, request):
        """
        保存推送过来的地址信息接口
        :param request: 接收的请求
        :return: 地址保存结果
        """
        logger.info('接收到请求:%s' % request)
        rq_decode = base64.b64decode(request.encode('utf-8')).decode()
        logger.info('请求参数:%s' % rq_decode)
        env_tree = XmlEnvelopeTree(rq_decode)
        dict_data = env_tree.xml_to_dict()
        logger.info('请求体字典数据:%s' % dict_data)
        # result = saveaddr_to_db(dict_data)
        # xml_tree = XmlEnvelopeTree(result)
        # logging.info('响应数据：%s' % xml_tree.envelope_encode())
        # return base64.b64encode(xml_tree.envelope_encode().encode('utf-8')).decode()

    @rpc(String, _returns=String)
    def cancelOrder(self, request):
        """
        取消推送过来的订单接口
        :param request: 接收的请求
        :return: 订单取消结果
        """
        logger.info("接收到请求：%s" % request)
        rq_decode = base64.b64decode(request.encode('utf-8')).decode()
        logger.info('请求参数:%s' % rq_decode)
        env_tree = XmlEnvelopeTree(rq_decode)
        dict_data = env_tree.xml_to_dict()
        logger.info('请求体字典数据:%s' % dict_data)
        result = cancel_order_data_validation(dict_data)
        xml_tree = XmlEnvelopeTree(result)
        logger.info('响应数据:%s' % xml_tree.envelope_encode())
        return base64.b64encode(xml_tree.envelope_encode().encode('utf-8')).decode()


soap_app = Application([OrderServices],
                       tns='webservice_test.myservice.views',
                       # in_protocol=HttpRpc(validator='soft'),
                       # 'SampleServices',
                       in_protocol=Soap11(validator="lxml"),
                       out_protocol=Soap11())
django_app = DjangoApplication(soap_app)
sum_app = csrf_exempt(django_app)
logger.info("wsdl is at: http://120.79.173.198:8000/OrderServices?wsdl")
