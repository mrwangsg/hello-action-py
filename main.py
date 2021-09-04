#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import sys
import threading
import time
import traceback

import requests

from config import Final
from util import util


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def bind_card(cookie, thread_id):
    """
    线程任务
    :param cookie:
    :param thread_id:
    :return:
    """
    global process, JD_Thread, JD_Min_Bean, JD_Voucher

    for _shop_id in shop_id_list[thread_id::JD_Thread]:
        status, prize_name, discount, vender_id, activity_id = util.get_shop_open_card_info(cookie, _shop_id)

        # 加锁 记得 释放锁
        lock.acquire()
        process[0] += 1
        lock.release()

        if status:
            lock.acquire()  # 加锁

            # 筛选条件
            if prize_name == "京豆":
                process[3] += int(discount)
                if int(discount) < int(JD_Min_Bean):
                    lock.release()
                    continue
                else:
                    process[1] += int(discount)

            if prize_name == "元红包":
                if not JD_Voucher:
                    lock.release()
                    continue
                else:
                    process[2] += int(discount)

            # 释放锁
            lock.release()
            if util.bind_with_vender(cookie, _shop_id, vender_id, activity_id):
                print("开卡成功", "在" + str(_shop_id) + "获得 " + str(discount) + prize_name)
            time.sleep(random.random())


def main():
    """
    启动多线程
    :return:
    """
    global JD_Cookie, JD_Send_Key, process
    flag, username, bean_num = util.get_user_info(JD_Cookie)

    if flag:
        print("账号名称: {}，现有京豆数量：".format(str(username), str(bean_num)))

        for _id in range(JD_Thread):
            threading.Thread(target=bind_card, args=(JD_Cookie, _id,)).start()

        while threading.active_count() != 1:
            print("\r账号:{}, 已经 尝试{}个店铺，总京豆数{}。其中符合过滤条件的京豆：共有{}京豆，已经获取。同时获得{}元代金券\t".format(username, process[0],
                                                                                           process[3], process[1],
                                                                                           process[2]), end="")
            time.sleep(0.5)
    else:
        print("cookie失效", JD_Cookie[-15:])

    print("\n账号{}，总共 尝试{}个店铺，总京豆数{}。其中符合过滤条件的京豆：共有{}京豆，已经获取。同时获得{}元代金券".format(username, process[0],

                                                                               process[3], process[1], process[2]))
    if JD_Send_Key:
        title_msg = "获得京豆:{}个，代金券:{}元".format(process[1], process[2])
        resp_msg = """
        # 账号{}，
        # 总共尝试{}个店铺，可以获得总京豆数{}。
        ##  其中符合过滤条件：
        ##    共有{}京豆，以及{}元代金券""".format(username, process[0], process[3], process[1], process[2])
        util.send_result(JD_Send_Key, title_msg, resp_msg)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('action with python')

    # 忽略警告
    requests.packages.urllib3.disable_warnings()

    # action中设置的值
    JD_Cookie = os.environ['JD_Cookie']
    if JD_Cookie is None:
        print("JD_Cookie不能为空！填写方式：github -> setting -> secret，填入jd登录cookie值！")
        sys.exit()
    JD_Send_Key = os.environ['JD_Send_Key']

    JD_Thread = int(os.environ['JD_Thread']) if os.environ['JD_Thread'] else Final.get__thread_num()
    JD_Min_Bean = int(os.environ['JD_Min_Bean']) if os.environ['JD_Min_Bean'] else Final.get__min_jd_bean()
    JD_Voucher = bool(os.environ['JD_Voucher']) if os.environ['JD_Voucher'] else Final.get__voucher()

    # 线程安全需要用到锁
    lock = threading.RLock()

    # 店铺遍历进度，获取京豆进度，获取代金券进度，总京豆数量
    process = [0, 0, 0, 0]

    try:
        # 获取待遍历的shopId 列表
        shop_id_list = util.get_shop_id()
        if len(shop_id_list) == 0:
            print("可遍历的店铺Id数量为零！")
            sys.exit()

        main()
    except:
        err_str = traceback.format_exc()
        print(err_str)

        if JD_Send_Key:
            title_msg = "运行异常！获得京豆:{}个，代金券:{}元".format(process[1], process[2])
            util.send_result(JD_Send_Key, err_str)

        sys.exit(-1)
