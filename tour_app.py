import pandas as pd
import streamlit as st
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from PIL import Image

# XLS 파일 읽기
df = pd.read_excel('./data/행복투어 샘플.xls', index_col = 0 )

# 이름 목록
names = list(df.index)

# 디자인 이미지 호출하여 삽입
image_path = './image/design.jpg'
image = Image.open(image_path)
st.image(image,use_column_width  = True)# caption='Sunrise by the mountains')

# 디자인 이미지 layout에 맞게 좌우 여백 추가 7.5%, 85%, 7.5% 
side_gap = 0.75
body_gap = 10-2*side_gap

# 티켓 생성 함수
def ticket(emoji,first,second,third,fourth):
    if emoji == 'bus' : 
        emoji = '#x1F68C'
        emoji_type = "flipped-symbola-emoji"
 
    elif emoji == 'airplane' :
        emoji = '#x1F6EB'
        emoji_type = 'symbola-emoji'
    elif emoji == 'home' : 
        emoji = '#x1F3E0'
        emoji_type = 'symbola-emoji'
    
    st.markdown(f"""
    <table>
      <tr>
        <td><span class="custom-ticket-font">{first[0]}</span><br><span class="custom-ticket-small-font">{first[1]}</span></td>
        <td><p class="{emoji_type}">&{emoji};</p></td>
        <td><span class="custom-ticket-font">{third[0]}</span><br><span class="custom-ticket-small-font">{third[1]}</span></td>
        <td><span class="custom-ticket-font">{fourth}</span><br><span class="custom-ticket-small-font">{'???'}</span></td>
      </tr>
    </table>
    """, unsafe_allow_html=True)

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

# C1: left blank, C2: body, C3: right blank
C1, C2, C3 = st.columns([side_gap, body_gap ,side_gap])
with C1: pass # C1: left blank
with C3: pass # C3: right blank
with C2:            #C2: body

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
                
                with st.expander("Day 1, 08/13(일)", expanded = True):
                    with st.container(): ticket('bus',['대전','DNCC'],'···',['청주공항','CJJ'],result['버스 좌석 1'].values[0])
                    with st.container(): ticket('airplane',['청주공항','CJJ'],'···',['제주공항','CJU'],'아시아나')
                    with st.container(): ticket('bus',['제주공항','CJU'],'···',['숙소','ROOM'],result['버스 좌석 2'].values[0])
                    with st.container(): ticket('home',['숙소','ROOM'],'···',['방 번호','NO.'],result['숙소 호수'].values[0])
                    st.write('')
                
                with st.expander("Day 2, 08/14(월)", expanded = True):
                    st.write("업데이트 중")
                    
                with st.expander("Day 3, 08/15(화)", expanded = True):
                    st.write("업데이트 중")
    else :
        st.markdown(multibox_blank_case, unsafe_allow_html=True)
        pass

    
    
    
    
    
    
    
    
    
    
    

    
    




    
    
    
    
    
    

# STYLE 지정


# 커스텀 component 만들기 위한 코드
custom_style = """
    <style>
        .custom-font {
            font-size: 1rem;
        }
        .custom-ticket-font {
            font-size: 1rem;
            text-align: center;
        }
        .custom-ticket-small-font {
            font-size: 0.7rem;
            text-align: center;
            color: #F97602;
        }
    </style>
"""
st.markdown(custom_style, unsafe_allow_html=True) # 커스텀 스타일을 적용


# 폰트 지정
streamlit_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@200&display=swap');

    html, body, [class*="css"]  {
    font-family: Noto Sans KR, sans-serif;
    }
    @font-face {
      font-family: 'Symbola';
      
      src: 
      url('./fonts/symbola-font.ttf') format('truetype'),
      url('./fonts/Symbola-Emoji.woff') format('woff'),
      url('path/to/Symbola-Emoji.eot?#iefix') format('embedded-opentype');
    }
    .flipped-symbola-emoji {
      font-family: 'Symbola', sans-serif;
      text-align: center;
      font-size: 1.5rem;
      margin: 0;
      transform: scaleX(-1);
    }
    .symbola-emoji {
      font-family: 'Symbola', sans-serif;
      text-align: center;
      font-size: 1.5rem;
      margin: 0;
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

div[data-testid="stExpander"] div[role="button"] p {
    font-size: 1rem;
}

ul.streamlit-expander {
    border-top-left-radius: 1rem solid #F0F2F6;
    border-top-right-radius: 1rem solid #F0F2F6;
    border: 0.1rem solid #F0F2F6;
}
.streamlit-expanderHeader {
    background-color: white;
    color: black;
    padding: 8px;

}
.streamlit-expanderContent {
    background-color: white;
    color: black; 
    padding: 0px 8px 8px 8px;
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


st.markdown("""
<style>
    table {
        width: 100%;
        border-spacing: 0;
        border-top : 0.1rem dashed #F0F2F6;
        border-bottom : 0.1rem dashed #F0F2F6;
    }
    .css-5rimss th, .css-5rimss td{
        padding: 0px 0px 0px 0px;
    }
    td, th {
        text-align: center;
    }
    
    td:nth-child(1),th:nth-child(1) { 
        width: 30% ;
        border-left: 0.3rem solid #F0A23D;
        border-right: 1px solid #ffffff; 
        border-bottom: 0.1rem dashed #F0F2F6;
        border-top: 0.1rem dashed #F0F2F6;
    }

    td:nth-child(2),th:nth-child(2) { 
        width: 6%; 
        border-right: 1px solid #ffffff; 
        border-bottom: 0.1rem dashed #F0F2F6;
        border-top: 0.1rem dashed #F0F2F6;
    }
    td:nth-child(3),th:nth-child(3) { 
        width: 30% ;
        border-right: 2px dashed #F0A23D; 
        border-bottom: 0.1rem dashed #F0F2F6;
        border-top: 0.1rem dashed #F0F2F6;   
    }
    td:nth-child(4),th:nth-child(4) { 
        width: 30%;
        color: #F0A23D;
        font-weight: bold;
        background-color: #ffffff;
        border-right : 0.3rem solid #F0A23D;
    }
</style>
""", unsafe_allow_html=True)



