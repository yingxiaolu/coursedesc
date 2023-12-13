#用request向某端口发送json包

import requests
import json
from icecream import ic
# 目标端口的URL
# url = r'http://127.0.0.1:8763/api'  # 请替换为实际的目标端口和路由
url = r'http://36.150.110.203:8763/api'  # 请替换为实际的目标端口和路由
# 要发送的 JSON 数据
data = [{"course":"Advanced Perception for Intelligent Robotics","course_link":"http://www.ee.cuhk.edu.hk/en-gb/curriculum/mphil-phd-programme/course-list/eleg5600-advanced-perception-for-intelligent-robotics"},
        {"course":"Launching the Firm","course_link":"https://www.uu.se/en/admissions/master/selma/kursplan/?kpid=42360&type=1"}]

# 使用 requests 发送 POST 请求
response = requests.post(url, json=data)
ic(response)
# 检查请求是否成功
if response.status_code == 200:
    # 解析响应的 JSON 数据
    result = response.json()
    print(result)
else:
    print(f"Request failed with status code: {response.status_code}")
