"""
cron: 00 9-18 * * *
new Env(' JNET 仓发订单任务统计');
"""

#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
from jnet_notify_fenxiao import *


def main():
    rowsA = select(['order_status','cnt'], '''SELECT '待处理' order_status, COUNT(*) cnt
  FROM wms.orders where order_status = 4
union all
SELECT
  CASE order_status
    WHEN 5 THEN '已下架'
    WHEN 8 THEN '已出库'
  END AS order_status,
  COUNT(*) cnt
FROM wms.orders
WHERE order_status in (5,8) and DATE(date_sub(NOW(), INTERVAL 1 DAY)) = DATE(add_time)
GROUP BY order_status''')
    dingding_bot("仓发业务任务:", "## 仓发业务任务:\n"+formatMarkdown(rowsA, {
        '_id_': '序号',
        'order_status': '状态',
        'cnt': '数量'
    }), True,JNET_DD_BOT_TOKEN01,JNET_DD_BOT_SECRET01)



if __name__ == "__main__":
    main()
    
    
