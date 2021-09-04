#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import re
import traceback

import requests


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


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
        "Referer": "https://m.jd.com",
        "User-Agent": "Mozilla/5.0 (Linux; Android 9; COR-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/46.03.4.5155"
    }


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
    :return: bool: 是否成功, str: venderID
    """
    try:
        res = requests.get("https://shop.m.jd.com/?shopId=" + str(shop_id),
                           headers=get_headers(ran_cookie_str(), "shop.m.jd.com"), verify=False)

        _res = re.compile("venderId: '(\\d*)'").findall(res.text)
        if res.status_code == 200 and len(_res):
            return True, re.compile("venderId: '(\\d*)'").findall(res.text)[0]
        else:
            return False, None
    except:
        print("ERROR", "获取 venderId 错误", traceback.format_exc())
        return False, None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('action with python')

    # 忽略警告
    requests.packages.urllib3.disable_warnings()
    vender_id = get_venderId("840222")
    print("jd_venderId: ", vender_id)
