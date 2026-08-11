# jsonpath 问题排查说明

你现在遇到问题的核心是：jsonpath 在框架里被用来提取 JSON 内容，比如在 `check` 和 `jsonExData` 字段里使用表达式：

- `$..meg`
- `$..token`
- `$..id`

这意味着你的测试用例是依赖 JSONPath 语言去定位响应结构里的字段。

## 1. 你现在的代码中，jsonpath 的位置

在项目中，jsonpath 的关键使用点包括：

- [utils/asserts.py](../utils/asserts.py)：HTTP 响应断言
- [utils/extractor.py](../utils/extractor.py)：JSON 提取变量
- [testcases/test_runner.py](../testcases/test_runner.py)：主测试入口

它们的工作方式大致是：

1. 发送请求获得 `res.json()`
2. 执行 `jsonpath.jsonpath(res.json(), expression)`
3. 取出第一个结果并用于断言或提取变量

## 2. 为什么会出现“未知”

最常见原因有 4 个：

### 原因 A：安装包不匹配

你项目里依赖文件中出现过 `jsonpath` 这个包，但当前 Python 解释器中并未确认它是可导入的，直接检查时出现：

```text
ModuleNotFoundError: No module named 'jsonpath'
```

这说明你当前解释器或虚拟环境里没有正确安装 `jsonpath`。

### 原因 B：JSONPath 表达式写错了

`jsonpath` 的表达式依赖你返回的 JSON 根结构。

例如：

```json
{
  "meta": {
    "msg": "登陆成功"
  },
  "data": {
    "token": "abc"
  }
}
```

你要取 token，正确写法是：

```python
jsonpath.jsonpath(response.json(), '$.data.token')
```

或者：

```python
jsonpath.jsonpath(response.json(), '$..token')
```

如果接口返回结构不是你想象的层级，就会出现匹配不到结果。

### 原因 C：响应不是 JSON

你的断言代码里使用了：

```python
res.json()
```

所以接口返回的内容必须是真正的 JSON。

如果服务端返回了 HTML 页面、空字符串、文本、重定向页面，就会报错。

### 原因 D：包名与 API 不同

这点很重要：

- `jsonpath` 是一个用于路径表达式的第三方库
- 但你在项目里调用的是：

```python
import jsonpath
jsonpath.jsonpath(obj, '$..token')
```

如果你在环境里装的是另一个库，或者安装失败，就直接得到 `ModuleNotFoundError` 或“表达式解析失败”。

## 3. 你现在应该怎么验证

### 验证步骤 1：确认包能导入

```bash
python -c "import jsonpath; print(jsonpath.__file__)"
```

如果报错，就说明环境里面没装。

### 验证步骤 2：确认响应结构

你可以用一个非常简单的假接口测试：

```python
import jsonpath

payload = {
    "meta": {"msg": "登陆成功"},
    "data": {"token": "abc"}
}

print(jsonpath.jsonpath(payload, '$..token'))
```

正常应该输出：

```python
['abc']
```

### 验证步骤 3：确认你写的表达式对不对

例如：

```python
jsonpath.jsonpath(response.json(), '$.data.token')
```

如果返回 `False` 或空列表，就说明表达式打在了错误位置。

## 4. 你未来要怎么处理 jsonpath

建议你未来的工程实践：

- 用 `$.data.token` 这种显式路径表达式
- 避免用过度泛化的 `$..`，除非你明确知道响应结构里有多个递归匹配的情况
- 在测试报告中打印响应 JSON，确认 `res.json()` 的具体结构
- 若接口返回 JSON 为空或者字段位于 `data` 的另一层，请同步修改 Excel 用例中的 `check` 和 `jsonExData`

## 5. 当前最需要做的两件事

### 任务 A：安装正确依赖

把 `jsonpath` 包安装到你当前解释器中：

```bash
pip install jsonpath==0.82.2
```

### 任务 B：给接口一个稳定返回结构

你未来的最小后端接口应该按照你这个框架的用例字段来返回：

```json
{
  "meta": {
    "msg": "登陆成功"
  },
  "data": {
    "token": "abc"
  }
}
```

这样 `jsonpath` 可以直接拿到 `token`，也能进入下一个 API 测试的数据提取流程。
