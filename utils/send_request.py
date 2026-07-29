import requests
import allure
import pymysql

@allure.step("2.发送HTTP请求")
def send_http_request(request_data):
    res = requests.request(**request_data)
    return res

# 工具函数：发送JDBC请求
def send_jdbc_request(sql, index=0):
    # 执行数据库断言
    # 1.连接数据库
    # 桥（连接数据库）
    conn = pymysql.Connect(
        host="127.0.0.1",
        port=3306,
        database="mydb",
        user="root",
        password="123456",
        charset="utf8"
    )
    # 驴（创建游标）
    cur = conn.cursor() # 创建游标
                
    # 3.执行语句
    cur.excute(sql)
    result = cur.fetchone() # 返回一个元组
                
    # 4.关闭数据库
    cur.close()
    conn.close()
                
    
    return result[index]
