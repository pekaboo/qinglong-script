"""
cron: 00 13,15,17,19,21,23 * * *
new Env(' JNET DMS 分配');
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

from jnet_notify_fenxiao import MySQLTool, dingding_bot, formatMarkdown,selectDms,smtp
sys.path.append(r'../')
from env import *

# def select(cfg, sql, params=None):
#     DB_HOST = 'rm-j6c3543mp29dvhf93fo.mysql.rds.aliyuncs.com'
#     DB_USER = 'ru_dms_user'
#     DB_PASSWORD = '5nGaWg_hZSB'
#     DB_DATABASE = 'dms'
#     # 创建MySQLTool实例
#     my_tool = MySQLTool(DB_HOST, DB_USER,  DB_PASSWORD, DB_DATABASE)
#     result = my_tool.execute_query(sql, params)
#     if len(result) == 0:
#         return []
#     rows = []
#     for ri in range(len(result)):
#         r = {
#             '_id_': ri+1
#         }
#         for i in range(len(cfg)):
#             r[cfg[i]] = result[ri][i]
#         rows.append(r)
#     return rows

def getPartnerId(row):
    print("正在处理订单====> ", row['tracking_number'])
    # # # # # # # # 菜鸟到门():单边小于120cm，重量15-20kg
    # 1000kg以上特殊处理
    # print(row)
    # 菜鸟外单(2):单边长小于60cm,重量小于15kg
    
    if(row['receiver_country']=='KZ' or row['receiver_country']=='BY'):
        return 3
    if(row['length']<60 and row['length']<60 and row['length']<60  and row['weight']<15):
        return 2 
    # dpd(3):小于：单边150cm 三边相加小于200cm ,重量15-20kg
    if((row['length']<150 and row['length']<150 and row['length']<150) and (row['length']+row['width']+row['height']<200) and (row['weight']>=15 and row['weight']<20)):
        return 3
    # 菜鸟外单到门(5):单边小于120cm， 三边相加小于200cm,重量20-30kg
    if((row['length']<120 and row['length']<120 and row['length']<120) and (row['length']+row['width']+row['height']<200) and (row['weight']>=20 and row['weight']<30)):
        return 5 
    # 菜鸟外单到门(6): 大于：单边120cm， 三边相加180cm,重量20-30kg
    if((row['length']>=120 or row['length']>=120 or row['length']>=120) and (row['length']+row['width']+row['height']>=180) and (row['weight']>=20 and row['weight']<30)):
        return 6
    if(row['weight']>=1000):
        print("需要拆包")
        return None
    #其他都是DPD
    return 3
    # return None #row['tracking_number']+" 长:"+str(row['length'])+" 宽:"+str(row['width'])+" 高:"+str(row['height'])+" 重量:"+str(row['weight']) +" 渠道:"+str(row['upstream_express_model_code'])+" 收件地址:"+str(row['receiver_addr'])
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

def  distribute(tk,forwardPartnerId,barcode):
    print("barcode: ", barcode, "forwardPartnerId: ", forwardPartnerId)
def  distribute1(tk,forwardPartnerId,barcode):
    print("barcode: ", barcode)  
    import requests
    url = "https://dms-open-station.j-net.cn/WorkStationForwardService/forward"
    payload = "{\n    \"trackingNumbers\": [\n        \"JNTRU3600000549111YQ\"\n    ],\n    \"forwardType\": \"Partner\",\n    \"forwardPartnerId\": \"FORWORD_PARTNER\"\n}"
    payload = payload.replace("JNTRU3600000549111YQ",barcode )
    payload = payload.replace("FORWORD_PARTNER",str(forwardPartnerId) )
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Authorization': 'Bearer '+tk,
    'Connection': 'keep-alive',
    'Origin': 'https://dms-ui-station.j-net.cn',
    'Platform': 'web',
    'Referer': 'https://dms-ui-station.j-net.cn/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'Content-Type': 'application/json;charset=UTF-8'
    }
    print(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

import concurrent.futures
def  main():
    JNET_DD_BOT_RU_PRO= '676a4354589aec610fcc5c421a8b3d987798acba8078b33cac29ae7a14bbb260'             # 钉钉机器人的 DD_BOT_SECRET
    JNET_DD_BOT_RU_PRO_SEC= 'SECb916117f8d33ad8a98f7833f97cb6fd71be1b6d9df9d8723627ba836338d2f2a'               # 钉钉机器人的 DD_BOT_TOKEN
    DB_SQL='''SELECT t1.id as order_id,
       t1.refer_number,
       t1.tracking_number,
       t1.express_model_code,
       t1.upstream_express_model_code,
       t1.weight,
       t1.length,
       t1.width,
       t1.height,
       t1.create_date,
       t1.receiver_addr,
       t1.receiver_country,
       t3.*
FROM t_order t1
         INNER JOIN (SELECT distinct t.order_id -- 在库内
                     FROM t_work_station_io t
                     WHERE t.check_in_date IS NOT NULL
                       AND t.check_out_date IS NULL
                       AND t.work_station_id = -5) t2 ON t1.id = t2.order_id
         LEFT JOIN (SELECT t.id,
                           t.work_station_id,
                           t.order_id,
                           t.forward_type,
                           t.forward_station_id,
                           t.forward_partner_id,
                           t.forward_partner_label,
                           t.forward_partner_tracking_number,
                           t.forward_date,
                           t.forward_ext,
                           t.forward_partner_run_status,
                           t.forward_partner_expected_run_date,
                           t.forward_partner_run_date,
                           t.forward_partner_run_message
                    FROM t_work_station_forward AS t
                    WHERE 1 = 1
                      and t.work_station_id = -5) t3 ON t1.id = t3.order_id
WHERE 1 = 1
  and t3.forward_partner_id is null
  and t1.upstream_express_model_code != 'OZON_FBS'
  and t1.upstream_express_model_code != 'RU-ZQ'
  and t1.upstream_express_model_code != 'RU-KP'
  and t1.express_model_code = 'WLMS';'''
    DB_SELECTED_FIELD = ['order_id', 'refer_number', 'tracking_number', 'express_model_code', 'upstream_express_model_code', 'weight', 'length', 'width', 'height', 'create_date', 'receiver_addr','receiver_country', 'id', 'work_station_id', 'order_id', 'forward_type', 'forward_station_id', 'forward_partner_id', 'forward_partner_label', 'forward_partner_tracking_number', 'forward_date', 'forward_ext', 'forward_partner_run_status', 'forward_partner_expected_run_date', 'forward_partner_run_date', 'forward_partner_run_message']
    rowsA = selectDms(DB_SELECTED_FIELD, DB_SQL)
    print("共有", len(rowsA), "个订单需要分配")
    tk = loginStation("RU-MASTER","admin", "jp@Qqk82Kp$wN4")
    
    needHandle = []
    for row in rowsA:
        print(row['tracking_number']+" 长:"+str(row['length'])+" 宽:"+str(row['width'])+" 高:"+str(row['height'])+" 重量:"+str(row['weight']) +" 渠道:"+str(row['upstream_express_model_code'])+" 收件地址:"+str(row['receiver_addr']))
        pid = getPartnerId(row)
        if pid: 
            distribute1(tk,pid, row['tracking_number'])
        else:
            needHandle.append(row)
    # dingding_bot("1.待处理的尾程订单", "![](https://badgen.net/badge/1/待处理的尾程订单/green?icon=now)\n"+formatMarkdown(needHandle, {
    #     '_id_': '序号',
    #     'tracking_number': '订单' 
    # }), True,None,None)
    
    
    # 查询结果
    DB_SQL='''

SELECT  
       t1.tracking_number, 
       t3.forward_partner_run_message,
       t3.forward_partner_expected_run_date
FROM t_order t1
         INNER JOIN (SELECT distinct t.order_id -- 在库内
                     FROM t_work_station_io t
                     WHERE t.check_in_date IS NOT NULL
                       AND t.check_out_date IS NULL
                       AND t.work_station_id = -5) t2 ON t1.id = t2.order_id
         LEFT JOIN (SELECT t.id,
                           t.work_station_id,
                           t.order_id,
                           t.forward_type,
                           t.forward_station_id,
                           t.forward_partner_id,
                           t.forward_partner_label,
                           t.forward_partner_tracking_number,
                           t.forward_date,
                           t.forward_ext,
                           t.forward_partner_run_status,
                           t.forward_partner_expected_run_date,
                           t.forward_partner_run_date,
                           t.forward_partner_run_message
                    FROM t_work_station_forward AS t
                    WHERE 1 = 1
                      and t.work_station_id = -5) t3 ON t1.id = t3.order_id
WHERE 1 = 1
  and t3.forward_partner_id is not null and t3.forward_partner_run_status = 'Error' and  t3.forward_partner_expected_run_date>= NOW() - INTERVAL 1 DAY
  and t1.upstream_express_model_code != 'OZON_FBS'
  and t1.upstream_express_model_code != 'RU-ZQ'
  and t1.upstream_express_model_code != 'RU-KP'
  and t1.express_model_code = 'WLMS';'''
    DB_SELECTED_FIELD = ['tracking_number', 'forward_partner_run_message', 'forward_partner_expected_run_date']
    rowsA = selectDms(DB_SELECTED_FIELD, DB_SQL)
    smtp("近一天分配失败的清单", formatMarkdown(rowsA),rowsA,'jessie.xu@j-net.com','近一天分配失败的清单')
    dingding_bot("DMS分配服务商","![](https://badgen.net/badge/1/待处理的尾程订单/green?icon=now)\n"+formatMarkdown(needHandle, {
        '_id_': '序号',
        'tracking_number': '订单' 
    }) +  "\n![](https://badgen.net/badge/2/近一天分配失败的清单，详细清单已发生到邮箱/green?icon=now)\n"+formatMarkdown(rowsA, {
        '_id_': '序号',
        'tracking_number': '订单' 
    }), True,None,None)

if __name__ == "__main__":
    main()