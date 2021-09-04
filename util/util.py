#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/4 17:18
# @Author  : sgwang
# @File    : util.py
# @Software: PyCharm
import os
import random
import re
import sys
import traceback
from datetime import datetime

import requests
import yaml

from config import Final


def get_file_path(file_name=""):
    """
    获取文件绝对路径
    :param file_name: 文件名
    :return:
    """
    return Final.get__root_work_path() + os.sep + file_name


def get_shop_id():
    """
    获取 shopid, 如果网络上的更新时间比本地早则使用本地的，其它则使用网络上的
    """
    net_res, local_res = None, None

    try:
        net_res = requests.get(Final.get__shop_id_url(), timeout=Final.get__high_time_out())
        if net_res.status_code != 200:
            raise Exception
    except Exception:
        print("获取线上的文件失败！URL: {}".format(Final.get__shop_id_url()))

    local_file = get_file_path(Final.get__shop_id_local())
    if os.path.exists(local_file):
        try:
            local_res = yaml.safe_load(open(local_file, "r", encoding="utf-8"))
        except Exception:
            print("文件内容格式不符合yaml标准！")
            sys.exit()
    else:
        print("项目中，没有找到{}文件".format(Final.get__shop_id_local()))

    try:
        if net_res is not None and local_res is not None:
            net_update_time = datetime.strptime(str(yaml.safe_load(net_res.text)['update_time']), '%Y-%m-%d')
            local_update_time = datetime.strptime(str(local_res['update_time']), '%Y-%m-%d')
            if (net_update_time - local_update_time).days > 0:
                ret_res = yaml.safe_load(net_res.text)
            else:
                ret_res = local_res

        elif net_res is not None:
            ret_res = yaml.safe_load(net_res.text)

        elif local_res is not None:
            ret_res = local_res

        else:
            print("{}文件找不到，没有可以遍历的shopId，退出程序！！！".format(Final.get__shop_id_local()))
            sys.exit()

    except Exception:
        print("解析格式有误，退出程序！")
        sys.exit()

    return list(set(ret_res['shop_id']))


def get_headers(cookie, host):
    """
    返回请求头
    :param cookie:
    :param host:
    :return:
    """
    return {
        "Cookie": cookie,
        "Host": host,
        "User-Agent": Final.get__user_agent(),
        "Referer": "https://m.jd.com",
    }


def get_user_info(cookie):
    """
    获取用户信息
    :type cookie: str
    :return: bool: 是否成功, str: 用户名, str: 用户金豆数量
    """
    try:
        res = requests.get(Final.get__user_info_url(), headers=get_headers(cookie, "me-api.jd.com"), verify=False)
        if res.status_code == 200 and res.json()["msg"] == "success":
            data = res.json()["data"]
            return True, data["userInfo"]["baseInfo"]["nickname"], data["assetInfo"]["beanNum"]
        else:
            return False, None, None
    except Exception:
        import traceback
        print("获取用户信息错误", traceback.format_exc())
        return False, None, None


def get_shop_open_card_info(cookie, shop_id):
    """
    获取店铺会员信息
    :param cookie:
    :param shop_id:
    :return: bool: 是否成功, str: 奖励名称, str: 奖励数量, str: vender_id, str: activityId
    """
    try:
        status, vender_id = get_venderId(shop_id)
        if not status:
            return False, None, None, None, None

        params = {
            "appid": "jd_shop_member",
            "functionId": "getShopOpenCardInfo",
            "body": '{"venderId":"' + vender_id + '","channel":406}',
            "client": "H5",
            "clientVersion": "9.2.0",
            "uuid": "88888"
        }
        host = "api.m.jd.com"
        url = "https://api.m.jd.com/client.action"
        res = requests.get(url, params=params, headers=get_headers(cookie, host), verify=False)

        if res.status_code == 200 and res.json()['success']:
            if not res.json()['result']['userInfo']['openCardStatus'] and res.json()['result']['interestsRuleList'] \
                    is not None:
                for interests_info in res.json()['result']['interestsRuleList']:
                    if interests_info['prizeName'] == "京豆":
                        return True, interests_info['prizeName'], interests_info['discountString'], vender_id, \
                               interests_info['interestsInfo']['activityId']
                    elif interests_info['prizeName'] == "元红包":
                        return True, interests_info['prizeName'], interests_info['discountString'], vender_id, \
                               interests_info['interestsInfo']['activityId']
        return False, None, None, None, None
    except Exception:
        print("获取店铺信息错误", traceback.format_exc())
        return False, None, None, None, None


def ran_cookie_str():
    """
    生成随机的cookie，避免查询venderId时，次数过度被封cookie
    :return: str: Cookie
    """
    init_str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'

    key_salt = ''
    pin_salt = ''
    num = random.randint(1, len(init_str))

    for i in range(num):
        key_salt += random.choice(init_str)
    for i in range(num):
        pin_salt += random.choice(init_str)

    return "pt_key=" + key_salt + ";pt_pin=" + pin_salt


def get_venderId(shop_id):
    """
    将 `shop_id` 转换为 `venderId`
    :param shop_id:
    :return: bool: 是否成功, str: venderId
    """
    try:
        res = requests.get((Final.get__vender_id_url() + str(shop_id)),
                           headers=get_headers(ran_cookie_str(), "shop.m.jd.com"), verify=False)

        _res = re.compile("venderId: '(\\d*)'").findall(res.text)
        if res.status_code == 200 and len(_res):
            return True, re.compile("venderId: '(\\d*)'").findall(res.text)[0]
        else:
            return False, None
    except Exception:
        print("获取venderId错误", traceback.format_exc())
        return False, None


def bind_with_vender(cookie, shop_id, vender_id, activity_id):
    """
    入会
    :param cookie: 用户cookie
    :param shop_id: 店铺 id
    :param vender_id: 店铺 别名id
    :param activity_id: 活动 id 重要!(如果没有这个就不能获得奖励)
    :return:
    """
    try:
        params = {
            "appid": "jd_shop_member",
            "functionId": "bindWithVender",
            "body": '{'
                    + '"venderId":"' + vender_id + '"'
                    + ',"shopId":"' + str(shop_id) + '"'
                    + ',"writeChildFlag":0,"activityId":' + str(activity_id)
                    + ',"registerExtend":{"v_sex":"' + Final.get__reg_sex()
                    + '","v_birthday":"' + Final.get__reg_birthday()
                    + '","v_name":"' + Final.get__reg_name() + '"}'
                    + ',"bindByVerifyCodeFlag":1'
                    + ',"channel":406}',
            "client": "H5",
            "clientVersion": "9.2.0",
            "uuid": "88888"
        }

        res = requests.get(Final.get__bind_store_url(), params=params, headers=get_headers(cookie, "api.m.jd.com"),
                           verify=False)
        if res.json()["success"] and res.json()["result"]["giftInfo"] is not None:
            return True
        else:

            return False
    except Exception:
        print("加入店铺{}".format(shop_id), "会员错误。", traceback.format_exc())
        return False


def send_result(SendKey, title_msg, desp_msg=""):
    api = f"https://sc.ftqq.com/{SendKey}.send"
    data = {
        "text": title_msg,
        "desp": desp_msg
    }
    requests.post(api, data=data, verify=False)


if __name__ == "__main__":
    print(Final.get__thread_num())

    # 忽略警告
    requests.packages.urllib3.disable_warnings()
    title_msg = "京豆运行结果："
    desp_msg = """
        #服务器又炸啦！
        ##请尽快修复服务器
        """
    send_result("SCT71327TiSJ6UqRpDKhjoBUJEJy5ysnH", title_msg, desp_msg)
