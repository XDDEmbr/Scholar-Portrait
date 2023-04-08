import os
import yaml
import streamlit as st
import streamlit_authenticator as stauth
from utils.connect_db import init_connection


conn = init_connection() 
cur = conn.cursor()

auth_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'auth.yaml'))

def load_usernames(filename):
    with open(filename) as f:
        data = yaml.safe_load(f)
        usernames = data.get('credentials', {}).get('usernames', {})
        return [(username, values['email'], values['name'], values['password'])
                for username, values in usernames.items()]

def insert_users(users):
    for user in users:
        username, email, name, password = user
        cur.execute('SELECT COUNT(*) FROM UserInfo WHERE username=?', (username,))
        result = cur.fetchone()
        if result[0] == 0:
            cur.execute('INSERT INTO UserInfo (username, email, name, password) VALUES (?,?,?,?)', user)
    conn.commit()

users=load_usernames(auth_path)

def get_config():
    with open(auth_path,'r') as file:
        config = yaml.safe_load(file)
    return config
def update_config(config):
    with open(auth_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    return config
def get_authenticator():
    config = get_config()
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )
    return authenticator, config
authenticator, config = get_authenticator()

def login():
    insert_users(users)
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = False
    if st.session_state.authentication_status:
        authentication_status = st.session_state.authentication_status  
    name, authentication_status, username = authenticator.login('Login', 'main')
    st.session_state.authentication_status = authentication_status
    st.session_state['username'] = username

    if authentication_status == None:
        st.warning('Please enter your username and password!')
    elif authentication_status:
        st.balloons()
        st.sidebar.write('Welcome *%s*👋' % username)
        authenticator.logout('Logout', 'sidebar')
    elif authentication_status == False:
        st.error('Username or password is incorrect')
    return username

# 注册
def register_user():
    try:
        if authenticator.register_user('Register user','main', preauthorization=False):
            update_config(config)
            st.success('User registered successfully, please log in')
    except Exception as e:
        st.error(e)
# 忘记密码
def forgot_password():
    try:
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Forgot password','main')
        if username_forgot_pw:
            st.success('New password sent securely')
            # Random password to be transferred to user securely
        elif username_forgot_pw == False:
            st.error('Username not found')
    except Exception as e:
        st.error(e)
# 忘记用户名
def forgot_username():
    try:
        username_forgot_username, email_forgot_username = authenticator.forgot_username('Forgot username','main')
        if username_forgot_username:
            st.success('Username sent securely')
            # Username to be transferred to user securely
        else:
            st.error('Email not found')
    except Exception as e:
        st.error(e)  
# 重置密码
def reset_password():
    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        try:
            if authenticator.reset_password(username, 'Reset password','main'):
                update_config(config)
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)
# 更新用户详细信息
def update_user_details():
    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        try:
            if authenticator.update_user_details(username, 'Update user details','main'):
                update_config(config)
                st.success('Entries updated successfully')
        except Exception as e:
            st.error(e)
def login_warning():
    """Shows a message as user warning."""
    st.markdown('''
    Please first **Log in** to view the contents of this page.
    ''')

