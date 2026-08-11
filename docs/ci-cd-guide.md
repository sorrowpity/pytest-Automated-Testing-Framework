# Jenkins CI/CD 落地思路

你未来要使用 Jenkins 做 CI/CD，所以这里先整理一个可执行的落地路径。

## 1. CI/CD 的总体目标

你的自动化测试框架运行的核心目标是：

- 每次代码提交或分支合并时，自动拉起测试
- 自动执行 pytest 测试用例
- 生成 Allure/HTML 报告
- 把失败信息、日志、报告归档到构建产物中
- 让测试结果成为 PR/分支是否可以合并的质量门禁

## 2. 推荐流水线步骤

### Step 1：拉取代码

在 Jenkins 中配置 Git 仓库并拉取源码。

### Step 2：创建虚拟环境

执行：

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 3：安装项目依赖

使用：

```bash
pip install -r requirements.txt
```

### Step 4：执行 pytest

```bash
pytest -vs ./testcases/test_runner.py --alluredir ./report/json_report --clean-alluredir
```

### Step 5：生成 Allure 报告

```bash
allure generate ./report/json_report -o ./report/html_report --clean
```

### Step 6：归档产物

Jenkins 里建议归档如下内容：

- `report/html_report/`
- `report/json_report/`
- `log/test.log`
- pytest 失败输出（console）

## 3. Jenkins 组件建议

建议至少加入以下组件：

- Git 插件
- Pipeline 插件
- Allure 插件
- HTML Publisher 插件

## 4. 一条最小的 Jenkins 流水线示例

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/your-org/pytest-Automated-Testing-Framework.git'
            }
        }

        stage('Install') {
            steps {
                sh 'python -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest -vs ./testcases/test_runner.py --alluredir ./report/json_report --clean-alluredir'
                sh 'allure generate ./report/json_report -o ./report/html_report --clean'
            }
        }

        stage('Publish') {
            steps {
                archiveArtifacts artifacts: 'report/html_report/**, log/test.log', fingerprint: true
                allure includeProperties: false, jdk: '', results: [[path: 'report/json_report']]
            }
        }
    }
}
```

## 5. CI/CD 里的注意点

- 测试环境尽量独立，不要依赖本地手工环境
- 数据库账号、接口地址、环境变量要从 Jenkins 配置里传入
- 用例执行时不要直接依赖人为登录状态
- 接口测试需要有稳定环境，否则 CI 会经常失败

## 6. 下一步建议

后续你应该做下一轮落地：

1. 把这套接口用 Flask/FastAPI 先跑起来
2. 给 Jenkins 准备一个执行镜像或 Python 环境
3. 让 pytest 在 Jenkins 中自动执行并产出 Allure 报告
4. 把报告页面视图嵌入 Jenkins
