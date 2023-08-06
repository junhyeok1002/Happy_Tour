import pandas as pd
import numpy as np
import streamlit as st
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from PIL import Image
import gspread

# # 로컬 DB연결용 코드
# # XLS 파일 읽기
# df = pd.read_excel('./data/제주수양회 총괄시트.xlsx', sheet_name='홈페이지 DB',index_col = 0 )
# # 바뀐 엑셀 형식에 맞추어 전처리
# df = df.T.set_index('#').T.set_index('이름')


# 구글 시트 DB연결 코드
# session_state를 사용하여 앱로딩시 db를 전부호출하여 cache에 놔두기 위함 : api호출수를 많이 줄일 수 있음
if 'google_sheet' not in st.session_state:
    # API-KEY SECRET처리
    credentials = {
      "type": st.secrets["type"],
      "project_id":  st.secrets["project_id"],
      "private_key_id":  st.secrets["private_key_id"],
      "private_key":  st.secrets["private_key"],
      "client_email":  st.secrets["client_email"],
      "client_id":  st.secrets["client_id"],
      "auth_uri":  st.secrets["auth_uri"],
      "token_uri":  st.secrets["token_uri"],
      "auth_provider_x509_cert_url":  st.secrets["auth_provider_x509_cert_url"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url"],
      "universe_domain": st.secrets["universe_domain"],
    }

    gc = gspread.service_account_from_dict(credentials)
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1XH6tveL3sTkwGjZLgsm9pCzZacd0b9VPVVX2FhuOVSw/edit#gid=1959638981"
    doc = gc.open_by_url(spreadsheet_url)
    worksheet = doc.worksheet("홈페이지 DB")

    # 시트 데이터를 가져오기
    data = worksheet.get_all_values()

    df = pd.DataFrame(data[2:], columns=data[1])
    df.drop(columns='#', inplace=True)
    df.set_index('이름', inplace=True)
    st.session_state['google_sheet'] = df

# 이름 목록
df = st.session_state['google_sheet']
names = list(df.index)

# 디자인 이미지 호출하여 삽입
image_path = './image/design.jpg'
image = Image.open(image_path)
st.image(image,use_column_width  = True)# caption='Sunrise by the mountains')

# 디자인 이미지 layout에 맞게 좌우 여백 추가 7.5%, 85%, 7.5% 
side_gap = 0.75
body_gap = 10-2*side_gap

# C1: left blank, C2: body, C3: right blank
C1, C2, C3 = st.columns([side_gap, body_gap ,side_gap])
with C1: pass # C1: left blank
with C3: pass # C3: right blank
with C2:            #C2: body
    
    # 가이드북
    url = "https://sandy-ear-231.notion.site/Jeju-Femilesian-Festival-6a151c8c1eeb475ca1bc1d7557fbc4a2?pvs=4"
    st.markdown(
    f"""
    <div style="padding: 0px 0px 8px 0px;">
        <a href="{url}" target="_blank" rel="noopener noreferrer">
            <div style="
                width :100%;
                font-family:Hahmlet, Diphylleia;
                display: inline-block;
                padding: 0.3rem;
                color: #F0A23D;
                background-color: #ffffff;
                border-radius: 0.5rem;
                letter-spacing: -0.13rem;
                border: 0.07rem solid #F0A23D;
                text-decoration: none;
                text-align: center;
                font-weight: bold;">
                Tour 가이드북
            </div>
        </a>
    </div>
    """,
    unsafe_allow_html=True)  
    

#     hidden = """
#     <style>
#     div[data-baseweb="popover"]{
#       visibility: hidden;
#     }"""

#     visible = """
#     <style>
#     div[data-baseweb="popover"]{
#       visibility: visible;
#     }"""
#     option = hidden
#     st.markdown(hidden, unsafe_allow_html=True)  
        

    
    # 멀티셀렉트 박스
    name_list = st.multiselect('검색',names, placeholder = "성함을 입력해주세요.", label_visibility = 'collapsed')

    # 초기 흐름 제어 : 검색하면 처리하도록
    if len(name_list) > 0:
        
        # 띄어쓰기 처리
        name_list = [name.replace(" ","") for name in name_list] 
        
        # 탭 나누기
        tabs= st.tabs(name_list)
        for i, name in enumerate(name_list):
            with tabs[i]:
                # 이름에 오타가 났을때 db저장된 이름과 유사도를 확인하여 찾으시는 이름을 제시해주는 코드 
                # multiselect search 방식을 바꾸면서 아래의 if문 블럭은 현재 필요없는 코드임
                if (name not in df.index) or (list(df.index).count(name) > 1) : #이름이 DB목록에 없을 경우 발동
                    # 유사한 결과 찾기
                    matches = process.extract(name, names, scorer=fuzz.token_set_ratio, limit=500)

                    # 뒤의 숫자가 0인 요소 제거 후 내림차순으로 정렬하여 연관도 Top 5만 선정
                    matches = [(name, score) for name, score in matches if score != 0]
                    matches = sorted(matches, key=lambda x: x[1], reverse=True)[:5]
                    matches_list = [name for name, score in matches]

                    wrong_name = name[:]
                    name = st.radio(f"찾으시는 성함을 클릭해주세요. 아래에도 없을 경우 이주노 전도사님께 문의부탁드립니다", matches_list)
                
                # 검색된 name을 가진 사람의 정보를 1행 DataFrame으로 만든 변수 : result
                result = df[df.index == name]
                
              
                # 아래 대형 공사중 : metric 사용하지 않고, html/css로 디자인하기
                # st.markdown('<div class="rounded-text-box"> 아래 부분 디자인 갈아 엎는중, 글짜 크기키우기, 배치 디자인 다시, 이모지 너무 유치해보이는데 고급스럽게 바꿀 방법찾기, 등등.... </div>', unsafe_allow_html=True)
                

                with st.container():
                    # ①교회-청주공항 버스 : 개인이동, 선발대 처리
                    if result['①교회-청주공항 버스'].values[0] in ('개인이동','선발대'): boarding_time1 = "-"
                    else : boarding_time1 = "오후 2:30"

                    # ②청주-제주 비행기 : 비행기 시간 처리
                    info_air = result['②청주-제주 비행기'].values[0].replace("pm"," ")
                    try:
                        day, airline, time = info_air.split()
                        if day != '13일' : boarding_time2 = f'{day} {time}'
                        elif int(time[:2]) < 12: boarding_time2 = f'오전 {time}'
                        elif int(time[:2]) == 12: boarding_time2 = f'오후 {time}'
                        elif int(time[:2]) > 12: boarding_time2 = f'오후 {int(time[:2])-12}:{time[3:5]}'

                    except :
                        airline = info_air
                        boarding_time2 = "-"

                    # ③제주공항-숙소 : 버스 개인이동 수양관   
                    if result['③제주공항-숙소 버스'].values[0] in ('개인이동','수양관'): boarding_time3 = "-"
                    else : boarding_time3 = "오후 7:00"                        


                    st.markdown(f"""
                    <table class = "first-day">
                      <tr style="color:#F0A23D ;background-color: white ;border-top: 0.3rem solid #F0A23D;font-family:Diphylleia;border-right : 0.2rem solid #F0F2F6;">
                        <th colspan="4"><span class="custom-ticket-font" style="font-size:1rem;letter-spacing: -0.13rem;">Day 1, 08/13 주일</span></th>
                      </tr>
                      <tr>
                        <td><span class="custom-ticket-font">대전</span><br>
                            <span class="custom-ticket-small-font1">DNCC</span></td>
                        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F68C;</p><br>
                            <p class="symbola-emoji" style = "font-size:1.2rem;">&#8594;</p></td>
                        <td><span class="custom-ticket-font">청주공항</span><br>
                            <span class="custom-ticket-small-font1">CJJ</span></td>
                        <td><span class="custom-ticket-font" style="color: #F0A23D;">{result['①교회-청주공항 버스'].values[0]}</span><br>
                            <span class="custom-ticket-small-font1" style="color: black;">{boarding_time1}</span></td>
                      </tr>
                      <tr>
                        <td><span class="custom-ticket-font">청주공항</span><br>
                            <span class="custom-ticket-small-font1">CJJ</span></td>
                        <td ><p class="symbola-emoji" style = "font-size:1.4rem;"><br>&#x2708;</p><br>
                            <p class="symbola-emoji" style = "font-size:1.2rem;">&#8594;</p></td> 
                        <td><span class="custom-ticket-font">제주공항</span><br>
                            <span class="custom-ticket-small-font1">CJU</span></td>
                        <td><span class="custom-ticket-font" style="color: #F0A23D;">{airline}</span><br>
                            <span class="custom-ticket-small-font1" style="color: black;">{boarding_time2}</span></td>
                      </tr>                              
                      <tr>
                        <td><span class="custom-ticket-font">제주공항</span><br>
                            <span class="custom-ticket-small-font1">CJU</span></td>
                        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F68C;</p><br>
                            <p class="symbola-emoji" style = "font-size:1.2rem;">&#8594;</p></td>
                        <td><span class="custom-ticket-font">식당/숙소</span><br>
                            <span class="custom-ticket-small-font1"  style="letter-spacing: -0.05rem;">MEAL/ROOM</span></td>
                        <td><span class="custom-ticket-font" style="color: #F0A23D;">{result['③제주공항-숙소 버스'].values[0]}</span><br>
                            <span class="custom-ticket-small-font1" style="color: black;">{boarding_time3}</span></td>
                      </tr>                              
                      <tr>
                        <td><span class="custom-ticket-font">숙소</span><br>
                            <span class="custom-ticket-small-font1">ROOM</span></td>
                        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F3E0;</p><br>
                            <span class="custom-ticket-small-font1" style="color:black; letter-spacing: -0.13rem;">{result['④숙소명 층/호수'].values[0].split()[1]}</span></td>                                
                        <td><span class="custom-ticket-font">방 번호</span><br>
                            <span class="custom-ticket-small-font1">NO.</span></td>
                        <td><span class="custom-ticket-font" style="color: #F0A23D;font-size: 0.9rem;">{result['④숙소명 층/호수'].values[0].split()[0]}</span><br>
                            <span class="custom-ticket-small-font1" style="font-size: 0.8rem; color: black;">{result['④숙소명 층/호수'].values[0].split()[1]}</span></td>
                      </tr>                          
                    </table>
                    """, unsafe_allow_html=True)
                    
                    
                    with  st.expander("첫째 날, 동행", expanded = False):  
                        transports = [result['①교회-청주공항 버스'].values[0], airline, \
                                      result['③제주공항-숙소 버스'].values[0],result['④숙소명 층/호수'].values[0] ]
                        tab_name = ["교회-청주", "청주-제주", "공항-숙소","룸메이트"]
                        for i, tab in enumerate(st.tabs(tab_name)):
                            with tab:
                                st.markdown(f'<span class="name-font" style="font-size:1.5rem;">{tab_name[i]}, {transports[i]} 명단</span>', unsafe_allow_html=True)
                                mine = result.loc[name,df.columns[i]]
                                data_list = list(df[df[df.columns[i]] == mine].index)

                                n = 4  # 열 개수 (n) 설정
                                loop = int(str(n-len(data_list)%n))
                                for j in range(loop): data_list.append("")
                                    
                                sum_text = '' #HTML 텍스트 누적용
                                temp = list() # 임시 리스드 생성
                                for temp_name in data_list:
                                    temp.append(temp_name)
                                    if len(temp) == n:
                                        temp_text = f'''<tr>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[0]}</span></label></td>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[1]}</span></label></td>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[2]}</span></label></td>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[3]}</span></label></td>
                                        </tr>'''
                                        
                                        sum_text += temp_text
                                        temp = list()
                                  
                                st.markdown(f"""
                                <table class = "name" style="table-layout: fixed;border: 0rem solid #ffffff;border-top : 0.2rem solid #F0F2F6;">
                                  {sum_text}
                                </table>
                                """, unsafe_allow_html=True)
                                st.write("")
                            
                            
                            
                            
                            
                    
                
                # 2일차
                theme_url = {'물놀이' : ['https://sandy-ear-231.notion.site/c8730b2e5d2f4636962550f876747bee?pvs=4',"오후 05:00"],
                             '액티비티' : ['https://sandy-ear-231.notion.site/92670ed2db424e8089bb93d68eed64d4?pvs=4',"오후 05:30"],
                             '인생샷' : ['https://sandy-ear-231.notion.site/9ca017fc6f9c40f1badab4192e2ce4a1?pvs=4',"오후 05:20"],
                             '자연' : ['https://sandy-ear-231.notion.site/6a061529159d467587eab7a90d2c1896?pvs=4',"오후 05:00"],
                             '힐링' : ['https://sandy-ear-231.notion.site/becd45dddbee435aacecf49ba776a8ed?pvs=4',"오후 05:30"],
                             '의전' : ['http://www.sja21.com/main/main.html',"-"]
                            }

                theme = result.loc[name,'⑤테마']                    
                url = theme_url[theme][0]

                with st.container():
                    st.markdown(f"""
                    <table class = "second-day">
                      <tr style="color:#B57200 ;background-color: white ;border-top: 0.3rem solid #B57200;font-family:Diphylleia;border-right : 0.2rem solid #F0F2F6;">
                        <th colspan="4"><span class="custom-ticket-font" style="font-size:1rem;letter-spacing: -0.13rem;">Day 2, 08/14 월요일</span></th>
                      </tr>                        
                      <tr>
                        <td><span class="custom-ticket-font">숙소</span><br>
                            <span class="custom-ticket-small-font2">ROOM</span></td>
                        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F68C;</p><br>
                            <p class="symbola-emoji" style = "font-size:1.2rem;">&#x21C4;</p></td>
                        <td><span class="custom-ticket-font">{theme}</span><br>
                            <span class="custom-ticket-small-font2">THEME</span></td>
                        <td><span class="custom-ticket-font" style="color: #B57200;">{result['⑥테마별 버스'].values[0]}</span><br>
                            <span class="custom-ticket-small-font2" style="color: black;">오후 12:00<br>{theme_url[theme][1]}</span></td>
                      </tr>                           
                    </table> 
                    """, unsafe_allow_html=True)
                    
                      
            
                    with st.expander("둘째 날, 동행", expanded = False):  
                        transports = [result['⑤테마'].values[0], result['⑥테마별 버스'].values[0]]
                        tab_name = [f"테마여행", f"숙소-{theme}"]
                        for i, tab in enumerate(st.tabs(tab_name)):
                            with tab:
                                st.markdown(f'<span class="name-font" style="font-size:1.5rem;">{tab_name[i]}, {transports[i]} 명단</span>', unsafe_allow_html=True)
                                mine = result.loc[name,df.columns[i+4]]
                                data_list = list(df[df[df.columns[i+4]] == mine].index)

                                n = 4  # 열 개수 (n) 설정
                                loop = int(str(n-len(data_list)%n))
                                for j in range(loop): data_list.append("")
                                    
                                sum_text = '' #HTML 텍스트 누적용
                                temp = list() # 임시 리스드 생성
                                for temp_name in data_list:
                                    temp.append(temp_name)
                                    if len(temp) == n:
                                        temp_text = f'''<tr>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[0]}</span></label></td>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[1]}</span></label></td>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[2]}</span></label></td>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[3]}</span></label></td>
                                        </tr>'''
                                        sum_text += temp_text
                                        temp = list()
                                        
                                st.markdown(f"""
                                <table class = "name" style="table-layout: fixed;border: 0rem solid #ffffff;border-top : 0.2rem solid #F0F2F6;">
                                  {sum_text}
                                </table>
                                """, unsafe_allow_html=True)
                                st.write("")
                        
                        st.markdown(
                        f"""
                        <div style="padding: 0px 0px 0px 0px;">
                            <a href="{url}" target="_blank" rel="noopener noreferrer">
                                <div style="
                                    width :100%;
                                    display: inline-block;
                                    padding: 0.1rem;
                                    color: #B57200;
                                    font-family:Nanum Pen Script, Diphylleia;
                                    font-size: 1.2rem;
                                    background-color: #ffffff;
                                    border-radius: 0.5rem;
                                    border: 0.07rem solid #B57200;
                                    text-decoration: none;
                                    text-align: center;
                                    font-weight: bold;">
                                    {theme} 테마 TIP
                                </div>
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True)      
                        st.write('')
                        

                    
                # 3일차
                with st.container():
                    bus_to_cju = result['⑦단체활동 버스'].values[0]
                    bus_to_cju_time = '오후 6:30'

                    # ⑧제주-청주 비행기 : 비행기 시간 처리
                    info_air2 = result['⑧제주-청주 비행기'].values[0].replace("pm"," ")

                    try:
                        day2, airline2, time2 = info_air2.split()  
                        boarding_time4 = f'오후 {int(time2[:2])-12}:{time2[3:5]}'

                    except :
                        airline2 = info_air2
                        boarding_time4 = "-"
                        bus_to_cju = info_air2
                        bus_to_cju_time = '-'

                    #
                    bus_to_dncc_time = '-'
                    if result['⑨청주공항-교회 버스'].values[0] =='개인이동' : bus_to_dncc_time = '-'
                    elif airline2 in ('아시아나'):bus_to_dncc_time = '오후 10:00'
                    elif airline2 in ('이스타','진에어'):bus_to_dncc_time = '오후 11:00'

                    st.markdown(f"""
                    <table class = "third-day">
                      <tr style="color:#8B4600 ;background-color: white ;border-top: 0.3rem solid #8B4600;font-family:Diphylleia;border-right : 0.2rem solid #F0F2F6;">
                        <th colspan="4"><span class="custom-ticket-font" style="font-size:1rem;letter-spacing: -0.12rem;">Day 3, 08/15 화요일</span></th>
                      </tr>                       
                      <tr>
                        <td><span class="custom-ticket-font">숙소</span><br>
                            <span class="custom-ticket-small-font3">ROOM</span></td>
                        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F68C;</p><br>
                            <p class="symbola-emoji" style = "font-size:1.2rem;">&#x21C4;</p></td>
                        <td><span class="custom-ticket-font">단체관광</span><br>
                            <span class="custom-ticket-small-font3">TOUR</span></td>
                        <td><span class="custom-ticket-font" style="color: #8B4600;">{result['⑦단체활동 버스'].values[0]}</span><br>
                            <span class="custom-ticket-small-font3" style="color: black;">오후 12:00</span></td>
                      </tr>
                      <tr>
                        <td><span class="custom-ticket-font">숙소</span><br>
                            <span class="custom-ticket-small-font3">ROOM</span></td>
                        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F68C;</p><br>
                            <p class="symbola-emoji" style = "font-size:1.2rem;">&#8594;</p></td>
                        <td><span class="custom-ticket-font">제주공항</span><br>
                            <span class="custom-ticket-small-font3">CJU</span></td>
                        <td><span class="custom-ticket-font" style="color: #8B4600;">{bus_to_cju}</span><br>
                            <span class="custom-ticket-small-font3" style="color: black;">{bus_to_cju_time}</span></td>
                      </tr>                              
                      <tr>
                        <td><span class="custom-ticket-font">제주공항</span><br>
                            <span class="custom-ticket-small-font3">CJU</span></td>
                        <td ><p class="symbola-emoji" style = "font-size:1.4rem;"><br>&#x2708;</p><br>
                            <p class="symbola-emoji" style = "font-size:1.2rem;">&#8594;</p></td>                                
                        <td><span class="custom-ticket-font">청주공항</span><br>
                            <span class="custom-ticket-small-font3">CJJ</span></td>
                        <td><span class="custom-ticket-font" style="color: #8B4600;">{airline2}</span><br>
                            <span class="custom-ticket-small-font3" style="color: black;">{boarding_time4}</span></td>
                      </tr>                              
                      <tr>
                        <td><span class="custom-ticket-font">청주공항</span><br>
                            <span class="custom-ticket-small-font3">CJJ</span></td>
                        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F68C;</p><br>
                            <p class="symbola-emoji" style = "font-size:1.2rem;">&#8594;</p></td>
                        <td><span class="custom-ticket-font">대전</span><br>
                            <span class="custom-ticket-small-font3">DNCC</span></td>
                        <td><span class="custom-ticket-font" style="color: #8B4600;">{result['⑨청주공항-교회 버스'].values[0]}</span><br>
                            <span class="custom-ticket-small-font3" style="color: black;">{bus_to_dncc_time}</span></td>
                      </tr>                           
                    </table>
                    """, unsafe_allow_html=True)

                    with  st.expander("셋째 날, 동행", expanded = False): 
                        transports = [result['⑦단체활동 버스'].values[0],bus_to_cju, airline2 ,result['⑨청주공항-교회 버스'].values[0]]
                        tab_name = ["단체활동", "숙소-공항","제주-청주","청주-교회"]
                        idx = [6,6.5,7,8]
                        for i, tab in enumerate(st.tabs(tab_name)):
                            with tab:
                                st.markdown(f'<span class="name-font" style="font-size:1.5rem;">{tab_name[i]}, {transports[i]} 명단</span>', unsafe_allow_html=True)
                                
                                
                                if idx[i] ==6.5 and result.loc[name,df.columns[idx[2]]] == '개별': i = 2
                                elif  idx[i] ==6.5 and result.loc[name,df.columns[idx[2]]] != '개별': i = 0
                                    
                                mine = result.loc[name,df.columns[idx[i]]]
                                data_list = list(df[df[df.columns[idx[i]]] == mine].index)
                                
                                
                                
                                n = 4  # 열 개수 (n) 설정
                                loop = int(str(n-len(data_list)%n))
                                for j in range(loop): data_list.append("")
                                    
                                sum_text = '' #HTML 텍스트 누적용
                                temp = list() # 임시 리스드 생성
                                for temp_name in data_list:
                                    temp.append(temp_name)
                                    if len(temp) == n:
                                        temp_text = f'''<tr>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[0]}</span></label></td>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[1]}</span></label></td>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[2]}</span></label></td>
                                        <td><label class="clickable-text"><input type="checkbox"><span>{temp[3]}</span></label></td>
                                        </tr>'''                                        
                                        sum_text += temp_text
                                        temp = list()
                                        
                                st.markdown(f"""
                                <table class = "name" style="table-layout: fixed;border: 0rem solid #ffffff;border-top : 0.2rem solid #F0F2F6;">
                                  {sum_text}
                                </table>
                                """, unsafe_allow_html=True)
                                st.write("")                        
    else :
        pass


# HTML에 CSS-STYLE 지정
with open('style.css', encoding = "utf-8")as f:
    style = f.read()
st.markdown(f"<style>{style}</style>", unsafe_allow_html = True)


# 필요 없지만 언제 쓸지 모르는 코드
# multibox_control
# multibox_blank_case = """
# <style>
# div[class="row-widget stMultiSelect"]:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2){
#     visibility: hidden;
# }
# div[class="row-widget stMultiSelect"]:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2):before {
#     content: "성함을 입력해주세요."; visibility: visible;
# }    
# </style>
# """    
# st.markdown(multibox_blank_case, unsafe_allow_html=True)