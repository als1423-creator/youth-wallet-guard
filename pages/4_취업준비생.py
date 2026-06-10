import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import datetime

load_dotenv()

st.title("💼 취업준비생 맞춤 금융 구조대")
st.write("돈을 모으고 싶나요(적금), 급전이 필요한가요(신용대출), 아니면 방이 필요한가요(전세대출)? AI가 맞춤형으로 찾아드립니다.")

# 1. 🔑 API 키 세팅
fss_api_key = os.getenv("FSS_API_KEY")
openai_api_key = st.sidebar.text_input("OpenAI API Key (sk-...)", type="password")

if not fss_api_key:
    st.error("❌ 에러: .env 파일에 FSS_API_KEY가 없습니다.")
    st.stop()
if not openai_api_key:
    st.info("👈 좌측 사이드바에 OpenAI API 키를 입력하세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# 💡 2. 라디오 버튼에 '방 구하기' 부활!
st.markdown("---")
product_type = st.radio(
    "🎯 현재 가장 필요한 금융 서비스를 선택하세요:",
    ["💰 돈 모으기 (적금)", "💳 급전 빌리기 (신용대출)", "🏠 방 구하기 (전세자금대출)"],
    horizontal=True
)
st.markdown("---")

if "messages_4" not in st.session_state:
    st.session_state["messages_4"] = [{"role": "assistant", "content": "안녕하세요! 취업 준비 중이시군요. 저축, 대출, 전세 중 선택하신 목적에 맞게 질문해 주시면 찰떡같이 찾아드릴게요."}]

for msg in st.session_state["messages_4"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. 🚀 API 통신 및 GPT 로직
if prompt := st.chat_input("예: 백수도 받을 수 있는 전세대출 조건 알려줘"):
    st.session_state["messages_4"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("금감원 금고에서 데이터 털어오는 중..."):
            
            # 💡 선택한 라디오 버튼에 따라 주소 3가지로 분기
            if "적금" in product_type:
                url = "http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"
                concept = "적금"
            elif "신용대출" in product_type:
                url = "http://finlife.fss.or.kr/finlifeapi/creditLoanProductsSearch.json"
                concept = "신용대출"
            else:
                url = "http://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json"
                concept = "전세자금대출"

            params = {
                "auth": fss_api_key, 
                "topFinGrpNo": "020000",
                "pageNo": "1"
            }
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    products = data.get('result', {}).get('baseList', [])
                    
                    if not products:
                        st.warning("⚠️ 현재 조건에 맞는 상품이 금감원에 없습니다.")
                        st.stop()

                    current_year_month = datetime.datetime.now().strftime("%Y년 %m월")
                    api_context = f"명심해. 현재 시점은 {current_year_month}이야. 다음은 금감원 API에서 방금 가져온 최신 [{concept}] 상품 데이터야:\n\n"
                    
                    for p in products[:5]: 
                        api_context += f"🏦 은행명: {p.get('kor_co_nm')}, 📌 상품명: {p.get('fin_prdt_nm')}, 📝 가입방법: {p.get('join_way')}\n"
                    
                    # 🧠 GPT 멱살 잡는 빡센 가스라이팅
                    system_prompt = f"""너는 오직 데이터에 기반한 금융 전문 AI 챗봇이야. 
                    사용자가 방을 구하든 돈이 필요하든, 절대 '룸쉐어', '부모님과 상의', '임시 거주 시설 이용' 같은 인생 조언이나 헛소리를 하지 마. 
                    무조건 네가 방금 받은 금감원 [{concept}] 데이터 리스트 안에서, 어떤 은행의 어떤 상품을 가입해야 하는지 실질적인 '금융 상품 추천'만 팩트로 꽂아줘."""

                    messages_for_ai = [
                        {"role": "system", "content": system_prompt},
                        {"role": "system", "content": api_context},
                        {"role": "user", "content": prompt}
                    ]
                    
                    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages_for_ai)
                    ai_answer = completion.choices[0].message.content
                    
                    st.markdown(ai_answer)
                    st.session_state["messages_4"].append({"role": "assistant", "content": ai_answer})
                else:
                    st.error(f"❌ 금감원 서버 연결 실패 (상태 코드: {response.status_code})")
            except Exception as e:
                st.error(f"❌ 챗봇 에러: {e}")