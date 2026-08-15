# pytest 电商接口自动化测试平台

基于 **Python + pytest + Allure** 的电商接口自动化测试平台，覆盖 **商品 / 购物车 / 订单** 完整业务链路，支持 **Excel 数据驱动**、**MySQL/SQLite 双模式数据库断言**、**1000+ 造数**、**Locust 性能压测**，集成 **Jenkins Pipeline CI/CD**，自动推送报告到 **GitHub Pages** 并通过 **钉钉机器人** 通知（PC + 手机双链接）。

在线报告: [查看最新 Allure 报告](https://sorrowpity.github.io/pytest-Automated-Testing-Framework/)

---

## 架构总览

```
Excel 用例 (data/data1.xlsx, 34 条)
       |
       v
test_runner.py  ----  pytest 参数化执行
       |
       +-- analyse_case.py   解析用例 -> 构造 HTTP 请求
       +-- send_request.py   发送请求 + MySQL/SQLite 双模式 JDBC 断言
       +-- asserts.py        JSONPath 断言 + 数据库断言
       +-- extractor.py      JSON 提取 + SQL 提取(变量传递)
       +-- allure_utils.py   Allure 报告标记
       |
       v
电商 Mock 后端 (mock_backend.py, Flask)
       |   商品 / 分类 / 购物车 / 订单 / 用户 / 上传
       v
数据库 (MySQL / SQLite)  <-  1000 商品 + 100 买家 造数 (mock_seed.py)
       |
       v
Allure 报告 -> GitHub Pages -> 钉钉通知 (PC + 手机)

性能压测 (locustfile.py) -> Locust 报告 (QPS / 延迟 / 失败率)
```

## 核心业务链路（下单全流程）

```
登录拿 token -> 查商品拿 goods_id -> 加购物车 -> 创建订单(扣库存)
     -> 支付(状态流转) -> 取消订单(库存回滚)
```

6 个接口变量传递，覆盖 **数据一致性**（库存扣减/回滚、支付状态）、**越权**、**SQL 注入**、**幂等** 等测试维度。

## CI/CD 流水线

| 阶段 | 说明 |
|------|------|
| 检出代码 | Git SCM 拉取 main 分支 |
| 安装依赖 | venv + pip install -r requirements.txt |
| 启动 Mock 后端 | Flask 开发服务器(后台运行) |
| 执行测试 | pytest 34 条用例, 生成 Allure JSON |
| 生成报告 | Allure 命令行生成 HTML 报告 |
| 发布到 GitHub Pages | 推送报告到 gh-pages 分支(手机可看) |
| 钉钉通知 | Python 直调 Webhook, PC + 手机双链接 |

流水线配置文件: [Jenkinsfile](Jenkinsfile)

---

## 快速开始

### 环境要求
- Python 3.8+
- MySQL 5.7+(或使用 SQLite)
- Allure Commandline 2.x
- Locust 2.x(性能测试)

### 安装
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

### 配置(环境变量注入,不写代码里)

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| DB_BACKEND | mysql 或 sqlite | sqlite |
| MYSQL_HOST | MySQL 主机 | 127.0.0.1 |
| MYSQL_PORT | MySQL 端口 | 3306 |
| MYSQL_DATABASE | 数据库名 | mydb |
| MYSQL_USER | 用户名 | root |
| MYSQL_PASSWORD | 密码 | 空 |

### 初始化数据库 + 造数
```bash
# MySQL
mysql -u root -p < sql/init_mysql.sql
DB_BACKEND=mysql python mock_seed.py   # 造 1000 商品 + 100 买家

# SQLite(自动建表)
python mock_seed.py   # 建表 + 造数(幂等)
```

### 启动 Mock Backend
```bash
python mock_backend.py   # http://127.0.0.1:8888
```

### 运行测试
```bash
python run.py
# 或
pytest -vs ./testcases/test_runner.py --alluredir ./report/json_report --clean-alluredir
```

### 性能压测
```bash
# Web UI：http://localhost:8089 配置并发/时长
locust -f locustfile.py --host http://127.0.0.1:8888

# 无头：100 并发、每秒 10 爬坡、60 秒、输出 CSV
locust -f locustfile.py --host http://127.0.0.1:8888 \
    --headless -u 100 -r 10 -t 60s --csv=report/perf
```

---

## 项目结构

```
Jenkinsfile            # Jenkins Pipeline 定义
conftest.py            # pytest fixture(数据库清理)
mock_backend.py        # Flask Mock 电商后端
mock_database.py       # SQLite/MySQL 统一 DB 访问层 + 建表
mock_seed.py           # 批量造数(1000 商品 + 100 买家)
locustfile.py          # Locust 性能压测脚本
run.py                 # 一键运行入口
requirements.txt       # Python 依赖
config/config.py       # 配置(环境变量驱动) + 清理 SQL
data/data1.xlsx        # Excel 测试用例(34 条)
data/mock_test.db      # SQLite 数据库文件
sql/init_mysql.sql     # MySQL 建库建表脚本
testcases/test_runner.py  # pytest 测试入口
utils/                 # 工具模块
  analyse_case.py      # 用例解析
  allure_utils.py      # Allure 初始化
  asserts.py           # HTTP + JDBC 断言
  dingtalk_notify.py   # 钉钉通知
  excel_utils.py       # Excel 读取
  extractor.py         # JSON + JDBC 变量提取
  send_request.py      # HTTP + JDBC 请求
file/                  # 上传测试文件
report/                # 测试报告(json + html + 性能)
log/                   # 运行日志
```

---

## 业务模块与接口清单

统一前缀 `/api/private/v1`，双角色鉴权（管理员 admin-token / 买家 token）：

| 模块 | 接口 | 鉴权 | 说明 |
|------|------|------|------|
| 认证 | `POST /login` | 公开 | 管理员 + 买家双角色登录 |
| 商品 | `GET /goods` | 公开 | 分页 + 搜索(1000 商品) |
| | `GET /goods/:id` | 公开 | 商品详情 |
| | `POST/PUT/DELETE /goods` | 管理员 | 后台增删改 |
| 分类 | `GET /categories` | 公开 | 分类列表 |
| 购物车 | `POST/GET/PUT/DELETE /cart` | 买家 | 加购/查询/改数量/删除 |
| 订单 | `POST /orders` | 买家 | 创建订单(扣库存) |
| | `GET /orders` `GET /orders/:id` | 买家 | 订单列表/详情 |
| | `PUT /orders/:id/pay` | 买家 | 支付(幂等) |
| | `PUT /orders/:id/cancel` | 买家 | 取消(库存回滚) |
| 用户管理 | `GET/POST/PUT /users` | 管理员 | 买家用户管理 |
| 上传 | `POST /upload` | 任意 | 文件上传 |

## 数据模型(8 张表)

| 表 | 说明 |
|----|------|
| sp_manager | 管理员表 |
| sp_user | 买家用户表(100 买家) |
| sp_category | 商品分类表(10 分类) |
| sp_attribute | 商品属性表 |
| sp_goods | 商品表(1000 商品) |
| sp_cart | 购物车表 |
| sp_order | 订单表 |
| sp_order_item | 订单明细表 |

## 测试用例(34 条)

| 模块 | 条数 | 覆盖点 |
|------|------|--------|
| 认证 | 6 | 双角色登录、密码错误、用户不存在、SQL 注入拦截 |
| 商品 | 11 | 分页(1000 数据量)、搜索、详情、增删改、缺参/负价边界、鉴权 |
| 购物车 | 6 | 加购、重复加购累加、改数量、删除、未登录、越权 |
| 订单 | 10 | 创建/扣库存、支付/状态流转、幂等、取消/库存回滚、库存不足、越权 |
| 用户管理 | 1 | 管理员查询用户列表 |
| 错误用例(禁用) | 2 | 演示失败流程时手动开启 |

> 含 2 条**默认关闭**的错误用例(id 35/36)，用于演示钉钉失败通知：把 `data1.xlsx` 里对应行 `is_true` 改为 `TRUE` 即可触发。

## Excel 用例字段

| 字段 | 说明 |
|------|------|
| method / path | HTTP 方法与路径(支持 `{{变量}}`) |
| headers/params/data/json/files | 请求参数 |
| check | JSONPath 断言表达式 |
| expected | 预期结果 |
| sql_check / sql_expected | 数据库断言(数据一致性校验) |
| jsonExData / sqlExData | 变量提取(传递给下一条用例) |
| is_true | TRUE=启用 |

## 技术栈

| 类别 | 技术 |
|------|------|
| 测试框架 | pytest, Allure |
| 数据驱动 | Excel(openpyxl) + Jinja2 模板 |
| HTTP 客户端 | requests |
| 断言 | JSONPath + 自定义 SQL 断言 |
| 数据库 | MySQL / SQLite 双模式(PyMySQL) |
| Mock 后端 | Flask(电商业务) |
| 性能测试 | Locust |
| CI/CD | Jenkins Pipeline(Declarative) |
| 报告 | Allure + GitHub Pages |
| 通知 | 钉钉机器人 Webhook(HMAC-SHA256) |
| 安全 | Jenkins Credentials 管理所有密钥 |
