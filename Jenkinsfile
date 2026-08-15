pipeline {
    agent any

    environment {
        MYSQL_PASSWORD    = credentials('mysql-password')
        DB_BACKEND        = 'mysql'
        DINGTALK_WEBHOOK  = credentials('dingtalk-webhook')
        DINGTALK_SECRET   = credentials('dingtalk-secret')
        GITHUB_TOKEN      = credentials('github-token')
        GITHUB_PAGES_URL  = 'https://sorrowpity.github.io/pytest-Automated-Testing-Framework/'
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

        stage('初始化数据') {
            steps {
                // 幂等造数（1000 商品 + 100 买家），DB_BACKEND 已设为 mysql
                bat '.venv\\Scripts\\python.exe mock_seed.py'
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
                // 直接用系统 Allure 命令行（跟插件是同一个，不经过 Python 包装器）
                bat 'D:\\allure\\allure-2.44.0\\bin\\allure.bat generate ./report/json_report -o ./report/html_report --clean'
                allure includeProperties: false, results: [[path: 'report/json_report']]
            }
        }

        stage('发布报告到 GitHub Pages') {
            steps {
                bat '''
                    git clone --depth 1 -b gh-pages https://%GITHUB_TOKEN%@github.com/sorrowpity/pytest-Automated-Testing-Framework.git gh-pages-tmp
                    cd gh-pages-tmp
                    git rm -rf .
                    xcopy /E /Y ..\\report\\html_report\\* .
                    echo . > .nojekyll
                    dir index.html
                    dir data\\suites.json
                    git config user.name "Jenkins CI"
                    git config user.email "jenkins@bot.local"
                    git add --all
                    git commit -m "Allure report [%BUILD_DISPLAY_NAME%]"
                    git push origin gh-pages
                    cd ..
                    rmdir /S /Q gh-pages-tmp
                '''
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
