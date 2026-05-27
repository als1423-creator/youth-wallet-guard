import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="청년지갑지킴이 메인", page_icon="💸", layout="centered")

st.title("💸 청년지갑지킴이: 맞춤형 정책 챗봇")
st.markdown("""
**환영한다! 여긴 복잡한 정부 지원 정책을 상황에 맞게 알려주는 '청년지갑지킴' 다.**

👈 **[사용 방법]**
1. 밑에 **OpenAI API Key**를 입력해라. 
2. 키를 입력 했으면, 왼쪽 사이드바 메뉴에서 너한테 맞는 **고객군(사회초년생, 대학생 등)**을 선택해서 들어가라.
""")

st.markdown("---")

# API Key 세션 메모리 초기화
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# API Key 입력창 (비밀번호처럼 가리기)
api_key_input = st.text_input("🔑 OpenAI API Key를 입력하세요 (sk-...):", type="password", value=st.session_state.api_key)

# 입력값이 바뀌면 메모리에 저장하고 새로고침
if api_key_input != st.session_state.api_key:
    st.session_state.api_key = api_key_input
    st.rerun()

# 상태 메시지 출력
if st.session_state.api_key:
    st.success("✅ API Key 장착 완료! 왼쪽 사이드바 메뉴를 눌러서 챗봇을 실행해라.")
else:
    st.warning("⚠️ API Key를 입력해야 사이드바 챗봇들이 정상적으로 작동한다.")