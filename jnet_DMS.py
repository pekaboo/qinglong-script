"""
cron: 00 18 * * *
new Env(' JNET 分销数据');
"""

#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import pymysql
import base64
import hashlib
import hmac
import json
import os
import re
import threading
import time
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

import requests


import sys

from jnet_notify_fenxiao import MySQLTool, dingding_bot, formatMarkdown
sys.path.append(r'../')
from env import *

def select(cfg, sql, params=None):
    DB_HOST = 'rm-j6c3543mp29dvhf93fo.mysql.rds.aliyuncs.com'
    DB_USER = 'ru_dms_user'
    DB_PASSWORD = '5nGaWg_hZSB'
    DB_DATABASE = 'dms'
    # 创建MySQLTool实例
    my_tool = MySQLTool(DB_HOST, DB_USER,  DB_PASSWORD, DB_DATABASE)
    result = my_tool.execute_query(sql, params)
    if len(result) == 0:
        return []
    rows = []
    for ri in range(len(result)):
        r = {
            '_id_': ri+1
        }
        for i in range(len(cfg)):
            r[cfg[i]] = result[ri][i]
        rows.append(r)
    return rows

def loginStation(station,account,password):
    import requests
    import json

    url = "https://dms-open-station.j-net.cn/AuthService/login"

    payload = json.dumps({
    "station":  station,
    "account":  account,
    "password":  password,
    })
    headers = {
    'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {{StationSercerAuthorization}}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.json()['status'] == 'success':
        print(response.json()['data'])
        return response.json()['data']
    raise Exception(response.json()['message'])
  
def  receive(tk,barcode):
    print("barcode: ", barcode)  
    url = "https://dms-open-station.j-net.cn/OrderPreService/receive"

    payload = "{\"barcode\":\""+barcode+"\"}"
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Authorization': 'Bearer '+tk,
    'Connection': 'keep-alive',
    'Origin': 'https://dms-ui-station-pda.j-net.cn',
    'Platform': 'web',
    'Referer': 'https://dms-ui-station-pda.j-net.cn/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'visitor-name': 'admin',
    'Content-Type': 'application/json;charset=UTF-8'
    }

    response =  requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


import concurrent.futures
def  main():
    DB_SQL='''select  p.tracking_number from t_order_pre p left join t_sys_conf c on p.express_model_code = c.conf_key
                                   where c.conf_kind = 'EXPRESS_MODEL_CODE' and c.auto_receive = 1 and p.order_id is null;'''
    DB_SELECTED_FIELD = ['tracking_number']
    rowsA = select(DB_SELECTED_FIELD, DB_SQL)
    tk = loginStation("RU-MASTER","admin", "jp@Qqk82Kp$wN4")
    # for row in rowsA:
    #     receive(tk,row['tracking_number'])
    # Create a ThreadPoolExecutor with a maximum of 5 threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit the receive function for each barcode
        futures = [executor.submit(receive,tk, row['tracking_number']) for row in rowsA]

        # Wait for all the futures (requests) to complete
        concurrent.futures.wait(futures)
    
    
    # DB_SELECTED_FIELD = ['tracking_number']
    # rowsA = select(DB_SELECTED_FIELD, DB_SQL)
    # dingding_bot("待自动揽收", "![](https://img.shields.io/badge/%F0%9F%A7%BE-%20%E5%88%86%E9%94%80%E6%B8%85%E5%8D%95-FFDD67.svg?style=flat-square)\n"+formatMarkdown(rowsA, {
    #      '_id_': '序号',
    #     'tracking_number': '待自动揽收单号' 
    # }), True,None,None)


if __name__ == "__main__":
    main()

