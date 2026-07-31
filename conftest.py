import pytest
import pymysql
from config.config import *
# 胶水文件

@pytest.fixture(scope="session",autouse=True)
def destroy_data():

    yield
    sqls = {SQL1,SQL2,SQL3}
    
    conn = pymysql.Connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            charset="utf8",
            autocommit=True
    )
    # 驴（创建游标）
    cur = conn.cursor() # 创建游标
                    
    # 3.执行语句
    for sql in sqls:
        cur.excute(sql)
    
                    
    # 4.关闭数据库
    cur.close()
    conn.close()
    print("资源销毁")
    
