import pytest

# 胶水文件

@pytest.fixture(scope="session",autouse=True)
def f():
    print("测试前置操作")
    yield
    print("测试后置操作")
    
