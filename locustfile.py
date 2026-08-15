# -*- coding: utf-8 -*-
"""Locust 性能测试脚本（针对电商 Mock 后端）。

用法（先启动 mock_backend.py）:
    # Web UI 方式：打开 http://localhost:8089 配置并发/时长
    locust -f locustfile.py --host http://127.0.0.1:8888

    # 无头方式：100 并发、每秒 10 用户爬坡、跑 60 秒、输出 CSV 报告
    locust -f locustfile.py --host http://127.0.0.1:8888 \
        --headless -u 100 -r 10 -t 60s --csv=report/perf

关注指标：QPS、响应时间(avg/p95)、失败率。
"""
from locust import HttpUser, task, between


class EcommerceUser(HttpUser):
    """模拟电商用户，主要压读接口 + 登录。下单会改库存，这里不做（避免污染数据）。"""

    wait_time = between(1, 3)  # 每个虚拟用户请求间隔 1~3 秒

    @task(3)  # 权重 3：商品列表分页查询（最典型读接口）
    def query_goods(self):
        self.client.get(
            "/api/private/v1/goods",
            params={"pagenum": 1, "pagesize": 10},
            name="商品列表分页查询",
        )

    @task(2)  # 权重 2：登录（并发登录场景）
    def login(self):
        self.client.post(
            "/api/private/v1/login",
            json={"username": "user001", "password": "123456"},
            name="用户登录",
        )

    @task(1)  # 权重 1：商品详情
    def goods_detail(self):
        self.client.get("/api/private/v1/goods/2", name="商品详情查询")
