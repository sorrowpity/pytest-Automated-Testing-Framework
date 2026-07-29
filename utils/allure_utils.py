import allure

def allure_init(case):
    # 初始化allure报告
    allure.dynamic.feature(case["feature"])
    allure.dynamic.story(case["story"])
    # allure.dynamic.title(case["title"])
    allure.dynamic.title(f"ID: {case["id"]}--{case['title']}")