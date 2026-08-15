# -*- coding: utf-8 -*-
"""批量造数脚本：分类 + 商品(1000) + 买家(100)。

用法:
    python mock_seed.py                     # 本地 SQLite
    DB_BACKEND=mysql python mock_seed.py    # MySQL（需先执行 sql/init_mysql.sql）
"""
import time

from mock_database import init_db, execute, query_one, _is_mysql

CATEGORIES = ["手机数码", "电脑办公", "家用电器", "服饰鞋包", "食品生鲜",
              "图书文娱", "美妆个护", "运动户外", "家居家具", "母婴玩具"]

BUYER_COUNT = 100
GOODS_PER_CAT = 100
TOTAL_GOODS = GOODS_PER_CAT * len(CATEGORIES)


def seed_categories():
    if query_one("SELECT COUNT(*) AS c FROM sp_category")["c"] > 0:
        print("分类已存在，跳过")
        return
    for name in CATEGORIES:
        execute(
            "INSERT INTO sp_category (cat_name, cat_pid, cat_level, cat_deleted) VALUES (?, 0, 1, 0)",
            (name,),
        )
    print(f"分类造数完成：{len(CATEGORIES)} 个")


def seed_goods():
    if query_one("SELECT COUNT(*) AS c FROM sp_goods")["c"] > 0:
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
        )
    print(f"商品造数完成：{TOTAL_GOODS} 件")


def seed_buyers():
    if query_one("SELECT COUNT(*) AS c FROM sp_user WHERE username LIKE 'user%'")["c"] >= BUYER_COUNT:
        print("买家已存在，跳过")
        return
    for i in range(1, BUYER_COUNT + 1):
        execute(
            "INSERT INTO sp_user (username, password, state) VALUES (?, '123456', 1)",
            (f"user{i:03d}",),
        )
    print(f"买家造数完成：{BUYER_COUNT} 个")


if __name__ == "__main__":
    if not _is_mysql():
        init_db()  # SQLite 先建表；MySQL 需先跑 init_mysql.sql
    seed_categories()
    seed_goods()
    seed_buyers()
    backend = "MySQL" if _is_mysql() else "SQLite"
    print(f"[{backend}] 造数完成")
