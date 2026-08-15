import sqlite3
from pathlib import Path

import pytest

from config.config import *
from mock_seed import reset_data


@pytest.fixture(scope="session", autouse=True)
def reset_db():
    # ==================== setup：先把数据库重置到确定干净状态 ====================
    # 为什么放在 setup 而不是只靠 teardown：
    #   teardown 只有在测试会话**正常结束**时才会执行；一旦进程被 kill（Jenkins 里的
    #   taskkill、手动 Ctrl+C、seed 脚本崩溃到一半），teardown 根本没机会跑，下一次
    #   测试就会顶着脏数据上。setup 重置则每次都从「清空 + 重造」开始，天然免疫历史
    #   脏数据（含重复 admin 去重后留下的 id 空洞）。
    # 注意：MySQL 需先执行 sql/init_mysql.sql 建表；若表不存在，这里会抛出明确错误。
    reset_data()

    yield

    # ==================== teardown：清理本次测试产生的数据 ====================
    # 让数据库在两次运行之间也保持干净（方便人工查看）；best-effort，失败不阻断测试。
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
                    # SQLite 对个别 MySQL-only 语句可能不兼容，降级跳过，不让 fixture 中断测试
                    pass
            conn.commit()
            cur.close()
            conn.close()
    except Exception as exc:
        # 该项目的示例环境并不一定具备 MySQL；清理失败不应让测试整体红灯
        print(f"数据库清理未执行（{exc.__class__.__name__}）：{exc}")

    print("资源销毁")
