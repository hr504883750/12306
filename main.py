# !/usr/bin/env python
# -*- coding:utf8 -*-
# author: hr
import datetime
import json
import re
import urllib
import requests
import time

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用证书提示
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from codes.chaojiying import chaojiying
from stations import StationInfo
from station_version import station_name

class QPSpider(object):
    # 创建会话
    def __init__(self):
        self.session = requests.Session()
        self.header = {
            'Referer': 'https://kyfw.12306.cn/otn/login/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                       }


    def get_cookie(self):
        # 获取cookie
        url = "https://kyfw.12306.cn/otn/login/init"
        self.session.get(url=url, verify=False)

    def load_code(self):
        # 完成验证码下载
        yzm_url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand"
        response = self.session.get(url=yzm_url, verify=False)
        with open("yzm.jpg", "wb")as f:
            f.write(response.content)

    def check_code(self):
        """
        验证码验证与上传
        {"result_message":"验证码校验成功","result_code":"4"}
        {"result_message":"验证码校验失败","result_code":"5"}
        """
        img_num = chaojiying.send_yzm()
        if img_num:
            check_url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
            data = {'answer': '118,55,170,53',
                    'login_site': 'E',
                    'rand': 'jrand'}
            data['answer'] = str(img_num)
            response = self.session.post(url=check_url, data=data, verify=False)
            if int(response.json()['result_code']) == 4:
                 return print("<<" * 10 + response.json()['result_message'])
            print("<<" * 10 + response.json()['result_message'])
            print("重新获取验证码")
            self.load_code()
            time.sleep(1)
            self.check_code()
        else:
            self.check_code()

    def check_tickets(self, train_date, from_code, to_code):
    # def check_tickets(self):
        """
        检查余票
        索引：信息
        0:车牌码
        3：车次     23:软卧 True
        4：起始站   26:无座 True
        7：终点站   28：硬卧 True
        8：出发时间  29：硬座 True
        9：结束时间
        10：历时时间
        12: leftTicket,leftTicketStr
        13: 日期
        15: train_location
        30：二等座
        31：一等座
        32：商务座

        """
        url = "https://kyfw.12306.cn/otn/leftTicket/queryA?"
        # 格式 '2018-09-06'  'SZQ'  'WHN'
        params = {
            "leftTicketDTO.train_date": train_date,
            "leftTicketDTO.from_station": from_code,
            "leftTicketDTO.to_station": to_code,
            "purpose_codes": "ADULT"
        }
        # params = {
        #     "leftTicketDTO.train_date": "2018-09-06",
        #     "leftTicketDTO.from_station": "SZQ",
        #     "leftTicketDTO.to_station": "WHN",
        #     "purpose_codes": "ADULT"
        # }
        response = self.session.get(url=url, params=params)
        print(response.status_code)
        train_list = json.loads(response.content.decode("utf-8"))['data']['result']
        for train in train_list:
            item_list = train.split("|")
            # 考虑到无的可能性，加异常判断
            if item_list[3][0] != "G":
                try:
                    if item_list[29] == "有" or int(item_list[29]) > 0 or item_list[28] == "有" or int(item_list[28]) > 0:
                        print("""
                        车次:%s
                        起始站:%s
                        终点站:%s
                        出发时间:%s
                        结束时间:%s
                        历时时间:%s
                        软卧:%s
                        硬卧:%s
                        硬座:%s
                        """ % (item_list[3], item_list[4], item_list[7], item_list[8], item_list[9],
                               item_list[10], item_list[23], item_list[28], item_list[29]))
                        yield item_list
                except:
                    continue
            else:
                try:
                    if item_list[30] == "有" or int(item_list[30]) > 0:
                        print("""
                        车次:%s
                        起始站:%s
                        终点站:%s
                        出发时间:%s
                        结束时间:%s
                        历时时间:%s
                        二等座:%s
                        一等座:%s
                        商务座:%s
                        """ % (item_list[3], item_list[4], item_list[7], item_list[8], item_list[9],
                              item_list[10], item_list[30], item_list[31], item_list[32]))
                        yield item_list

                except:
                    continue

    def login(self, train_date, from_code, to_code):
        """
        {"result_message":"登录成功","result_code":0,"uamtk":"De-hac3r2WrFyKzvuffkkSFZQGq6ZQKklJZjP8Dq7WUmk1210"}

        """
        login_data = {"username": "*********",   #添加12306账号
                      "password": "********",	#添加12306账号
                      "appid": "otn"}
        login_url = "https://kyfw.12306.cn/passport/web/login"
        response = self.session.post(url=login_url, data=login_data, verify=False)
        # 返回 {"result_message":"登录成功","result_code":0,"uamtk":"uMKaFsIx9fe00Ao7Wz_4hh5nNPgMEhJA9ycppxWBnusy01210"}
        if response.json()["result_code"] == 0:
            # 伪登录
            print("<<"*10 + '登录成功')

            # 再次登录
            redirect_url = "https://kyfw.12306.cn/otn/login/userLogin"
            self.session.post(url=redirect_url, data={'_json_att': ''})
            # 重定向到登录

            # 用户信息令牌认证
            response = self.session.post(url="https://kyfw.12306.cn/passport/web/auth/uamtk", data={'appid': 'otn'})
            # 返回{"result_message":"验证通过","result_code":0,"apptk":null,"newapptk":"3N0obxFKyC-AK-MiBaKNcxY80FcuSbDPff-z9YZ7Rj0rw1210"}
            # 用户信息令牌认证2
            data1 = json.loads(response.content.decode('utf8'))
            data1 = {'tk': data1['newapptk']}
            self.session.post(url="https://kyfw.12306.cn/otn/uamauthclient", data=data1)
            #返回{"apptk":"3N0obxFKyC-AK-MiBaKNcxY80FcuSbDPff-z9YZ7Rj0rw1210","result_code":0,"result_message":"验证通过","username":"郝瑞"}

            # 个人中心
            response = self.session.get(url='https://kyfw.12306.cn/otn/index/initMy12306')
            # print(response.content.decode('utf8'))

            # # 车票查询界面
            # check_ticket_url = "https://kyfw.12306.cn/otn/leftTicket/init"
            # self.session.get(url=check_ticket_url)

            # 车票码查询
            item_sub = []
            for item_list in self.check_tickets(train_date, from_code, to_code):
                item_sub.append(item_list)
            item_list2 = item_sub[0]
            print(item_list2)

            # 车票下单
            order_ticket_url = "https://kyfw.12306.cn/otn/login/checkUser"
            data = {
                "_json_att": ''
            }
            response = self.session.post(url=order_ticket_url, data=data)
            print(response.content.decode("utf8"))
            #{"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"flag":false},"messages":[],"validateMessages":{}}
            params = {"secretStr": urllib.parse.unquote(item_list2[0]),
                    "train_date": "2018-09-05",
                    "back_train_date": "2018-09-01",
                    "tour_flag": "dc",
                    "purpose_codes": "ADULT",
                    "query_from_station_name": "深圳",
                    "query_to_station_name": "武汉",
                    "undefined": "",
                    }
            response = self.session.get(url="https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest", params=params)
            print(response.content.decode())
            #{"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":"N","messages":[],"validateMessages":{}}

            data2 = {
                "_json_att": ''
            }
            response = self.session.post(url='https://kyfw.12306.cn/otn/confirmPassenger/initDc', data=data2)
            html = response.content.decode('utf8')
            # print(html)
            globalRepeatSubmitToken = re.findall(r"globalRepeatSubmitToken = '(.*?)'", html)[0]
            key_check_isChange = re.findall(r"'key_check_isChange':'(.*?)'", html)[0]
            data3 = {
                "_json_att": '',
                "REPEAT_SUBMIT_TOKEN": globalRepeatSubmitToken
            }
            response = self.session.post(url='https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs', data=data3)
            html = response.content.decode('utf8')
            print(html)
            # 选择购票用户
            data4 = {
                'cancel_flag': '2',
                'bed_level_order_num':'000000000000000000000000000000',
                'passengerTicketStr': 'O,0,1,郝瑞,1,***********,,N', #请自行修改身份证
                'oldPassengerStr':'郝瑞,1,*********,1_',  #请自行修改身份证
                'tour_flag': 'dc',
                'randCode':'',
                'whatsSelect': '1',
                '_json_att':'',
                'REPEAT_SUBMIT_TOKEN': globalRepeatSubmitToken
            }
            self.session.post(url='https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo', data=data4)
            # 提交购票用户信息
            GMT_FORMAT = '%a %b %d %Y 00:00:00 GMT'
            time1 = time.strptime(item_list2[13], '%Y%m%d')
            time2 = time.strftime(GMT_FORMAT, time1) + "+0800 (中国标准时间)"
            data5 = {
                'train_date': time2,
                'train_no': item_list2[2], #车列信息
                'stationTrainCode': item_list2[3],
                'seatType': 'O',
                'fromStationTelecode': item_list2[4],
                'toStationTelecode': item_list2[7],
                'leftTicket': item_list2[12],
                'purpose_codes': '00',
                'train_location': item_list2[15],
                '_json_att': '',
                'REPEAT_SUBMIT_TOKEN': globalRepeatSubmitToken,

            }
            self.session.post(url='https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount', data=data5)
            data6 = {"passengerTicketStr": "O,0,1,郝瑞,1,***********,,N", #请自行修改身份证
                   "oldPassengerStr": "郝瑞,1,*************,1_", # 请自行修改身份信息
                   "randCode": "",
                   "purpose_codes": "00",
                   "key_check_isChange": key_check_isChange,
                   "leftTicketStr": item_list2[12],
                   "train_location": "Q6",
                   "choose_seats": "1F",
                   "seatDetailType": "000",
                   "whatsSelect": "1",
                   "roomType": "00",
                   "dwAll": "N",
                   "_json_att": "",
                   "REPEAT_SUBMIT_TOKEN": globalRepeatSubmitToken
                   }
            response = self.session.post(url='https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue', data=data6)
            print(response.content.decode('utf8'))


        else:
            print("登录失败正在重新登陆")
            time.sleep(5)
            self.login(train_date, from_code, to_code)





    def main(self):
        train_date = input("请输入出发时间(eg:2018-09-05):")
        from_station = input("请输入出发城市:")
        to_station = input("请输入目的城市:")

        self.get_cookie()
        self.load_code()
        self.check_code()


        sta_inf = StationInfo(station_name)
        sta_inf.station_info()
        from_code = sta_inf.from_select(from_station)
        to_code = sta_inf.to_select(to_station)
        self.login(train_date, from_code, to_code)


        # 测试
        # self.check_tickets()

        # self.check_tickets(train_date, from_code, to_code)




if __name__ == "__main__":
    qp = QPSpider()
    qp.main()