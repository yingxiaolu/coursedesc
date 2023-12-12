import pymysql
import pickle
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer(r'.\all-MiniLM-L6-v2')
    
def course_desc_inmysql():
    db= pymysql.connect(
                host='rm-wz9fveh412f250974oo.mysql.rds.aliyuncs.com',
                port=3306,
                user='lixuan',
                password='ieshei8E1Eishoom8')
    cursor=db.cursor()
    #获取whyschool数据库中的course表中字段name和description中的所有内容
    sql="select name,description from why_school.course"
    cursor.execute(sql)
    results=cursor.fetchall()

    sql="select name,description from why_school.course_major_outcome"
    cursor.execute(sql)
    results+=cursor.fetchall()

    with open(r'D:\github\kw_extracct\大模型生成WS项目\mid_cache\sql_data.pkl','wb') as f:
        pickle.dump(results,f)
        
def embeding_course():
    with open(r'D:\github\kw_extracct\大模型生成WS项目\mid_cache\sql_data.pkl','rb') as f:
        data=pickle.load(f)
    output=[]#course_name, decrption, name_embeding
    for k,item in tqdm(enumerate(data)):
        name=item[0]
        desc=item[1]
        embed=model.encode(name,convert_to_tensor=True,show_progress_bar=False)
        output.append([name,desc,embed])
    with open(r'D:\github\kw_extracct\大模型生成WS项目\mid_cache\sql_data.pkl','wb') as f:
        pickle.dump(output,f)

# embeding_course()

with open(r'sql_data\sql_data.pkl','rb') as f:
    sql_data=pickle.load(f)
corpus_embed=[item[2] for item in sql_data]
def get_similary_course_desc(course_name)->(str,str):
    '''
    返回最相似课程描述, sql_data中每个元素为[course_name,desc,embeding]
    ->[course_name,desc]
    '''
    global sql_data,corpus_embed
    query_embed=model.encode(course_name,convert_to_tensor=True,show_progress_bar=False)
    hits=util.semantic_search(query_embed,corpus_embed,query_chunk_size=1000,corpus_chunk_size=50000,top_k=1)
    return sql_data[hits[0][0]['corpus_id']][0:2]