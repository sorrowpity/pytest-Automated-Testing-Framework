from utils.excel_utils import read_excel
import pytest
import jsonpath
import requests
import pymysql
from jinja2 import Template
import allure

class TestRunner:
    
    # 读取测试数据
    data = read_excel()
    
    # 提取后的数据需要初始化一个全局的
    all = {}

    @pytest.mark.parametrize("case", data)
    def test_case(self, case):
        
        # 引用全局变量的all
        all = self.all
        
        # 根据all的值来渲染case
        case = eval(Template(str(case)).render(all))
        
        # 初始化allure报告
        allure.dynamic.feature(case["feature"])
        allure.dynamic.story(case["story"])
        allure.dynamic.title(case["title"])
        
        # 数据解析，1.url不存在 ，2。部分字符串需要变成字典，3.预期结果这个参数不能在请求中传输，不然会报错
        method = case["method"]
        url = "http://127.0.0.1:8888/api/private/v1/" + case["path"]
        headers = eval(case["headers"]) if isinstance(case["headers"], str) else None
        params = eval(case["params"]) if isinstance(case["params"], str) else None
        data = eval(case["data"]) if isinstance(case["data"], str) else None
        json = eval(case["json"]) if isinstance(case["json"], str) else None
        files = eval(case["files"]) if isinstance(case["files"], str) else None
        
        
        request_data = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "data": data,
            "json": json,
            "files": files
        }
        # print(request_data)
        
        
        
        #2发送请求
        res = requests.request(**request_data)
        #打印结果 调试需要
        print(res.json())
        # 3断言
        # assert res.json()["meta"]["msg"] == case["expected"]
        
        # HTTP响应断言
        if case["check"]:
            assert jsonpath.jsonpath(res.json(), case["check"])[0] == case["expected"]
        else:
            assert case["expected"] in res.text
            # res.json 是字典，res.text 是字符串
            
        # 数据库断言
        # 如果表中sql_check 和 sql_expected 都存在，那么就执行数据库断言
        if case["sql_check"] and case["sql_expected"]:
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
            cur.excute(case["sql_check"])
            result = cur.fetchone() # 返回一个元组
            
            # 4.关闭数据库
            cur.close()
            conn.close()
            

            assert result[0] == case["sql_expected"]
        
        
        # 步骤4 提取
        
        # json提取
        if case["jsonExData"]:
            # 首先要把 jsonExData 的key 和 value 拆开，使用eval()函数把字符串转换成字典
            for key, value in eval(case["jsonExData"]).items():
                # print(key, value)
                # 1.提取数据
                # 2.把提取的数据存入全局变量
                all[key] = jsonpath.jsonpath(res.json(), value)[0]
                # print(all)
                
                
        # 数据库sql提取
        if case["sqlExData"]:
            # 首先要把 sqlExData 的key 和 value 拆开，使用eval()函数把字符串转换成字典
            for key, value in eval(case["sqlExData"]).items():
                # print(key, value)
                # 1.执行语句
                # 2.把提取的数据存入全局变量
                conn = pymysql.Connect(
                    host="127.0.0.1",
                    port=3306,
                    database="mydb",
                    user="root",
                    password="123456",
                    charset="utf8"
                )
                cur = conn.cursor()
                cur.execute(value)
                result = cur.fetchone()
                cur.close()
                conn.close()
                all[key] = result[0]
                # print(all)