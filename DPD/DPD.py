import requests
import pandas as pd
from jnet_notify_fenxiao import formatMarkdown, smtp


def gettrack(no):
    # https://dpd-site-tracing-backend-api-prod.dpd.ru/api/v3/order?orderNumber=RU089415742&lang=EN
    req = requests.get('https://dpd-site-tracing-backend-api-prod.dpd.ru/api/v3/order?orderNumber=' + no + '&lang=EN')
    if 'type' in req.json():
        return "Not found"
    else:
        tk = req.json()['state']
        # 根据时间排序取最后一个
        tk.sort(key=lambda x: x['state_moment'])
        return tk[-1]['state_name'],tk[-1]['state_moment']
aaa = [
  'RU089570713',
# 'RU089570717',
# 'RU089570723',
# 'RU089570703',
# 'RU089570845',
# 'RU089570710',
# 'RU089570714',
# 'RU089570721',
# 'RU089578813',
# 'RU089570708',
# 'RU089570716',
# 'RU089570722',
# 'RU089570725',
# 'RU089570705',
# 'RU089570712',
# 'RU089570718',
# 'RU089570726',
# 'RU089570728',
# 'RU089570709',
# 'RU089570715',
# 'RU089570719',
# 'RU089570919',
# 'RU089570727',
# 'RU089570711',
# 'RU089574413',
# 'RU089570720',
# 'RU089570724',
# 'RU089579072'
]
bbb = []
for a in aaa:
    x,y = gettrack(a)
    print(a,x,y)
    bbb.append({
        'a':a,
        'x':x,
        'y':y
    })
# print(bbb)

df = pd.DataFrame(bbb)
# 将 DataFrame 写入新的 Excel 文件
df.to_excel('output.xlsx', index=False)

smtp("清单", 'test',bbb,'jun.wang@j-net.com','清单')