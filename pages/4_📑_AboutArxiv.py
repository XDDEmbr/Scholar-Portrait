import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
from utils.auth import login_warning
from plotly.subplots import make_subplots


arxiv_dataset = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','dataset/', 'arxiv-metadata-oai-snapshot.json'))
nrows=10000

@st.cache_data
def load_dataset(dataset,nrows):
    df = pd.read_json(dataset,lines=True,nrows=nrows)
    df["versions"] = df["versions"].apply(json.dumps)
    df["authors_parsed"] = df["authors_parsed"].apply(json.dumps)
    df.update_date = pd.to_datetime(df.update_date, infer_datetime_format=True)
    return df

@st.cache_data
def load_data(filename):  
    date = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','dataset/', filename))
    df = pd.read_csv(date)
    return df

def about_main():
    st.header('📑AboutArxiv')
    with st.expander("Dataset Show",expanded=False):
        df = pd.DataFrame(load_dataset(arxiv_dataset,nrows))
        st.dataframe(df.head(1000)) 
        col_intro,col_json = st.columns(2)
        with col_intro:
            st.markdown('[ArXiv](https://arxiv.org/) 是一个由:blue[Cornell University]维护的在线预印本数据库，提供了学术论文的免费公开访问。该数据库主要覆盖物理学、数学、计算机科学、统计学、电气工程等领域。它包含了大量的学术论文和研究成果，为学术研究提供了丰富的数据来源。')
            st.text('[id]:  arXiv ID，可用于访问论文 \n\n[submitter]:  论文提交者\n\n[authors]: 论文作者\n\n[title]:  论文标题\n\n[comments]: 论文页数和图表等其他信息\n\n[journal-ref]: 论文发表的期刊\n\n[doi]:  数字对象标识符\n\n[abstract]:  论文摘要\n\n[categories]:  论文在 arXiv 系统的所属类别或标签\n\n[versions]:  论文版本\n\nhttps://arxiv.org/abs/{id}:  本文的页面，包括其摘要和进一步链接\n\nhttps://arxiv.org/pdf/{id}:  下载PDF的直接链接')

        with col_json:
            st.json({
            "versions": json.loads(df.loc[1, "versions"]),
            "authors_parsed": json.loads(df.loc[1, "authors_parsed"])
            })

    with st.expander("Visual Analytics",expanded=False):
        df1 = load_data('mouth_count.csv')
        fig = px.line(df1, x="date", y="count", title="Number of papers submitted per month")
        st.plotly_chart(fig)

        df2 = load_data('category_count.csv')
        st.bar_chart(df2,x='num_categories',y='category_count')

        df3 = load_data('weekday_count.csv')
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',  '#8c564b','#e377c2']
        fig = px.bar(df3, x='weekday', y='num_articles', color='weekday',
                    color_discrete_sequence=colors, labels={'weekday': 'Weekday', 'num_articles': 'Number of Articles'})
        st.plotly_chart(fig)

        df4 = load_data('len_title_abstract.csv')
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces for title length and abstract length
        fig.add_trace(
            go.Scatter(x=df4['date'], y=df4['avg_title_len'], name='Title Length', line=dict(color='red')),
            secondary_y=False,)

        fig.add_trace(
            go.Scatter(x=df4['date'], y=df4['avg_abstract_len'], name='Abstract Length', line=dict(color='blue')),
            secondary_y=True, )

        # Set axes labels and titles
        fig.update_layout(
            xaxis=dict(title='Date'),
            yaxis=dict(title='Average Title Length', color='red'),
            yaxis2=dict(title='Average Abstract Length', color='blue'),
            title='Average Title and Abstract Lengths over Time',)
        st.plotly_chart(fig)


        df5 = load_data('authors.csv')
        df5['update_date'] = pd.to_datetime(df5['update_date'])
        grouper_year = pd.Grouper(key="update_date", freq="Y")
        bins = [1, 2, 3, 4, 5,float("inf")]
        labels = ["1", "2", "3", "4", "5+"]
        df5['authors_buckets'] = pd.cut(df5['authors_count'], bins=bins, labels=labels, include_lowest=True)

        agg_authors = df5.groupby([grouper_year, 'authors_buckets']).size().reset_index(name='count')
        agg_authors['percentage'] = agg_authors.groupby('update_date')['count'].apply(lambda x: x / float(x.sum()))
        agg_authors = agg_authors.pivot(index='update_date', columns='authors_buckets', values='percentage')

        colors = ["#2ecc71", "#f1c40f", "#e74c3c", "#3498db", "#9b59b6"]
        fig = px.bar(agg_authors, x=agg_authors.index, y=agg_authors.columns,
                    color_discrete_sequence=colors, barmode="stack")
        fig.update_layout(xaxis_tickformat="%Y", title="Distribution of the number of authors per paper",
                        xaxis_title="Year", yaxis_title="Percentage of Papers")
        fig.update_yaxes(tickformat=".0%", range=[0, 1])
        st.plotly_chart(fig)
    # from streamlit_modal import Modal

    # import streamlit.components.v1 as components


    # modal = Modal("Demo Modal",key='test',padding=30,max_width=800)
    # open_modal = st.button("Open")
    # if open_modal:
    #     modal.open()

    # if modal.is_open():
    #     with modal.container():
    #         st.write("Text goes here")

    #         html_string = '''

    # <!DOCTYPE html>
    # <html>
    # <head>
    #     <title>个人简历</title>
    #     <meta charset="utf-8">
    #     <meta name="viewport" content="width=device-width, initial-scale=1.0">
    #     <style type="text/css">
    #         body {
    #             font-family: Arial, sans-serif;
    #             background-color: #f1f1f1;
    #             margin: 0;
    #             padding: 0;
    #         }

    #         header {
    #             background-color: #333;
    #             color: #fff;
    #             padding: 20px;
    #             display: flex;
    #             align-items: center;
    #         }

    #         h1 {
    #             font-size: 36px;
    #             margin: 0;
    #         }

    #         img {
    #             display: block;
    #             margin-right: 20px;
    #             border-radius: 50%;
    #             width: 150px;
    #             height: 150px;
    #             object-fit: cover;
    #         }

    #         .container {
    #             margin: 50px auto;
    #             max-width: 800px;
    #             background-color: #fff;
    #             padding: 20px;
    #             border-radius: 5px;
    #             box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    #             line-height: 1.5;
    #         }

    #         h2 {
    #             font-size: 24px;
    #             margin-top: 20px;
    #             margin-bottom: 10px;
    #         }

    #         p {
    #             margin: 0;
    #         }

    #         ul {
    #             margin: 0;
    #             padding-left: 20px;
    #         }

    #         li {
    #             margin: 10px 0;
    #         }

    #         section {
    #             margin-top: 30px;
    #             margin-bottom: 30px;
    #         }

    #         table {
    #             width: 100%;
    #             border-collapse: collapse;
    #             margin-top: 20px;
    #         }

    #         th {
    #             background-color: #333;
    #             color: #fff;
    #             padding: 10px;
    #             text-align: left;
    #         }

    #         td {
    #             padding: 10px;
    #             border: 1px solid #ddd;
    #         }

    #         @media screen and (max-width: 768px) {
    #             .container {
    #                 margin: 20px;
    #                 padding: 10px;
    #             }

    #             h1 {
    #                 font-size: 24px;
    #             }

    #             img {
    #                 width: 100%;
    #                 height: auto;
    #             }
    #         }
    #     </style>
    # </head>
    # <body>
    # <header>
    # <img src="https://via.placeholder.com/150" alt="学者头像">
    # <div class="header-text">
    #     <h1>张三</h1>
    #     <h2>博士，副教授</h2>
    #     <p>研究领域：计算机视觉、机器学习</p>
    # </div>
    # </header>
    # <section>
    # <h2>基本信息</h2>
    # <ul>
    #     <li><strong>姓名：</strong>张三</li>
    #     <li><strong>性别：</strong>男</li>
    #     <li><strong>出生日期：</strong>1980年1月1日</li>
    #     <li><strong>联系方式：</strong>zhangsan@example.com</li>
    # </ul>
    # </section>
    # <section>
    # <h2>教育背景</h2>
    # <ul>
    #     <li><strong>博士：</strong>计算机科学与技术，清华大学，2009年</li>
    #     <li><strong>硕士：</strong>计算机科学与技术，清华大学，2004年</li>
    #     <li><strong>学士：</strong>计算机科学与技术，北京大学，2001年</li>
    # </ul>
    # </section>
    # <section>
    # <h2>工作经历</h2>
    # <ul>
    #     <li><strong>副教授：</strong>清华大学，2017年至今</li>
    #     <li><strong>讲师：</strong>清华大学，2012年-2017年</li>
    #     <li><strong>助理研究员：</strong>中国科学院自动化研究所，2009年-2012年</li>
    # </ul>
    # </section>
    # </body>
    # </html>
    #         '''
    #         components.html(html_string)

    #         st.write("Some fancy text")
    #         value = st.checkbox("Check me")
    #         st.write(f"Checkbox checked: {value}")
    
if __name__ == '__main__':
    if st.session_state.authentication_status:
        about_main()
    elif st.session_state.authentication_status == None:
        login_warning()       





