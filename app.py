import streamlit as st
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 페이지 기본 설정
st.set_page_config(page_title="청년지갑구조대 메인", page_icon="💸", layout="centered")

st.title("💸 청년지갑구조대: 실시간 맞춤형 정책 챗봇")
st.markdown("""
**환영합니다! 청년지갑구조대는 흩어져 있는 청년 지원 정책과 금융 정보를 사용자의 상황에 맞게 안내해 드리는 서비스입니다.**

본 서비스는 **온통청년** 및 **금융감독원**의 공공 API를 연동하여 실시간으로 최신 데이터를 제공합니다.

👈 **[서비스 이용 방법]**
1. 좌측 사이드바 메뉴에서 본인에게 해당하는 **타겟 고객군(사회초년생, 대학생 등)**을 선택해 주세요.
2. 궁금한 정책이나 대출 정보(예: "청년 전세자금 대출 조건을 알려주세요")를 채팅창에 입력해 주세요.
3. AI 챗봇이 실시간으로 공공 데이터를 분석하여 가장 정확한 조건과 혜택을 요약해 드립니다.
""")

st.markdown("---")

# 시스템 API Key 세팅 상태 확인
if os.getenv("OPENAI_API_KEY") and (os.getenv("YOUTH_API_KEY") or os.getenv("FSS_API_KEY")):
    st.success("✅ 시스템 정상: 공공 API 및 AI 연동이 완료되었습니다. 좌측 메뉴를 통해 챗봇을 시작해 주세요.")
else:
    st.error("❌ 서버 오류: 시스템 환경 변수에 API 키가 누락되었습니다. 관리자에게 문의하세요.")