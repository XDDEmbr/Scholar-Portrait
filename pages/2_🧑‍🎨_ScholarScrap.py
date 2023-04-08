import random
import requests
import pandas as pd
from time import sleep
import streamlit as st
import plotly.express as px
from utils.scrap import Scarp
from utils.auth import login_warning

html_temp = """
                    <div style="background-color:{};padding:1px">
                    
                    </div>
                    """

def scarp_main():
    
    with st.sidebar:
        st.markdown("""
      # 🔗Tips~
      根据用户输入，从Google Scholar中提取研究论文相关信息~
      """)
      
        st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
        st.markdown("""
    # 🔗How does it work?
    在文本字段中输入关键字，并选择从Google Scholar结果中抓取多少页~  
    """)

    hide="""<style>footer{visibility: hidden;	position: relative;}.viewerBadge_container__1QSob{visibility: hidden;}<style>"""
    st.markdown(hide, unsafe_allow_html=True)
    # 标题
    st.markdown("""
    ## 🧑‍🎨Scholar Scrap
    从Google Scholar上抓取研究论文相关信息~
    """)
    # 抓取功能
    # 创建repository
    paper_repos_dict = {
                        'Paper Title' : [],
                        'Year' : [],
                        'Author' : [],
                        'Citation' : [],
                        'Publication site' : [],
                        'Url of paper' : [] }
    # 在repository添加信息
    def add_in_paper_repo(papername,year,author,cite,publi,link):
        paper_repos_dict['Paper Title'].extend(papername)
        paper_repos_dict['Year'].extend(year)
        paper_repos_dict['Author'].extend(author)
        paper_repos_dict['Citation'].extend(cite)
        paper_repos_dict['Publication site'].extend(publi)
        paper_repos_dict['Url of paper'].extend(link)
        df = pd.DataFrame(paper_repos_dict)  
        return df

    # headers 爬取Google学术搜索结果页面
    # 定义了一个HTTP请求的头部信息和两个变量。头部信息中包含了浏览器类型和版本等信息，这些信息可以帮助服务器了解客户端的环境。
    # url_begin和url_end分别是链接的起始部分和结束部分，其中{}部分可以用具体的参数来替换，从而得到完整的链接。
    # headers：是一个字典类型，包含了用户代理信息，用来模拟浏览器访问网页，避免被反爬虫机制禁止访问。

    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    url_begin = 'https://scholar.google.com/scholar?start={}&q='
    url_end = '&hl=en&as_sdt=0,5='

    # 输入
    col1, col2 = st.columns([3,1])
    with col1:
        input_scarp = st.text_input("Search in Google Scholar", key='ScholarScrap',placeholder="What are you looking for?", disabled=False)
    with col2:
        total_to_scrap = st.slider("How many pages to scrap?", min_value=1, max_value=10, step=1, value=2)

    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True) #背景颜色为rgba(55, 53, 47, 0.16)



    # 创造学者url
    if input_scarp:
        text_formated = "+".join(input_scarp.split())
        input_url = url_begin+text_formated+url_end
        if input_url:
            response=requests.get(input_url,headers=headers,timeout=600,verify=False)
            
            total_papers = 10 * total_to_scrap
            for i in range (0,total_papers,10):
                # 得到每一页的url
                url = input_url.format(i)
                # 得到每一页的内容
                doc = Scarp.get_paperinfo(url, headers)

                # 收集标签
                paper_tag,cite_tag,link_tag,author_tag = Scarp.get_tags(doc)

                # 每页的论文标题
                papername = Scarp.get_papertitle(paper_tag)

                # 论文发表年份、发表网站、作者
                year , publication , author = Scarp.get_author_year_publi_info(author_tag)

                # 论文引数 
                cite = Scarp.get_citecount(cite_tag)

                # 论文网址
                link = Scarp.get_link(link_tag)

                # 加入repository
                final = add_in_paper_repo(papername,year,author,cite,publication,link)

                # use sleep to avoid status code 429
                sleep()
        
            final['Year'] = final['Year'].astype('int')
            final['Citation'] = final['Citation'].apply(Scarp.cite_number).astype('int')
            
            # 用expander组件来创建一个可展开的面板，其中包含了一个数据框 final。
            # 同时，代码还通过 convert_df 函数将数据框 final 转换成了 CSV 格式，最后使用 st.download_button 组件添加一个下载按钮，使用户可以下载 CSV 文件。 
            # label 参数为下载按钮的显示文本，data 参数为下载的数据，file_name 参数指定要下载的文件名，mime 参数为文件类型。
            with st.expander("Extracted papers"):
                st.dataframe(final)
                csv = Scarp.convert_df(final)
                file_name_value = "_".join(input_scarp.split())+'.csv'
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=file_name_value,
                mime='text/csv',
            )

            # 绘制，两列的格式
            col1, col2 = st.columns([2,1])

            # 显示论文发表年份和引用的分布情况，用户可以选择使用引用作为气泡大小
            with col1:
                with st.expander("Distribution of papers by year and citation", expanded=True):
                    size_button = st.checkbox('Set Citation as bubble size', value=True)
                    size_value = None
                    if size_button:
                        size_value = 'Citation'
                    final_sorted = final.sort_values(by='Year', ascending=True)
                    fig1 = px.scatter(
                          final_sorted, 
                          x="Year", 
                          color="Publication site",
                          size=size_value, 
                          log_x=True, 
                          size_max=60
                          )
                    fig1.update_xaxes(type='category')
                    st.plotly_chart(fig1, theme="streamlit", use_container_width=True)

            # 显示出版物网站的百分比
            with col2:
                percentage_sites = {}
                sites = list(final_sorted['Publication site'])
                for i in sites:
                    percentage_sites[i] = sites.count(i)/len(sites)*100
                df_per = pd.DataFrame(list(zip(percentage_sites.keys(), percentage_sites.values())), columns=['sites', 'percentage'])
          
                fig2 = px.pie(
                      df_per, 
                      values="percentage", 
                      names="sites", 
                      )
                with st.expander("发表网站的百分比", expanded=True):
                    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)

            with st.expander("作者发表文献的百分比", expanded=True): 
                # 将每篇文章的作者列表按照逗号分隔并且去除空格，并生成新的DataFrame
                author_list = final_sorted['Author'].str.split(",|，", expand=True).apply(lambda x: x.str.strip())
      
                # 对新的DataFrame使用groupby函数按照作者进行分组，并使用value_counts函数计算每个作者的文章数量
                author_counts = author_list.stack().value_counts()
      
                # 将统计结果生成新的DataFrame，并将作者和对应的文章数量作为列名
                df_au_per = pd.DataFrame({"authors": author_counts.index, "article_count": author_counts.values})
      
                # 绘制柱状图，以作者作为分类，文章数量作为值
                colors = ['#'+"".join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(len(df_au_per))]
                fig = px.bar(df_au_per, x='authors', y='article_count', color=colors)
                fig.update_traces(texttemplate='%{y}', textposition='outside', textfont_size=12)
                fig.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)

if __name__ == '__main__':
    if st.session_state.authentication_status:
        scarp_main()
    elif st.session_state.authentication_status == None:
        login_warning()       
