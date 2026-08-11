# Flask 最小后端接口说明

这个项目目前的测试框架要求一个真实接口层来对接 Excel 中的接口用例。为了不改坏原测试框架，我已经补上一个最小可运行的 Flask 服务：

- [mock_backend.py](../mock_backend.py)

## 这个 Flask 服务解决什么问题

它会提供你 Excel 用例中需要的接口：

- 登录接口
- 用户列表接口
- 新增用户接口
- 修改用户状态接口
- 文件上传接口

这样你的 pytest 框架就可以通过 HTTP 请求调用真实接口，不必只停留在“某些函数假设”的道理层面。

## 运行方式

打开一个终端，进入项目根目录，然后执行：

```bash
python mock_backend.py
```

默认服务监听：

```text
http://127.0.0.1:8888
```

## 接口说明

### POST /api/private/v1/login

请求：

```json
{
  "username": "admin",
  "password": "123456"
}
```

返回：

```json
{
  "meg": "登陆成功",
  "data": {
    "token": "mock-token-123"
  }
}
```

### GET /api/private/v1/users

需要请求头：

```json
{
  "Authorization": "mock-token-123"
}
```

### POST /api/private/v1/users

新增用户接口，依赖 Authorization 头。

### PUT /api/private/v1/users/<id>/state/<state>

修改状态，支持：true / false。

### POST /api/private/v1/upload

上传文件接口，使用 multipart/form-data。
