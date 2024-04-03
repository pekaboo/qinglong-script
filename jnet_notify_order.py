"""
cron: 00 9,12,18 * * *
new Env(' JNET 仓发订单任务统计');
"""

#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
from jnet_notify_fenxiao import *
def main():
    rowsA = select(['order_status','cnt'], '''select *
from (SELECT '2. 剩余待处理' order_status, COUNT(*) cnt
      FROM wms.orders
      where order_status = 4
      union all

      SELECT '1. 昨日出库数' order_status, COUNT(*) cnt
      FROM wms.orders
      where order_status = 8
        and DATE(date_sub(NOW(), INTERVAL 1 DAY)) = DATE(add_time)

      union all

      SELECT '3. 今日已下架' order_status, COUNT(*) cnt
      FROM wms.orders
      where order_status = 5
        and DATE(NOW()) = DATE(add_time)
      union all

      SELECT '4. 今日已出库' order_status, COUNT(*) cnt
      FROM wms.orders
      where order_status = 8
        and DATE(NOW()) = DATE(add_time)) a
order by a.order_status
''')

    # 我的通知
    # JNET_DD_BOT_RU_PRO= 'dd5d6ab675280baebe1b27e1886cc77cbde10c3c1260db3fd10f6193eaa7818e'             # 钉钉机器人的 DD_BOT_SECRET
    # JNET_DD_BOT_RU_PRO_SEC= 'SEC6c3ce660fe65ab1df513bb9d0f304fd1bb32780455b52face67bdb7c8a610087'               # 钉钉机器人的 DD_BOT_TOKEN
    # 大卖
    # JNET_DD_BOT_TOKEN01= '7ec6aa45aafa293bffc08d1428d88f40efb81ada6f3d0221cebeae2fc39bd4e3'             # 钉钉机器人的 DD_BOT_SECRET
    # JNET_DD_BOT_SECRET01= 'SEC0fc2a039f62f6939f1b6d9972994b6529b9186c9fe6b78bab1c2bc266ba04513'               # 钉钉机器人的 DD_BOT_TOKEN
    # 俄罗斯产品部
    JNET_DD_BOT_RU_PRO= '676a4354589aec610fcc5c421a8b3d987798acba8078b33cac29ae7a14bbb260'             # 钉钉机器人的 DD_BOT_SECRET
    JNET_DD_BOT_RU_PRO_SEC= 'SECb916117f8d33ad8a98f7833f97cb6fd71be1b6d9df9d8723627ba836338d2f2a'               # 钉钉机器人的 DD_BOT_TOKEN
    dingding_bot("仓发业务:", "## 仓发业务任务:\n"+formatMarkdown(rowsA, {
        'order_status': '状态',
        'cnt': '数量'
    }), True,None,None)
def order():
    import requests
    import json 
    url = "http://ec.wangyitu.tech:5085/api/jnetrpt/sql"

    payload = json.dumps({
    "sql": """
select *
from (select '3.今天' a, type, count(1) cnt
      from (select 'TMS' type, WAYBILL_NUM
            from JNETTMS.T_ORDER
            where to_char(CREATE_DATE, 'yyyymmdd') = to_char(sysdate, 'yyyymmdd')
            union all
            select 'WLMS-TC' type, SHIPPING_NUM waybill_num
            from JNETWLMS.T_SENDIN_ORDER
            where to_char(CREATE_DATE, 'yyyymmdd') = to_char(sysdate, 'yyyymmdd')
            union all
            select 'WLMS-WC' type, WAYBILL_NUM
            from JNETWLMS.T_SENDOUT_ORDER
            where to_char(CREATE_DATE, 'yyyymmdd') = to_char(sysdate, 'yyyymmdd'))
      group by type
      union all
      select '2.本月' a, type, count(1) cnt
      from (select 'TMS' type, WAYBILL_NUM
            from JNETTMS.T_ORDER
            where to_char(CREATE_DATE, 'yyyymm') = to_char(sysdate, 'yyyymm')
            union all
            select 'WLMS-TC' type, SHIPPING_NUM waybill_num
            from JNETWLMS.T_SENDIN_ORDER
            where to_char(CREATE_DATE, 'yyyymm') = to_char(sysdate, 'yyyymm')
            union all
            select 'WLMS-WC' type, WAYBILL_NUM
            from JNETWLMS.T_SENDOUT_ORDER
            where to_char(CREATE_DATE, 'yyyymm') = to_char(sysdate, 'yyyymm'))
      group by type
      union all
      select '1.上月' a, type, count(1) cnt
      from (select 'TMS' type, WAYBILL_NUM
            from JNETTMS.T_ORDER
            where to_char(CREATE_DATE, 'yyyymm') = to_char(add_months(sysdate , -1)  , 'yyyymm')
            union all
            select 'WLMS-TC' type, SHIPPING_NUM waybill_num
            from JNETWLMS.T_SENDIN_ORDER
            where to_char(CREATE_DATE, 'yyyymm') = to_char(add_months(sysdate , -1)  , 'yyyymm')
            union all
            select 'WLMS-WC' type, WAYBILL_NUM
            from JNETWLMS.T_SENDOUT_ORDER
            where to_char(CREATE_DATE, 'yyyymm') = to_char(add_months(sysdate , -1), 'yyyymm'))
      group by type)
order by a 
""",
    "column": [
        "a",
        "type",
        "cnt"
    ]
    })
    headers = { 
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)  
    if(data['code']==200): 
        rows = data['data']
        print(rows)
        dingding_bot("订单统计","![订单统计]()\n"+formatMarkdown(rows, {
            '_id_': '序号',
            'a': '日期' ,
            'type': '业务' ,
            'cnt': '数量🔢' ,
        }) , True,None,None) 
if __name__ == "__main__":
    main()
    order()