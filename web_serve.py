#写一个用flask框架, 处理路由到/api的请求, 请求包含[{"name":"link"...}...], 返回json格式为{"name":"desc"}
from collect_info import crawler_links,get_similary_course_desc
# from query_sql import get_similary_course_desc
from flask import Flask, request, jsonify
from icecream import ic
from flask_cors import CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/api', methods=['POST'])
def process_api_request():
    # 获取 POST 请求的 JSON 数据
    request_data = request.get_json()#需要一个列表字典
    #[{ course: "", course_link: "" }]
    course_link=[]#
    # 检查请求中是否包含 "course_name" 字段
    for item in request_data:
        course_link.append({'name':item['course'],'link':item['course_link']})
    ic()
    ic(course_link)
    crawled_data=crawler_links(course_link)#[{'name': name,'desc': desc}...]
    response_data = []
    for data in crawled_data:
        response_data.append({"course":data['name'],"desc":data['desc'],"code":200})
    for dic in response_data:
        if len(dic['desc'])<10:
                dic["desc"]=get_similary_course_desc(dic['course'])[1]
                dic['code']=404
    ic(response_data)
    return jsonify(response_data)

if __name__ == '__main__':
    # 启动 Flask 应用
    ic('hello, start flask app')
    app.run(debug=True,port=8763)
    pass
