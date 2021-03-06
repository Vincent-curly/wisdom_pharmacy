# coding:utf-8
"""
  Time : 2021/1/27 下午3:30
  Author : vincent
  FileName: authorityControl
  Software: PyCharm
  Last Modified by: vincent
  Last Modified time: 2021/1/27 下午3:30
"""
from django.utils.safestring import mark_safe


def get_menu_html(menu_data, permission_data):
    """显示：菜单 + [子菜单] + 权限(url)"""
    menu_str = """
    <a href="javascript:;"><span class="{menu_icon}"></span>&nbsp;&nbsp;{menu_title}</a>
    """

    permission_str = """
        <dd><a data-url="{per_url}" data-id="{per_id}" data-title="{per_title}" class="nav-active"
            href="javascript:;" data-type="tabAdd">&nbsp;&nbsp;&nbsp;<span class="iconfont icon-node-tree1"></span>&nbsp;&nbsp;{per_title}</a></dd>
    """
    final_html = """<li class="layui-nav-item">
                    <a href="javascript:;"><span class="iconfont icon-zhuye"></span>&nbsp;&nbsp;首页</a>
                </li>"""
    permission_html = ''
    menu_html = ''
    # for menu in menu_data:
    for num in range(len(menu_data)):
        menu_html += menu_str.format(menu_icon=menu_data[num]['icon'], menu_title=menu_data[num]['title'])
        # for item in permission_data:
        final_html += '<li class="layui-nav-item">' + menu_html + '<dl class="layui-nav-child">'
        menu_html = ''
        for n in range(len(permission_data)):
            if permission_data[n]['menu_id'] == menu_data[num]['id']:
                permission_html += permission_str.format(
                    per_url=permission_data[n]['url'],
                    per_id=permission_data[n]['per_id'],
                    per_title=permission_data[n]['title'])
                final_html += permission_html
                permission_html = ''
                if n == len(permission_data) - 1:
                    final_html += '</dl></li>'
            else:
                if n == len(permission_data) - 1:
                    final_html += '</dl></li>'
                    break
                elif n < len(permission_data) - 1:
                    continue
    return mark_safe(final_html)        # 返回字符串用mark_safe，否则传到模板会转义


if __name__ == '__main__':
    permitions = [
        # {'title': '订单审核', 'url': "{% url 'management:orderAudit' type='home' %}", 'menu_id': 1, 'per_id': 'order_audit'},
        # {'title': '处方查询', 'url': "{% url 'management:prescriptionQuery' type='home' %}", 'menu_id': 1, 'per_id': 'prescri_query'},
        # {'title': '订单初始化', 'url': "{% url 'management:orderInitial' type='home' %}", 'menu_id': 1, 'per_id': 'order_initial'},
        # {'title': '处方调剂', 'url': "{% url 'management:Adjust' type='home' %}", 'menu_id': 2, 'per_id': 'prescription_adjust'},
        # {'title': '商品管理', 'url': "{% url 'management:goodsManage' %}", 'menu_id': 3, 'per_id': 'goods_manage'},
        # {'title': '商品详情管理', 'url': "{% url 'management:goodsDetailsManage' %}", 'menu_id': 3, 'per_id': 'goods_details_manage'},
        # {'title': '品牌管理', 'url': '', 'menu_id': 3, 'per_id': 'brand_manage'},
        # {'title': '分类管理', 'url': '', 'menu_id': 3, 'per_id': 'category_manage'},
        {'title': '菜单管理', 'url': "{% url 'management:menuManage' type='home' %}", 'menu_id': 4, 'per_id': 'menu_manage'},
        {'title': '用户管理', 'url': "{% url 'management:userManage' %}", 'menu_id': 4, 'per_id': 'user_manage'},
        {'title': '角色管理', 'url': "{% url 'management:roleManage' type='home' %}", 'menu_id': 4, 'per_id': 'role_manage'},
        {'title': '煎煮中心管理', 'url': "{% url 'management:decoctionCenterManage' type='home' %}", 'menu_id': 4, 'per_id': 'decoction_center_manage'},
        {'title': '机构来源管理', 'url': "{% url 'management:companyManage' type='home' %}", 'menu_id': 4, 'per_id': 'company_manage'}
    ]
    menu_list = [
        # {'id': 1, 'title': '客服中心', 'icon': 'iconfont icon-huaban-'}
        # {'id': 2, 'title': '调剂中心', 'icon': 'iconfont icon-jiaoyiguanli'},
        # {'id': 3, 'title': '产品管理', 'icon': 'iconfont icon-chanpinguanli2'},
        {'id': 4, 'title': '系统管理', 'icon': 'iconfont icon-xitongguanli2'}
    ]
    print(get_menu_html(menu_list, permission_data=permitions))