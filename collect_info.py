import re
from icecream import ic
from tqdm import tqdm
import requests
import json
import pickle
from bs4 import BeautifulSoup
# from utils.web_sql_crawler import  search_info,crawler_web_paragraphs
# from utils.sentence_compare import sentence_compare
requests.packages.urllib3.disable_warnings()
from sentence_transformers import SentenceTransformer, util
#检测当前是不是linux
import platform
if platform.system()=='Linux':
    model_path=r'./all-MiniLM-L6-v2'
    sqldata_path=r'./sql_data/sql_data.pkl'
else:
    model_path=r'.\all-MiniLM-L6-v2'
    sqldata_path=r'.\sql_data\sql_data.pkl'
model = SentenceTransformer(model_path)

with open(sqldata_path,'rb') as f:
    sql_data=pickle.load(f)

def crawler_web_paragraphs(link)-> list[str]:
    '''
    功能: 爬取网页中的各级段落和有序无序列表中的文本, 并清洗返回
    '''
    if re.search(r"(http|https)://", link) is None:
        return []
    # print(f"\033[0;33m{link}\033[0m")

    link = re.sub(r"(\n|\t)+", "", link)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
    try:
        res = requests.get(link, headers=headers, verify=False)
    except Exception:
        return []
    if res.status_code != 200:
        return []

    try:
        soup = BeautifulSoup(res.content, 'html.parser')
    except Exception:
        print(f"\033[0;36m{link}\033[0m")
        return []

    paragraphs_soup = soup.select("p,ul,ol,dl,h1,h2,h3,h4,h5,h6,h7")
    # ul_soup = soup.select("ul")
    # ol_soup = soup.select("ol")
    # all_soup = paragraphs_soup + ul_soup + ol_soup

    paragraphs_text = list(map(lambda x: x.get_text(), paragraphs_soup))
    paragraphs_filter = list(filter(lambda x: len(str(x).split()) > 2, paragraphs_text))
    def clear_sentence(sentence):
        '''
        功能: 保证文本中间距一致
        '''
        sentence = re.sub(r"(?<!\s)(\xa0|\n|\t)(?!\s+)", " ", sentence)
        sentence = re.sub(r"(\xa0|\n|\t)(?<=\s)", "", sentence)
        sentence = re.sub(r"(\xa0|\n|\t)(?=\s)", "", sentence)
        return sentence

    paragraphs_clear = list(map(clear_sentence, paragraphs_filter))
    return paragraphs_clear

def sentence_compare(sent1,sent2):
    queries_embeddings=model.encode(sent1,convert_to_tensor=True,show_progress_bar=False)
    corpus_embeddings=model.encode(sent2,convert_to_tensor=True,show_progress_bar=False)
    hit=util.semantic_search(queries_embeddings, corpus_embeddings,query_chunk_size=1000,corpus_chunk_size=50000,top_k=1)
    return hit[0][0]['score']

def crawler_links(name_link_object)-> list[dict]:
    '''
    从link找到name相关的描述部分, 要求这部分扣去name仍高相关, 长度够长
    
    输入[{'name': name, 'link': link}...]
    输出[{'name': name, 'link': link, ...'paragraph': paragraph}...]
    '''
    name_paragraphs = []
    for name_link in name_link_object:
        name = re.sub(r"\*+$", "", name_link['name'].strip())
        paragraph = ""
        name_clear = re.sub(r"[^\w\s]+", "", name)
        link = name_link['link']
        result = crawler_web_paragraphs(link)
        result = list(map(lambda x: re.sub(r"(\s+|\t|\n)", " ", x).strip(), result))
        exist=set()
        for index in range(len(result)):
            res = result[index]
            res_clear = re.sub(r"[^\w\s]+", "", res)#将res中的非字母非空格非数字的字符替换为空
            # if sentence_compare(name_clear, res_clear)>0.5 and len(res_clear)>20:
            #     paragraph+="\n"+res_clear
            
            if len(res_clear.split()) <= len(name_clear.split()) * 2 and sentence_compare(name_clear, res_clear)>0.6:
                for sub_index in range(index + 1, len(result)):
                    if len((result[index] + result[sub_index]).split()) > 15:
                        sub_value = result[sub_index]
                        sub_value_clear = re.sub(r"[^\w\s]+", "", sub_value)
                        if sub_value_clear in exist:
                            continue
                        sim_score = sentence_compare(name_clear, re.sub(fr"{name_clear}", "", sub_value_clear))
                        if sim_score < 0.35:
                            continue
                        paragraph += " " + sub_value
                        exist.add(sub_value_clear)
                        break
                    
        # name_paragraphs.append({'name': name,'link':link,'web_data':result, 'paragraph': paragraph})
        name_paragraphs.append({'name': name,'desc': paragraph})
    return name_paragraphs


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

def get_mid_data1():
    path=r'D:\github\kw_extracct\大模型生成WS项目\原T5模型输入表格'
    jsonpaths=[]
    import os
    import pickle
    from tqdm import tqdm
    for root,dir,files in os.walk(path):
        for file in files:
            if file.endswith('.json'):
                jsonpaths.append(os.path.join(root,file))
    name_link_object=[]
    for k,jsonpath in tqdm(enumerate(jsonpaths)):
        jsondata=json.load(open(jsonpath,'r',encoding='utf-8'))
        for item in jsondata:
            if isinstance(item,dict) and "course_link" in item and len(item["course_link"])!=0:
                for pair in item["course_link"]:
                    if len(pair['link'])>10:
                        name_link_object.append({"name":pair['course'],"link":pair['link']})
                    if len(name_link_object)>=100:
                        break
            if len(name_link_object)>=100:
                break
        if len(name_link_object)>=100:
            break
    crawl_data=crawler_links(name_link_object)
    cachepath=r'D:\github\kw_extracct\大模型生成WS项目\mid_cache\crawl_data.pkl'
    with open(cachepath,'wb') as f:
        pickle.dump(crawl_data,f)
    # print(name_link_object)
    
# get_mid_data1()
# def get_mid_data2():
#     cachepath=r'D:\github\kw_extracct\大模型生成WS项目\mid_cache\crawl_data.pkl'
#     with open(cachepath,'rb') as f:
#         data=pickle.load(f)
#     for one in data:
#         web_data="\n".join(one['web_data'])
#         one['web_data']=web_data
#         one['summary']=summarizer.summarize_string(web_data)
#     with open(cachepath,'wb') as f:
#         pickle.dump(data,f)
    
# get_mid_data2()

# def get_sql_desc(course_name):
#     '''
#     功能: 从数据库中搜索专业课程的信息
#     '''
#     pass

