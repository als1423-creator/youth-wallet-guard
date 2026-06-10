import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

st.title("🪖 군전역예정자 자립 구조대")
st.write("군 적금 수령부터 전역 후 자취방 구하기까지. AI가 든든하게 지원합니다.")

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

if "messages_3" not in st.session_state:
    st.session_state["messages_3"] = [{"role": "assistant", "content": "충성! 전역을 앞둔 장병 여러분을 위한 금융 챗봇입니다. 적금 만기액 굴리는 법이나, 전역 후 살 방을 구하기 위한 대출 정보를 질문하십시오."}]

for msg in st.session_state["messages_3"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("예: 전역하고 원룸 구할 건데 전세대출 추천 바랍니다."):
    st.session_state["messages_3"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("금감원 데이터 탐색 중..."):
            
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
                    
                    system_prompt = f"""너는 군 전역을 앞둔 군인들의 사회 진출을 돕는 금융AI야. 가끔씩 씩씩한 '다나까'체를 사용해.
                    절대 '부대 간부와 상의해라', '부모님 집에 얹혀살아라' 같은 도덕책 헛소리 금지. 
                    무조건 제공된 금감원 [{concept}] 데이터 안에서, 전역자가 현실적으로 이용할 수 있는 은행 상품 정보를 확실하게 팩트로 전달해."""

                    completion = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "system", "content": api_context}, {"role": "user", "content": prompt}]
                    )
                    ai_answer = completion.choices[0].message.content
                    
                    st.markdown(ai_answer)
                    st.session_state["messages_3"].append({"role": "assistant", "content": ai_answer})
            except Exception as e:
                st.error(f"❌ 챗봇 에러: {e}")