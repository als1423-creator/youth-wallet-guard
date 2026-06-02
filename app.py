import streamlit as st

st.set_page_config(page_title="청년지갑지킴이 메인", page_icon="💸", layout="centered")

st.title("💸 청년지갑지킴이: 맞춤형 정책 챗봇")
st.markdown("""
**환영한다! 여긴 복잡한 정부 지원 정책을 상황에 맞게 알려주는 '청년지갑지킴이' 다.**

👈 **[사용 방법]**
1. 아래 **API Key 3개**를 모두 입력해라.
2. 왼쪽 사이드바에서 너한테 맞는 **고객군**을 선택해서 들어가라.
""")

st.markdown("---")

# --- 세션 초기화 ---
for key, default in [("api_key", ""), ("youth_api_key", ""), ("fss_api_key", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- OpenAI API Key ---
st.subheader("1️⃣ OpenAI API Key")
openai_input = st.text_input(
    "ChatGPT 응답 생성에 사용됩니다 (sk-...):",
    type="password",
    value=st.session_state.api_key,
)
if openai_input != st.session_state.api_key:
    st.session_state.api_key = openai_input
    st.rerun()

if st.session_state.api_key:
    st.success("✅ OpenAI API Key 입력 완료")
else:
    st.warning("⚠️ OpenAI API Key를 입력해야 챗봇이 작동합니다.")

st.markdown("---")

# --- 온통청년 API Key ---
st.subheader("2️⃣ 온통청년 API Key")
st.caption(
    "공공데이터포털(data.go.kr)에서 **'청년정책조회서비스'** 를 검색해 신청 후 발급받은 서비스키를 입력하세요."
)
youth_input = st.text_input(
    "온통청년(청년정책조회서비스) 서비스키:",
    type="password",
    value=st.session_state.youth_api_key,
)
if youth_input != st.session_state.youth_api_key:
    st.session_state.youth_api_key = youth_input
    st.rerun()

if st.session_state.youth_api_key:
    st.success("✅ 온통청년 API Key 입력 완료")
else:
    st.info("ℹ️ 입력하지 않으면 청년정책 조회가 비활성화됩니다.")

st.markdown("---")

# --- 금융감독원 API Key ---
st.subheader("3️⃣ 금융감독원 API Key")
st.caption(
    "금융상품통합비교공시(finlife.fss.or.kr)에 회원가입 후 발급받은 API Key를 입력하세요."
)
fss_input = st.text_input(
    "금융감독원 금융상품 비교공시 API Key:",
    type="password",
    value=st.session_state.fss_api_key,
)
if fss_input != st.session_state.fss_api_key:
    st.session_state.fss_api_key = fss_input
    st.rerun()

if st.session_state.fss_api_key:
    st.success("✅ 금융감독원 API Key 입력 완료")
else:
    st.info("ℹ️ 입력하지 않으면 금융상품 비교 기능이 비활성화됩니다.")

st.markdown("---")

# --- 최종 상태 ---
ready = st.session_state.api_key and (st.session_state.youth_api_key or st.session_state.fss_api_key)
if ready:
    st.success("🚀 준비 완료! 왼쪽 사이드바에서 고객군을 선택해 챗봇을 실행해라.")
else:
    st.warning("⚠️ OpenAI Key + (온통청년 또는 금융감독원 Key 중 하나 이상)을 입력해야 합니다.")
