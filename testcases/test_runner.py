import pytest
import jsonpath
import requests
from jinja2 import Template
import allure

from utils.excel_utils import read_excel
from utils.allure_utils import allure_init
from utils.analyse_case import analyse_case
from utils.send_request import send_http_request
from utils.send_request import send_jdbc_request

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
        
        # 0.初始化allure
        allure_init(case)
        
        
        # 核心步骤1.分析case
        request_data = analyse_case(case)
        
        
        # 核心步骤2.发送HTTP请求
        res = send_http_request(request_data)
        

        # 3.处理断言
        
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
            
            assert send_jdbc_request(case["sql_check"]) == case["sql_expected"]
        
        
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
                value = send_jdbc_request(value)
                all[key] = value
                # print(all)