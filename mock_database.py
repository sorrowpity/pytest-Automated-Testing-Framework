import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "mock_test.db"


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    cur = conn.cursor()

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

    cur.execute(
        "SELECT COUNT(*) FROM sp_manager WHERE mg_name = 'admin'"
    )
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO sp_manager (mg_name, mg_pwd, mg_state) VALUES (?, ?, ?)",
            ("admin", "123456", 1),
        )

    cur.execute(
        "SELECT COUNT(*) FROM sp_user WHERE username = 'admin'"
    )
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO sp_user (username, password, state) VALUES (?, ?, ?)",
            ("admin", "123456", 1),
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

    conn.commit()
    conn.close()


def query_one(sql: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        return None
    return row[0]


if __name__ == "__main__":
    init_db()
    print(f"SQLite database ready at: {DB_PATH}")
