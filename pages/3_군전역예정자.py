import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

st.title("🪖 군 전역 예정자 자립 챗봇")
st.write("사회 나갈 준비하느라 고생 많다. 전역 후 바로 써먹을 전세/금융 정보 깔끔하게 정리해 줄게.")

fss_api_key = os.getenv("FSS_API_KEY")
openai_api_key = st.sidebar.text_input("OpenAI API Key (sk-...)", type="password")

if not fss_api_key:
    st.error("❌ 에러: .env 파일에 FSS_API_KEY가 없습니다.")
    st.stop()
if not openai_api_key:
    st.info("👈 좌측 사이드바에 OpenAI API 키를 입력하세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

if "messages_3" not in st.session_state:
    st.session_state["messages_3"] = [{"role": "assistant", "content": "전역 앞두고 있냐? 고생했다. 사회 나오면 당장 돈 나갈 데 많을 텐데, 전세자금대출이나 금융 상품 궁금한 거 있으면 뭐든 물어봐."}]

for msg in st.session_state["messages_3"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("예: 전역 후 자취방 구할 때 전세 대출 조건은?"):
    st.session_state["messages_3"].append({"role": "user", "content": prompt})
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
                    api_context = f"지금 {current_year_month} 기준 금감원 전세자금대출 데이터다:\n\n"
                    for p in products[:5]: 
                        api_context += f"🏦 은행명: {p.get('kor_co_nm')}, 📌 상품명: {p.get('fin_prdt_nm')}, 💰 한도: {p.get('loan_lmt')}, 📝 가입방법: {p.get('join_way')}\n"
                    
                    # 🧠 말투 수정: 다나까 버리고 직설적으로
                    messages_for_ai = [
                        {"role": "system", "content": "너는 전역 예정자들을 위한 금융 멘토야. 말투는 그냥 편한 친구나 형처럼 직설적이고 친근하게 해. 제공된 데이터를 기반으로 하되, 겉치레 멘트 빼고 진짜 도움 될 만한 현실적인 팁 위주로 꽂아줘. 뜬구름 잡는 소리는 하지 말고."},
                        {"role": "system", "content": api_context},
                        {"role": "user", "content": prompt}
                    ]
                    
                    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages_for_ai)
                    ai_answer = completion.choices[0].message.content
                    
                    st.markdown(ai_answer)
                    st.session_state["messages_3"].append({"role": "assistant", "content": ai_answer})
                else:
                    st.error("❌ 금감원 서버 연결 실패")
            except Exception as e:
                st.error(f"❌ 챗봇 에러: {e}")