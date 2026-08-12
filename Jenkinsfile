pipeline {
    agent any

    environment {
        MYSQL_PASSWORD = credentials('mysql-password')   // Jenkins 凭证 ID
        DB_BACKEND     = 'mysql'
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
            dingtalk (
                robot: 'test-notify',
                type: 'MARKDOWN',
                title: '✅ 自动化测试通过',
                text: [
                    "### ✅ 自动化测试通过",
                    "",
                    "| 项目 | 详情 |",
                    "|------|------|",
                    "| 构建编号 | [${BUILD_DISPLAY_NAME}](${BUILD_URL}) |",
                    "| Git 提交 | ${GIT_COMMIT} |",
                    "| 分支 | ${GIT_BRANCH} |",
                    "",
                    "[📊 查看 Allure 报告](${BUILD_URL}allure)"
                ]
            )
        }
        failure {
            dingtalk (
                robot: 'test-notify',
                type: 'MARKDOWN',
                title: '❌ 自动化测试失败 — 请关注',
                text: [
                    "### ❌ 自动化测试失败",
                    "",
                    "| 项目 | 详情 |",
                    "|------|------|",
                    "| 构建编号 | [${BUILD_DISPLAY_NAME}](${BUILD_URL}) |",
                    "| Git 提交 | ${GIT_COMMIT} |",
                    "| 分支 | ${GIT_BRANCH} |",
                    "",
                    "[📋 查看构建日志](${BUILD_URL}console)",
                    "",
                    "[📊 查看 Allure 报告](${BUILD_URL}allure)"
                ]
            )
        }
    }
}
