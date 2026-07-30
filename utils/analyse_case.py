import allure
from config.config import BASE_URL

@allure.step("1.解析请求数据")
def analyse_case(case):
    # 1.数据解析，1.url不存在 ，2。部分字符串需要变成字典，3.预期结果这个参数不能在请求中传输，不然会报错
    method = case["method"]
    url = BASE_URL + case["path"]
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
    
    # 加上返回值
    return request_data
