import pytest
import logging

from jinja2 import Template

from utils.excel_utils import read_excel
from utils.allure_utils import allure_init
from utils.analyse_case import analyse_case
from utils.send_request import send_http_request
from utils.asserts import http_assert, jdbc_assert
from utils.extractor import json_extractor, jdbc_extractor

class TestRunner:
    
    # 读取测试数据
    data = read_excel()
    
    # 提取后的数据需要初始化一个全局的
    all = {}

    # data 形似 [{},{}]
    # case 形似 {}
    @pytest.mark.parametrize("case", data)
    def test_case(self, case):
        
        # 引用全局变量的all
        all = self.all
        
        # 根据all的值来渲染case
        # case 先转str,然后根据all提取的参数信息来渲染，Template 是把字符串转为模板对象，再调用render对case中
        # 可能包含的 {{}}类型进行 字典形式的key 取得value
        # jinja2
        case = eval(Template(str(case)).render(all))
        
        # 0.初始化allure
        allure_init(case)
        
        
        # 测试用例的描述信息日志,日志信息是个完整的字符串
        logging.info(f"0.用例ID:{case['id']} 模块:{case['feature']} 场景:{case['story']} 标题:{case['title']}")
        
        
        # 核心步骤1.分析case
        request_data = analyse_case(case)
        
        
        # 核心步骤2.发送HTTP请求
        res = send_http_request(request_data)
        

        # 3.处理断言
        
        # HTTP断言
        http_assert(case,res)
        
        # 数据库断言
        jdbc_assert(case)
        
        
        # 步骤4 提取
        
        # json提取
        json_extractor(case,res,all)
                
                
        # 数据库sql提取
        jdbc_extractor(case,all)
        