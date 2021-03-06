from django.db import models

# Create your models here.


class Role(models.Model):
    """后台角色信息表"""
    role_name = models.CharField(max_length=50, unique=True, null=False, verbose_name='角色名称')
    permissions = models.ManyToManyField("Permission")
    # 定义角色和权限的多对多关系

    class Meta:
        db_table = 'tb_role'
        verbose_name = verbose_name_plural = '角色信息表'


class Menu(models.Model):
    """菜单"""
    title = models.CharField(max_length=32, unique=True, verbose_name='菜单名称')
    icon = models.CharField(max_length=100, verbose_name='菜单图标', null=True, blank=True)
    menu_type = models.CharField(max_length=10, verbose_name='菜单类型')
    parent = models.ForeignKey("Menu", null=True, blank=True, on_delete=models.CASCADE)
    # 定义菜单间的自引用关系
    # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）
    # blank=True 意味着在后台管理中填写可以为空，根菜单没有父级菜单

    def __str__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)

    class Meta:
        db_table = 'tb_menu'
        verbose_name = verbose_name_plural = "菜单"


class Permission(models.Model):
    """权限"""
    title = models.CharField(max_length=32, unique=True, verbose_name='权限')
    url = models.CharField(max_length=128)
    per_id = models.CharField(max_length=100, verbose_name='选项卡id', null=True, blank=True)
    menu = models.ForeignKey("Menu", null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        # 显示带菜单前缀的权限
        return '{menu}---{permission}'.format(menu=self.menu, permission=self.title)

    class Meta:
        db_table = 'tb_authority'
        verbose_name = verbose_name_plural = "权限"


class User(models.Model):
    """后台管理用户信息表"""
    # user_id = models.AutoField(primary_key=True, verbose_name='用户ID')
    username = models.CharField(max_length=50, unique=True, null=False, verbose_name='用户名')
    work_num = models.CharField(max_length=50, unique=True, null=True, verbose_name='工号')
    name = models.CharField(max_length=50, null=True, unique=True, verbose_name='姓名')
    password = models.CharField(max_length=100, null=False, verbose_name='密码')
    email = models.CharField(max_length=100, verbose_name='电子邮箱')
    nickname = models.CharField(max_length=100, verbose_name='昵称')
    department = models.CharField(max_length=100, verbose_name='部门')
    register_time = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    # auto_now_add：当对象首次被创建时,自动将该字段的值设置为当前时间.通常用于表示对象创建时间
    # auto_now：当对象被保存时, 自动将该字段的值设置为当前时间.通常用于表示 “last - modified” 时间戳
    login_time = models.DateTimeField(auto_now_add=False, null=True, verbose_name='最近登录时间')
    rank = models.IntegerField(default=0, verbose_name='管理员级别')
    is_disabled = models.IntegerField(default=1, verbose_name='是否禁用')
    rights = models.CharField(max_length=100, verbose_name='权限')
    # role = models.ForeignKey('Role', on_delete=models.CASCADE, verbose_name='角色')
    role = models.ManyToManyField("Role")

    class Meta:
        db_table = 'tb_admin'
        verbose_name = verbose_name_plural = '用户信息表'


class Goods(models.Model):
    """商品(中药饮片)信息表"""
    goods_code = models.CharField(max_length=10, unique=True, verbose_name='商品编码')
    goods_name = models.CharField(max_length=50, null=False, verbose_name='商品名称')
    short_code = models.CharField(max_length=50, null=False, verbose_name='简码(商品名称首字母大写)')
    english_name = models.CharField(max_length=100, null=False, verbose_name='英文名称')
    chinese_name = models.CharField(max_length=100, null=False, verbose_name='中文名称')
    price = models.DecimalField(max_digits=10, decimal_places=5, default=0, verbose_name='价格')
    stock = models.IntegerField(default=0, verbose_name='库存')
    unit = models.CharField(max_length=5, default='g', verbose_name='单位')
    status = models.IntegerField(default=1, verbose_name='是否停用')
    alias1 = models.CharField(max_length=20, verbose_name='别名1')
    alias2 = models.CharField(max_length=20, verbose_name='别名2')
    alias3 = models.CharField(max_length=20, verbose_name='别名3')
    alias4 = models.CharField(max_length=20, verbose_name='别名4')
    alias5 = models.CharField(max_length=20, verbose_name='别名5')
    alias6 = models.CharField(max_length=20, verbose_name='别名6')
    alias7 = models.CharField(max_length=20, verbose_name='别名7')
    alias8 = models.CharField(max_length=20, verbose_name='别名8')
    alias9 = models.CharField(max_length=20, verbose_name='别名9')
    alias10 = models.CharField(max_length=20, verbose_name='别名10')
    goods_norms = models.CharField(max_length=100, null=True, verbose_name='商品规格')
    goods_orgin = models.CharField(max_length=100, null=True, verbose_name='商品产地')
    goods_type = models.SmallIntegerField(default='0', verbose_name='商品(药材)类型:0 中药，1 西药')
    oper_id = models.IntegerField(null=True, verbose_name='主要记录修改者，方便追溯')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='数据更新时间')

    class Meta:
        db_table = 'tb_goods'
        verbose_name = verbose_name_plural = '商品信息表'


class GoodsDetails(models.Model):
    goods_code = models.CharField(max_length=10, primary_key=True, verbose_name='商品编码')
    goods_name = models.CharField(max_length=50, null=False, verbose_name='商品名称')
    property = models.CharField(max_length=100, verbose_name='性味')
    channels = models.CharField(max_length=100, verbose_name='归经')
    actions = models.TextField(verbose_name='功效作用')
    usage_dosage = models.TextField(verbose_name='用法用量')
    precaution = models.CharField(max_length=200, verbose_name='禁忌')

    class Meta:
        db_table = 'tb_goodsDetails'
        verbose_name = verbose_name_plural = '商品详情表'


class DecoctCenter(models.Model):
    """煎煮中心信息表"""
    code = models.AutoField(primary_key=True, verbose_name='煎煮中心编号')
    name = models.CharField(max_length=50, unique=True, null=False, verbose_name='煎煮中心名称')
    note = models.CharField(max_length=50, default='', verbose_name='备注')
    register_time = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    province = models.CharField(max_length=10, null=False, verbose_name='煎煮中心所在省份')
    city = models.CharField(max_length=10, null=False, verbose_name='煎煮中心所在城市')
    zone = models.CharField(max_length=10, null=False, verbose_name='煎煮中心所在区县')
    address = models.CharField(max_length=200, null=False, verbose_name='煎煮中心详细地址')
    status = models.SmallIntegerField(default=1, verbose_name='是否停用')

    class Meta:
        db_table = 'tb_decoct_center'
        verbose_name = verbose_name_plural = '煎煮中心信息表'


class Institution(models.Model):
    """机构信息表类"""
    company_num = models.AutoField(primary_key=True, verbose_name='机构编号')
    company_name = models.CharField(max_length=32, unique=True, verbose_name='机构名称')
    register_time = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    status = models.SmallIntegerField(default=1, verbose_name='是否停用')
    company_pass = models.CharField(max_length=50, verbose_name='密码')
    company_type = models.IntegerField(default=0, verbose_name='公司类型  0 医院管理系统, 1 医院his, 2 其他')
    storage_type = models.ForeignKey('DecoctCenter', on_delete=models.CASCADE, verbose_name='煎煮中心')
    is_doc_outh = models.IntegerField(default=0, verbose_name='提供给第三方移动网络平台医生认证 0 不需要，1 需要')
    is_send_msg = models.IntegerField(default=0, verbose_name='0发短信,1不发短信')
    salesman = models.CharField(max_length=20, verbose_name='业务员')
    sales_tel = models.CharField(max_length=20, verbose_name='业务员电话')
    his_abutment = models.CharField(max_length=20, verbose_name='医院对接人')
    his_abutment_tel = models.CharField(max_length=20, verbose_name='医院对接人电话')
    his_grade = models.CharField(max_length=50, verbose_name='医院的分类比如三甲医院、二甲医院、社区医院')
    his_addr = models.CharField(max_length=255, verbose_name='医院地址')
    business_practice_name = models.CharField(max_length=1000, verbose_name='营业执照')
    medical_licensing_license_name = models.CharField(max_length=1000, verbose_name='医疗机构执业许可证')
    distribution_description = models.CharField(max_length=255, verbose_name='配送时段描述')
    default_consignee = models.CharField(max_length=255, verbose_name='默认收货人')
    default_tel = models.CharField(max_length=255, verbose_name='默认收货人电话')
    defalut_addr = models.CharField(max_length=255, verbose_name='默认收货地址')
    defalut_djdj = models.FloatField(default=1.5, verbose_name='默认代煎价格')
    isOnline = models.IntegerField(default=0, verbose_name='对接完成:0是未上线，1是已上线(目前数据不准确,需要实时更新)')
    oper_id = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='主要记录修改者id,方便追溯')
    short_name = models.CharField(max_length=255, verbose_name='简称')
    platform_type = models.IntegerField(default=0, verbose_name='订单煎煮中心分配规则:0 默认 ,1 按医疗机构 ,2 按地址')
    ascription = models.IntegerField(default=0, verbose_name='机构所属分类 0 医院, 1 企业单位')

    class Meta:
        db_table = 'tb_off_oper'
        verbose_name = verbose_name_plural = '医疗机构信息'



