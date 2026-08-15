pipeline {
    agent any

    environment {
        MYSQL_PASSWORD    = credentials('mysql-password')
        DB_BACKEND        = 'mysql'
        DINGTALK_WEBHOOK  = credentials('dingtalk-webhook')
        DINGTALK_SECRET   = credentials('dingtalk-secret')
        GITHUB_TOKEN      = credentials('github-token')
        GITHUB_PAGES_URL  = 'https://sorrowpity.github.io/pytest-Automated-Testing-Framework/'
        PYTHONIOENCODING  = 'utf-8'
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
                // 整库重置造数（清空 + 重造，保证干净状态），DB_BACKEND 已设为 mysql
                bat '.venv\\Scripts\\python.exe mock_seed.py --reset'
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
                    rem gh-pages 是纯生成物分支（每次整目录覆盖），用 --force 避免 non-fast-forward
                    git push --force origin gh-pages
                    set PUSH_RESULT=%errorlevel%
                    cd ..
                    rmdir /S /Q gh-pages-tmp
                    rem 把 push 的真实退出码返回给 Jenkins：否则 rmdir 成功后会把 push 失败掩盖成绿色
                    exit /b %PUSH_RESULT%
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
