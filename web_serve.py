#写一个用flask框架, 处理路由到/api的请求, 请求包含[{"name":"link"...}...], 返回json格式为{"name":"desc"}
from collect_info import crawler_links,get_similary_course_desc
# from query_sql import get_similary_course_desc
from flask import Flask, request, jsonify
from icecream import ic

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def process_api_request():
    # 获取 POST 请求的 JSON 数据
    request_data = request.get_json()#需要一个列表字典
    course_link=[]
    # 检查请求中是否包含 "course_name" 字段
    for item in request_data:
        for k,v in item.items():
            course_link.append({"name":k,"link":v})
    ic()
    ic(course_link)
    crawled_data=crawler_links(course_link)
    # ic(crawled_data)
    for dic in crawled_data:
        if len(dic['desc'])<10:
            dic['desc']=get_similary_course_desc(dic['name'])[1]
    response_data = []
    for dic in crawled_data:
        response_data.append({dic['name']:dic['desc']})
    ic(response_data)
    return jsonify(response_data)

if __name__ == '__main__':
    # 启动 Flask 应用
    ic('hello, start flask app')
    app.run(debug=True)
    pass
