import os
import io
import json
import random
import pyodbc
import datetime
import pydeck as pdk
import pandas as pd
import streamlit as st
import plotly.express as px
from utils.scrap import Scarp
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image, ImageOps,ImageDraw
from utils.database import init_connection,QueryExecutor
from streamlit_elements import elements, dashboard, mui, editor, media, lazy, sync, nivo

conn = init_connection()
cur = conn.cursor()
Qe = QueryExecutor()

scholar_id = Qe.get_scholar_id()

# 查询基本信息
cur.execute('SELECT scholar_name,scholar_gender,scholar_title,scholar_institution,scholar_department,scholar_email,scholar_homepage,scholar_bio,scholar_photo FROM Scholar WHERE scholar_id=?', (scholar_id,))
result = cur.fetchone() 
if result is not None:
    scholar_name,scholar_gender,scholar_title,scholar_institution,scholar_department,scholar_email,scholar_homepage,scholar_bio,scholar_photo = result
    sch_photo = Image.open(io.BytesIO(scholar_photo))
# 查询研究兴趣
cur.execute('SELECT interest_name FROM Interest WHERE scholar_id=?', (scholar_id,))
result = cur.fetchall() 
if result is not None:
    interests= [row[0] for row in result]

# 查询教育背景
cur.execute('SELECT school,major,degree,degree_category,education_st_year,education_end_year FROM Education WHERE scholar_id=?', (scholar_id,))
results = cur.fetchall() 
edu = []
for result in results:
    if result is not None:
        school,major,degree,degree_category,education_st_year,education_end_year = result
        edu.append((school, major, degree, degree_category, education_st_year, education_end_year))

# 查询工作经历
cur.execute('SELECT experience_title,experience_institution,experience_department,experience_st_year,experience_end_year,address,longitude,latitude FROM Experience WHERE scholar_id=?', (scholar_id,))
results  = cur.fetchall()
exp = []
for result in results:
    if result is not None:
        experience_title,experience_institution,experience_department,experience_st_year,experience_end_year,address,longitude,latitude = result
        exp.append((experience_title,experience_institution,experience_department,experience_st_year,experience_end_year,address,longitude,latitude))

# 查询获奖信息
cur.execute('SELECT award_title,award_year,award_sponsor FROM Award WHERE scholar_id=?', (scholar_id,))
results = cur.fetchall() 
award = []
for result in results:
    if result is not None:
        award_title,award_year,award_sponsor = result
        award.append((award_title,award_year,award_sponsor))

# 查询基金信息
cur.execute('SELECT fund_title,fund_year,fund_sponsor,fund_amount FROM Fund WHERE scholar_id=?', (scholar_id,))
results = cur.fetchall() 
fund = []
for result in results:
    if result is not None:
        fund_title,fund_year,fund_sponsor,fund_amount = result
        fund.append((fund_title,fund_year,fund_sponsor,fund_amount))

# 查询出版物信息
cur.execute('SELECT publication_title,YEAR(publication_year) as pub_year,publication_type,journal,publisher,coauthors,doi,abstract,keywords,link FROM Publication WHERE scholar_id=?', (scholar_id,))
results = cur.fetchall() 
pub = []
for result in results:
    if result is not None:
        publication_title,pub_year,publication_type,journal,publisher,coauthors,doi,abstract,keywords,link = result
        pub.append((publication_title,pub_year,publication_type,journal,publisher,coauthors,doi,abstract,keywords,link))

def show_portrait():
        


    # --- 基本信息 ---
    col1, col2 = st.columns([1,3], gap="small")
    with col1:
         st.image(sch_photo, width=230)

    with col2:
        st.title(scholar_name)
        st.write(f"**性别**：{scholar_gender}")
        st.write(f"**职称**：{scholar_title}")
        st.write(f"**所在单位**：{scholar_institution+scholar_department}")
        colmail,colhome = st.columns(2)
        with colmail:
            st.write("📫",scholar_email)
        with colhome:
            st.write(f"[📎HomePage]({scholar_homepage})")

    # --- 个人简介 ---
    st.write('\n')
    st.subheader("👤个人简介")  
    st.write(scholar_bio)

    # --- 教育背景 $ 研究兴趣---
    st.write('\n')
    coledu,colint = st.columns([3,2])
    with coledu:
        st.subheader("🎓教育背景")
        st.write("---")
        for row in edu:      
            formatted_row = '- \t'.join(['{:<30}'.format(str(e)) for e in row])
            st.write('- 🔶 ' + formatted_row)
            st.write('\n')
    with colint:
        st.subheader("💟研究兴趣")
        st.write("---")
        interests_str = ','.join(interests)
        wordcloud = WordCloud(width=80, height=40, background_color='white',scale=20,font_path='./fonts/simhei.ttf').generate(interests_str)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)


    # --- 工作经历 ---
    st.write('\n')
    st.subheader("🗺️工作经历")
    st.write("---")
    colexp,colmap = st.columns([1,3])
    with colexp:
        for row in exp:
            st.write('- 🎈 ',f'**{row[1]}|{row[2]}**')
            st.write('-',str(row[3])+'——'+str(row[4]))
            st.text('🏴󠁧󠁢󠁷󠁬󠁳󠁿'+row[5])
            st.write('- 🎗️', row[0])
    with colmap:
        exp1 = pd.DataFrame(exp, columns=['title','institution','department','st_year','end_year','address','lon','lat'])
        exp1['lon'] = exp1['lon'].astype(float)
        exp1['lat'] = exp1['lat'].astype(float)

        df1 = exp1[['address', 'lon', 'lat']].iloc[[0]]
        df1.columns = ['address', 'lon', 'lat']
        df2 = exp1[['address', 'lon', 'lat']].iloc[[1, 2]]
        df2.columns = ['address', 'lon', 'lat']
        df2 = df2.reset_index(drop=True)
        df2.columns = [col + '2' for col in df2.columns]
        result = pd.concat([df1, df2], axis=1)
        if pd.isna(result['address2']).all():
            result = result.iloc[:-1]
        else:
            result['address'].iloc[1] = result['address2'].iloc[0]
            result['lon'].iloc[1] = result['lon2'].iloc[0]
            result['lat'].iloc[1] = result['lat2'].iloc[0]

        # Set the map center to Shanghai
        view_state = pdk.ViewState(
            latitude=31.2304,
            longitude=121.4737,
            zoom=3,
            pitch=50)

        arc_layer = pdk.Layer(
            'ArcLayer',
            data=result,
            get_source_position=["lon", "lat"],
            get_target_position=["lon2", "lat2"],
            get_source_color=[200, 30, 0, 160],
            get_target_color=[200, 30, 0, 160],
            auto_highlight=True,
            get_width=3,
            pickable=True
            )

        # # Draw the map
        st.pydeck_chart(pdk.Deck(
            #map_style='mapbox://styles/mapbox/light-v9',
            map_style = None,
            initial_view_state=view_state,
            layers=[arc_layer],
            tooltip={
                #'html': '<b>{exp1.institution} - {end_occupation}</b><br/>{location} to {end_location}',
                'html': '<b>{institution}</b><br/>{title}</b><br/>{address}',
                'style': {
                    'backgroundColor': 'steelblue',
                    'color': 'white'
                }
            }))
  
    # --- 获奖经历 ---
    st.write('\n')
    st.subheader("🎖️所获奖项")
    st.write("---")
    for row in award:      
        formatted_row = '- \t'.join(['{:<30}'.format(str(e)) for e in row])
        st.write('- 🏆  ' + formatted_row)
        st.write('\n')
  
    # --- 所获基金 ---
    st.write('\n')
    st.subheader("💰所获基金")
    st.write("---")
    for row in fund:      
        formatted_row = '- \t'.join(['{:<30}'.format(str(e)) for e in row])
        st.write('- 💲  ' + formatted_row)
        st.write('\n')

    # --- 出版物信息 ---
    st.write('\n')
    st.subheader("📚出版物信息")
    st.write("---")
    with st.expander("出版物信息"):
        for row in pub:            
            st.write(f'- 📗 <a href="{row[9]}"><span style="color:rgba(6, 137, 244, 0.867)">{row[0]}</span></a>.{scholar_name},{row[5]}.<span style="color:#6A5ACD">{row[3]}</span>.{str(row[1])}', unsafe_allow_html=True)
    public = pd.DataFrame(pub,columns=('title','year','type','journal','publisher','coauthors','doi','abstract','keywords','link'))
    with st.expander("Extracted papers"):
        st.dataframe(public)
        csv = Scarp.convert_df(public)
        file_name_value = "_".join(scholar_name.split())+'.csv'
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=file_name_value,
        mime='text/csv',
    )
    colsite,colauth = st.columns([2,3])
    with colsite:
        percentage_sites = {}
        sites = list(public['journal'])
        for i in sites:
            percentage_sites[i] = sites.count(i)/len(sites)*100
        df_per = pd.DataFrame(list(zip(percentage_sites.keys(), percentage_sites.values())), columns=['sites', 'percentage'])

        fig2 = px.pie(
                df_per, 
                values="percentage", 
                names="sites", 
                )
        st.plotly_chart(fig2, theme="streamlit", use_container_width=True)
    with colauth:
        coauthors_count = {}
        coaus = [i.strip() for item in public['coauthors'] for i in item.split(',')] 
        for i in coaus:
            coauthors_count[i] = coaus.count(i)
        df_coau = pd.DataFrame(list(zip(coauthors_count.keys(), coauthors_count.values())), columns=['co_author', 'co_counts'])
        fig = px.scatter(df_coau, x="co_author", y="co_counts", size="co_counts", color='co_author',hover_data=["co_counts"],size_max=60)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        # 论文数量随年份变化趋势
        year_counts = public.groupby("year").size().reset_index(name="count")
        year_counts["count"] = year_counts["count"].astype(str)
        year_counts_dict = year_counts.to_dict('records') 
        year_counts_line = [{    "id": scholar_name,    "color": "hsl(58, 70%, 50%)",    "data": [{"x": str(row['year']), "y": row['count']} for row in year_counts_dict]}]

    layout = [
        # Editor item is positioned in coordinates x=0 and y=0, and takes 6/12 columns and has a height of 3.
        dashboard.Item("Pine Chart", 0, 0, 6, 3),
        # Chart item is positioned in coordinates x=6 and y=0, and takes 6/12 columns and has a height of 3.
        dashboard.Item("Line Chart", 6, 0, 6, 3)
    ]

    percentage_categories = {}
    types = [i.strip() for item in public['type'] for i in item.split(';')] 
    for i in types:
        percentage_categories[i] = types.count(i)
    df_per = pd.DataFrame(list(zip(percentage_categories.keys(), percentage_categories.values())), columns=['types', 'percentage'])
    type_data = [{"id": row["types"], "value": row["percentage"]} for index, row in df_per.iterrows()]

    with elements("Visiual"):
        with dashboard.Grid(layout, draggableHandle=".draggable"):
            with mui.Card(key="Line Chart", sx={"display": "flex", "flexDirection": "column"}):
                mui.CardHeader(title="Papers-Year", className="draggable")
                with mui.CardContent(sx={"flex": 1, "minHeight": 0}):                   
                    nivo.Line(
                        data=year_counts_line,
                        margin={ 'top': 50, 'right': 110, 'bottom': 50, 'left': 60 },
                        xScale={ 'type': 'point' },
                        yScale={
                            'type': 'linear',
                            'min': 0,
                            'max': 8,
                            'stacked': True,
                            'reverse': False,
                            'tickFormat': ',d'
                        },
                        axisTop=None,
                        axisRight=None,
                        axisBottom={
                            'orient': 'bottom',
                            'tickSize': 5,
                            'tickPadding': 5,
                            'tickRotation': 0,
                            'legend': '年份',
                            'legendOffset': 36,
                            'legendPosition': 'middle'
                        },
                        axisLeft={
                            'orient': 'left',
                            'tickSize': 5,
                            'tickPadding': 5,
                            'tickRotation': 0,
                            'legend': '论文数量',
                            'legendOffset': -40,
                            'legendPosition': 'middle'
                        },
                        pointSize=10,
                        pointColor={ 'theme': 'background' },
                        pointBorderWidth=2,
                        pointBorderColor={ 'from': 'serieColor' },
                        pointLabelYOffset=-12,
                        useMesh=True,
                        enableGridX=False,
                        enableGridY=True,
                        legends=[
                            {
                                'anchor': 'bottom-right',
                                'direction': 'column',
                                'justify': False,
                                'translateX': 100,
                                'translateY': 0,
                                'itemsSpacing': 0,
                                'itemDirection': 'left-to-right',
                                'itemWidth': 80,
                                'itemHeight': 20,
                                'itemOpacity': 0.75,
                                'symbolSize': 12,
                                'symbolShape': 'circle',
                                'symbolBorderColor': 'rgba(0, 0, 0, .5)',
                                'effects': [
                                    {
                                        'on': 'hover',
                                        'style': {
                                            'itemBackground': 'rgba(0, 0, 0, .03)',
                                            'itemOpacity': 1
                                        }
                                    }
                                ]
                            }
                        ]                   
                )

            with mui.Card(key="Pine Chart", sx={"display": "flex", "flexDirection": "column"}):
                mui.CardHeader(title="Precentage of Categories", className="draggable")
                with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
                    defs=[
                        {
                            "id": "dots",
                            "type": "patternDots",
                            "background": "inherit",
                            "color": "rgba(255, 255, 255, 0.3)",
                            "size": 4,
                            "padding": 1,
                            "stagger": True
                        },
                        {
                            "id": "lines",
                            "type": "patternLines",
                            "background": "inherit",
                            "color": "rgba(255, 255, 255, 0.3)",
                            "rotation": -45,
                            "lineWidth": 6,
                            "spacing": 10
                        }
                    ]               
                    nivo.Pie(
                    data=type_data,                   
                    margin={ "top": 40, "right": 80, "bottom": 80, "left": 80 },
                    innerRadius=0.5,
                    padAngle=0.7,
                    cornerRadius=3,
                    activeOuterRadiusOffset=8,
                    borderWidth=1,
                    arcLinkLabelsSkipAngle=10,
                    arcLinkLabelsTextColor="grey",
                    arcLinkLabelsThickness=2,
                    arcLabelsSkipAngle=10,
                    defs=[
                        {
                            "id": "dots",
                            "type": "patternDots",
                            "background": "inherit",
                            "color": "rgba(255, 255, 255, 0.3)",
                            "size": 4,
                            "padding": 1,
                            "stagger": True
                        },
                        {
                            "id": "lines",
                            "type": "patternLines",
                            "background": "inherit",
                            "color": "rgba(255, 255, 255, 0.3)",
                            "rotation": -45,
                            "lineWidth": 6,
                            "spacing": 10
                        }
                    ],
                    fill = [{"match": {"id": type_data[i]["id"]}, "id": random.choice(defs)["id"]} for i in range(len(type_data))],
                    legends=[
                        {
                            "anchor": "bottom",
                            "direction": "row",
                            "justify": False,
                            "translateX": 0,
                            "translateY": 56,
                            "itemsSpacing": 0,
                            "itemWidth": 100,
                            "itemHeight": 18,
                            "itemTextColor": "#999",
                            "itemDirection": "left-to-right",
                            "itemOpacity": 1,
                            "symbolSize": 18,
                            "symbolShape": "circle",
                            "effects": [
                                {
                                    "on": "hover",
                                    "style": {
                                        "itemTextColor": "#000"
                                    }
                                }
                            ]
                        }
                    ]
                )
                    