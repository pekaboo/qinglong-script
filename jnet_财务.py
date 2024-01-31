"""
cron: 00 18 * * *
new Env(' JNET 财务数据📊');
"""
from jnet_notify_fenxiao import *

def main():
    import requests
    import json 
    url = "http://ec.wangyitu.tech:5085/api/jnetrpt/sql"

    payload = json.dumps({
    "sql": """with a as (
    select to_char(h.CREATE_DATE,'yyyymmdd') day,a.NAME,sum(h.AMOUNT) AMOUNT
from JNETPAY.T_TRANSACTION_HISTORY h
         left join JNETPAY.T_ACCOUNT a on h.ACCOUNT_ID = a.ID
where h.TRANSACTION_TYPE = 10 and  to_char(h.CREATE_DATE,'yyyymmdd')> to_char(sysdate-1,'yyyymmdd')
group by to_char(h.CREATE_DATE,'yyyymmdd'),a.NAME
order by a.NAME,to_char(h.CREATE_DATE,'yyyymmdd') desc
)
select * from  a
union
select '_1','今天合计',sum(AMOUNT)AMOUNT from a

union
 select '_2','本月合计', (select sum(h.AMOUNT) AMOUNT from JNETPAY.T_TRANSACTION_HISTORY h where h.TRANSACTION_TYPE = 10 and to_char(h.CREATE_DATE,'yyyymm')=to_char(sysdate,'yyyymm')
) AMOUNT from dual
union
select '_3','上月合计', (select sum(h.AMOUNT) AMOUNT from JNETPAY.T_TRANSACTION_HISTORY h where h.TRANSACTION_TYPE = 10 and to_char(h.CREATE_DATE,'yyyymm')=to_char(add_months(sysdate,-1),'yyyymm')
) AMOUNT from dual

""",
    "column": [
        "day",
        "NAME",
        "amount"
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
        dingding_bot("JNET 收款","![JNET 收款]()\n"+formatMarkdown(rows, {
            '_id_': '序号',
            'day': '日期' ,
            'NAME': '名称' ,
            'amount': '金额💰' ,
        }) , True,None,None)

if __name__ == "__main__":
    main()

