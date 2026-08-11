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

# mysql 资源（如果切到真实 mysql，这些行会在 teardown 时执行）
SQL1 = "delete from sp_category where cat_name = '大码服装'"
SQL2 = "delete from sp_attribute where attr_name = 'VIP尺码'"
SQL3 = "delete from sp_goods where goods_name = '大码牛仔裤'"