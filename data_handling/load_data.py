# import pandas as pd
# import ast

# # 读取CSV文件
# df = pd.read_csv('D:/学习资料/毕设/Scholar-Portrait/dataset/arxiv_processed.csv',usecols=("abstract", "title", "categories", "update_date"))


# # Load CSV file
# #df = pd.read_csv('your_file.csv')

# # Convert update_date column to datetime
# df['update_date'] = pd.to_datetime(df['update_date'], format='%Y-%m-%d')

# # Filter for articles updated after 2015
# df = df[df['update_date'] >= '2023-01-01']
# df = df[["title", "abstract", "categories"]]
# # Save filtered dataframe to new CSV file
# df.to_csv('processed_arxiv.csv',index=False)



# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

# from os.path import join
# import requests
# from tqdm import tqdm

# from config import data_dir





# to_download = ['ids_test.pkl',
#  'arxiv_processed.csv',
#  'ids.pkl',
#  'index.faiss',
#  'index_test.faiss',
#  'arxiv_processed_test.csv']

# # Download files
# base_url = "https://miguelpeixoto.net/paper_recommendation_system/"

# for file in to_download:
#     url = join(base_url, file)
#     print(f"[+] Downloading {url}")
#     r = requests.get(url, allow_redirects=True, stream=True)
#     with open(join(data_dir, file), "wb") as f:
#         for chunk in tqdm(r.iter_content(chunk_size=1024)):
#             if chunk:
#                 f.write(chunk)

