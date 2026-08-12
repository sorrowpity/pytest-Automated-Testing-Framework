"""钉钉机器人通知工具 — python utils/dingtalk_notify.py <status> <build_url> <build_name> <git_commit>"""
import sys
import json
import time
import hmac
import hashlib
import base64
import os
import requests


def send_dingtalk(status, build_url, build_name, git_commit):
    webhook = os.environ["DINGTALK_WEBHOOK"]
    secret = os.environ["DINGTALK_SECRET"]

    timestamp = str(round(time.time() * 1000))
    sign_str = f"{timestamp}\n{secret}"
    sign = base64.b64encode(
        hmac.new(secret.encode(), sign_str.encode(), hashlib.sha256).digest()
    ).decode()

    url = f"{webhook}&timestamp={timestamp}&sign={sign}"

    if status == "success":
        title = "✅ 自动化测试通过"
        text = (
            f"### ✅ 自动化测试通过\n\n"
            f"- 构建：[{build_name}]({build_url})\n"
            f"- 提交：{git_commit}\n\n"
            f"[📊 查看 Allure 报告]({build_url}allure)"
        )
    else:
        title = "❌ 自动化测试失败"
        text = (
            f"### ❌ 自动化测试失败\n\n"
            f"- 构建：[{build_name}]({build_url})\n"
            f"- 提交：{git_commit}\n\n"
            f"[📋 查看日志]({build_url}console)\n"
            f"[📊 Allure 报告]({build_url}allure)"
        )

    payload = {
        "msgtype": "markdown",
        "markdown": {"title": title, "text": text},
    }

    resp = requests.post(url, json=payload)
    print(f"钉钉通知已发送: {resp.json()}")
    return resp


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("用法: python dingtalk_notify.py <success|failure> <BUILD_URL> <BUILD_DISPLAY_NAME> <GIT_COMMIT>")
        sys.exit(1)
    send_dingtalk(*sys.argv[1:5])
