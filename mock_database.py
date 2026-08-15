# -*- coding: utf-8 -*-
"""统一数据库访问层：SQLite（本地）/ MySQL（Jenkins）双模式。

职责划分：
- mock_backend.py   业务读写（加购、下单、支付……）
- mock_seed.py      批量造数（1000 商品 / 100 买家）
- utils/send_request.py  断言查询（send_jdbc_request 独立实现，连同一个库）
"""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "mock_test.db"


def _is_mysql():
    return os.environ.get("DB_BACKEND", "sqlite").lower() == "mysql"


def get_conn():
    """按 DB_BACKEND 返回连接。行统一用 dict 风格访问：row["goods_name"]。"""
    if _is_mysql():
        import pymysql

        return pymysql.Connect(
            host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            database=os.environ.get("MYSQL_DATABASE", "mydb"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            charset="utf8",
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _sql(sql: str) -> str:
    """SQL 统一用 ? 占位；MySQL 时替换成 %s，并转义字面 %（LIKE 通配符）。

    顺序很关键：先转义字面 %，再把 ? 换成 %s，否则 %s 会被二次转义成 %%s。
    """
    if _is_mysql():
        sql = sql.replace("%", "%%")  # LIKE 'user%' -> 'user%%'
        sql = sql.replace("?", "%s")
    return sql


def execute(sql: str, params=()):
    """执行 INSERT/UPDATE/DELETE，返回 lastrowid。"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql(sql), params)
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    conn.close()
    return last_id


def query_one(sql: str, params=()):
    """返回单行（dict 风格）或 None。"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql(sql), params)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def query_all(sql: str, params=()):
    """返回多行（list[dict 风格]）。"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql(sql), params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def init_db():
    """本地 SQLite 建表（幂等）+ 最小种子。send_request 断言前也会调用。"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ==================== 管理员表 ====================
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sp_manager (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mg_name TEXT NOT NULL,
            mg_pwd TEXT NOT NULL,
            mg_state INTEGER DEFAULT 1
        )
        """
    )

    # ==================== 用户（买家）表 ====================
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sp_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            state INTEGER DEFAULT 1
        )
        """
    )

    # ==================== 商品分类表 ====================
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sp_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cat_name TEXT NOT NULL,
            cat_pid INTEGER DEFAULT 0,
            cat_level INTEGER DEFAULT 0,
            cat_deleted INTEGER DEFAULT 0,
            cat_icon TEXT DEFAULT '',
            cat_src TEXT DEFAULT ''
        )
        """
    )

    # ==================== 商品属性表 ====================
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sp_attribute (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attr_name TEXT NOT NULL,
            cat_id INTEGER DEFAULT 0,
            attr_sel TEXT DEFAULT '',
            attr_write TEXT DEFAULT '',
            attr_vals TEXT DEFAULT '',
            delete_time INTEGER DEFAULT NULL
        )
        """
    )

    # ==================== 商品表 ====================
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sp_goods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goods_name TEXT NOT NULL,
            goods_price REAL DEFAULT 0.0,
            goods_number INTEGER DEFAULT 0,
            goods_weight INTEGER DEFAULT 0,
            cat_id INTEGER DEFAULT 0,
            goods_introduce TEXT DEFAULT '',
            goods_big_logo TEXT DEFAULT '',
            goods_small_logo TEXT DEFAULT '',
            goods_state INTEGER DEFAULT 0,
            add_time INTEGER DEFAULT 0,
            is_del INTEGER DEFAULT 0,
            hot_mumber INTEGER DEFAULT 0,
            is_promote INTEGER DEFAULT 0,
            upd_time INTEGER DEFAULT NULL,
            delete_time INTEGER DEFAULT NULL
        )
        """
    )

    # ==================== 购物车表 ====================
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sp_cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goods_id INTEGER NOT NULL,
            goods_num INTEGER DEFAULT 1,
            add_time INTEGER DEFAULT 0
        )
        """
    )

    # ==================== 订单表 ====================
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sp_order (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            total_price REAL DEFAULT 0.0,
            pay_status INTEGER DEFAULT 0,
            order_status INTEGER DEFAULT 0,
            create_time INTEGER DEFAULT 0,
            pay_time INTEGER DEFAULT NULL
        )
        """
    )

    # ==================== 订单明细表 ====================
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sp_order_item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            goods_id INTEGER NOT NULL,
            goods_num INTEGER NOT NULL,
            goods_price REAL DEFAULT 0.0
        )
        """
    )

    # ==================== 最小种子数据 ====================
    cur.execute("SELECT COUNT(*) FROM sp_manager WHERE mg_name = 'admin'")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO sp_manager (mg_name, mg_pwd, mg_state) VALUES (?, ?, ?)",
            ("admin", "123456", 1),
        )

    cur.execute("SELECT COUNT(*) FROM sp_user WHERE username = 'admin'")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO sp_user (username, password, state) VALUES (?, ?, ?)",
            ("admin", "123456", 1),
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"SQLite database ready at: {DB_PATH}")
