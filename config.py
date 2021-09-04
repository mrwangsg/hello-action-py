#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/4 17:03
# @Author  : sgwang
# @File    : config.py
# @Software: PyCharm
import os


class Final:
    """
    存储静态的配置信息
    """

    # 线程数
    __thread_num = int(4)

    # 最小获得京豆数少于此的不会获取
    __min_jd_bean = int(3)

    # 是否获取代金券？true: 获取, false: 不获取。代金券有有效期限！
    __voucher = False

    # 注册信息
    __reg_sex = '男'
    __reg_birthday = '2021-09-04'
    __reg_name = '王中国'

    # 等待超时时长
    __low_time_out = int(5)
    __middle_time_out = int(10)
    __high_time_out = int(30)

    # 请求头信息
    __user_agent = "okhttp/3.12.1;jdmall;android;version/10.0.1;build/88405;screen/1080x2250;os/9;network/wifi;"

    # 用户信息路径，venderId获取地址
    __user_info_url = "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion"
    __vender_id_url = "https://shop.m.jd.com/?shopId="
    __bind_store_url = "https://api.m.jd.com/client.action"

    # 获取shop_id，分线上的和项目的
    __shop_id_local = "shopid.yaml"
    __shop_id_url = "https://antonvanke.github.io/JDBrandMember/shopid.yaml"

    # 工作路径
    __root_work_path = os.getcwd()

    @classmethod
    def get__bind_store_url(cls):
        return cls.__bind_store_url

    @classmethod
    def get__vender_id_url(cls):
        return cls.__vender_id_url

    @classmethod
    def get__voucher(cls):
        return cls.__voucher

    @classmethod
    def get__min_jd_bean(cls):
        return cls.__min_jd_bean

    @classmethod
    def get__user_info_url(cls):
        return cls.__user_info_url

    @classmethod
    def get__root_work_path(cls):
        return cls.__root_work_path

    def set__root_work_path(self, root_work_path):
        self.__root_work_path = root_work_path

    @classmethod
    def get__low_time_out(cls):
        return cls.__low_time_out

    @classmethod
    def get__middle_time_out(cls):
        return cls.__middle_time_out

    @classmethod
    def get__high_time_out(cls):
        return cls.__high_time_out

    @classmethod
    def get__thread_num(cls):
        return cls.__thread_num

    @classmethod
    def get__reg_sex(cls):
        return cls.__reg_sex

    @classmethod
    def get__reg_birthday(cls):
        return cls.__reg_birthday

    @classmethod
    def get__reg_name(cls):
        return cls.__reg_name

    @classmethod
    def get__user_agent(cls):
        return cls.__user_agent

    @classmethod
    def get__shop_id_local(cls):
        return cls.__shop_id_local

    @classmethod
    def get__shop_id_url(cls):
        return cls.__shop_id_url


if __name__ == "__main__":
    print(Final.get__thread_num())

    print("项目中，没有找到{}文件".format(Final.get__shop_id_local()))
