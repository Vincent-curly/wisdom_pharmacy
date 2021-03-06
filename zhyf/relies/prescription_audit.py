# coding:utf-8
"""
  Time : 2021/2/24 上午1:40
  Author : vincent
  FileName: prescription_audit
  Software: PyCharm
  Last Modified by: vincent
  Last Modified time: 2021/2/24 上午1:40
"""
import re


def reverse_18(*drug_list):
    result = []
    s_lists = [{'.?甘草.?': ['.?甘遂', '.?.?大戟.?', '.?海藻.?', '.?芫花']},
               ['.?川乌', '.?草乌', '.?.?附子.?.?.?', '.?.?.?黑顺片.?.?.?', '淡附片.?.?.?.?.?'],
               {'.?藜芦': ['.?人参.?', '.?沙参.?.?.?', '.?丹参.?.?.?', '.?玄参.?.?.?', '.?.?细辛.?.?.?',
                         '.?.?白芍.?.?.?', '.?.?赤芍.?.?']},
               ['.?.?贝母.?.?.?.?', '.?.?瓜篓.?.?', '.?天花粉.?.?.?', '.?.?.?半夏.?.?', '.?白蔹.?.?.?', '.?白及.?.?.?']]
    gancao_match_first = drug_match('.?甘草.?', *drug_list)
    if gancao_match_first:
        gancao_match_second = drug_match(s_lists[0]['.?甘草.?'], *drug_list)
        if gancao_match_second:
            for drug in gancao_match_second:
                result.append(gancao_match_first[0] + '与' + drug + '十八反')
        else:
            pass
    wutou_match_first = drug_match(s_lists[1], *drug_list)
    if wutou_match_first:
        wutou_match_second = drug_match(s_lists[3], *drug_list)
        if wutou_match_second:
            for drug in wutou_match_second:
                result.append(wutou_match_first[0] + '与' + drug + '十八反')
        else:
            pass
    lilu_match_first = drug_match('.?藜芦', *drug_list)
    if lilu_match_first:
        lilu_match_second = drug_match(s_lists[2]['.?藜芦'], *drug_list)
        if lilu_match_second:
            for drug in lilu_match_second:
                result.append(lilu_match_first[0] + '与' + drug + '十八反')
        else:
            pass
    return result


def fear_19(*drug_list):
    result = []
    s_lists = [{'.?硫磺.?': '.?芒硝.?'}, {'.?水银.?': '.?砒霜.?'}, {'.?狼毒': '.?密陀僧'},
               {'.?巴豆': '.?牵牛.?'}, {'.?丁香.?.?.?': '.?.?郁金.?.?.?'}, {'.?川乌': '.?犀角'},
               {'.?草乌': '.?犀角'}, {'.?牙硝': '.?三棱.?.?.?'}, {'.?肉桂.?.?.?': '.?赤石脂.?.?.?'},
               {'.?人参.?': '.?.?五灵脂.?.?.?'}]
    for s_list in s_lists:
        for key, value in s_list.items():
            fear_first = drug_match(key, *drug_list)
            fear_second = drug_match(value, *drug_list)
            if fear_first and fear_second:
                result.append(fear_first[0] + '与' + fear_second[0] + '十九畏')
    return result


def usage_match(*drug_list):
    result = []
    s_lists = [{'包煎': ['.?.?.?旋覆花.?.?.?', '.?.?车前子.?.?.?', '.?.?蒲黄.?.?.?', '.?滑石.?.?.?', '海金沙.?.?.?',
                       '.?.?葶苈子.?.?.?', '蚕砂', '青黛.?.?.?', '.?.?马勃']},
               {'先煎': ['.?石膏.?.?.?', '.?.?寒水石.?.?.?', '.?.?磁石.?.?.?', '.?.?赭石.?', '.?.?.?石英.?.?.?',
                       '.?龙骨.?.?.?', '.?蛤壳.?.?.?', '.?.?石决明.?.?.?', '.?瓦楞子.?.?.?', '.?龟甲', '.?鳖甲.?.?.?',
                       '.?龙齿.?.?.?', '鹿角', '水牛角', '.?川乌', '.?草乌', '.?.?附子.?.?.?', '.?.?.?黑顺片.?.?.?',
                       '淡附片.?.?.?.?.?', '.?商陆', '.?.?南星', '.?.?.?半夏.?.?', '.?牡蛎.?.?.?']},
               {'后下': ['薄荷.?.?.?', '砂仁', '.?肉豆蔻.?.?.?', '沉香', '肉桂.?.?.?', '.?木香.?.?.?', '钩藤.?.?.?',
                       '.?.?大黄.?.?.?', '番泻叶', '徐长卿', '檀香.?.?.?']},
               {'另煎': ['.?人参.?', '西洋参.?', '鹿茸.?', '燕窝', '银耳', '三七', '冬虫夏草', '西红花']},
               {'烊化': ['阿胶.?.?.?.?.?', '龟板胶.?.?.?.?.?', '鹿角胶.?.?.?.?.?', '枇杷叶膏', '.?.?芒硝.?.?.?', '玄明粉']},
               {'冲服': ['.?.?.?.?.?.?.?.?粉']}]
    for s_list in s_lists:
        for key, value in s_list.items():
            m_usage_first = drug_match(value, *drug_list)
            if m_usage_first:
                for drug in m_usage_first:
                    for num in range(len(drug_list)):
                        if drug_list[num]['medicines'] == drug:
                            if drug_list[num]['m_usage'] is None:
                                result.append(drug + '缺少用法' + '【' + key + '】')
                            else:
                                pass
                        else:
                            continue
            else:
                continue
    return result


def poisonous_and_dose_match(*drug_list):
    result = []
    s_lists = [{'土荆皮': {'notice': '有毒,禁内服'}}, {'土鳖虫': {'notice': '有小毒,孕妇禁服', 'dose': '3~9g'}},
               {'山豆根': {'notice': '有毒', 'dose': '3~6g'}}, {'.?川乌': {'notice': '有大毒', 'dose': '1.5~3g'}},
               {'川楝子': {'notice': '有小毒', 'dose': '4.5~9g'}}, {'.?.?附子.?.?.?': {'notice': '有毒,孕妇慎用', 'dose': '3~6g'}},
               {'白果': {'notice': '有毒', 'dose': '4.5~9g'}}, {'.?.?.?半夏.?.?': {'notice': '有毒', 'dose': '3~9g'}},
               {'全蝎': {'notice': '有毒', 'dose': '3~6g'}}, {'苍耳子': {'notice': '有毒', 'dose': '3~9g'}},
               {'附子': {'notice': '有毒,孕妇禁用', 'dose': '3~15g'}}, {'苦杏仁': {'notice': '有小毒', 'dose': '4.5~9g'}},
               {'.?草乌': {'notice': '有毒', 'dose': '1.5~3g'}}, {'牵牛子': {'notice': '有毒,孕妇忌服', 'dose': '3~6g'}},
               {'.?鹤虱': {'notice': '有小毒', 'dose': '3~9g'}}, {'香加皮': {'notice': '有毒', 'dose': '3~6g'}},
               {'重楼': {'notice': '有小毒,孕妇忌服', 'dose': '3~9g'}}, {'急性子': {'notice': '有小毒,孕妇禁服', 'dose': '3~4.5g'}},
               {'常山': {'notice': '有毒,孕妇慎用', 'dose': '5~9g'}}, {'蛇床子': {'notice': '有小毒', 'dose': '3~4.5g'}},
               {'猪牙皂': {'notice': '有小毒,孕妇禁用', 'dose': '1~1.5g'}}, {'绵马贯众': {'notice': '有小毒,孕妇慎用', 'dose': '4.5~9g'}},
               {'蒺藜': {'notice': '有小毒,孕妇慎用', 'dose': '6~9g'}}, {'蕲蛇': {'notice': '有毒', 'dose': '3~9g'}},
               {'朱砂': {'notice': '有毒,宜外用', 'dose': '0.1~0.5g'}}, {'马兜铃': {'notice': '有毒,儿童,老年人慎用,孕妇禁用', 'dose': '3~9g'}},
               {'天仙藤': {'notice': '有毒,儿童,老年人慎用,孕妇禁用', 'dose': '4.5~9g'}}, {'吴茱萸': {'notice': '有小毒', 'dose': '1.5~4.5g'}},
               {'苦楝皮': {'notice': '有毒', 'dose': '1.5~9g'}}, {'蜈蚣': {'notice': '有毒,孕妇禁用', 'dose': '3~5g'}},
               {'山慈菇': {'notice': '有毒', 'dose': '3~9g'}}, {'仙茅': {'notice': '有毒', 'dose': '3~9g'}},
               {'两面针': {'notice': '有小毒', 'dose': '5~10g'}}, {'丁公藤': {'notice': '有小毒,孕妇禁服', 'dose': '3~6g'}},
               {'干漆': {'notice': '有毒,孕妇慎用', 'dose': '2.4~4.5g'}}, {'千金子': {'notice': '有毒,孕妇忌用', 'dose': '1~2g'}},
               {'马钱子': {'notice': '有大毒', 'dose': '0.3~0.6g'}}, {'巴豆': {'notice': '有大毒'}},
               {'.?甘遂': {'notice': '有毒,孕妇禁用', 'dose': '0.5~1.5g'}}, {'华山参': {'notice': '有毒', 'dose': '0.1~0.2g'}},
               {'红粉': {'notice': '有大毒,外用适量'}}, {'.?芫花': {'notice': '有毒', 'dose': '1.5~3g'}},
               {'京大戟': {'notice': '有毒', 'dose': '1.5~3g'}}, {'商陆': {'notice': '有毒,孕妇禁用', 'dose': '3~9g'}},
               {'硫黄': {'notice': '有毒,孕妇慎用', 'dose': '1.5~3g'}}, {'雄黄': {'notice': '有毒,内服慎用,孕妇禁用', 'dose': '0.05~0.1g'}},
               {'篦麻子': {'notice': '有毒,外用适量'}}, {'罂粟壳': {'notice': '有毒,幼儿及哺乳期妇女忌用', 'dose': '3~6g'}},
               {'制天南星': {'notice': '有毒,孕妇慎用', 'dose': '3~9g'}}, {'水蛭': {'notice': '有小毒', 'dose': '1.5~3g'}},
               {'.?艾叶': {'notice': '有小毒', 'dose': '3~9g'}}, {'北豆根': {'notice': '有小毒', 'dose': '3~9g'}},
               {'.?.?细辛.?.?.?': {'notice': '有小毒', 'dose': '1~3g'}}]
    for s_list in s_lists:
        for key, value in s_list.items():
            poisonous_first = drug_match(key, *drug_list)
            if poisonous_first:
                if value['dose']:
                    max_dose = float(value['dose'].split('~')[1].split('g')[0])
                    for drug in poisonous_first:
                        for num in range(len(drug_list)):
                            if drug_list[num]['medicines'] == drug:
                                if float(drug_list[num]['dose']) > max_dose:
                                    result.append(drug + value['notice'] + ',超量' + value['dose'])
                                else:
                                    result.append(drug + value['notice'])
                            else:
                                continue
                else:
                    for drug in poisonous_first:
                        result.append(drug + value['notice'])
            else:
                continue
    return result


def drug_match(ss, *drug_list):
    m_list = []
    if isinstance(ss, list):
        for s in ss:
            for drug in drug_list:
                m = re.match(s, drug['medicines'])
                if m is not None:
                    m_list.append(m.group())
    else:
        for drug in drug_list:
            m = re.match(ss, drug['medicines'])
            if m is not None:
                m_list.append(m.group())
    return m_list


if __name__ == '__main__':
    d = [{'medicines': '人参片', 'dose': '10', 'm_usage': None},
         {'medicines': '五灵脂', 'dose': '10', 'm_usage': None},
         {'medicines': '姜厚朴', 'dose': '15', 'm_usage': None},
         {'medicines': '瓦楞子', 'dose': '15', 'm_usage': None},
         {'medicines': '白蔹', 'dose': '10', 'm_usage': None},
         {'medicines': '藜芦', 'dose': '10', 'm_usage': None},
         {'medicines': '法半夏', 'dose': '15', 'm_usage': None},
         {'medicines': '醋延胡索', 'dose': '10', 'm_usage': None},
         {'medicines': '白芍', 'dose': '15', 'm_usage': None},
         {'medicines': '车前子', 'dose': '10', 'm_usage': None},
         {'medicines': '甘草片', 'dose': '6', 'm_usage': None},
         {'medicines': '砂仁', 'dose': '10', 'm_usage': None},
         {'medicines': '制川乌', 'dose': '10', 'm_usage': None},
         {'medicines': '竹茹（丝）', 'dose': '10', 'm_usage': None}]
    print(reverse_18(*d)+fear_19(*d)+usage_match(*d)+poisonous_and_dose_match(*d))
    # print(poisonous_and_dose_match(*d))
