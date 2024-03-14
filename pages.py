import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import folium
import json
import time
from matplotlib.cm import get_cmap

# Get the 'tab10' colormap
tab10 = get_cmap('tab10')

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
    df = pd.DataFrame(data)
    
    # 한국어가 깨져서 영어로 바꿔줌
    df['문화종류'] = df['문화종류'].map({'연극': 'Play', '어린이/가족': 'Kids/Family', '퍼포먼스': 'Performance'})
    
    # '문화종류' 열의 값 별 빈도수 계산 후 데이터프레임으로 변환
    df_count = df['문화종류'].value_counts().reset_index()
    df_count.columns = ['문화종류', '빈도']

    # 시각화 함수(막대, 원그래프)
    def plot_bar_chart(df):
        fig, ax = plt.subplots()
        ax.bar(df['문화종류'], df['빈도'], color=['turquoise', 'limegreen', 'gold', 'hotpink', 'cyan'])
        ax.set_xlabel('Culture Type')
        ax.set_ylabel('Frequency')
        ax.set_title('Frequency of Culture Types (Bar Chart)')
        st.pyplot(fig)

    def plot_pie_chart(df):
        fig, ax = plt.subplots()
        ax.pie(df['빈도'], labels=df['문화종류'], autopct='%1.1f%%')
        ax.set_title('Frequency of Culture Types (Pie Chart)')
        st.pyplot(fig)

    # 인터페이스
    st.title('장르별 데이터 빈도 시각화')
    st.write('막대 그래프와 원 그래프로 데이터를 시각화합니다.')
    st.divider()

    # 시각화 종류 선택
    visualization_option = st.selectbox('시각화 종류 선택', ['막대 그래프', '원 그래프'])

    # 선택에 따라 시각화
    if visualization_option == '막대 그래프':
        plot_bar_chart(df_count)
    elif visualization_option == '원 그래프':
        plot_pie_chart(df_count)
    
    
    
def runtime():
    st.title("러닝타임별 데이터 빈도 시각화")
    st.write('막대 그래프로 데이터를 시각화합니다.')
    st.divider()
    # 데이터프레임(data)의 '시간' 열에서 값의 빈도
    b = data['시간'].value_counts()

    # '90분' -> 90
    b.index = b.index.str.replace('분', '').astype(int)

    # 30기준으로 묶기
    b_grouped = b.groupby(pd.cut(b.index, bins=range(0, max(b.index) + 30, 30))).sum()

    # 색상 설정
    colors = [tab10.colors[i % 10] for i in range(len(b_grouped))]

    # 그래프 그리기
    fig, ax = plt.subplots()
    ax.set_title('running time')  # 그래프 제목 설정
    ax.set_xlabel('Running Time (minutes)')  # x축 레이블 설정
    ax.set_ylabel('Number of Performances')  # y축 레이블 설정
    ax.bar(b_grouped.index.astype(str), b_grouped, color=colors)
    plt.xticks(range(0, len(b_grouped.index), 2), [str(i.right) for i in b_grouped.index][::2])  # 2 단위로 레이블 표시
    st.pyplot(fig)

    
def sido():
    st.title("지역별 공연 극장 분포")
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
