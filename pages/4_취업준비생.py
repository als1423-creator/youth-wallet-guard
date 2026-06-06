import streamlit as st
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드 (.env 금고 열기)
load_dotenv()

CATEGORY = "취업 준비생"

# 페이지 기본 설정
st.set_page_config(page_title=f"{CATEGORY} 맞춤형 정책 챗봇", page_icon="💡")
st.title(f"💡 {CATEGORY} 맞춤형 정책 챗봇")
st.markdown("정부 공공 API와 연동하여 실시간 정책 및 금융 정보를 분석해 드립니다.")

# API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    st.error("❌ 오류: 서버 환경 변수에 API 키가 설정되지 않았습니다. 메인 페이지로 돌아가 확인해주세요.")
    st.stop()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 세션 상태(대화 기록) 초기화
MSG_KEY = f"msg_{CATEGORY}"
if MSG_KEY not in st.session_state:
    st.session_state[MSG_KEY] = [{"role": "assistant", "content": f"안녕하세요! {CATEGORY}을 위한 정책 및 금융 정보를 안내해 드립니다. 어떤 지원 혜택이 궁금하신가요?"}]

if st.button("🗑️ 대화 내역 초기화"):
    st.session_state[MSG_KEY] = [{"role": "assistant", "content": f"안녕하세요! {CATEGORY}을 위한 정책 및 금융 정보를 안내해 드립니다. 어떤 지원 혜택이 궁금하신가요?"}]
    st.rerun()

st.markdown("---")

# 이전 채팅 기록 화면에 출력
for msg in st.session_state[MSG_KEY]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 질문 입력창
if prompt := st.chat_input(f"{CATEGORY} 지원 정책에 대해 물어보세요 (예: 국민취업지원제도 신청 자격이 어떻게 되나요?)"):
    st.session_state[MSG_KEY].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("공공 데이터망을 조회하여 최신 정보를 분석 중입니다..."):
            try:
                # 🚨 [주의] 현재 정부 API 명세서가 없어서 임시로 OpenAI 기본 지식만 사용하도록 연결해둠.
                # 조원들이 API URL이랑 파라미터 규격 가져오면 여기에 requests 외부 통신 로직이 추가될 예정.
                
                sys_prompt = (
                    f"당신은 대한민국 정부 지원 정책 및 금융 전문가 '청년