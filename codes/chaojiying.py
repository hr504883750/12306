#!/usr/bin/env python
# coding:utf-8
import json

import requests
from hashlib import md5
from codes import contents



class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }
        self.point = {"1": "38.5,74.5",
                      "2": "110.5,74.5",
                      "3": "182.5,74.5",
                      "4": "254.5,74.5",
                      "5": "38.5,146.5",
                      "6": "110.5,146.5",
                      "7": "182.5,146.5",
                      "8": "254.5,146.5"}

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()

    #返回json字符串示例:{"err_no":0,"err_str":"OK","tifen":821690,"tifen_lock":0}
    def query_core(self):
        """
        查询分数
        """
        data = {
            'user': self.username,
            'pass2': self.password
        }
        r = requests.post('http://upload.chaojiying.net/Upload/GetScore.php', data=data)
        r = r.json()
        return r['tifen']

    def change_code(self, res):
        result = res['pic_str'].replace("|", ",")
        list = result.split(",")
        x_list = list[::2]
        y_list = list[1::2]
        num_list = []
        index_list = []
        for x, y in zip(x_list, y_list):
            x = int(x)
            y = int(y)
            if 5 <= x <= 72:
                if 41 <= y <= 108:
                    img_num = '1'
                elif 113 <= y <= 180:
                    img_num = '5'
            elif 77 <= x <= 144:
                if 41 <= y <= 108:
                    img_num = '2'
                elif 113 <= y <= 180:
                    img_num = '6'
            elif 149 <= x <= 216:
                if 41 <= y <= 108:
                    img_num = '3'
                elif 113 <= y <= 180:
                    img_num = '7'
            elif 221 <= x <= 288:
                if 41 <= y <= 108:
                    img_num = '4'
                elif 113 <= y <= 180:
                    img_num = '8'
            else:
                print("<<" * 10 + "误差太大出错:", res['err_no'])
                develope_resl = self.ReportError(res['pic_id'])
                print(type(develope_resl))
                print("<<" * 10 + "返回分值处理结果:", develope_resl['err_str'])
                return None
            num_list.append(img_num)
        for index in num_list:
            point_result = self.point[index]
            index_list.append(point_result)
        index_result = ",".join(index_list)
        return index_result



    #{"err_no":0,"err_str":"OK","pic_id":"1662228516102","pic_str":"8vka","md5":"35d5c7f6f53223fbdc5b72783db0c2c0"}
    def send_yzm(self):
        with open('./yzm.jpg', 'rb') as f:
            im = f.read()
        print("<<"*10 +"剩余题分:{}".format(self.query_core()))
        res = chaojiying.PostPic(im, 9004)
        if res['err_no'] == 0:
            index_result = self.change_code(res)
            if index_result:
                print("<<"*10 + "本次验证码识别地址为：", index_result)
                return index_result
            self.send_yzm()
        print("<<"*10 + "打码识别出错:", res['err_no'])
        develope_resl = self.ReportError(res['pic_id'])
        print(type(develope_resl))
        print("<<"*10 + "返回分值处理结果:", develope_resl['err_str'])
        return None


# if __name__ == '__main__':
# 实例化对象
chaojiying = Chaojiying_Client(contents.USERNAME, contents.PASSWORD, '897176')
    # chaojiying.send_yzm()

