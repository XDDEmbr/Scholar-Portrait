import os
from PIL import Image
import streamlit as st
from pathlib import Path
import streamlit_book as stb
from utils.auth import login_warning
from utils.scholar_reg import Registration
from utils.scholar_por import show_portrait
from streamlit_option_menu import option_menu

# hide_st_style = """
# <style>
# footer {
#     visibility: hidden;
#     position: relative;
# }
# .viewerBadge_container__1QSob {
#     visibility: hidden;
# }
# </style>
# """
# st.markdown(hide_st_style, unsafe_allow_html=True)
html_temp = """
                    <div style="background-color:{};padding:1px">
                    
                    </div>
                    """

def reg_main():
    # 侧边栏
    with st.sidebar:
        selected_option = option_menu(
       menu_title = 'Registration',
       menu_icon = 'list-columns-reverse',
       icons = ['person-plus','file-person'],
       options = ['学者注册', '画像查看'],
       styles = {
           "container": {"padding": "5px"},
           "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px"}} )
        
        st.markdown("""
        # 👻About Scholar Registration
        学者库的目的仅用作学术研究使用，请放心注册~
        """)   
        # st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
        # st.markdown("""
        # # ☎️Get In Touch With Me!
        # 如果您想反馈问题或者提出建议，欢迎与我联系：📧XDDEmbrace@163.com
        # """)


    if selected_option == '学者注册':
        # 标题
        st.markdown("""
        ## 🎩Scholar Registration
        欢迎注册，成为我们学者库中的一员~
        """)        
        with st.expander("👤个人基本信息", expanded=False):
            # 显示学者注册页面（个人基本信息）
            Registration.show_scholar_reg_info()

        with st.expander("🎨研究兴趣与个人简介", expanded=False):
            # 显示学者注册页面（演技兴趣与个人简介）
            Registration.show_scholar_reg_interest()

        with st.expander("🎓教育背景", expanded=False):
            # 显示学者注册页面（教育背景）
            Registration.show_scholar_reg_education()

        with st.expander("🗺️工作经历", expanded=False):
            # 显示学者注册页面（工作经历）
            Registration.show_scholar_reg_experience()

        with st.expander("🎖️获奖信息", expanded=False):
            # 显示学者注册页面（获奖信息）
            Registration.show_scholar_reg_award()

        with st.expander("💰基金信息", expanded=False):
            # 显示学者注册页面（基金信息）
            Registration.show_scholar_reg_fund()

        with st.expander("📚出版物信息", expanded=False):
            # 显示学者注册页面（出版物信息）
            Registration.show_scholar_reg_public()

        Registration.submit_info()
        Registration.show_inof()

    if selected_option == '画像查看':
        st.markdown("""
        ## 👁️‍🗨️Scholar Portrait
        下面是您的学者画像呈现~
        """)
        reg_css = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','style_demo/', 'reg.css'))
               # --- LOAD CSS, PDF & PROFIL PIC ---
        with open(reg_css) as f:
            st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
        show_portrait()



if __name__ == '__main__':
    if st.session_state.authentication_status:
        reg_main()
    elif st.session_state.authentication_status == None:
        login_warning()       

