pipeline {
    agent any

    environment {
        MYSQL_PASSWORD    = credentials('mysql-password')
        DB_BACKEND        = 'mysql'
        DINGTALK_WEBHOOK  = credentials('dingtalk-webhook')
        DINGTALK_SECRET   = credentials('dingtalk-secret')
    }

    stages {

        stage('检出代码') {
            steps {
                checkout scm
            }
        }

        stage('安装依赖') {
            steps {
                bat '''
                    python -m venv .venv
                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('启动 Mock 后端') {
            steps {
                bat '''
                    set BUILD_ID=dontKillMe
                    start /B .venv\\Scripts\\python.exe mock_backend.py
                    ping -n 4 127.0.0.1 > NUL
                '''
            }
        }

        stage('执行测试') {
            steps {
                bat '''
                    .venv\\Scripts\\python.exe -m pytest -vs ./testcases/test_runner.py ^
                        --alluredir ./report/json_report ^
                        --clean-alluredir
                '''
            }
        }

        stage('生成报告') {
            steps {
                bat '.venv\\Scripts\\python.exe -m allure generate ./report/json_report -o ./report/html_report --clean'
                allure includeProperties: false, results: [[path: 'report/json_report']]
            }
        }
    }

    post {
        always {
            // 无论成功失败都执行：归档产物 + 清理后端进程
            archiveArtifacts artifacts: 'report/html_report/**, log/test.log', fingerprint: true
            bat 'taskkill /F /IM python.exe /FI "WINDOWTITLE eq *mock_backend*" 2>NUL || exit 0'
        }
        success {
            // 使用 Python 直调钉钉 Webhook（绕过插件语法版本问题）
            script {
                def msg = """{
                    "msgtype": "markdown",
                    "markdown": {
                        "title": "✅ 自动化测试通过",
                        "text": "### ✅ 自动化测试通过\\n\\n- 构建：[${BUILD_DISPLAY_NAME}](${BUILD_URL})\\n- 提交：${GIT_COMMIT}\\n\\n[📊 查看 Allure 报告](${BUILD_URL}allure)"
                    }
                }"""
                bat """
                    .venv\\Scripts\\python.exe -c "
import requests, time, hmac, hashlib, base64
secret = '${DINGTALK_SECRET}'
timestamp = str(round(time.time() * 1000))
sign_str = timestamp + '\\n' + secret
sign = base64.b64encode(hmac.new(secret.encode(), sign_str.encode(), hashlib.sha256).digest()).decode()
url = '${DINGTALK_WEBHOOK}&timestamp=' + timestamp + '&sign=' + sign
requests.post(url, json=${msg})
print('钉钉通知已发送')
"
                """
            }
        }
        failure {
            script {
                def msg = """{
                    "msgtype": "markdown",
                    "markdown": {
                        "title": "❌ 自动化测试失败",
                        "text": "### ❌ 自动化测试失败\\n\\n- 构建：[${BUILD_DISPLAY_NAME}](${BUILD_URL})\\n- 提交：${GIT_COMMIT}\\n\\n[📋 查看日志](${BUILD_URL}console)\\n[📊 Allure 报告](${BUILD_URL}allure)"
                    }
                }"""
                bat """
                    .venv\\Scripts\\python.exe -c "
import requests, time, hmac, hashlib, base64
secret = '${DINGTALK_SECRET}'
timestamp = str(round(time.time() * 1000))
sign_str = timestamp + '\\n' + secret
sign = base64.b64encode(hmac.new(secret.encode(), sign_str.encode(), hashlib.sha256).digest()).decode()
url = '${DINGTALK_WEBHOOK}&timestamp=' + timestamp + '&sign=' + sign
requests.post(url, json=${msg})
print('钉钉通知已发送')
"
                """
            }
        }
    }
}
