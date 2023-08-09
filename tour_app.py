import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import gspread
from streamlit.components.v1 import html
import time

# 사용자 정의 함수들 import
from user_functions.Jeju_Femilesion_Festival import *

# 사이드바 접어놓기
st.set_page_config(initial_sidebar_state='collapsed')
with st.sidebar: Apply_CSS_Style() # CSS 스타일

try:
    # 구글 시트 DB연결 코드 : session_state를 사용하여 db를 cache에 놔두기 위함 : api호출 수 감소목적
    if 'google_sheet_initial' not in st.session_state:
        st.session_state['google_sheet_initial'] = False   
    if ('google_sheet' not in st.session_state) and (st.session_state['google_sheet_initial'] == False):
        url = "https://docs.google.com/spreadsheets/d/1XH6tveL3sTkwGjZLgsm9pCzZacd0b9VPVVX2FhuOVSw/edit#gid=1959638981"
        sheet_name = "홈페이지 DB"

        # 스프레드시트URL, 시트명으로 함수(시트 -> 데이터프레임) 호출하여 session_state에 할당
        st.session_state['google_sheet'] = SpreadSheet_to_Dataframe(url, sheet_name)
        st.session_state['google_sheet_initial'] = True 

    # session_state에서 df로 데이터 받아오기 : 세션스테이트를 두는 이유는 앱첫실행시 api를 한번만 호출하기 위함
    df = st.session_state['google_sheet']

    # 디자인 상단 이미지 호출하여 삽입
    image_path = './image/design.jpg'
    image = Image.open(image_path)
    st.image(image,use_column_width  = True)

    # 디자인 layout 나누기 : 좌우 여백 추가 left_blank = 7.5%, body = 85%, right_blank = 7.5% 
    side_gap = 0.75 ; body_gap = 10-2*side_gap
    left_blank, body, right_blank = st.columns([side_gap, body_gap ,side_gap])

    with left_blank : pass
    with right_blank: pass 
    with body:     
#         # 가이드북 링크 연결 박스
#         URL_Box(url = "https://sandy-ear-231.notion.site/Jeju-Femilesian-Festival-6a151c8c1eeb475ca1bc1d7557fbc4a2?pvs=4",
#                 color = "#F0A23D",
#                 fonts = "Hahmlet, Diphylleia",
#                 font_size = "1rem",
#                 lettering = "Tour 가이드북",
#                 letter_spacing =  '-0.13rem')


        # 검색창 : MultiSelect-Box = 하나 입력 시 dropdown이 닫히도록 설계    
        if 'name_list' not in st.session_state: st.session_state['name_list'] = list()
        name_list = st.multiselect('검색', list(df.index), placeholder="성함을 입력해주세요.", label_visibility='collapsed',\
                               default = st.session_state['name_list'], on_change = call_back)

        # 검색 흐름 제어 : 검색하면 처리하도록
        if len(name_list) > 0:        
            # 검색된 사람 별로 탭 나누기
            tabs= st.tabs(name_list) 
            for i, name in enumerate(name_list):
                with tabs[i]:
                    # 검색된 name을 가진 사람의 정보를 1행 DataFrame으로 만든 변수 : result
                    result = df[df.index == name]

                    # 1일차
                    with st.container():
                        # 첫째날 티켓 예외처리
                        dncc_to_cjj, boarding_time1, airline, boarding_time2, cju_to_room, boarding_time3, floor, room_num \
                        = First_Day_Exception_Handling(result)

                        # 첫째날 티켓테이블 출력
                        First_Day_Ticket(dncc_to_cjj, boarding_time1, airline, boarding_time2, cju_to_room, boarding_time3, floor, room_num)

                        # 첫째날, 동행 파트
                        with  st.expander("첫째 날, 동행", expanded = False):  
                            transports = [dncc_to_cjj, airline, cju_to_room, result['④숙소명 층/호수'].values[0]]
                            tab_name = ["교회-청주", "청주-제주", "공항-숙소","룸메이트"]
                            cols = df.columns[0:4]
                            together_tab(tab_name, transports, df, name, cols)                     

                    # 2일차
                    with st.container():
                        # 둘째날 테마별 티켓테이블 출력 : 둘째날은 예외없음
                        theme = result.loc[name,'⑤테마'] 
                        theme_bus = result['⑥테마별 버스'].values[0]
                        url = Second_Day_Ticket(result, theme, theme_bus)

                        # 둘째날, 동행 파트
                        with st.expander("둘째 날, 동행", expanded = False):  
                            transports = [theme, theme_bus]
                            tab_name = [f"테마여행", f"숙소-{theme}"]
                            cols = df.columns[4:6]
                            together_tab(tab_name, transports, df, name, cols) 
                            
#                             ## 테마활동 TIP 페이지 링크 연결 박스
#                             URL_Box(url =  url,
#                                    color = "#B57200",
#                                    fonts = "Nanum Pen Script, Diphylleia",
#                                    font_size = "1.2rem",
#                                    lettering = f"{theme} 테마 TIP",
#                                    letter_spacing = '0rem')
#                             st.write('')

                    # 3일차
                    with st.container():
                        # 셋째날 티켓 예외처리
                        group_tour_bus, group_tour_time, bus_to_cju, bus_to_cju_time, airline2, boarding_time4, bus_to_dncc, bus_to_dncc_time = \
                        Third_Day_Exception_Handling(result)

                        # 셋째날 티켓테이블 출력
                        Third_Day_Ticket(group_tour_bus, group_tour_time, bus_to_cju, bus_to_cju_time, \
                                         airline2, boarding_time4, bus_to_dncc, bus_to_dncc_time)

                        # 셋째날, 동행 파트
                        with  st.expander("셋째 날, 동행", expanded = False): 
                            transports = [group_tour_bus, bus_to_cju, airline2, bus_to_dncc]
                            tab_name = ["단체활동", "숙소-공항","제주-청주","청주-교회"]
                            cols = df.columns[6:]
                            together_tab(tab_name, transports, df, name, cols)

        # 검색 흐름 제어 : 검색하면 안하면 pass 처리하도록
        else : pass

    
except KeyError as e:
    st.warning("앱을 나갔다가 다시 실행시켜주세요!")
    st.write(e)
except Exception as e:#에러 시 
    st.write(e)


