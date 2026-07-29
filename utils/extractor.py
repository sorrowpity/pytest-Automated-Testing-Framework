import jsonpath
import allure

from utils.send_request import send_jdbc_request


def json_extractor(case,res,all):
    if case["jsonExData"]:
        with allure.step("4.JSON提取"):
        # 首先要把 jsonExData 的key 和 value 拆开，使用eval()函数把字符串转换成字典
            for key, value in eval(case["jsonExData"]).items():
                # print(key, value)
                # 1.提取数据
                # 2.把提取的数据存入全局变量
                value = jsonpath.jsonpath(res.json(), value)[0]
                
                all[key] = value
                # print(all)
                

def jdbc_extractor(case,all):
    with allure.step("4.JDBC提取"):
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