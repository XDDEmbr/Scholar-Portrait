import os
import requests
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from utils.auth import login,register_user,reset_password,forgot_password,forgot_username,update_user_details


st.set_page_config(page_title="Scholar Portrait", page_icon="🎓",layout="wide")
# Creates the side navigaton bar
main_page_sidebar = st.sidebar.empty()
with main_page_sidebar:
    selected_option = option_menu(
       menu_title = 'Authenticator',
       menu_icon = 'list-columns-reverse',
       icons = ['box-arrow-in-right', 'person-plus', 'x-circle','arrow-counterclockwise','x-circle','arrow-clockwise'],
       options = ['Login', 'Create Account', 'Forgot Password?', 'Reset Password','Forgot Username?','Update User Details'],
       styles = {
           "container": {"padding": "5px"},
           "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px"}} )

def load_lottieurl(url:str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    local_css(os.path.abspath(os.path.join(os.path.dirname(__file__), 'style_demo/', 'style.css')))
    # ---- LOAD ASSETS ----
    lottie_main_json = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_87TU0lC9cJ.json")
    
    # ---- HEADER SECTION ----
    with st.container():
        st.subheader("Hi, I am ScholarPortrait~ :wave:")
        st.subheader("为您提供多维全面的科研学者画像")
        st.write(
            "我们聚焦于大数据技术以此来构建学者个人信息图谱的可视化系统..."
        )
        st.write("[Learn More >](https://space.bilibili.com/503176216?spm_id_from=333.1007.0.0)")

    # ---- WHAT I DO ----
    with st.container():
        st.write("---")
        left_column, right_column = st.columns(2)
        with left_column:
            st.header("What I do")
            st.write("##")
            st.write(
                """
                ScholarPortrait平台为您提供如下服务:
                - 科研学者人才画像构建与可视化.
                - 学者搜索与画像查看及合作对接.
                - 科研学者人才情报与分布地图.

                世界上有超过一亿不同领域的专家学者，我们帮您快速找到适合的人才，O(∩_∩)O.
                """
            )
            st.write("[Learn More >](https://onetozr-scholarportrait-app-v5bnwi.streamlit.app/)")
        with right_column:
            st_lottie(lottie_main_json,height=350)

    # ---- CONTACT ----
    with st.container():
        st.write("---")
        st.header("☎️Get In Touch With Me!")
        st.write("##")

        # Documention: https://formsubmit.co/ !!! CHANGE EMAIL ADDRESS !!!
        contact_form = """
        <form action="https://formsubmit.co/XDDEmbrace@163.COM" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="text" name="name" placeholder="Your name" required>
            <input type="email" name="email" placeholder="Your email" required>
            <textarea name="message" placeholder="Your message here" required></textarea>
            <button type="submit">Send</button>
        </form>
        """
        left_column, right_column = st.columns(2)
        with left_column:
            st.markdown(contact_form, unsafe_allow_html=True)
        with right_column:
            st.empty()

col1,col2,col3 = st.columns([1,2,1])
   
if selected_option == 'Create Account':
   with col2:
       register_user()
if selected_option == 'Forgot Password?':
   with col2:
       forgot_password()
if selected_option == 'Forgot Username?':
   with col2:
       forgot_username()
if selected_option == 'Reset Password':
   with col2:
       reset_password()      
if selected_option == 'Update User Details':
   with col2:
      update_user_details()

if selected_option == 'Login':
   with col2:
       login()       
   if st.session_state.authentication_status:   
       main()    
