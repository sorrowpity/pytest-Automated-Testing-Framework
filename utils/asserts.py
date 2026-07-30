import jsonpath
import allure
import logging

from utils.send_request import send_jdbc_request

@allure.step("3.HTTP响应断言")
def http_assert(case,res):
    # HTTP响应断言
    if case["check"]:
        result = jsonpath.jsonpath(res.json(), case["check"])[0]
        logging.info(f"3.HTTP响应断言内容: 实际结果({result}) == 预期结果({case["expected"]})")
        assert result == case["expected"]
    else:
        logging.info(f"3.HTTP响应断言内容: 预期结果({case["expected"]}) in 实际结果({res.text})")
        assert case["expected"] in res.text
        # res.json 是字典，res.text 是字符串


def jdbc_assert(case):
    # 如果表中sql_check 和 sql_expected 都存在，那么就执行数据库断言
    if case["sql_check"] and case["sql_expected"]:
        # 执行数据库断言
        with allure.step("3.JDBC响应断言"):
            result = send_jdbc_request(case["sql_check"])
            logging.info(f"3.JDBC响应断言内容: 实际结果({result}) == 预期结果({case["sql_expected"]})")
            assert result == case["sql_expected"]