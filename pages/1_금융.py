import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

st.title("💬 통합 금융 방어선 챗봇")
st.write("니 상황을 짧게 말하고 전세대출이나 금융 상품 궁금한 거 물어봐라. 헛소리 없이 데이터로 조져준다.")

fss_api_key = os.getenv("FSS_API_KEY")
openai_api_key = st.sidebar.text_input("OpenAI API Key (sk-...)", type="password")

if not fss_api_key:
    st.error("❌ 에러: .env 파일에 FSS_API_KEY가 없습니다.")
    st.stop()
if not openai_api_key:
    st.info("👈 좌측 사이드바에 OpenAI API 키를 입력하세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "반갑다. 초년생이든 취준생이든 쫄지 말고 물어봐. 팩트만 꽂아서 대답해 줄게."}]

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("예: 나 백수인데 전세대출 가능한 곳 있어?"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("금감원 데이터 털어오는 중..."):
            url = "http://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json"
            params = {"auth": fss_api_key, "topFinGrpNo": "020000", "pageNo": "1"}
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    products = data.get('result', {}).get('baseList', [])
                    
                    current_year_month = datetime.datetime.now().strftime("%Y년 %m월")
                    api_context = f"지금 {current_year_month} 기준 금감원 전세자금대출 최신 데이터다:\n\n"
                    for p in products[:5]: 
                        api_context += f"🏦 은행명: {p.get('kor_co_nm')}, 📌 상품명: {p.get('fin_prdt_nm')}, 💰 한도: {p.get('loan_lmt')}, 📝 가입방법: {p.get('join_way')}\n"
                    
                    # 🧠 통합 프롬프트: 알아서 눈치채고 대답
                    sys_prompt = """너는 청년(사회초년생, 대학생, 군전역예정자, 취준생) 전체를 아우르는 통합 금융 멘토야. 
                    사용자의 질문 맥락에서 현재 상황을 파악하고, 그에 맞춰 편안하고 직설적인 동네 형/누나 말투로 대답해. 
                    '부모님께 손 벌려라', '룸쉐어 해라' 같은 쓰레기 훈수는 절대 두지 마. 
                    오직 제공된 금감원 데이터를 바탕으로, 당장 현실적으로 가입 가능한 상품 정보만 팩트로 명확하게 꽂아줘."""
                    
                    messages_for_ai = [
                        {"role": "system", "content": sys_prompt},
                        {"role": "system", "content": api_context},
                        {"role": "user", "content": prompt}
                    ]
                    
                    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages_for_ai)
                    ai_answer = completion.choices[0].message.content
                    
                    st.markdown(ai_answer)
                    st.session_state["messages"].append({"role": "assistant", "content": ai_answer})
                else:
                    st.error("❌ 금감원 서버 연결 실패")
            except Exception as e:
                st.error(f"❌ 챗봇 에러: {e}")