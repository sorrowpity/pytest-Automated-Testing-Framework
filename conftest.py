import sqlite3
from pathlib import Path

import pytest

from config.config import *

# 胶水文件

@pytest.fixture(scope="session", autouse=True)
def destroy_data():
    yield

    # 对当前示例环境做“无破坏性”的清理：优先支持 sqlite，MySQL 仅在明确配置时执行
    sqls = CLEANUP_SQLS

    try:
        if DB_BACKEND.lower() == "mysql":
            import pymysql

            conn = pymysql.Connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                charset="utf8",
                autocommit=True,
            )
            cur = conn.cursor()
            for sql in sqls:
                cur.execute(sql)
            cur.close()
            conn.close()
        else:
            db_path = Path(__file__).resolve().parent / DB_SQLITE_PATH
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            for sql in sqls:
                try:
                    cur.execute(sql)
                except Exception:
                    # SQLite 对 MySQL-only 语句可能不具备兼容性；这里做降级清理，不让 fixture 中断测试
                    pass
            conn.commit()
            cur.close()
            conn.close()
    except Exception as exc:
        # 该项目的示例环境并不一定具备 MySQL，失败不应该让测试整体红灯
        print(f"数据库清理未执行（{exc.__class__.__name__}）：{exc}")

    print("资源销毁")
    
