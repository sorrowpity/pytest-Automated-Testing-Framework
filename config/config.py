# 环境基准地址
BASE_URL = "http://127.0.0.1:8888/api/private/v1/"

# excel格式的测试用例文件配置
EXCEL_FILE = "../data/data1.xlsx"
SHEET_NAME = "Sheet1"

# mysql数据库配置信息
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "mydb"
DB_USER = "root"
DB_PASSWORD = "123456"

# mysql 资源
SQL1 = "delete from sp_category where cat_name = '大码服装'",
SQL2 = "delete from sp_attribute where attr_name = 'VIP尺码'",
SQL3 = "delete from sp_goods where goods_name = '大码牛仔裤'"