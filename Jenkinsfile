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
                bat 'start /B .venv\\Scripts\\python.exe mock_backend.py'
                bat 'timeout /t 3 /nobreak'
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
            // 后续在这里接入钉钉通知
            echo '测试全部通过，后续在此接入钉钉通知'
        }
        failure {
            // 失败时的钉钉通知
            echo '测试有失败，后续在此接入钉钉告警'
        }
    }
}
