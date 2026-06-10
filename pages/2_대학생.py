import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

st.title("🎓 대학생 금융 구원투수 챗봇")
st.write("학업과 아르바이트를 병행하느라 고생하는 대학생을 위한 학자금 및 자취 금융 정보를 제공합니다.")

fss_api_key = os.getenv("FSS_API_KEY")
openai_api_key = st.sidebar.text_input("OpenAI API Key (sk-...)", type="password")

if not fss_api_key:
    st.error("❌ 에러: .env 파일에 FSS_API_KEY가 없습니다.")
    st.stop()
if not openai_api_key:
    st.info("👈 좌측 사이드바에 OpenAI API 키를 입력하세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# 💡 주의: 2번 방이니까 messages_2 로 독립!
if "messages_2" not in st.session_state:
    st.session_state["messages_2"] = [{"role": "assistant", "content": "안녕하세요! 강의 듣고 알바하느라 바쁘죠? 학자금 부담이나 자취방 구하는 데 도움 될 만한 금융 정보를 알려줄게요."}]

for msg in st.session_state["messages_2"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("예: 대학생도 전세자금대출 받을 수 있어?"):
    st.session_state["messages_2"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("금감원 데이터 분석 중..."):
            url = "http://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json"
            params = {"auth": fss_api_key, "topFinGrpNo": "020000", "pageNo": "1"}
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    products = data.get('result', {}).get('baseList', [])
                    
                    current_year_month = datetime.datetime.now().strftime("%Y년 %m월")
                    api_context = f"명심해. 현재 시점은 {current_year_month}이야. 금감원 최신 전세자금대출 데이터야:\n\n"
                    for p in products[:5]: 
                        api_context += f"🏦 은행명: {p.get('kor_co_nm')}, 📌 상품명: {p.get('fin_prdt_nm')}, 📅 공시월: {p.get('dcls_month')}, 💰 대출한도: {p.get('loan_lmt')}, 📝 가입방법: {p.get('join_way')}\n"
                    
                    # 🧠 대학생 맞춤 가스라이팅
                    messages_for_ai = [
                        {"role": "system", "content": "너는 학업과 생활비를 고민하는 대학생을 위한 금융 상담 챗봇이야. 제공된 금감원 데이터를 활용하되, 대학생 입장에서 이해하기 쉽게 용어를 쉽게 풀어서 설명하고, 금리가 낮고 조건이 까다롭지 않은 상품 위주로 추천해줘. 과도한 빚보다는 계획적인 소비를 강조해."},
                        {"role": "system", "content": api_context},
                        {"role": "user", "content": prompt}
                    ]
                    
                    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages_for_ai)
                    ai_answer = completion.choices[0].message.content
                    
                    st.markdown(ai_answer)
                    st.session_state["messages_2"].append({"role": "assistant", "content": ai_answer})
                else:
                    st.error("❌ 금감원 서버 연결 실패")
            except Exception as e:
                st.error(f"❌ 챗봇 에러: {e}")