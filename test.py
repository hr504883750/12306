# !/usr/bin/env python
# -*- coding:utf8 -*-
# author: hr

import requests
import json

# 创建会话
session = requests.Session()
yzm_url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand"
response = session.get(url=yzm_url, verify=False)

# 完成验证码下载
with open("yzm.png", "wb")as f:
    f.write(response.content)

# 验证码校验
point = {"1": "36,75",
         "2": "106,75",
         "3": "181,75",
         "4": "254,75",
         "5": "40,145",
         "6": "110,145",
         "7": "181,145",
         "8": "256,145"}
img_num = input("验证码选项")


def choice_point(img_num):
    point_list = img_num.split(",")
    index_list = []
    for index in point_list:
        point_result = point[index]
        index_list.append(point_result)
    index_result = ",".join(index_list)
    return index_result

check_url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
data = {'answer': '118,55,170,53',
        'login_site': 'E',
        'rand': 'jrand'}
data['answer'] = choice_point(img_num)

response = session.post(url=check_url, data=data, verify=False)
print(response.json())
print(json.loads(response.text)['result_code'])
exit()

# 登录
login_data = {"username": "13733454523",
              "password": "hr135798523",
              "appid": "otn"}


login_url = 'https://kyfw.12306.cn/passport/web/login'
response = session.post(url=login_url,data=login_data, verify=False)


print(response.text)