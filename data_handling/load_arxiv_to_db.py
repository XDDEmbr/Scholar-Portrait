from utils.connect_db import init_connection
import json
import os

conn = init_connection()
global c
c = conn.cursor()

def insert_paper(data):
    # 连接数据库


    # 插入 paper_info 表单
    paper_info = (data['id'], data['submitter'], data['authors'],data['title'], data['comments'], 
                  data['journal-ref'], data['doi'],data['report-no'], data['license'], data['categories'],data['abstract'],data['update_date'])
    c.execute("INSERT INTO ArXiv VALUES (?, ?, ?, ?, ?,?,?,?, ?, ?, ?,?)", paper_info)

    # 插入 paper_versions 表单
    for version in data['versions']:
        paper_version = (data['id'], version['version'], version['created'])
        c.execute("INSERT INTO Versions VALUES (?, ?, ?)", paper_version)

    # 插入 authors 表单
    for author in data['authors_parsed']:
        first_name = author[0]
        last_name = author[1]
        affiliation = author[2]
        author_info = (data['id'], first_name, last_name, affiliation)
    c.execute("INSERT INTO Authors VALUES (?, ?, ?, ?)", author_info)
    # 提交并关闭数据库连接
    conn.commit()


def insert_papers_from_file(file_path):
    # 连接数据库

    # 初始化 JSON 解码器
    decoder = json.JSONDecoder()

    # 打开文件流，循环读取并解码 JSON 对象
    with open(file_path, 'r') as f:
        buffer = ''
        for line in f:
            buffer += line.strip()
            try:
                # 尝试解码 JSON 对象
                obj, pos = decoder.raw_decode(buffer)
                buffer = buffer[pos:].strip()
                # 插入到数据库                
                paper_id = obj['id']
                c.execute("SELECT * FROM ArXiv WHERE id=?", (paper_id,))
                result = c.fetchone()
                if result:
                    # 如果已存在则不做插入，直接进入下一次循环
                    continue
                # 如果不存在则插入数据到数据库
                insert_paper(obj)
            except json.JSONDecodeError:
                # 如果解码失败则继续读取
                pass

if __name__ == '__main__':
    arxiv=os.path.abspath(os.path.join(os.path.dirname(__file__), 'dataset/', 'arxiv-metadata-oai-snapshot.json'))
    insert_papers_from_file(arxiv)
  

