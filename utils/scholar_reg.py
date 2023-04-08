import os
import io
import pyodbc
import datetime
import streamlit as st
from PIL import Image, ImageOps,ImageDraw
from utils.database import QueryExecutor,init_connection

conn = init_connection()
cur = conn.cursor()
Qe = QueryExecutor()
html_temp = """
                    <div style="background-color:{};padding:1px">
                    
                    </div>
                    """

class Registration:

    def show_inof():
        is_claim = Qe.is_claim()
        if is_claim == True:
            st.info('您已经加入学者库，可以进一步查看您的画像信息了！')
    
    # 基本信息
    def show_scholar_reg_info():
        col1, col2 = st.columns(2)
        placeholder_image = Image.open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','images/', 'placeholder.png')))
        # 左侧用来上传学者图片
        with col1:
            uploaded_file = st.file_uploader("上传学者图片（可选）", type=["png", "jpg", "jpeg"])

            # 如果有图片上传，则显示图片，否则显示占位符
            if uploaded_file:
                scholar_image = uploaded_file.read()
                # 将图片裁剪为正方形
                scholar_image = Image.open(uploaded_file)
                scholar_image = ImageOps.fit(scholar_image, (10000, 10000), Image.ANTIALIAS)
                # 将图片转换为圆形，并展示在界面上
                mask_size = 300        
                mask = Image.new('L', (mask_size, mask_size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, mask_size, mask_size), fill=255)
                scholar_image = ImageOps.fit(scholar_image, (mask_size, mask_size))
                scholar_image.putalpha(mask)
                st.image(scholar_image, use_column_width=False)
            else:
                # 显示占位符
                st.image(placeholder_image, width=300)
            scholar_homepage = st.text_input('个人主页',placeholder='Url')

        # 右侧用来输入学者信息
        with col2:
            scholar_name = st.text_input(':red[*] 姓名')
            scholar_gender = st.selectbox(':red[*] 性别', ['男', '女'])
            scholar_title = st.text_input('职称')
            scholar_org = st.text_input(':red[*] 当前所在机构')
            scholar_dep = st.text_input('当前所在系')
            scholar_mail = st.text_input(':red[*] 邮箱')
            if st.button('Save',help='保存已输入的信息',key='button1'):
                image_bytes = io.BytesIO()
                scholar_image.save(image_bytes, format='PNG')
                image_bytes = image_bytes.getvalue()
                cur.execute('SELECT MAX(scholar_id) FROM Scholar')
                max_id = cur.fetchone()[0]
                new_id = 1 if max_id is None else max_id + 1
                Qe.insert_scholar(new_id,scholar_name,scholar_gender,scholar_title,scholar_org,scholar_dep,scholar_mail,scholar_homepage,pyodbc.Binary(image_bytes))
                st.success('保存成功！')

    # 研究兴趣
    def show_scholar_reg_interest():
        col3, col4 = st.columns(2)
        with col3:
        # 定义可选的研究兴趣选项
            research_interests_options = Qe.get_interest()            
            # 在侧边栏中添加研究兴趣的多选框
            research_interests = st.multiselect(
                "选择您的研究兴趣（最多10个）",
                research_interests_options,
                max_selections=10,
                key='interest_select'
            )
            # 确保最多选择10个研究兴趣
            if len(research_interests) > 10:
                st.warning("您最多只能选择10个研究兴趣！")
                research_interests = research_interests[:10]
            # 显示所选的研究兴趣
            if research_interests:
                st.write("您选择了以下研究兴趣：")                
                for interest in research_interests:
                    st.write("► " + interest)                   
            else:
                st.write(":red[*] 请选择您的研究兴趣。")           
        with col4:
            scholar_bio=st.text_area('个人简介',height=400,placeholder="请输入你的个人简介~",key='scholar_bio')
            if st.button('保存'):
                Qe.insert_scholar_bio(scholar_bio)

    # 教育背景
    def show_education_input(key):
        col5,col6 = st.columns(2)
        st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
        with col5:
            scholar_school = st.text_input(':red[*] 就读学校',key=f'{key}_school')
            scholar_major = st.text_input(':red[*] 就读专业',key=f'{key}_major')
            scholar_degree = st.selectbox(':red[*] 所获学位',['学士','硕士','博士'],key=f'{key}_degree')     
        with col6:        
            min_date = datetime.date(1950, 1, 1)
            max_date = datetime.date(1950, 1, 1)
            st_edu_data = st.date_input(
                ':red[*] 开始日期',
                datetime.date(2023, 4, 5),
                min_value = min_date,
                key=f'{key}_edu_start_date'
                )
            end_edu_data = st.date_input(
                ':red[*] 结束日期',
                datetime.date(2023, 4, 5),
                min_value = max_date,
                key=f'{key}_edu_end_date'
                )
            scholar_sub_category = st.text_input(':red[*] 学位类别',key=f'{key}_degree_category')  
            if st.button('删除', key=f'{key}_edu_delete'):
                # 通过删除对应的 session state 来删除此教育背景输入框
                del st.session_state[f'edu_{key}_values'],st.session_state[f'edu_{key}']                      
        return scholar_school, st_edu_data, end_edu_data, scholar_major, scholar_degree,scholar_sub_category

    def show_scholar_reg_education():
        # 初始化教育背景段计数器
        if 'edu_count' not in st.session_state:
            st.session_state.edu_count = 1
        # 显示当前所有教育背景段
        for i in range(st.session_state.edu_count + 1):
            edu_values = st.session_state.get(f'edu_{i}_values')
            if edu_values:
                scholar_school, st_edu_data, end_edu_data, scholar_major, scholar_degree, scholar_sub_category = Registration.show_education_input(i)
                st.session_state[f'edu_{i}_values'] = (scholar_school, st_edu_data, end_edu_data, scholar_major, scholar_degree, scholar_sub_category)
        # 显示 "Add" 按钮
        if st.button('Add', key='education_add'):
            # 增加教育背景段计数器
            st.session_state.edu_count += 1
            # 添加新的教育背景段
            st.session_state[f'edu_{st.session_state.edu_count}'] = Registration.show_education_input(st.session_state.edu_count)
            # 存储教育背景段的值
            st.session_state[f'edu_{st.session_state.edu_count}_values'] = st.session_state[f'edu_{st.session_state.edu_count}']
   
    # 工作经历 
    def show_experience_input(key):
        col7, col8 = st.columns(2)
        st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"), unsafe_allow_html=True)
        with col7:
            experience_institution = st.text_input(':red[*] 工作单位', key=f'{key}_institution')
            experience_department = st.text_input('所在部门', key=f'{key}_department')
            experience_title = st.text_input('职位', key=f'{key}_title')
        with col8:
            min_date = datetime.date(1950, 1, 1)
            st_ep_data = st.date_input(
                '开始日期',
                datetime.date(2023, 4, 5),
                min_value=min_date,
                key=f'{key}_ep_start_date'
            )
            end_ep_data = st.date_input(
                '结束日期',
                datetime.date(2023, 4, 5),
                key=f'{key}_ep_end_date'
            )
            experience_address = st.text_input(':red[*] 工作地点', key=f'{key}_address')
            if st.button('删除', key=f'{key}_exper_delete'):
                # 通过删除对应的 session state 来删除此工作经历输入框
                del st.session_state[f'exper_{key}']
                del st.session_state[f'exper_{key}_values']
        return experience_institution, experience_department, experience_title, st_ep_data, end_ep_data, experience_address

    def show_scholar_reg_experience():
        # 初始化工作经历段计数器
        if 'exper_count' not in st.session_state:
            st.session_state.exper_count = 1
        # 显示当前所有工作经历段
        for i in range(st.session_state.exper_count + 1):
            exper_values = st.session_state.get(f'exper_{i}_values')
            if exper_values:
                experience_institution, experience_department, experience_title, st_ep_data, end_ep_data, experience_address = Registration.show_experience_input(i)
                st.session_state[f'exper_{i}_values'] = (experience_institution, experience_department, experience_title, st_ep_data, end_ep_data, experience_address
)
        # 显示 "Add" 按钮
        if st.button('Add', key='experience_add'):
            # 增加工作经历段计数器
            st.session_state.exper_count += 1
            # 添加新的工作经历段
            st.session_state[f'exper_{st.session_state.exper_count}'] = Registration.show_experience_input(st.session_state.exper_count)
            # 存储工作经历段的值
            st.session_state[f'exper_{st.session_state.exper_count}_values'] = st.session_state[f'exper_{st.session_state.exper_count}']
    
    # 获奖信息
    def show_award_input(key):
        col9,col10 = st.columns(2)
        st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"), unsafe_allow_html=True)
        with col9:
            award_title = st.text_input('奖项名称',key=f'{key}_award_title')
            award_sponsor = st.text_input('颁奖机构',key=f'{key}_award_sponsor')     
            min_date = datetime.date(1950, 1, 1)
            award_data = st.date_input(
                '获奖日期',
                datetime.date(2023, 4, 5),
                min_value = min_date,
                key=f'{key}_award_data'
                )
            with col10:
                award_discribe = st.text_area('奖项描述',height=200,placeholder='请输入你的奖项描述~',key=f'{key}_award_discribe')
                if st.button('删除', key=f'{key}_award_delete'):
                    # 通过删除对应的 session state 来删除此奖项输入框
                    del st.session_state[f'award_{key}_values'],st.session_state[f'award_{key}']
        return award_title,award_sponsor,award_data,award_discribe

    def show_scholar_reg_award():
         # 初始化获奖段计数器
        if 'award_count' not in st.session_state:
            st.session_state.award_count = 1
        # 显示当前所有获奖段
        for i in range(st.session_state.award_count + 1):
            award_values = st.session_state.get(f'award_{i}_values')
            if award_values:
                award_title,award_sponsor,award_data,award_discribe = Registration.show_award_input(i)
                st.session_state[f'award_{i}_values'] = (award_title,award_sponsor,award_data,award_discribe)
        # 显示 "Add" 按钮
        if st.button('Add', key='award_add'):
            # 增加获奖段计数器
            st.session_state.award_count += 1
            # 添加新的获奖段
            st.session_state[f'award_{st.session_state.award_count}'] = Registration.show_award_input(st.session_state.award_count)
            # 存储获奖段的值
            st.session_state[f'award_{st.session_state.award_count}_values'] = st.session_state[f'award_{st.session_state.award_count}']

    # 基金信息
    def show_fund_input(key):
        col11,col12 = st.columns(2)
        st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"), unsafe_allow_html=True)
        with col11:
            fund_title = st.text_input('基金名称',key=f'{key}_fund_title')
            fund_sponsor = st.text_input('基金机构',key=f'{key}_fund_sponsor')     
            
        with col12:
            min_date = datetime.date(1950, 1, 1)
            fund_data = st.date_input(
            '获得基金日期',
            datetime.date(2023, 4, 5),
            min_value = min_date,
            key=f'{key}_fund_data'
            ) 
            fund_amount = st.text_input('基金金额',key=f'{key}_fund_amount')
            if st.button('删除', key=f'{key}_fund_delete'):
                # 通过删除对应的 session state 来删除此基金输入框
                del st.session_state[f'fund_{key}_values'],st.session_state[f'fund_{key}']
        return fund_title,fund_sponsor,fund_data,fund_amount

    def show_scholar_reg_fund():
        # 初始化基金段计数器
        if 'fund_count' not in st.session_state:
            st.session_state.fund_count = 1
        # 显示当前所有基金段
        for i in range(st.session_state.fund_count + 1):
            fund_values = st.session_state.get(f'fund_{i}_values')
            if fund_values:
                fund_title,fund_sponsor,fund_data,fund_amount = Registration.show_fund_input(i)
                st.session_state[f'fund_{i}_values'] = (fund_title,fund_sponsor,fund_data,fund_amount)
        # 显示 "Add" 按钮
        if st.button('Add', key='fund_add'):
            # 增加基金段计数器
            st.session_state.fund_count += 1
            # 添加新的基金段
            st.session_state[f'fund_{st.session_state.fund_count}'] = Registration.show_fund_input(st.session_state.fund_count)
            # 存储基金段的值
            st.session_state[f'fund_{st.session_state.fund_count}_values'] = st.session_state[f'fund_{st.session_state.fund_count}']

    # 出版物信息
    def show_public_input(key):
        col13,col14 = st.columns(2)
        st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"), unsafe_allow_html=True)
        with col13:
            publication_title = st.text_input('出版物标题',key=f'{key}_publication_title')
            min_date = datetime.date(1950, 1, 1)
            publication_data = st.date_input(
                '出版时间',
                datetime.date(2023, 4, 5),
                min_value = min_date,
                key=f'{key}_publication_data'
                ) 
            publication_type = st.text_input('出版物类型',key=f'{key}_publication_type')
            journal = st.text_input('发表期刊',key=f'{key}_joural')
            publisher = st.text_input('关键词',key=f'{key}_pubisher')
            coauthors = st.text_input('合作者',placeholder='注意不同合作者之间用“ , ”分隔开',key=f'{key}_coauthors')
        with col14: 
            abstract = st.text_area('摘要',height=306,help='请输入摘要~',key=f'{key}_abstract')   
            doi = st.text_input('DOI',key=f'{key}_doi')
            link = st.text_input('URL',key=f'{key}_link')        
            if st.button('删除', key=f'{key}_public_delete'):
                # 通过删除对应的 session state 来删除此出版物输入框
                del st.session_state[f'public_{key}_values'],st.session_state[f'public_{key}']   
        return publication_title,publication_data,publication_type,journal,publisher,coauthors,abstract,doi,link 

    def show_scholar_reg_public():
        # 初始化出版物段计数器
        if 'public_count' not in st.session_state:
            st.session_state.public_count = 1
        # 显示当前所有出版物段
        for i in range(st.session_state.public_count + 1):
            public_values = st.session_state.get(f'public_{i}_values')
            if public_values:
                publication_title,publication_data,publication_type,journal,publisher,coauthors,abstract,doi,link = Registration.show_public_input(i)
                st.session_state[f'public_{i}_values'] = (publication_title,publication_data,publication_type,journal,publisher,coauthors,abstract,doi,link)
        # 显示 "Add" 按钮
        if st.button('Add', key='public_add'):
            # 增加出版物段计数器
            st.session_state.public_count += 1
            # 添加新的出版物段
            st.session_state[f'public_{st.session_state.public_count}'] = Registration.show_public_input(st.session_state.public_count)
            # 存储出版物段的值
            st.session_state[f'public_{st.session_state.public_count}_values'] = st.session_state[f'public_{st.session_state.public_count}']

    def insert_all_education():
        for i in range(1, st.session_state.edu_count + 1):
            edu_values = st.session_state.get(f'edu_{i}_values')
            if edu_values:
                school, start_date, end_date, major, degree, degree_category = edu_values
                Qe.insert_education(school, major, degree, degree_category, start_date, end_date)

    def insert_all_experience():
        for i in range(1, st.session_state.exper_count + 1):
            exper_values = st.session_state.get(f'exper_{i}_values')
            if exper_values:
                institution, department, title, start_date, end_date, address = exper_values
                latitude, longitude = Qe.get_latitude_longitude()
                Qe.insert_experience(title,institution, department, start_date, end_date, address,latitude, longitude)
    
    def insert_all_award():
        # Get all the inserted award information from session state
        for i in range(st.session_state.award_count + 1):
            award_values = st.session_state.get(f'award_{i}_values')
            if award_values:
                # Unpack the award_values tuple
                award_title, award_sponsor, award_data, award_discribe = award_values
                # Insert the award information into the database    
                Qe.insert_award(award_title, award_data, award_sponsor,award_discribe)
    
    def insert_all_fund():
        # 获取所有基金段
        for i in range(1, st.session_state.fund_count + 1):
            fund_values = st.session_state.get(f'fund_{i}_values')
            if fund_values:
            # 插入每个基金段
                fund_title, fund_sponsor, fund_date, fund_amount = fund_values
                Qe.insert_fund(fund_title, fund_date,fund_sponsor, fund_amount)

    def insert_all_publication():
        for i in range(1, st.session_state.public_count + 1):
            public_values = st.session_state.get(f'public_{i}_values')
            if public_values:
                publication_title, publication_data, publication_type, journal, publisher, coauthors, abstract, doi, link = public_values
                Qe.insert_publication(publication_title, publication_data, publication_type, journal, publisher, coauthors, abstract, doi, link)
   
    def submit_info():
        research_interests = st.session_state.interest_select
        scholar_bio = st.session_state.scholar_bio
        if st.button('Submit',key='submit_info',help='提交你的信息'):
            for interest in research_interests:
                Qe.insert_interest(interest)
            Qe.insert_scholar_bio(scholar_bio)
            Registration.insert_all_education()
            Registration.insert_all_experience()
            Registration.insert_all_award()
            Registration.insert_all_fund()
            Registration.insert_all_publication() 


            
        

            