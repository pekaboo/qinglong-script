import sys
import os
def fillInfo(SKU):
    sys.path.append(r'/Users/wangjun/Code/GITEE/mac-config-sync/Script/pyscript/common/selenium/')
    from SeleniumHelper import SeleniumHelper
    try:
        a = SeleniumHelper()
        product_sku = SKU;
        product_title = SKU;
        product_title_en = SKU;
        product_declared_name_zh = SKU;
        product_declared_name = SKU;
        product_declared_value = 1;
        product_weight = 1;
        product_length = 1;
        product_width = 1;
        product_height = 1;
        # a.drive("http://j-net.yunwms.com/#") 
        # a.drive("http://j-net.yunwms.com/product/product/list") 
        # a.click('//*[@id="fix_header_content"]/div/div[1]/ul/li[7]/input[1]')

        a.drive("http://j-net.yunwms.com/product/product/create") 
        a.input('//*[@id="product_sku"]',product_title)
        a.input('//*[@id="product_title"]',product_title)
        a.input('//*[@id="product_title_en"]',product_title_en)
        a.input('//*[@id="product_declared_value"]',product_declared_value)
        a.input('//*[@id="product_declared_name_zh"]',product_declared_name_zh)
        a.input('//*[@id="product_declared_name"]',product_declared_name)
        a.input('//*[@id="product_weight"]',product_weight)
        a.input('//*[@id="product_length"]',product_length)
        a.input('//*[@id="product_width"]',product_width)
        a.input('//*[@id="product_height"]',product_height)
    except Exception as e:
        # os 弹窗
        os.system("osascript -e 'display notification \""+str(e)+"\" with title \"错误\"'")

    # a.click('//*[@id="productForm"]/div/input[1]') 
def main():
    sys.path.append(r'/Users/wangjun/Code/GITEE/mac-config-sync/Script/pyscript/common')
    from AppSimpleUI import UserUi
    fields = ['SKU']
    values = ['']

    ui = UserUi('创建EC产品', 400, 300, fields, values)
    print(ui.data)
    fillInfo(ui.data['SKU'])
main()