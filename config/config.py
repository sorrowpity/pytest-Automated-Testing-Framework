# 环境基准地址
BASE_URL = "http://127.0.0.1:8888/api/private/v1/"

# excel格式的测试用例文件配置
EXCEL_FILE = "../data/data1.xlsx"
SHEET_NAME = "Sheet1"

# 数据库后端选择：mysql 或 sqlite
DB_BACKEND = "sqlite"

# mysql数据库配置信息（保留，便于未来切到真实库）
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "mydb"
DB_USER = "root"
DB_PASSWORD = "123456"

# sqlite mock 数据库路径（使用与 mock_database.py 一致的文件）
DB_SQLITE_PATH = "data/mock_test.db"

# mysql 资源（如果切到真实 mysql，这些行会在 teardown 时执行）
SQL1 = "delete from sp_category where cat_name = '大码服装'"
SQL2 = "delete from sp_attribute where attr_name = 'VIP尺码'"
SQL3 = "delete from sp_goods where goods_name = '大码牛仔裤'"