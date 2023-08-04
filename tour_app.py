import pandas as pd
import numpy as np
import streamlit as st
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from PIL import Image


# XLS 파일 읽기
df = pd.read_excel('./data/제주수양회 총괄시트.xlsx', sheet_name='홈페이지 DB',index_col = 0 )
# test =  pd.read_excel('./data/행복투어 샘플.xls',index_col = 0 )

# 바뀐 엑셀 형식에 맞추어 전처리
df = df.T.set_index('#').T.set_index('이름')

# 이름 목록
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
    
    # 멀티셀렉트 박스
    # multibox_control
    multibox_blank_case = """
    <style>
    div[class="row-widget stMultiSelect"]:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2){
        visibility: hidden;
    }
    div[class="row-widget stMultiSelect"]:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2):before {
        content: "성함을 입력해주세요."; visibility: visible;
    }    
    </style>
    """    
    
    name_list = st.multiselect('검색',\
                               names,max_selections=None,label_visibility = 'collapsed')

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
                        tab_name = ["교회-청주공항", "청주-제주공항", "제주공항-숙소","숙소 룸메이트"]
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
                                        temp_text = f'<tr><td>{temp[0]}</td><td>{temp[1]}</td><td>{temp[2]}</td><td>{temp[3]}</td></tr>'
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
                        tab_name = [f"테마여행", f"숙소-{theme} 장소"]
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
                                        temp_text = f'<tr><td>{temp[0]}</td><td>{temp[1]}</td><td>{temp[2]}</td><td>{temp[3]}</td></tr>'
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
                        tab_name = ["단체활동", "숙소-제주공항","제주-청주공항","청주공항-교회"]
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
                                        temp_text = f'<tr><td>{temp[0]}</td><td>{temp[1]}</td><td>{temp[2]}</td><td>{temp[3]}</td></tr>'
                                        sum_text += temp_text
                                        temp = list()
                                        
                                st.markdown(f"""
                                <table class = "name" style="table-layout: fixed;border: 0rem solid #ffffff;border-top : 0.2rem solid #F0F2F6;">
                                  {sum_text}
                                </table>
                                """, unsafe_allow_html=True)
                                st.write("")                        
                        
                        
                        
                        
                        
                        
                    
                    
                    
                    
                    
                    
                    
                st.write("메모 : 캡쳐 이미지 버튼 만들기, api로 실시간 db연결 , 검색창 흐름제어 다시고민 ,최적화하기 ")
                
                st.warning("메모 : 모두처리 했지만 이동시 개인별 예외케이스가 다양해서 혹시 실수가 없는지 더 집중적으로 교차검증이 필요할 것 같습니다!! 특히 시간 처리에 유의! 개별이동은 시간처리를 하이픈(-)로 하였음")
    else :
        st.markdown(multibox_blank_case, unsafe_allow_html=True)
        pass

    
    
    
    
    
    
    
    
    
    
    

    
    




    
    
    
    
    
    

# STYLE 지정


# 커스텀 component 만들기 위한 코드
# 폰트 지정
streamlit_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@200&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Emoji:wght@700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Pen+Script&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Diphylleia&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Hahmlet&display=swap');
    
    html, body, [class*="css"]  {
    font-family: Hahmlet,sans-serif;
    }
    
   
    
    @font-face {
      font-family: Symbola;
      
      src: 
      url('./fonts/symbola-font.ttf') format('truetype'),
      url('./fonts/Symbola-Emoji.woff') format('woff'),
      url('path/to/Symbola-Emoji.eot?#iefix') format('embedded-opentype');
    }
    .flipped-symbola-emoji {
      font-family: Noto Emoji, sans-serif;
      text-align: center;
      font-size: 1.5rem;
      margin: 0;
      transform: scaleX(-1);
    }
    .symbola-emoji {
      font-family: Noto Emoji, sans-serif;
      text-align: center;
      font-size: 1.5rem;
      margin: 0;
    }    
    
    
    .custom-font {
        font-size: 1rem;
    }
    .custom-ticket-font {
        font-size: 1rem;
        text-align: center;
    }
    .custom-ticket-small-font1 {
        font-size: 0.7rem;
        text-align: center;
        color: #F0A23D;
    }
    .custom-ticket-small-font2 {
        font-size: 0.7rem;
        text-align: center;
        color: #B57200;
    }
    .custom-ticket-small-font3 {
        font-size: 0.7rem;
        text-align: center;
        color: #8B4600;
    }    
    .name-font {
        font-size: 1rem;
        font-family: 'Nanum Pen Script', cursive;
    }
</style>
"""
st.markdown(streamlit_style, unsafe_allow_html=True)





### @ 아래코드는 HTML, CSS를 이용해 디테일한 스타일을 지정하기 위함

# 상하좌우 여백 제거 + max-width: 100% 뺴면 PC버전에서도 알맞게 보임
# .appview-container .main .block-container {.....}

# 툴바 없애기
# #MainMenu {visibility: hidden;} footer {visibility: hidden;}

# 이미지 확대 버튼 숨기기 -> 자연스러운 UI/UX를 위함 : 확대 버튼이 width layout을 해치는 문제가 있었음 
# button[title="View fullscreen"]{visibility: hidden;}

# expander fontsize 수정
# div[data-testid="stExpander"] div[role="button"]

# multibox 내부 글자 숨기거나, 설정하기
# div[class="row-widget stMultiSelect"]

# expander 스타일 설정
# .streamlit-expander

# 화면 너비의 비율%설정으로 모바일에서 깨지는 현상 해결하기  
# [data-testid="column"]:nth-child(1,2,3.....)

st.markdown('''
<style>

.appview-container .main .block-container {
    padding-top: 0rem;
    padding-left: 0rem;
    padding-right: 0rem;
    padding-bottom: 0rem;
}

#MainMenu, header , footer {visibility: hidden;}

button[title="View fullscreen"]{visibility: hidden;}

.streamlit-expander{
    border-radius: 0rem;
    border-top: 0rem solid #F0F2F6;
    border-bottom: 0.2rem solid #F0F2F6;
    border-right: 0.2rem solid #F0F2F6;
    border-left : 0rem ;
}
.streamlit-expanderHeader {
    background-color: white;
    display: flex;
    justify-content: right;
    color: black;
    padding: 4px 8px;
}
.streamlit-expanderContent {
    background-color: white;
    color: black; 
    padding: 0px 8px 8px 8px;
    
}
div[data-testid="stExpander"] div[role="button"] p {
    font-size: 0.8rem;
    font-weight: 100;
}
div[data-testid="stExpander"]{
    border-left : 0.3rem solid #F0F2F6;
}

div[data-baseweb="tab-panel"]{
    padding-top:0.5rem;
}
div[data-testid="stMarkdownContainer"] p{
    margin-block-start: 0rem;
    margin-block-end: 0rem;
}


[data-testid="column"]:nth-child(1){
    width: calc(7.5% - 1rem) !important;
    flex: 1 1 calc(7.5% - 1rem) !important;
    max-width: calc(7.5% - 1rem) !important;
    min-width: calc(7% - 1rem) !important;}
[data-testid="column"]:nth-child(2){
    width: calc(85% - 1rem) !important;
    flex: 1 1 calc(85% - 1rem) !important;
    min-width: calc(85% - 1rem) !important;
    max-width: calc(90% - 1rem) !important;}
[data-testid="column"]:nth-child(3){
    width: calc(7.5% - 1rem) !important;
    flex: 1 1 calc(7.5% - 1rem) !important;
    max-width: calc(7.5% - 1rem) !important;
    min-width: calc(7% - 1rem) !important;}
</style>''', unsafe_allow_html=True)

style = ''
with open('style.css')as f:
    style = f.read()
st.markdown(f"<style>{style}</style>", unsafe_allow_html = True)



# firstday - table
st.markdown("""
<style>
    table {
        width: 100%;
        border-spacing: 0;
    }
    .css-5rimss th, .css-5rimss td{
        padding: 0px 0px 0px 0px;
    }
    .first-day td, .first-day th {
        text-align: center;
        border-bottom: 0.15rem dashed #F0F2F6;
        border-top: 0.15rem dashed #F0F2F6;
        border-right : 0.2rem solid #F0F2F6;
    }
    .first-day td:nth-child(1), .first-day th:nth-child(1) { 
        width: 30% ;
        border-left: 0.3rem solid #F0A23D;
        border-right: 1px solid #ffffff; 
    }
    .first-day td:nth-child(2), .first-day th:nth-child(2) { 
        width: 6%; 
        border-right: 1px solid #ffffff; 
        line-height: 0.5rem;
    }
    .first-day td:nth-child(3), .first-day th:nth-child(3) { 
        width: 30% ;
        border-right: 0.2rem double #F0F2F6; 
    }
    .first-day td:nth-child(4), .first-day th:nth-child(4) { 
        width: 30%;
        color: #D67D3E;
        font-weight: bold;
        background-color: #ffffff;
    }
    .first-day td:nth-child(2):first-line {
      line-height: 0.7rem;
    }
</style>
""", unsafe_allow_html=True)

# secondday - table
st.markdown("""
<style>
    table {
        width: 100%;
        border-spacing: 0;
    }
    .css-5rimss th, .css-5rimss td{
        padding: 0px 0px 0px 0px;
    }
    .second-day td, .second-day th {
        text-align: center;
        border-bottom: 0.15rem dashed #F0F2F6;
        border-top: 0.15rem dashed #F0F2F6;
        border-right : 0.2rem solid #F0F2F6;
    }
    .second-day td:nth-child(1), .second-day th:nth-child(1) { 
        width: 30% ;
        border-left: 0.3rem solid #B57200;
        border-right: 1px solid #ffffff; 
    }
    .second-day td:nth-child(2), .second-day th:nth-child(2) { 
        width: 6%; 
        border-right: 1px solid #ffffff; 
        line-height: 0.5rem;
    }
    .second-day td:nth-child(3), .second-day th:nth-child(3) { 
        width: 30% ;
        border-right: 0.2rem double #F0F2F6; 
    }
    .second-day td:nth-child(4), .second-day th:nth-child(4) { 
        width: 30%;
        color: #D67D3E;
        font-weight: bold;
        background-color: #ffffff;
        line-height: 0.75rem;
    }
    .second-day td:nth-child(2):first-line {
      line-height: 0.4rem;
    }
    .second-day td:nth-child(4):first-line {
      line-height: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# thirdday - table
st.markdown("""
<style>
    table {
        width: 100%;
        border-spacing: 0;
    }
    .css-5rimss th, .css-5rimss td{
        padding: 0px 0px 0px 0px;
    }
    .third-day td, .third-day th {
        text-align: center;
        border-bottom: 0.15rem dashed #F0F2F6;
        border-right : 0.2rem solid #F0F2F6;
        border-top: 0.15rem dashed #F0F2F6;
    }
    .third-day td:nth-child(1), .third-day th:nth-child(1) { 
        width: 30% ;
        border-left: 0.3rem solid #8B4600;
        border-right: 1px solid #ffffff; 
    }
    .third-day td:nth-child(2), .third-day th:nth-child(2) { 
        width: 6%; 
        border-right: 1px solid #ffffff;
        line-height: 0.5rem;
    }
    .third-day td:nth-child(3), .third-day th:nth-child(3) { 
        width: 30% ;
        border-right: 0.2rem double #F0F2F6; 
    }
    .third-day td:nth-child(4), .third-day th:nth-child(4) { 
        width: 30%;
        color: #D67D3E;
        font-weight: bold;
        background-color: #ffffff;
    }
    .third-day td:nth-child(2):first-line {
      line-height: 0.7rem;
    }
</style>
""", unsafe_allow_html=True)

# name - table
st.markdown("""
<style>
    table {
        width: 100%;
        border-spacing: 0;
    }
    .css-5rimss th, .css-5rimss td{
        padding: 0px 0px 0px 0px;
    }
    .name td, .name th {
        text-align: center;
        border: 1px solid transparent;
</style>
""", unsafe_allow_html=True)

# #D08523  #B57200
#F97602

