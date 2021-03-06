from django.db import models

# Create your models here.


class Order(models.Model):
    """订单表类"""
    order_id = models.CharField(max_length=36, null=False, primary_key=True, verbose_name='订单id')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='订单创建时间(本地)')
    source_id = models.ForeignKey("management.Institution", on_delete=models.CASCADE, null=False,
                                  verbose_name='订单来源 机构编码')
    order_time = models.CharField(max_length=25, verbose_name='订单生成时间(医院)')
    treat_card = models.CharField(max_length=50, null=True, verbose_name='诊疗卡号')
    reg_num = models.CharField(max_length=50, null=False, verbose_name='挂单号')
    addr_str = models.CharField(max_length=120, null=False, verbose_name='收货地址')
    provinces = models.CharField(max_length=10, verbose_name='省份')
    city = models.CharField(max_length=10, verbose_name='城市')
    zone = models.CharField(max_length=10, verbose_name='区')
    consignee = models.CharField(max_length=20, null=False, verbose_name='收货人')
    con_tel = models.CharField(max_length=50, null=False, verbose_name='收货人电话')
    send_goods_time = models.CharField(max_length=25, null=True, verbose_name='送货时间')
    storage_type = models.ForeignKey("management.DecoctCenter", on_delete=models.CASCADE, verbose_name='仓库')
    is_hos_addr = models.IntegerField(null=False, verbose_name='是否送医院 0 未知, 1 送医院,2 送病人家里')
    update_time = models.DateTimeField(auto_now=True, verbose_name='数据更新时间')
    order_status = models.SmallIntegerField(default=5,
                                            verbose_name='状态 录入0-审核5-用户确认10-调剂中15-备药完成17-打包完成18-物流分拨20'
                                                         '-派送完毕25 -用户拒收97-审核失败98-用户放弃99')
    order_remark = models.CharField(max_length=100, null=True, verbose_name='订单备注')
    reason = models.CharField(max_length=500, default='', verbose_name='原因')
    audit_id = models.IntegerField(null=True, verbose_name='审核人员id')
    adjust_id = models.IntegerField(null=True, verbose_name='调剂人员id')
    batch = models.IntegerField(null=True, verbose_name='批次 1早批次 2午批次 3晚批次')

    class Meta:
        db_table = 'tb_order'
        verbose_name = verbose_name_plural = '订单信息'


class Prescription(models.Model):
    """处方表类"""
    prescri_id = models.CharField(max_length=36, null=False, primary_key=True, verbose_name='处方ID')
    order_id = models.ForeignKey('Order', on_delete=models.CASCADE, null=False, verbose_name='订单id')
    user_name = models.CharField(max_length=20, null=False, verbose_name='患者姓名')
    age = models.IntegerField(null=False, verbose_name='患者年龄')
    gender = models.IntegerField(null=False, verbose_name='患者性别 0 女，1 男，2 未知(病人没有登记性别的情况下)')
    tel = models.CharField(max_length=50, null=False, verbose_name='患者电话')
    is_pregnant = models.IntegerField(verbose_name='是否为孕妇 0 非孕妇，1 孕妇, 2 未知')
    is_hos = models.IntegerField(null=False, verbose_name='处方来源类型 0 默认,1门诊,2住院,3 其他')
    is_suffering = models.IntegerField(null=False, verbose_name='是否煎煮 取值范围：0 否，1 是')
    amount = models.IntegerField(null=False, verbose_name='剂数(付数)')
    suffering_num = models.IntegerField(null=False, verbose_name='煎煮袋数')
    ji_fried = models.IntegerField(verbose_name='几煎')
    prescri_type = models.IntegerField(verbose_name='处方类型 0:中药，1:西药，2:膏方，3:丸剂，5:散剂，7:免煎颗粒')
    is_within = models.IntegerField(null=False, verbose_name='服用方式 0 内服，1 外用')
    other_pres_num = models.CharField(max_length=50, null=False, verbose_name='医院处方号')
    special_instru = models.CharField(max_length=100, null=True, verbose_name='处方特殊说明 诊断信息')
    bed_num = models.CharField(max_length=50, null=True, verbose_name='床位号')
    hos_depart = models.CharField(max_length=50, null=True, verbose_name='医院科室')
    hospital_num = models.CharField(max_length=50, null=True, verbose_name='住院号')
    disease_code = models.CharField(max_length=50, null=True, verbose_name='病区号')
    doctor = models.CharField(max_length=50, null=True, verbose_name='医生姓名')
    paste_desc_file = models.CharField(max_length=100, null=True, verbose_name='膏方描述')
    prescript_remark = models.CharField(max_length=120, null=True, verbose_name='处方备注')
    per_pack_num = models.IntegerField(verbose_name='每剂几包')
    per_pack_dose = models.IntegerField(verbose_name='每包多少ml')
    medication_methods = models.CharField(max_length=50, null=True, verbose_name='用药方法')
    medication_instruction = models.CharField(max_length=50, null=True, verbose_name='用药指导')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='处方创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='数据更新时间')
    audit_result = models.CharField(max_length=500, default='', verbose_name='处方自动审核结果')
    adjust_num = models.CharField(max_length=100, null=True, verbose_name='调剂人员工号')
    print_type = models.SmallIntegerField(default=0, verbose_name='打印状态 0未打印,1已经打印')

    class Meta:
        db_table = 'tb_prescriptions'
        verbose_name = verbose_name_plural = '处方信息'


class PresDetails(models.Model):
    """处方明细(药材)表类"""
    prescription_details_id = models.CharField(max_length=36, primary_key=True, null=False, verbose_name='处方详情ID')
    prescri_id = models.ForeignKey('Prescription', on_delete=models.CASCADE, null=False, verbose_name='处方ID')
    medicines = models.CharField(max_length=100, null=False, verbose_name='药品名')
    goods_num = models.CharField(max_length=100, null=False, verbose_name='药材编号')
    dose = models.CharField(max_length=10, default='0.00', verbose_name='剂量')
    unit = models.CharField(max_length=50, null=False, verbose_name='单位')
    m_usage = models.CharField(max_length=100, null=True, verbose_name='药品特殊煎法')
    status = models.IntegerField(default='0', verbose_name='状态')
    type = models.IntegerField(default='0', verbose_name='药材类型：0 中药，1西药')
    goods_norms = models.CharField(max_length=100, null=True, verbose_name='药品规格')
    goods_orgin = models.CharField(max_length=100, null=True, verbose_name='药品产地')
    remark = models.CharField(max_length=100, null=True, verbose_name='备注')
    dose_that = models.CharField(max_length=100, null=True, verbose_name='药品注意事项说明')
    company_num = models.CharField(max_length=50, verbose_name='机构编号')
    unit_price = models.FloatField(default='0.00', verbose_name='医院药品销售单价')
    MedPerDos = models.CharField(max_length=20, null=True, verbose_name='用量(剂量)eg:2片/次(每次两片)')
    MedPerDay = models.CharField(max_length=20, null=True, verbose_name='执行频率(频次)（eg:一日3次）')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='数据更新时间')

    class Meta:
        db_table = 'tb_prescriptions_details'
        verbose_name = verbose_name_plural = '处方明细'


class Address(models.Model):
    """地址 custom_addr 表类"""
    addr_id = models.IntegerField(null=False, primary_key=True, verbose_name='地址id')
    username = models.CharField(max_length=30, null=False, verbose_name='患者姓名')
    treat_card = models.CharField(max_length=50, null=False, verbose_name='诊疗卡号')
    pres_num = models.CharField(max_length=50, null=False, verbose_name='医院处方号')
    consignee = models.CharField(max_length=30, null=False, verbose_name='收货人')
    con_tel = models.CharField(max_length=50, null=False, verbose_name='收货人电话')
    provinces = models.CharField(max_length=10, null=False, verbose_name='省份')
    city = models.CharField(max_length=10, null=False, verbose_name='城市')
    zone = models.CharField(max_length=10, null=False, verbose_name='区县')
    addr_detail = models.CharField(max_length=50, null=False, verbose_name='详细地址')
    fee = models.FloatField(null=False, verbose_name='物流费用')

    class Meta:
        db_table = 'tb_custom_addr'
        verbose_name = verbose_name_plural = '收货地址信息'