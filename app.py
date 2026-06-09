import streamlit as st
import os
from dotenv import load_dotenv

# 환경 변수 로드 (.env 금고 열기 - 정부 API 키용)
load_dotenv()

# 페이지 기본 설정
st.set_page_config(page_title="청년지갑구조대 메인", page_icon="💸", layout="centered")

# 🔥 [핵심 추가] 사이드바에 사용자 전용 OpenAI 키 입력창 생성
with st.sidebar:
    st.header("🔑 시스템 설정")
    st.markdown("챗봇을 사용하려면 본인의 OpenAI API 키가 필요합니다.")
    # type="password"로 설정해서 입력한 키가 화면에 **** 로 가려지게 만듦
    user_openai_key = st.text_input("OpenAI API Key 입력:", type="password")
    
    if user_openai_key:
        # 사용자가 키를 입력하면 세션(메모리)에 저장해서 모든 페이지에서 돌려쓰게 만듦
        st.session_state["USER_OPENAI_KEY"] = user_openai_key
        st.success("✅ 키가 임시 저장되었습니다.")
    else:
        st.warning("키를 입력해 주세요.")

st.title("💸 청년지갑구조대: 실시간 맞춤형 정책 챗봇")
st.markdown("""
**환영합니다! 청년지갑구조대는 흩어져 있는 청년 지원 정책과 금융 정보를 사용자의 상황에 맞게 안내해 드리는 서비스입니다.**

본 서비스는 **온통청년** 및 **금융감독원**의 공공 API를 연동하여 실시간으로 최신 데이터를 제공합니다.

👈 **[서비스 이용 방법]**
1. **좌측 사이드바에 본인의 OpenAI API Key를 먼저 입력해 주세요.** (키는 서버에 저장되지 않고 즉시 폐기됩니다.)
2. 좌측 메뉴에서 본인에게 해당하는 **타겟 고객군(사회초년생, 대학생 등)**을 선택해 주세요.
3. 궁금한 정책이나 대출 정보(예: "청년 전세자금 대출 조건을 알려주세요")를 채팅창에 입력해 주세요.
""")

st.markdown("---")

# 시스템 공공 API Key 세팅 상태 확인
if os.getenv("YOUTH_API_KEY") or os.getenv("FSS_API_KEY"):
    st.success("✅ 공공 데이터망(정부 서버) 연동 시스템 정상.")
else:
    st.error("❌ 서버 오류: 시스템 환경 변수에 공공 API 키가 누락되었습니다. 관리자에게 문의하세요.")