import streamlit as st
import requests
import os
import xml.etree.ElementTree as ET
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

st.title("🏛️ 청년 정책 털이 챗봇 (온통청년)")
st.write("금감원이 막히면 정부 지원금으로 간다. 온통청년 최신 정책 데이터를 긁어와서 팩트만 알려준다.")

# 🚨 온통청년 API 키는 금감원이랑 다르니까 따로 불러와야 한다.
youth_api_key = os.getenv("YOUTH_API_KEY")
openai_api_key = st.sidebar.text_input("OpenAI API Key (sk-...)", type="password")

if not youth_api_key:
    st.error("❌ 에러: .env 파일에 YOUTH_API_KEY가 없습니다. 당장 세팅해라.")
    st.stop()
if not openai_api_key:
    st.info("👈 좌측 사이드바에 OpenAI API 키를 꽂아 넣어라.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

if "messages_youth" not in st.session_state:
    st.session_state["messages_youth"] = [{"role": "assistant", "content": "반갑다. 월세 지원, 취업 지원금, 청년도약계좌 같은 온통청년 정책 궁금한 거 키워드로 짧게 쳐봐라. (예: 월세, 청년도약)"}]

for msg in st.session_state["messages_youth"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("예: 월세 지원 정책 알려줘"):
    st.session_state["messages_youth"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("온통청년 서버 문 부수고 들어가는 중..."):
            url = "https://www.youthcenter.go.kr/opi/empList.do"
            # srchWord에 유저 프롬프트를 통째로 넣으면 API가 멍청해서 못 찾을 수 있으니 키워드 중심으로 검색
            params = {
                "openApiVlak": youth_api_key,
                "display": "5",  # 5개만 긁어옴
                "pageIndex": "1",
                "srchWord": prompt[:10] # 너무 길면 에러나니까 앞에서 10글자만 잘라서 검색어로 던짐
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    # XML 데이터 찢어발기기
                    root = ET.fromstring(response.content)
                    
                    api_context = "다음은 온통청년 API에서 긁어온 실제 청년 정책 데이터다:\n\n"
                    emp_list = root.findall('.//emp')
                    
                    if not emp_list:
                        api_context += "현재 검색된 청년 정책이 없다. 키워드를 바꿔서 다시 검색하라고 안내해라.\n"
                    else:
                        for emp in emp_list:
                            biz_name = emp.findtext('polyBizSjnm', '이름 없음') # 정책명
                            biz_intro = emp.findtext('polyItcnCn', '내용 없음') # 정책 소개
                            biz_period = emp.findtext('rqutPrdCn', '기간 미정') # 신청 기간
                            api_context += f"📌 정책명: {biz_name}\n📅 신청기간: {biz_period}\n📝 요약: {biz_intro[:100]}...\n---\n"
                    
                    # 🧠 GPT 가스라이팅
                    sys_prompt = """너는 대한민국 청년들을 위한 정부 정책(온통청년) 안내 멘토다.
                    말투는 편안하고 직설적인 동네 형/누나처럼 해. 
                    내가 제공한 [온통청년 데이터]에 있는 내용만 팩트로 전달해. 
                    데이터가 없으면 아는 척하지 말고 '검색된 정책이 없다'고 딱 잘라 말해라."""
                    
                    messages_for_ai = [
                        {"role": "system", "content": sys_prompt},
                        {"role": "system", "content": api_context},
                        {"role": "user", "content": prompt}
                    ]
                    
                    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages_for_ai)
                    ai_answer = completion.choices[0].message.content
                    
                    st.markdown(ai_answer)
                    st.session_state["messages_youth"].append({"role": "assistant", "content": ai_answer})
                else:
                    st.error(f"❌ 온통청년 서버 터짐 (상태 코드: {response.status_code})")
            except Exception as e:
                st.error(f"❌ 챗봇/XML 파싱 에러: {e}")