import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

st.title("🎓 대학생 빈곤 탈출 챗봇")
st.write("알바비 모으기부터 대학가 자취방 구하기까지, 대학생 맞춤형 금융 정보를 제공합니다.")

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

if "messages_2" not in st.session_state:
    st.session_state["messages_2"] = [{"role": "assistant", "content": "반가워요! 주머니 사정이 가벼운 대학생을 위한 금융 꿀팁봇입니다. 알바비로 할 수 있는 적금이나, 자취방 보증금 대출을 물어보세요!"}]

for msg in st.session_state["messages_2"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("예: 대학생도 100만원 대출 받을 수 있는 곳 있어?"):
    st.session_state["messages_2"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("금감원 데이터 뒤지는 중..."):
            
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
                    
                    system_prompt = f"""너는 대학생 전문 금융 상담가야. 
                    절대 '기숙사 들어가라', '부모님께 손벌려라', '친구랑 같이 살아라' 같은 쓸데없는 훈수 금지. 
                    무조건 제공된 금감원 [{concept}] 데이터 안에서 대학생이 비대면(스마트폰)으로 가입하기 편하거나 부담이 적은 은행 상품을 직접적으로 추천해 줘."""

                    completion = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "system", "content": api_context}, {"role": "user", "content": prompt}]
                    )
                    ai_answer = completion.choices[0].message.content
                    
                    st.markdown(ai_answer)
                    st.session_state["messages_2"].append({"role": "assistant", "content": ai_answer})
            except Exception as e:
                st.error(f"❌ 챗봇 에러: {e}")