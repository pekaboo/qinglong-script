# ====================================================================================
# # 钉钉
DD_BOT_TOKEN= 'dd5d6ab675280baebe1b27e1886cc77cbde10c3c1260db3fd10f6193eaa7818e',                # 钉钉机器人的 DD_BOT_SECRET
DD_BOT_SECRET= 'SEC6c3ce660fe65ab1df513bb9d0f304fd1bb32780455b52face67bdb7c8a610087',                 # 钉钉机器人的 DD_BOT_TOKEN

# ====================================================================================
# DB & jnet_notify_fenxiao
# DB_HOST = '39.170.82.20'
# DB_USER = 'root'
# DB_PASSWORD = 'cycx_vo=oe8_mo5BY078rA_/_84j_C5'
# DB_DATABASE = 'dev_dms'
DB_HOST = 'rm-j6c3543mp29dvhf93fo.mysql.rds.aliyuncs.com'
DB_USER = 'ec_user_r'
DB_PASSWORD = 'EC_D6B9A0_6B9BDA053x'
DB_DATABASE = 'wms'
DB_SQL='''select p.product_barcode,  count(1) cnt,ba.ib_quantity  qty
from     wms.orders o
         left join order_product p on o.order_id = p.order_id
         inner join (select product_id,sum(ib_quantity) ib_quantity from inventory_batch group by product_id) ba on p.product_id = ba.product_id
where
   order_status = 8 and (remark = 'vicky_fx' or remark = '2158-fx' )
group by p.product_barcode order by 3'''
DB_SELECTED_FIELD = ['product_barcode', 'cnt', 'qty']