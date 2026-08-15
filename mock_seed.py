# -*- coding: utf-8 -*-
"""批量造数脚本：分类 + 商品(1000) + 买家(100)。

职责划分：
- mock_seed.py    造数（幂等造数 / reset_data 整库重置）
- mock_backend.py 业务读写（加购、下单、支付……）
- conftest.py     每个测试会话 setup 时调用 reset_data()，保证从确定干净状态开始

用法:
    python mock_seed.py                        # 幂等造数（已存在则跳过）
    python mock_seed.py --reset                # 整库重置（清空 + 重造，修掉脏数据 / id 空洞）
    DB_BACKEND=mysql python mock_seed.py       # MySQL（需先执行 sql/init_mysql.sql 建表）
    DB_BACKEND=mysql python mock_seed.py --reset   # MySQL 整库重置
"""
import sys
import time

from mock_database import init_db, execute, query_one, get_conn, _is_mysql

CATEGORIES = ["手机数码", "电脑办公", "家用电器", "服饰鞋包", "食品生鲜",
              "图书文娱", "美妆个护", "运动户外", "家居家具", "母婴玩具"]

BUYER_COUNT = 100
GOODS_PER_CAT = 100
TOTAL_GOODS = GOODS_PER_CAT * len(CATEGORIES)

# 8 张表，按「先子表后父表」顺序排列。
# 本项目没有外键约束，顺序不影响正确性，只是清库时的习惯（先清依赖方）。
TABLES = [
    "sp_order_item",
    "sp_order",
    "sp_cart",
    "sp_goods",
    "sp_attribute",
    "sp_category",
    "sp_user",
    "sp_manager",
]


def seed_admin(conn=None):
    """重建管理员账号（sp_manager + sp_user 各一条 admin），幂等。

    传入 conn 时复用同一连接（配合 reset_data 的单连接批量操作），不提交不关闭。
    """
    if query_one("SELECT COUNT(*) AS c FROM sp_manager WHERE mg_name = 'admin'", conn=conn)["c"] == 0:
        execute(
            "INSERT INTO sp_manager (mg_name, mg_pwd, mg_state) VALUES (?, '123456', 1)",
            ("admin",),
            conn=conn,
        )
    if query_one("SELECT COUNT(*) AS c FROM sp_user WHERE username = 'admin'", conn=conn)["c"] == 0:
        execute(
            "INSERT INTO sp_user (username, password, state) VALUES (?, '123456', 1)",
            ("admin",),
            conn=conn,
        )


def seed_categories(conn=None):
    """造 10 个商品分类。已存在则跳过（幂等）。"""
    if query_one("SELECT COUNT(*) AS c FROM sp_category", conn=conn)["c"] > 0:
        print("分类已存在，跳过")
        return
    for name in CATEGORIES:
        execute(
            "INSERT INTO sp_category (cat_name, cat_pid, cat_level, cat_deleted) VALUES (?, 0, 1, 0)",
            (name,),
            conn=conn,
        )
    print(f"分类造数完成：{len(CATEGORIES)} 个")


def seed_goods(conn=None):
    """造 1000 件商品。已存在则跳过（幂等）。

    注意：第 1 件商品固定 0 库存，供「库存不足下单失败」用例使用，不能被改成 100。
    """
    if query_one("SELECT COUNT(*) AS c FROM sp_goods", conn=conn)["c"] > 0:
        print("商品已存在，跳过")
        return
    now = int(time.time())
    for i in range(1, TOTAL_GOODS + 1):
        cat_id = (i - 1) // GOODS_PER_CAT + 1
        # 第 1 件商品固定 0 库存，供「库存不足下单失败」用例使用
        stock = 0 if i == 1 else 100
        price = round(10 + (i % 1000) * 0.1, 2)
        name = f"{CATEGORIES[cat_id - 1]}-{i:04d}"
        execute(
            "INSERT INTO sp_goods (goods_name, goods_price, goods_number, goods_weight, cat_id, goods_state, add_time) "
            "VALUES (?, ?, ?, 100, ?, 1, ?)",
            (name, price, stock, cat_id, now),
            conn=conn,
        )
    print(f"商品造数完成：{TOTAL_GOODS} 件")


def seed_buyers(conn=None):
    """造 100 个买家（user001 ~ user100）。已存在则跳过（幂等）。"""
    if query_one("SELECT COUNT(*) AS c FROM sp_user WHERE username LIKE 'user%'", conn=conn)["c"] >= BUYER_COUNT:
        print("买家已存在，跳过")
        return
    for i in range(1, BUYER_COUNT + 1):
        execute(
            "INSERT INTO sp_user (username, password, state) VALUES (?, '123456', 1)",
            (f"user{i:03d}",),
            conn=conn,
        )
    print(f"买家造数完成：{BUYER_COUNT} 个")


def seed_all(conn=None):
    """按依赖顺序重建全部种子数据：admin -> 分类 -> 商品 -> 买家。"""
    seed_admin(conn)
    seed_categories(conn)
    seed_goods(conn)
    seed_buyers(conn)


def reset_data():
    """整库重置：清空 8 张表后重造，回到确定的干净状态。

    与「存在即跳过」的幂等造数不同，本函数会**无条件清空再重造**：
    - MySQL  用 TRUNCATE，会顺带重置 AUTO_INCREMENT，修掉重复 admin 去重后留下的 id 空洞；
    - SQLite 用 DELETE + 清 sqlite_sequence，达到同样效果（id 重新从 1 排）。

    由 conftest.py 在每个测试会话 setup 时调用：保证测试永远从干净状态开始，
    不依赖上一次 teardown 是否正常执行（即使进程被 kill 也能自愈）。

    注意：MySQL 需先执行 sql/init_mysql.sql 建表；SQLite 会在这里自动 init_db 建表。
    """
    if not _is_mysql():
        # SQLite 先确保建表（幂等）；MySQL 的建表走 sql/init_mysql.sql
        init_db()

    # 单连接完成「清空 + 重造」：避免每条 INSERT 都新建连接（MySQL 新建连接开销大，
    # 1000 件商品若逐个连接会慢到几秒~几十秒）。
    conn = get_conn()
    try:
        for table in TABLES:
            if _is_mysql():
                # TRUNCATE 重置 AUTO_INCREMENT，连 id 空洞一起修掉
                execute(f"TRUNCATE TABLE {table}", conn=conn)
            else:
                execute(f"DELETE FROM {table}", conn=conn)
                # SQLite 的 AUTOINCREMENT 计数存在 sqlite_sequence 里，清掉才能让 id 从 1 重新排
                execute("DELETE FROM sqlite_sequence WHERE name = ?", (table,), conn=conn)
        seed_all(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    backend = "MySQL" if _is_mysql() else "SQLite"
    print(f"[{backend}] 整库重置完成")


if __name__ == "__main__":
    if not _is_mysql():
        init_db()  # SQLite 先建表；MySQL 需先跑 sql/init_mysql.sql

    if "--reset" in sys.argv:
        reset_data()
    else:
        seed_all()
        backend = "MySQL" if _is_mysql() else "SQLite"
        print(f"[{backend}] 造数完成")
