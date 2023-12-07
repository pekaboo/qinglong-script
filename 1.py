import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir="/Users/wangjun/Plugin/instantclient_19_19")

class OracleHelper:
    def __init__(self, host, port, user, pwd, dbname):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.dbname = dbname

    def __str__(self):
        return "host:%s,port:%s,user:%s,pwd:%s,dbname:%s" % (self.host, self.port, self.user, self.pwd, self.dbname)

    def __repr__(self):
        return "host:%s,port:%s,user:%s,pwd:%s,dbname:%s" % (self.host, self.port, self.user, self.pwd, self.dbname)

    def get_conn(self):
        """
        获取一个数据库连接
        :return:
        """ 
        try:
            conn = oracledb.connect(self.user, self.pwd, self.host + ":" + self.port + "/" + self.dbname)
            return conn
        except Exception as e:
            print("数据库连接失败：", e)

    def close_conn(self, conn):
        """
        关闭数据库连接
        :param conn:
        :return:
        """
        try:
            if conn:
                conn.close()
        except Exception as e:
            print("关闭数据库连接失败：", e)

    def get_data(self, sql):
        """
        查询数据
        :param sql:
        :return:
        """
        data = None
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            self.close_conn(conn)
        except Exception as e:
            print("查询数据失败：", e)
        finally:
            return data
    def exec(self,sql,data=None):
        print(sql,data)
        conn = self.get_conn()
        cur = conn.cursor()
        if data:
            cur.execute(sql,data)
        else:
            cur.execute(sql)
        conn.commit()
        cur.close()

 
# filepath = r"C:\Users\wangjun\Desktop\2021年终嘉年华数据\2022云帆合约计划.xlsx"
# columns = ['CUST_NAME','AUTH_ID','近3个月月均','建议合约类型']
# sheet_index = 1
# a = excel_to_json(filepath,columns,sheet_index,0)


helper = OracleHelper("121.41.103.158","1521","jnetrpt","ru4VB5qCc","wms01")
a = helper.get_data("select * from t_user")
print(a)