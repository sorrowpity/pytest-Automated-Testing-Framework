import sqlite3
from pathlib import Path

import requests
import allure
import pymysql
import logging
from config.config import *
from mock_database import init_db

@allure.step("2.发送HTTP请求")
def send_http_request(request_data):
    res = requests.request(**request_data)
    logging.info(f"2.发送HTTP请求, 响应文本为: {res.text}")
    return res

# 工具函数：发送JDBC请求
def send_jdbc_request(sql, index=0):
    """兼容当前 mock sqlite 数据库与未来真实 mysql 的查询入口。
    SQL 断言用例都能复用这一层；如果 MySQL 未配置或不可连，则自动降级到 sqlite。
    """
    try:
        if DB_BACKEND.lower() == "mysql":
            conn = pymysql.Connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                charset="utf8"
            )
            cur = conn.cursor()
            cur.execute(sql)
            result = cur.fetchone()
            cur.close()
            conn.close()
        else:
            init_db()
            db_path = Path(__file__).resolve().parent.parent / DB_SQLITE_PATH
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(sql)
            result = cur.fetchone()
            cur.close()
            conn.close()
    except Exception:
        # 最终兜底：没有条件去连真实 MySQL，就用 sqlite 的 mock 数据库
        init_db()
        db_path = Path(__file__).resolve().parent.parent / DB_SQLITE_PATH
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchone()
        cur.close()
        conn.close()

    if result is None:
        return None
    if isinstance(result, tuple):
        if len(result) <= index:
            return None
        return result[index]
    return result
