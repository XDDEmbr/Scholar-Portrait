import importlib
import streamlit as st
from geopy.geocoders import Nominatim
from utils.connect_db import init_connection 


class QueryExecutor:
    def __init__(self):
        self.conn = init_connection()
        self.cur = self.conn.cursor()
        self.user_id = self.get_user_id()
        self.scholar_id = self.get_scholar_id()

    
    def get_user_id(self):
        username = st.session_state['username']
        # 查询UserInfo表获取
        self.cur.execute('SELECT user_id FROM UserInfo WHERE username=?', (username,))
        user_id = self.cur.fetchone()
        if user_id is not None:
            user_id = user_id[0]
        return user_id


    def get_scholar_id(self):      
        user_id = self.user_id 
        # 查询Scholar表获取scholar_id
        self.cur.execute('SELECT scholar_id FROM Scholar WHERE user_id=?', (user_id,))
        scholar_id = self.cur.fetchone()
        if scholar_id is not None:
            scholar_id = scholar_id[0]
        return scholar_id
    
    def is_claim(self):
        user_id = self.user_id 
        self.cur.execute('SELECT COUNT(*) FROM Scholar WHERE user_id = ?',(user_id,)) 
        result = self.cur.fetchone()[0]
        if result > 0:
            is_claim = True
        else:
            is_claim = True
        return is_claim

    # 查询兴趣
    def get_interest(self):
        query = 'SELECT interest_name FROM InterestInfo'
        self.cur.execute(query)
        interests = [row[0] for row in self.cur.fetchall()] 
        return interests
        
    # 插入基本信息
    def insert_scholar(self,id,name,gender,title,institution,department,mail,homepage,photo):    
        user_id = self.user_id     
        insert = 'INSERT INTO Scholar (scholar_id,scholar_name,scholar_gender,scholar_title,scholar_institution,scholar_department,scholar_email,scholar_homepage,scholar_photo,user_id) VALUES (?,?,?,?,?,?,?,?,?,?)'
        params = (id,name,gender,title,institution,department,mail,homepage,photo, user_id)
        self.cur.execute(insert,params)
        self.conn.commit()

    # 插入研究兴趣
    def insert_interest(self,interest_name):       
        select = 'SELECT interest_id FROM InterestInfo WHERE interest_name = ?'
        self.cur.execute(select, (interest_name,))
        result = self.cur.fetchone()
        if result is not None:
            interest_id = result[0]
            insert = 'INSERT INTO Interest (interest_id, interest_name, scholar_id) VALUES(?,?,?)'
            params = (interest_id, interest_name, self.scholar_id)
            self.cur.execute(insert, params)
            self.conn.commit()
    
    # 插入个人简介
    def insert_scholar_bio(self,scholar_bio):       
        insert = 'UPDATE Scholar SET scholar_bio = ? WHERE scholar_id = ?'
        params = (scholar_bio,self.scholar_id)
        self.cur.execute(insert,params)
        self.conn.commit()  

    # 插入教育背景
    def insert_education(self,school,major,degree,degree_category,education_st_year,education_end_year):
        insert = 'INSERT INTO Education (scholar_id,school,major,degree,degree_category,education_st_year,education_end_year) VALUES(?,?,?,?,?,?,?)'
        params = (self.scholar_id,school,major,degree,degree_category,education_st_year,education_end_year)
        self.cur.execute(insert,params)
        self.conn.commit()
    

        # 将地址转换为经纬度
    def get_latitude_longitude(address):
        """
        将地址信息转换为经纬度
        :param address: 地址信息
        :return: 经纬度
        """
        geolocator = Nominatim(user_agent="Scholar_career_trajectory")
        location = geolocator.geocode(address)
        if location is not None:
            latitude = location.latitude
            longitude = location.longitude
        else:
            latitude, longitude = None, None
        return latitude, longitude

                  
    # 插入工作经历
    def insert_experience(self,exp_title,exp_institution,exp_department,exp_st_year,exp_end_year,address,longitude,latitude):
        insert = 'INSERT INTO Experience (scholar_id,experience_title,experience_institution,experience_department,experience_st_year,experience_end_year,address,longitude,latitude) VALUES(?,?,?,?,?,?,?,?,?)'
        params = (self.scholar_id,exp_title,exp_institution,exp_department,exp_st_year,exp_end_year,address,longitude,latitude)
        self.cur.execute(insert,params)
        self.conn.commit()


    # 插入获奖信息
    def insert_award(self,award_title,award_year,award_sponsor,award_discribe):
        insert = 'INSERT INTO Award (scholar_id,award_title,award_year,award_sponsor,award_discribe) VALUES(?,?,?,?,?)'
        params = (self.scholar_id,award_title,award_year,award_sponsor,award_discribe)
        self.cur.execute(insert,params)
        self.conn.commit()
  

    # 插入基金信息
    def insert_fund(self,fund_title,fund_year,fund_sponsor,fund_amount):
        insert = 'INSERT INTO Fund (scholar_id,fund_title,fund_year,fund_sponsor,fund_amount) VALUES(?,?,?,?,?)'
        params = (self.scholar_id,fund_title,fund_year,fund_sponsor,fund_amount)
        self.cur.execute(insert,params)
        self.conn.commit()
   

    # 插入出版物信息
    def insert_publication(self,pub_title,pub_year,pub_type,journal,publisher,coauthors,doi,abstract,link):
        insert = 'INSERT INTO Publication (scholar_id,publication_title,publication_year,publication_type,journal,publisher,coauthors,doi,abstract,link) VALUES(?,?,?,?,?,?,?,?,?,?)'
        params = (self.scholar_id,pub_title,pub_year,pub_type,journal,publisher,coauthors,doi,abstract,link)
        self.cur.execute(insert,params)
        self.conn.commit()
  







