import requests
import os

login_data={
    "method" : "post",
    "url" : "https://127.0.0.1:8888/api/private/v1/login",
    "files": {"username":"admin","password": "123456"}
}

cur_path = os.path.dirname(__file__) # 获取当前文件所在目录路径
file_path = os.path.join(cur_path, "./file/1.jpg") # 拼接文件路径

upload_data={
    "method" : "post",
    "url" : "https://127.0.0.1:8888/api/private/v1/upload",
    "headers": None,
    "files": {"file": ("1.jpg", open(file_path,"rb"),"jpg")}
}

res1 = requests.request(**login_data)
token = res1.json()["data"]["token"]
print(token)

# 文件上传
upload_data["headers"] = {"Authorization":token}

res2 = requests.request(**upload_data)
print(res2.json())