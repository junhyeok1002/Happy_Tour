import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import gspread
import time

# style.css 파일에 구현한 스타일을 적용하는 코드
def Apply_CSS_Style():
    # HTML에 CSS-STYLE 지정
    with open('style.css', encoding = "utf-8")as f:
        style = f.read()
    st.markdown(f"<style>{style}</style>", unsafe_allow_html = True)
    
def SpreadSheet_to_Dataframe(spreadsheet_url, sheet_name):
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
    
    # 구글 스프레드 시트를 받아오기
    gc = gspread.service_account_from_dict(credentials)
    doc = gc.open_by_url(spreadsheet_url)
    worksheet = doc.worksheet(sheet_name)
    
    #받아온 시트를 DataFrame으로 가공하는 작업
    data = worksheet.get_all_values() 
    df = pd.DataFrame(data[2:], columns=data[1])
    df.drop(columns='#', inplace=True)
    df.set_index('이름', inplace=True)
    
    # 새로운 열 추가 : 숙소-제주공항
    df.insert(7, '숙소-제주공항',np.nan)
    df.loc[df['⑧제주-청주 비행기'].isin(['개별']), '숙소-제주공항'] = "개별"
    df.loc[df['⑧제주-청주 비행기'].isin(['개인이동', '선발대', None,'-']), '숙소-제주공항'] = "-"
    df.loc[~df['⑧제주-청주 비행기'].isin(['개인이동', '선발대', '개별', None,'-']), '숙소-제주공항'] = df['⑦단체활동 버스']    
    
    return df

def URL_Box(url, color, fonts, font_size, lettering):
    st.markdown(
    f"""
    <div style="padding: 0px 0px 8px 0px;">
        <a href="{url}" target="_blank" rel="noopener noreferrer">
            <div style="
                width :100%;
                font-family: {fonts};
                font-size: {font_size};
                display: inline-block;
                padding: 0.3rem;
                color: {color};
                background-color: #ffffff;
                border-radius: 0.5rem;
                letter-spacing: -0.13rem;
                border: 0.07rem solid {color};
                text-decoration: none;
                text-align: center;
                font-weight: bold;">
                {lettering}
            </div>
        </a>
    </div>
    """,
    unsafe_allow_html=True)    
    
def call_back(): # 하나 입력 시 dropdown이 닫히도록 call_back 설계
    time.sleep(0.3)
    with st.container(): pass  
    time.sleep(0.1)
    with st.container(): pass  
    


# 첫날 예외처리
def First_Day_Exception_Handling(result):
    Exception = ('개인이동','선발대','개별',None, '','-','자택')
    
    # ①교회-청주공항 버스 : 개인이동, 선발대 처리
    dncc_to_cjj = result['①교회-청주공항 버스'].values[0]
    if dncc_to_cjj.endswith('호차') : boarding_time1 = "오후 2:30"
    else : boarding_time1 = "-"

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
    cju_to_room = result['③제주공항-숙소 버스'].values[0]
    if (cju_to_room.endswith('호차')) or (cju_to_room in ('수양관','스타리아','카니발')): boarding_time3 = "오후 7:00"
    else : boarding_time3 = "-"                        

    # ④숙소명 층/호수 : 예외처리  
    room_info = result['④숙소명 층/호수'].values[0]
    try:
        if room_info in Exception:
            floor = room_info
            room_num = '-'
        else : 
            floor = room_info.split()[0]
            room_num = room_info.split()[1] 
    except:
        floor = room_info
        room_num = "-"
        
    return dncc_to_cjj, boarding_time1, airline, boarding_time2, cju_to_room, boarding_time3, floor, room_num
    
    
    
# 첫날 티켓 디자인 html생성
def First_Day_Ticket(dncc_to_cjj, boarding_time1, airline, boarding_time2, cju_to_room, boarding_time3, floor, room_num):
    # 첫째날 table파트
    st.markdown(f"""
    <table class = "first-day">
      <tr style="color:#F0A23D ;background-color: white ;border-top: 0.3rem solid #F0A23D;
        font-family:Diphylleia;border-right : 0.2rem solid #F0F2F6;"><th colspan="4">
        <span class="custom-ticket-font" style="font-size:1rem;letter-spacing: -0.13rem;">Day 1, 08/13 주일</span></th>
      </tr>
      <tr>
        <td><span class="custom-ticket-font">대전</span><br>
            <span class="custom-ticket-small-font1">DNCC</span></td>
        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F68C;</p><br>
            <p class="symbola-emoji" style = "font-size:1.2rem;">&#8594;</p></td>
        <td><span class="custom-ticket-font">청주공항</span><br>
            <span class="custom-ticket-small-font1">CJJ</span></td>
        <td><span class="custom-ticket-font" style="color: #F0A23D;">{dncc_to_cjj}</span><br>
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
        <td><span class="custom-ticket-font" style="color: #F0A23D;">{cju_to_room}</span><br>
            <span class="custom-ticket-small-font1" style="color: black;">{boarding_time3}</span></td>
      </tr>                              
      <tr>
        <td><span class="custom-ticket-font">숙소</span><br>
            <span class="custom-ticket-small-font1">ROOM</span></td>
        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F3E0;</p><br>
            <span class="custom-ticket-small-font1" style="color:black; 
            letter-spacing: -0.13rem;">{room_num}</span></td>                               
        <td><span class="custom-ticket-font">방 번호</span><br>
            <span class="custom-ticket-small-font1">NO.</span></td>
        <td><span class="custom-ticket-font" style="color: #F0A23D;
            font-size: 0.9rem;">{floor}</span><br>
            <span class="custom-ticket-small-font1" style="font-size: 0.8rem;
            color: black;">{room_num}</span></td>
      </tr>                          
    </table>
    """, unsafe_allow_html=True)    

# 둘째 날 티켓 디자인 html생성 
def Second_Day_Ticket(result, theme, theme_bus):
    theme_url = {'물놀이' : ['https://sandy-ear-231.notion.site/c8730b2e5d2f4636962550f876747bee?pvs=4',"오후 05:00"],
                 '액티비티' : ['https://sandy-ear-231.notion.site/92670ed2db424e8089bb93d68eed64d4?pvs=4',"오후 05:30"],
                 '인생샷' : ['https://sandy-ear-231.notion.site/9ca017fc6f9c40f1badab4192e2ce4a1?pvs=4',"오후 05:20"],
                 '자연' : ['https://sandy-ear-231.notion.site/6a061529159d467587eab7a90d2c1896?pvs=4',"오후 05:00"],
                 '힐링' : ['https://sandy-ear-231.notion.site/becd45dddbee435aacecf49ba776a8ed?pvs=4',"오후 05:30"],
                 '예외' : ['http://www.sja21.com/main/main.html',"-"]
                }     
    
    # 둘째날은 예외처리
    try: 
        url = theme_url[theme][0]  
        theme_s_time = '오후 12:00'
        theme_e_time = theme_url[theme][1]
    except:  
        url = theme_url['예외']
        theme_s_time = '-'
        theme_e_time = '-'

    st.markdown(f"""
    <table class = "second-day">
      <tr style="color:#B57200 ;background-color: white ;border-top: 0.3rem solid #B57200;
        font-family:Diphylleia;border-right : 0.2rem solid #F0F2F6;">
        <th colspan="4"><span class="custom-ticket-font" style="font-size:1rem;
        letter-spacing: -0.13rem;">Day 2, 08/14 월요일</span></th>
      </tr>                        
      <tr>
        <td><span class="custom-ticket-font">숙소</span><br>
            <span class="custom-ticket-small-font2">ROOM</span></td>
        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F68C;</p><br>
            <p class="symbola-emoji" style = "font-size:1.2rem;">&#x21C4;</p></td>
        <td><span class="custom-ticket-font">{theme}</span><br>
            <span class="custom-ticket-small-font2">THEME</span></td>
        <td><span class="custom-ticket-font" style="color: #B57200;">{theme_bus}</span><br>
            <span class="custom-ticket-small-font2" style="color: black;">{theme_s_time}<br>{theme_e_time}</span></td>
      </tr>                           
    </table> 
    """, unsafe_allow_html=True)
    
# 셋째 날 예외처리
def Third_Day_Exception_Handling(result):
    Exception = ('개인이동','선발대','개별',None, '','-')
    
    # 숙소 - 단체활동 처리
    group_tour_bus = result['⑦단체활동 버스'].values[0]
    if (group_tour_bus.endswith('호차')) or (group_tour_bus in ('스타리아','카니발')): group_tour_time = '오후 12:00'
    else : group_tour_time = '-'

    # 숙소-제주공항, 제주-청주 비행기 처리
    bus_to_cju = result['숙소-제주공항'].values[0]
    if (bus_to_cju.endswith('호차')) or (bus_to_cju in ('스타리아','카니발')): bus_to_cju_time = '오후 6:30'
    else : bus_to_cju_time = '-'    

    info_air2 = result['⑧제주-청주 비행기'].values[0].replace("pm"," ")
    try: # 단체 이동 
        day2, airline2, time2 = info_air2.split()  
        boarding_time4 = f'오후 {int(time2[:2])-12}:{time2[3:5]}'

    except : # 개별이동
        airline2 = info_air2
        boarding_time4 = "-"


    # 청주공항-교회 버스 처리
    bus_to_dncc = result['⑨청주공항-교회 버스'].values[0]
    if bus_to_dncc in Exception : bus_to_dncc_time = '-'
    elif airline2 in ('아시아나',):bus_to_dncc_time = '오후 10:00'
    elif airline2 in ('이스타','진에어','에어로케이'):bus_to_dncc_time = '오후 11:00'
    else : bus_to_dncc_time = '-'
        
    return group_tour_bus, group_tour_time, bus_to_cju, bus_to_cju_time, airline2, boarding_time4, bus_to_dncc, bus_to_dncc_time

# 셋째 날 티켓 디자인 html생성
def Third_Day_Ticket(group_tour_bus, group_tour_time, bus_to_cju, bus_to_cju_time, airline2, boarding_time4, bus_to_dncc, bus_to_dncc_time):
    st.markdown(f"""
    <table class = "third-day">
      <tr style="color:#8B4600 ;background-color: white ;border-top: 0.3rem solid #8B4600;
        font-family:Diphylleia;border-right : 0.2rem solid #F0F2F6;">
        <th colspan="4"><span class="custom-ticket-font" style="font-size:1rem;
        letter-spacing: -0.12rem;">Day 3, 08/15 화요일</span></th>
      </tr>                       
      <tr>
        <td><span class="custom-ticket-font">숙소</span><br>
            <span class="custom-ticket-small-font3">ROOM</span></td>
        <td ><p class="flipped-symbola-emoji" style = "font-size:1.4rem;"><br>&#x1F68C;</p><br>
            <p class="symbola-emoji" style = "font-size:1.2rem;">&#x21C4;</p></td>
        <td><span class="custom-ticket-font">단체관광</span><br>
            <span class="custom-ticket-small-font3">TOUR</span></td>
        <td><span class="custom-ticket-font" style="color: #8B4600;">{group_tour_bus}</span><br>
            <span class="custom-ticket-small-font3" style="color: black;">{group_tour_time}</span></td>
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
        <td><span class="custom-ticket-font" style="color: #8B4600;">{bus_to_dncc}</span><br>
            <span class="custom-ticket-small-font3" style="color: black;">{bus_to_dncc_time}</span></td>
      </tr>                           
    </table>
    """, unsafe_allow_html=True)



    
def together_list(data_list):
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
    
def together_tab(tab_name, transports, df, name, cols):
    for i, tab in enumerate(st.tabs(tab_name)):
        with tab:
            st.markdown(f'''<span class="name-font" style="font-size:1.5rem;">
                {tab_name[i]}, {transports[i]} 명단</span>''', unsafe_allow_html=True)
            mine = df.loc[name,cols[i]]
            data_list = list(df[df[cols[i]] == mine].index)

            together_list(data_list) 
                