"""
cron: 00 13,15,17,19,21,23 * * *
new Env(' JNET DMS 查看昨天订单未出库');
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

import concurrent.futures
def  main():
    JNET_DD_BOT_RU_PRO= '676a4354589aec610fcc5c421a8b3d987798acba8078b33cac29ae7a14bbb260'             # 钉钉机器人的 DD_BOT_SECRET
    JNET_DD_BOT_RU_PRO_SEC= 'SECb916117f8d33ad8a98f7833f97cb6fd71be1b6d9df9d8723627ba836338d2f2a'               # 钉钉机器人的 DD_BOT_TOKEN
    DB_SQL='''
 SELECT
                	t1.id as order_order_id,t1.tracking_number,t1.refer_number, t3.*
                FROM
                	t_order t1
                	INNER JOIN (
                	SELECT
                		distinct t.order_id
                	FROM
                		t_work_station_io t
                	WHERE
                		t.check_in_date IS NOT NULL
                		AND t.check_out_date IS NULL
                		AND t.work_station_id = -5
                ) t2 ON t1.id = t2.order_id
                	LEFT JOIN (
                		SELECT
                			t.id,
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
                		FROM
                			t_work_station_forward AS t
                		WHERE 1 = 1
                		 and t.work_station_id = -5
                ) t3 ON t1.id = t3.order_id
                WHERE 1 = 1  and DATE( t1.create_date) = CURDATE() - INTERVAL 1 DAY
'''
    DB_SELECTED_FIELD = ['order_order_id','tracking_number','refer_number','id','work_station_id','order_id','forward_type','forward_station_id','forward_partner_id','forward_partner_label','forward_partner_tracking_number','forward_date','forward_ext','forward_partner_run_status','forward_partner_expected_run_date','forward_partner_run_date','forward_partner_run_message']
    rowsA = selectDms(DB_SELECTED_FIELD, DB_SQL) 
    smtp("查看昨天订单未出库", formatMarkdown(rowsA),rowsA,' xiao.xu@eu-exp.cn','近一天分配失败的清单')
    dingding_bot("查看昨天订单未出库","![查看昨天订单未出库]()\n"+ formatMarkdown(rowsA, {
        '_id_': '序号',
        'tracking_number': '订单' ,
        'refer_number': '订单' ,
    })+"\n 以上昨天订单未出库", True,None,None)

if __name__ == "__main__":
    main()