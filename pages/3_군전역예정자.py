import streamlit as st
import os
import requests
import xmltodict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

CATEGORY = "군 전역 예정자"

st.set_page_config(page_title=f"{CATEGORY} 맞춤형 정책 챗봇", page_icon="💡")
st.title(f"💡 {CATEGORY} 맞춤형 정책 챗봇")

with st.sidebar:
    st.header("🔑 시스템 설정")
    user_openai_key = st.text_input(
        "OpenAI API Key 입력:", 
        type="password", 
        value=st.session_state.get("USER_OPENAI_KEY", "")
    )
    if user_openai_key:
        st.session_state["USER_OPENAI_KEY"] = user_openai_key

if not st.session_state.get("USER_OPENAI_KEY"):
    st.error("❌ 좌측 사이드바에 본인의 OpenAI API Key를 입력해야 챗봇을 사용할 수 있습니다.")
    st.stop()

client = OpenAI(api_key=st.session_state["USER_OPENAI_KEY"])

MSG_KEY = f"msg_{CATEGORY}"
if MSG_KEY not in st.session_state:
    st.session_state[MSG_KEY] = [{"role": "assistant", "content": f"안녕하세요! {CATEGORY}를 위한 정책 정보를 안내해 드립니다. 어떤 혜택이 궁금하신가요?"}]

if st.button("🗑️ 대화 내역 초기화"):
    st.session_state[MSG_KEY] = [{"role": "assistant", "content": f"안녕하세요! {CATEGORY}를 위한 정책 정보를 안내해 드립니다. 어떤 혜택이 궁금하신가요?"}]
    st.rerun()

st.markdown("---")

for msg in st.session_state[MSG_KEY]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"{CATEGORY} 지원 정책에 대해 물어보세요 (예: 장병내일준비적금 만기 혜택이 어떻게 되나요?)"):
    st.session_state[MSG_KEY].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("정부 공공 데이터망에서 최신 정책을 가져오는 중입니다..."):
            try:
                url = "https://www.youthcenter.go.kr/opi/youthPlcyList.do"
                youth_api_key = os.getenv("YOUTH_API_KEY")
                
                if not youth_api_key:
                    st.error("❌ 서버 오류: .env 파일에 온통청년 API 키(YOUTH_API_KEY)가 없습니다.")
                    st.stop()

                params = {
                    "openApiVlak": youth_api_key,
                    "display": "5",
                    "pageIndex": "1",
                    "query": prompt
                }
                
                response = requests.get(url, params=params)
                dict_data = xmltodict.parse(response.text)
                
                try:
                    policies = dict_data['empInfo']['emp']
                    if not isinstance(policies, list):
                        policies = [policies]
                    
                    policy_info = ""
                    for p in policies:
                        policy_info += f"- 정책명: {p.get('polyBizSjnm')}\n  내용: {p.get('polyItcnCn')}\n\n"
                except KeyError:
                    policy_info = "검색된 관련 정책 데이터가 정부 서버에 없습니다."

                sys_prompt = (
                    f"당신은 대한민국 정부 지원 정책 전문가 '청년지갑구조대' 챗봇입니다. "
                    f"현재 상담 대상은 '{CATEGORY}'입니다. "
                    f"아래 [실시간 정부 API 검색 결과]를 최우선으로 바탕으로 사용자의 질문에 전문적이고 깍듯한 존댓말로 답변하세요. "
                    f"지원 자격, 혜택 금액, 신청 방법을 표나 글머리 기호로 요약해 주세요. 모르는 내용은 지어내지 마세요.\n\n"
                    f"[실시간 정부 API 검색 결과]\n{policy_info}"
                )
                
                messages = [{"role": "system", "content": sys_prompt}]
                messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state[MSG_KEY]])
                
                gpt_res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.3
                )
                
                answer = gpt_res.choices[0].message.content
                st.markdown(answer)
                st.session_state[MSG_KEY].append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"통신 중 오류 발생: {e} (연장 설치 안 했거나 정부 서버가 죽었을 확률 100%)")