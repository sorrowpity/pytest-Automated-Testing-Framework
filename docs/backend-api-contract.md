# 反推出来的测试后端接口设计

这个项目的自动化测试框架本质上是“Excel 用例驱动”的接口自动化测试。它读取 Excel 中一行行用例，随后依赖以下字段构造 HTTP 请求：

- method：请求方法
- path：接口路径
- headers：请求头
- params：URL 查询参数
- data：form 表单参数
- json：JSON 请求体
- files：上传文件封装
- check：JSONPath 断言路径
- expected：预期值
- jsonExData：响应 JSON 提取数据进入全局变量
- sqlExData：数据库 SQL 提取数据进入全局变量
- sql_check / sql_expected：数据库结果断言

因此，测试接口应该至少满足下面这些能力：

## 1. 登录接口

接口：POST /api/private/v1/login

作用：验证管理员账号密码，返回令牌。

请求格式：

```json
{
  "username": "admin",
  "password": "123456"
}
```

响应格式：

```json
{
  "meta": {
    "msg": "登陆成功"
  },
  "data": {
    "token": "mock-token-123"
  }
}
```

框架接收点：

- `jsonExData` 中提取 `TOKEN`：`$..token`
- 后续接口依赖 `Authorization` 头发送 token

## 2. 用户列表接口

接口：GET /api/private/v1/users

作用：在登录后查询管理员用户列表。

请求头：

```json
{
  "Authorization": "<TOKEN>"
}
```

响应格式：

```json
{
  "meta": {
    "msg": "获取管理员列表成功"
  },
  "data": {
    "users": [
      {
        "id": 1,
        "username": "admin"
      }
    ]
  }
}
```

未登录时返回：

```json
{
  "meta": {
    "msg": "无效token"
  }
}
```

## 3. 用户新增接口

接口：POST /api/private/v1/users

作用：新增用户。

请求格式：

```json
{
  "username": "jay",
  "password": "123456"
}
```

响应格式：

```json
{
  "meta": {
    "msg": "创建成功"
  },
  "data": {
    "id": 100
  }
}
```

框架接收点：

- `jsonExData` 提取用户 ID：`$..id`
- 提取后的变量名进入 `all` 全局变量，用于下一条用例渲染路径

## 4. 用户状态接口

接口：PUT /api/private/v1/users/{{JAY_ID}}/state/true

作用：修改用户状态。

响应格式：

```json
{
  "meta": {
    "msg": "设置状态成功"
  }
}
```

## 5. 文件上传接口

接口：POST /api/private/v1/upload

作用：上传图片或文件。

请求头：

```json
{
  "Authorization": "<TOKEN>"
}
```

请求体：multipart/form-data，包含 `file` 字段。

响应格式：

```json
{
  "meta": {
    "msg": "上传成功"
  },
  "data": {
    "url": "/upload/1.jpg"
  }
}
```

---

## 6. 你现在的框架对接口的要求总结

你的自动化框架本质上要求接口要具备：

1. 可被 HTTP 请求调用
2. 可以返回 JSON
3. 响应结构满足 JSONPath 表达式
4. 支持返回 `meta.msg` 或 `data` 结构
5. 支持令牌鉴权（Authorization 头）
6. 支持基础文件上传

---

## 7. 建议的后端落地方式

你现在可以用最小 Flask 后端把接口实现出来，优先级如下：

1. 登录接口
2. 用户列表接口
3. 用户新增接口
4. 用户状态更新接口
5. 文件上传接口

这样你后续就能拿真实接口结构去跑 pytest 测试用例而不需要继续伪造环境。
