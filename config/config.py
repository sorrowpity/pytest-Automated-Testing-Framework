import os

# 环境基准地址
BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8888/api/private/v1/")

# excel格式的测试用例文件配置
EXCEL_FILE = "../data/data1.xlsx"
SHEET_NAME = "Sheet1"

# 数据库后端选择：mysql 或 sqlite
DB_BACKEND = os.environ.get("DB_BACKEND", "sqlite")

# mysql数据库配置信息（通过环境变量注入，避免密码泄露）
DB_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
DB_NAME = os.environ.get("MYSQL_DATABASE", "mydb")
DB_USER = os.environ.get("MYSQL_USER", "root")
DB_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")

# sqlite mock 数据库路径（使用与 mock_database.py 一致的文件）
DB_SQLITE_PATH = "data/mock_test.db"

# 测试数据清理（teardown 时按顺序执行，保证可重复运行）
# 只清理测试产生的数据 + 重置被测试改动的行，不删种子数据
CLEANUP_SQLS = [
    "DELETE FROM sp_order_item",
    "DELETE FROM sp_order",
    "DELETE FROM sp_cart",
    "DELETE FROM sp_goods WHERE goods_name LIKE '测试%'",
    "UPDATE sp_goods SET is_del = 0, goods_price = 10.2, goods_number = 100 WHERE id = 2",
    "UPDATE sp_goods SET is_del = 0, goods_price = 10.3, goods_number = 100 WHERE id = 3",
    "UPDATE sp_goods SET is_del = 0 WHERE id = 1000",
    "DELETE FROM sp_user WHERE username LIKE 'test%'",
]