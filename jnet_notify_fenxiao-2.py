"""
cron: 00 18 * * *
new Env(' JNET 分销数据');
"""
from jnet_notify_fenxiao import *

def main():
    DB_SQL='''select p.product_barcode, sum(case when remark='vicky_fx' then 1 end) vicky, sum(case when remark='2158-fx' then 1 end) self, sum(1) cnt
from     wms.orders o
         left join order_product p on o.order_id = p.order_id
       where
   order_status = 8 and (remark = 'vicky_fx' or remark = '2158-fx' )
group by  p.product_barcode'''
    DB_SELECTED_FIELD = ['product_barcode', 'vicky','self','cnt']
    rowsA = select(DB_SELECTED_FIELD, DB_SQL)
    # dingding_bot("分销清单", "![](https://img.shields.io/badge/%F0%9F%A7%BE-%20%E5%88%86%E9%94%80%E6%B8%85%E5%8D%95-FFDD67.svg?style=flat-square)\n"+formatMarkdown(rowsA, {
    #     '_id_': '序号',
    #     'product_barcode': '商品条码',
    #     'cnt': '分销数量',
    #     'qty': '库存数量'
    # }), True,None,None)
    smtp("分销清单", formatMarkdown(rowsA),rowsA,'jessie.xu@j-net.com','分销清单')


if __name__ == "__main__":
    main()

