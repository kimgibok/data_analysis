import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pages import *



if 'page' not in st.session_state:
    st.session_state['page'] = 'HOME'

menus={'HOME':home, '시기별':period,'연령별':age, '지역별':sido}

with st.sidebar:
    for menu in menus.keys():
        if st.button(menu, use_container_width=True, type='primary' if st.session_state['page']==menu else 'secondary'):
            st.session_state['page']=menu
            st.rerun()

for menu in menus.keys():
    if st.session_state['page']==menu:
        menus[menu]()