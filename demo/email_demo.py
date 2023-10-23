from jnet_notify_fenxiao import formatMarkdown, select, smtp

import sys
sys.path.append(r'../')
from env import *

if __name__ == "__main__":
    DB_SQL='''select p.product_barcode 产品代码,  count(1) 数量,ba.ib_quantity  库存
    from     wms.orders o
            left join order_product p on o.order_id = p.order_id
            inner join (select product_id,sum(ib_quantity) ib_quantity from inventory_batch group by product_id) ba on p.product_id = ba.product_id
    where
    order_status = 8 and (remark = 'vicky_fx' or remark = '2158-fx' )
    group by p.product_barcode order by 3'''
    DB_SELECTED_FIELD = ['产品代码', '数量', '库存']
    rowsA = select(DB_SELECTED_FIELD, DB_SQL)
    # print(formatMarkdown(rowsA))
    smtp("分销清单", formatMarkdown(rowsA),rowsA,'1375721577@qq.com','1375721577')
