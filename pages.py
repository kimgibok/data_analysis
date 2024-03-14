import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import json
import time

# data load
@st.cache_data
def load_data():
    data = pd.read_csv("한국문화정보원_전국 연극장 및 소극장 데이터_20221130.CSV", encoding='cp949')
    return data

data = load_data()

def stream_data(data):
    for word in data.split():
        yield word + " "
        time.sleep(0.1)

def home():
    st.title("전국 연극장 및 소극장 데이터 분석")
    st.divider()
    st.dataframe(data, width=700, height=400)
    APP_SUB_TITLE = '전국 연극장 및 소극장 데이터_20221130.CSV'
    st.caption(APP_SUB_TITLE)
    st.info("2015년부터 2022년 데이터입니다")
    txt = "위 데이터를 기반으로 데이터들을 여러 분야 별로 시각화하여 분석하였습니다."
    st.write_stream(stream_data(txt))
    
    
def play_type():
    st.title("종류별")
    
    
    
def age():
    st.title("연령별")
    
    
    
def sido():
    st.title("공연 극장 분포")
    st.markdown("---") 
    # 전국데이터
    data
    # 서울데이터
    data_seoul = data[data['시도 명칭'] == '서울특별시']

    # 명칭 빈도수세기
    a= data['시도 명칭'].value_counts()
    b= data_seoul['시군구 명칭'].value_counts()

    # 사이드바: 지도종류, 지역선택
    tiles = ['OpenStreetMap', 'CartoDB positron', 'CartoDB dark_matter']
    with st.sidebar:
        st.divider()
        t = st.sidebar.radio('Map', tiles)
        m = st.selectbox('지역 선택', ('전국', '서울특별시'))
        
    if m == '전국':
        st.subheader("전국 공연 극장 분포")
        data_for_map = a
        geodata='SIDO_MAP_2022_cp949.json'
        key_on='feature.properties.CTP_KOR_NM'
        location=[36.194012, 127.5019596]
        zoom_start=7
    elif m == '서울특별시':
        st.subheader("서울 공연 극장 분포")
        data_for_map = b
        with open('seoul_municipalities_geo.json', 'r', encoding='utf-8') as f:
            geodata = json.load(f)
        key_on='feature.properties.SIG_KOR_NM'
        location=[37.5665, 126.9780]
        zoom_start=11
        
    # 지도 그리기
    map = folium.Map(location=location, zoom_start=zoom_start, scrollWheelZoom=True, tiles=t)
    choropleth = folium.Choropleth(
        geo_data=geodata,
        data=data_for_map,
        columns=[data_for_map.index, data_for_map.values],
        key_on=key_on,
        fill_color='BuPu',
        fill_opacity=0.8,
        line_opacity=0.2,
        highlight=True,
        # bins=253  # 조절 값
        bins=[10**i for i in range(5)]  # 값의 격차가 너무 커 로그스케일로 조절
    )
    choropleth.geojson.add_to(map)
    

    st_map = st_folium(map, width=600, height=700)
