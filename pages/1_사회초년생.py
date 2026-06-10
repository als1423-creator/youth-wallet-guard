import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

st.title("🌱 사회초년생 금융 방어선 챗봇")
st.write("갓 취업해서 독립이 막막한 초년생을 위한 맞춤 전세/금융 정보를 제공합니다.")

fss_api_key = os.getenv("FSS_API_KEY")
openai_api_key = st.sidebar.text_input("OpenAI API Key (sk-...)", type="password")

if not fss_api_key:
    st.error("❌ 에러: .env 파일에 FSS_API_KEY가 없습니다.")
    st.stop()
if not openai_api_key:
    st.info("👈 좌측 사이드바에 OpenAI API 키를 입력하세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# 💡 주의: 1번 방이니까 messages_1 로 확실하게 독립 (이거 안 바꾸면 4번 방이랑 채팅 섞임)
if "messages_1" not in st.session_state:
    st.session_state["messages_1"] = [{"role": "assistant", "content": "취업 축하드립니다! 이제 막 사회에 나와 독립을 준비하는 초년생을 위한 전세/금융 상품을 찾아드릴게요. 무엇이 궁금하신가요?"}]

for msg in st.session_state["messages_1"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("예: 월급 200인데 자취방 전세 대출 어디가 좋아?"):
    st.session_state["messages_1"].append({"role": "user", "content": prompt})
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
                    
                    # 🧠 사회초년생 맞춤 가스라이팅
                    messages_for_ai = [
                        {"role": "system", "content": "너는 이제 막 취업한 사회초년생을 위한 금융 상담 챗봇이야. 제공된 금감원 데이터를 활용하되, 부모님께 손 벌리라는 헛소리는 절대 하지 말고 초년생이 자립할 수 있게 실질적인 은행 상품 추천 위주로 팩트만 꽂아서 답변해줘."},
                        {"role": "system", "content": api_context},
                        {"role": "user", "content": prompt}
                    ]
                    
                    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages_for_ai)
                    ai_answer = completion.choices[0].message.content
                    
                    st.markdown(ai_answer)
                    st.session_state["messages_1"].append({"role": "assistant", "content": ai_answer})
                else:
                    st.error("❌ 금감원 서버 연결 실패")
            except Exception as e:
                st.error(f"❌ 챗봇 에러: {e}")
                