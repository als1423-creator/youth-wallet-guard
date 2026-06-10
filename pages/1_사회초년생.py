import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

st.title("🌱 사회초년생 금융 튜토리얼 챗봇")
st.write("월급 관리부터 독립 준비까지. 초년생을 위한 맞춤 금융 상품을 찾아드립니다.")

fss_api_key = os.getenv("FSS_API_KEY")
openai_api_key = st.sidebar.text_input("OpenAI API Key (sk-...)", type="password")

if not fss_api_key or not openai_api_key:
    st.warning("👈 좌측 사이드바에 OpenAI API 키를 넣고, .env에 금감원 키를 세팅하세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

st.markdown("---")
product_type = st.radio(
    "🎯 현재 가장 필요한 금융 서비스를 선택하세요:",
    ["💰 돈 모으기 (적금)", "💳 급전 빌리기 (신용대출)", "🏠 방 구하기 (전세자금대출)"],
    horizontal=True
)
st.markdown("---")

if "messages_1" not in st.session_state:
    st.session_state["messages_1"] = [{"role": "assistant", "content": "취업 축하드려요! 이제 막 돈을 벌기 시작한 초년생을 위한 저축, 대출, 전세 상품을 알려드릴게요. 무엇이 필요하신가요?"}]

for msg in st.session_state["messages_1"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("예: 월급 200인데 자취방 전세 대출 어디가 좋아?"):
    st.session_state["messages_1"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("금감원 데이터 분석 중..."):
            
            if "적금" in product_type:
                url, concept = "http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json", "적금"
            elif "신용대출" in product_type:
                url, concept = "http://finlife.fss.or.kr/finlifeapi/creditLoanProductsSearch.json", "신용대출"
            else:
                url, concept = "http://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json", "전세자금대출"

            params = {"auth": fss_api_key, "topFinGrpNo": "020000", "pageNo": "1"}
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    products = data.get('result', {}).get('baseList', [])
                    
                    if not products:
                        st.warning("⚠️ 조건에 맞는 상품이 없습니다.")
                        st.stop()

                    current_year_month = datetime.datetime.now().strftime("%Y년 %m월")
                    api_context = f"현재 시점은 {current_year_month}야. 금감원 실시간 [{concept}] 데이터:\n\n"
                    for p in products[:5]: 
                        api_context += f"🏦 은행명: {p.get('kor_co_nm')}, 📌 상품명: {p.get('fin_prdt_nm')}, 📝 가입방법: {p.get('join_way')}\n"
                    
                    system_prompt = f"""너는 이제 막 취업한 사회초년생의 금융 멘토야. 
                    절대 '부모님 찬스', '룸쉐어', '절약해라' 같은 오지랖이나 인생 조언 하지 마. 
                    무조건 금감원 [{concept}] 데이터 리스트 안에서, 초년생에게 적합한 실질적인 '은행 상품 추천'만 친절하게 팩트로 꽂아줘. 어려운 용어는 쉽게 풀어줘."""

                    completion = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "system", "content": api_context}, {"role": "user", "content": prompt}]
                    )
                    ai_answer = completion.choices[0].message.content
                    
                    st.markdown(ai_answer)
                    st.session_state["messages_1"].append({"role": "assistant", "content": ai_answer})
            except Exception as e:
                st.error(f"❌ 챗봇 에러: {e}")