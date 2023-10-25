"""
cron: 00 9-18 * * *
new Env(' JNET 仓发订单任务统计');
"""

#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
from jnet_notify_fenxiao import *


def main():
    rowsA = select(['order_status','cnt'], '''select * from (
    SELECT '2. 剩余待处理' order_status, COUNT(*) cnt
  FROM wms.orders where order_status = 4
union all
SELECT
  case when order_status = 8 and DATE(date_sub(NOW(), INTERVAL 1 DAY)) = DATE(add_time)
     THEN '1. 昨日出库数'
    when order_status = 5 and DATE(NOW()) = DATE(add_time)
     THEN '3. 今日已下架'
    when order_status = 8  and DATE(NOW()) = DATE(add_time) THEN '4. 今日已出库'
  END AS order_status,
  COUNT(*) cnt
FROM wms.orders
WHERE order_status in (5,8) and  DATE(add_time)>=DATE(date_sub(NOW(), INTERVAL 1 DAY))
GROUP BY order_status
) a order by a.order_status''')

    JNET_DD_BOT_TOKEN01= 'dd5d6ab675280baebe1b27e1886cc77cbde10c3c1260db3fd10f6193eaa7818e'             # 钉钉机器人的 DD_BOT_SECRET
    JNET_DD_BOT_SECRET01= 'SEC6c3ce660fe65ab1df513bb9d0f304fd1bb32780455b52face67bdb7c8a610087'               # 钉钉机器人的 DD_BOT_TOKEN
    dingding_bot("仓发业务任务:", "## 仓发业务任务:\n"+formatMarkdown(rowsA, {
        'order_status': '状态',
        'cnt': '数量'
    }), True,JNET_DD_BOT_TOKEN01,JNET_DD_BOT_SECRET01)



if __name__ == "__main__":
    main()
    
    
