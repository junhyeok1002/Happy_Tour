import pandas as pd
import streamlit as st
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from PIL import Image

# XLS 파일 읽기
df = pd.read_excel('./data/행복투어 샘플.xls', index_col = 0 )
# 이름 목록
names = list(df.index)


st.code(f"""
[theme]
base="light"
primaryColor="#F0A23D"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#31333F"
""", language="toml")





with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

    
custom_style = """
    <style>
        .rounded-text-box {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 10px;
        }
        .streamlit-layout .C1 {
            max-width: 7.5%;
        }
        .streamlit-layout .C3 {
            max-width: 7.5%;
        }
        .streamlit-layout .C2 {
            max-width: 85%;
        }
    </style>
"""
# 커스텀 스타일을 적용
st.markdown(custom_style, unsafe_allow_html=True)

    
st.markdown("""
<style>
    body {
        backgroundColor: blue;
        #F0A23D
    }
</style>
""", unsafe_allow_html=True)

hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''
st.markdown(hide_img_fs, unsafe_allow_html=True)

image_path = './image/design.jpg'
image = Image.open(image_path)
st.image(image,use_column_width  = True)# caption='Sunrise by the mountains')



side_gap = 0.75
body_gap = 10-2*side_gap

st.write('''<style>
[data-testid="column"]:nth-child(1){
    width: calc(7.5% - 1rem) !important;
    flex: 1 1 calc(7.5% - 1rem) !important;
    max-width: calc(7.5% - 1rem) !important;
}
</style>''', unsafe_allow_html=True)

st.write('''<style>
[data-testid="column"]:nth-child(2){
    width: calc(85% - 1rem) !important;
    flex: 1 1 calc(85% - 1rem) !important;
    min-width: calc(85% - 1rem) !important;
}
</style>''', unsafe_allow_html=True)

st.write('''<style>
[data-testid="column"]:nth-child(3){
    width: calc(7.5% - 1rem) !important;
    flex: 1 1 calc(7.5% - 1rem) !important;
    max-width: calc(7.5% - 1rem) !important;
}
</style>''', unsafe_allow_html=True)


C1, C2, C3 = st.columns([side_gap, body_gap ,side_gap])
with C1: st.empty()
with C3: st.empty()   
with C2:

    # 검색어 입력
    change_text = """
    <style>
    div.st-cu.st-cb.st-bi.st-cv.st-cw.st-cx {visibility: hidden;}
    div.st-cu.st-cb.st-bi.st-cv.st-cw.st-cx:before {content: ""; visibility: visible;}
    </style>
    """
    st.markdown(change_text, unsafe_allow_html=True)

    name_list = st.multiselect('성함을 입력해주세요(한번에 여러 명 검색가능합니다.)', names,max_selections=None)

    # 초기 흐름 제어 : 검색하면 처리하도록
    if len(name_list) > 0:
        # 띄어쓰기 처리
        name_list = [name.replace(" ","") for name in name_list] 

        # 탭 나누기
        tabs= st.tabs(name_list)
        for i, name in enumerate(name_list):
            with tabs[i]:
                if (name not in df.index) or (list(df.index).count(name) > 1) :
                    # 유사한 결과 찾기
                    matches = process.extract(name, names, scorer=fuzz.token_set_ratio, limit=500)

                    # 뒤의 숫자가 0인 요소 제거 후 내림차순으로 정렬하여 연관도 Top 5만 선정
                    matches = [(name, score) for name, score in matches if score != 0]
                    matches = sorted(matches, key=lambda x: x[1], reverse=True)[:5]
                    matches_list = [name for name, score in matches]

                    wrong_name = name[:]
                    name = st.radio(f"찾으시는 성함을 클릭해주세요. 아래에도 없을 경우 이주노 전도사님께 문의부탁드립니다", matches_list)

                result = df[df.index == name]
                
                st.markdown('<div class="rounded-text-box"> 아래 부분 디자인 갈아 엎는중 </div>', unsafe_allow_html=True)
                
                epsilon = 0.0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001
                with st.expander("8월 13일(첫날)", expanded = True):
                    col1, col2, col3, col4, col5 = st.columns([epsilon,epsilon,epsilon,5,5])
                    
#                     st.write('''<style>
#                     [data-testid="column"]:nth-child(4){
#                         width: calc(42.5% - 1rem) !important;
#                         flex: 1 1 calc(42.5% - 1rem) !important;
#                         min-width: calc(42.5% - 1rem) !important;
#                     }
#                     </style>''', unsafe_allow_html=True)
                    
                    
                    with col4:
                        # 모서리가 둥근 텍스트 박스 안에서 작업
                        col4.metric(":green[🛧 대전 → 청주공항]", f"{result['버스 좌석 1'].values[0]}")
                        col4.metric(":green[🛧 제주공항 → 숙소]", f"{result['버스 좌석 2'].values[0]}")
                    with col5:
                        col5.metric(":green[🛧 청주공항 → 제주공항]", f"{result['비행기 좌석'].values[0]}")
                        col5.metric("숙소배정", f"{result['숙소 호수'].values[0]}")

                with st.expander("8월 14일(테마활동 둘째날이 맞나요?? ㅎㅎ)", expanded = True):
                    col1, col2, col3, col4, col5 = st.columns([epsilon,epsilon,epsilon,5,5])

                    col4.metric("@테마장소이름넣기@", f"{result['테마'].values[0]}", "테마")
                    col5.metric("제주숙소 → 테마장소", f"{result['버스 좌석 3'].values[0]}", "버스좌석")
    else :
        pass 