import os
import sys
import time
import faiss
import pandas as pd
import streamlit as st
from os.path import join
from utils.auth import login_warning
from utils.load_dir import data_dir,testing,model_dir
from sentence_transformers import SentenceTransformer
from utils.get_url_tags import  get_url,load_user_tags,get_user_tags_from_query

# Explicitly set the environment variable TOKENIZERS_PARALLELISM to false
os.environ["TOKENIZERS_PARALLELISM"] = "false"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


if not hasattr(st.session_state, "selected_categories"):
    st.session_state.selected_categories = []

@ st.cache_resource
def load_data():
    print("Loading data!")
    if testing:
        data = pd.read_csv(join(data_dir, "arxiv_processed_test.csv"), dtype=str)
    else:
        data = pd.read_csv(join(data_dir, "arxiv_processed.csv"), dtype=str)
    return data

@ st.cache_resource
def load_model():
    print("Loading model!")
    model = SentenceTransformer("all-mpnet-base-v2", device="cuda")
    return model

@ st.cache_resource
def load_index():
    print("Loading index!")

    if testing:
        index = faiss.read_index(join(model_dir, "index_test.faiss"))
    else:
        index = faiss.read_index(join(data_dir, "index.faiss"))
    return index

model = load_model()
data = load_data()
index = load_index()
user_tags = load_user_tags()

def draw_sidebar():
    """Should include dynamically generated filters"""

    with st.sidebar:
        # Filter by category of our data
        categories = data["categories"].unique()

        # Sidebar
        st.sidebar.header("Filters")
        st.sidebar.subheader("By Category")

        # multiselect
        selected_categories = st.sidebar.multiselect("Select categories", categories)

        # Add a button to apply the filters
        if st.sidebar.button("Apply filters"):
            st.session_state.selected_categories = selected_categories

            # Reload the page
            st.experimental_rerun()
        global k    
        k = st.number_input("Number of results", 1, 50, 10)

html_temp = """
                    <div style="background-color:{};padding:1px">
                    
                    </div>
                    """

def search_main():
    st.markdown("""
    ## 🔍Scholar Search
    在ScholarPartrait中搜索你感兴趣的~
    """)
    draw_sidebar()
    colselect, colsearch = st.columns([1,3])
    with colselect:
        selected_col = st.selectbox('',['学者','论文'])
    with colsearch:
        query = st.text_input("Search in ScholarPartrait", placeholder="搜索学者、论文", disabled=False)
            


    def show_search_result():
        # 使用预训练的all-mpnet-base-v2模型对查询进行编码，得到查询的向量表示。
        # 然后使用这个向量表示和之前构建的索引，搜索最相关的文献。
        # 最后，将搜索结果整理成一个DataFrame，方便进行展示和筛选。
        start_time = time.time()
        D, I = index.search(model.encode(query).reshape(1, -1), k) #对输入的query进行编码并通过annoy索引进行k近邻搜索，返回的结果是距离（D）和对应的索引（I）
        end_time = time.time()

        df = pd.DataFrame()
        for idx, score in zip(I[0], D[0]): #遍历返回的索引和距离
            to_add = data.iloc[idx]  #通过索引获取原始数据中对应的行

            # Add score
            to_add["score"] = score

            df = pd.concat([df, to_add], axis=1)

        df = df.T

        i = 0
        for _, row in df.iterrows():

            title = row["title"].replace("\n", " ").replace("\t", " ").replace("[", " ").replace("]", " ").replace("'", " ") #处理标题中的特殊字符
            url = get_url(row["id"])
            authors = eval(row["authors_parsed"])
            authors = [x[1] + " " + x[0] for x in authors] # 将作者信息转换为姓和名的形式

            # If category not in st.session_state.selected_categories
            categories = row["categories"].split()
            if len(st.session_state.selected_categories) > 0:
                c = True
                for cat in categories:
                    if cat in st.session_state.selected_categories:
                        c = False
                if c:
                    continue

            if len(authors) > 3:
                authors = ", ".join(authors[:3]) + " et al."
            else:
                authors = ", ".join(authors)

            # Add Score and Title with link
            # Author, date, categories
            # categories should be blue

            html = f"""
                ### [**{round(row['score']*100)}**] - :red[[{title}]({url})]  
                <font size="5"> *{authors}*  <br>
                {row['update_date']} - :blue[{row['categories'].replace(' ', ', ')}]"""


            #### User Tags ####

            user_tag_list = get_user_tags_from_query(row["title"] + " " + row["abstract"], user_tags, model)
            if any([prob > 0.5 for tag, prob in user_tag_list]):
                html += f"""<br> <font size="4"> User Tags: """
                for tag, prob in user_tag_list:
                    if prob > 0.5:
                        html += f":red[[{tag}] ({round(prob*100)}%)], "
                # Remove last ,
                html = html[:-2]

            # Show html
            st.markdown(html, unsafe_allow_html=True)
   
            #### Abstract ####

            # Add abstract with normal text
            st.markdown(
                f"""
            <font size="4.5">
                {row['abstract']}
            """,
                unsafe_allow_html=True,
            )

            st.markdown("---")

        # Show sucessful query message and tell how many documents we passed
        st.success(f"Found {len(I[0])} results in {end_time - start_time:.2f} seconds on database of {len(data)} papers.")

    if query:
        with st.container():                
            if selected_col == "学者":
                tab1 = st.tabs(["👩‍🎓学者"])
            if selected_col == "论文":
                tab1,tab2 = st.tabs(["📃论文","👩‍🎓学者"])
                with tab1:
                    show_search_result()
                #tab1, tab2, tab3 = st.tabs(["📃摘要","👩‍🎓学者", "🪧标题"])

if __name__ == '__main__':
    if st.session_state.authentication_status:
        search_main()
    elif st.session_state.authentication_status == None:
        login_warning() 