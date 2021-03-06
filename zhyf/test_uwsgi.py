# coding:utf-8
"""
  Time : 2021/1/28 下午5:49
  Author : vincent
  FileName: test_uwsgi
  Software: PyCharm
  Last Modified by: vincent
  Last Modified time: 2021/1/28 下午5:49
"""
# 测试py文件
# test.py


def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    return [b"Hello World"] # python3
    # return ["Hello World"] # python2
