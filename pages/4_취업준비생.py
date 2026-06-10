import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

st.title("💼 취업준비생 금융 방어선 챗봇")
st.write("소득 없어도 쫄지 마라. 취준생도 알아두면 무조건 돈 되는 금융 정보 싹 정리해 줄게.")

fss_api_key = os.getenv("FSS_API_KEY")
openai_api_key = st.sidebar.text_input("OpenAI API Key (sk-...)", type="password")

if not fss_api_key:
    st.error("❌ 에러: .env 파일에 FSS_API_KEY가 없습니다.")
    st.stop()
if not openai_api_key:
    st.info("👈 좌측 사이드바에 OpenAI API 키를 입력하세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

if "messages_4" not in st.session_state:
    st.session_state["messages_4"] = [{"role": "assistant", "content": "취업 준비하느라 고생이 많다. 소득 없다고 기죽을 거 없어. 당장 쓸 수 있는 알짜배기 금융 정보 다 털어줄 테니까 궁금한 거 물어봐."}]

for msg in st.session_state["messages_4"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("예: 백수도 받을 수 있는 전세대출 조건 알려줘"):
    st.session_state["messages_4"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("금감원 금고 털러 가는 중..."):
            url = "http://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json"
            params = {"auth": fss_api_key, "topFinGrpNo": "020000", "pageNo": "1"}
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    products = data.get('result', {}).get('baseList', [])
                    
                    current_year_month = datetime.datetime.now().strftime("%Y년 %m월")
                    api_context = f"지금 {current_year_month} 기준 금감원 전세자금대출 데이터다:\n\n"
                    for p in products[:5]: 
                        api_context += f"🏦 은행명: {p.get('kor_co_nm')}, 📌 상품명: {p.get('fin_prdt_nm')}, 💰 한도: {p.get('loan_lmt')}, 📝 가입방법: {p.get('join_way')}\n"
                    
                    # 🧠 말투 수정: 훈수 금지, 팩트 중심 친근한 형 컨셉
                    messages_for_ai = [
                        {"role": "system", "content": "너는 취업 준비생을 위한 금융 멘토야. 말투는 편한 형이나 누나처럼 친근하고 직설적으로 해. '부모님 의지해라', '룸쉐어 해라' 같은 뻔한 소리 하지 말고, 제공된 데이터를 바탕으로 실질적으로 가입할 수 있는 상품 정보만 팩트로 꽂아줘."},
                        {"role": "system", "content": api_context},
                        {"role": "user", "content": prompt}
                    ]
                    
                    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages_for_ai)
                    ai_answer = completion.choices[0].message.content
                    
                    st.markdown(ai_answer)
                    st.session_state["messages_4"].append({"role": "assistant", "content": ai_answer})
                else:
                    st.error("❌ 금감원 서버 연결 실패")
            except Exception as e:
                st.error(f"❌ 챗봇 에러: {e}")