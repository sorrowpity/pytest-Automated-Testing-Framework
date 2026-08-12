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
            archiveArtifacts artifacts: 'report/html_report/**, log/test.log', fingerprint: true
            bat 'taskkill /F /IM python.exe /FI "WINDOWTITLE eq *mock_backend*" 2>NUL || exit 0'
        }
        success {
            bat '.venv\\Scripts\\python.exe utils\\dingtalk_notify.py success %BUILD_URL% %BUILD_DISPLAY_NAME% %GIT_COMMIT%'
        }
        failure {
            bat '.venv\\Scripts\\python.exe utils\\dingtalk_notify.py failure %BUILD_URL% %BUILD_DISPLAY_NAME% %GIT_COMMIT%'
        }
    }
}
