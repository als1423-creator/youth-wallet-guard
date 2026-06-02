"""카테고리별 챗봇 페이지 공통 렌더링 함수"""
import streamlit as st
from openai import OpenAI
from . import youth_center_api, fss_api


def render_chat_page(category: str):
    # 1. OpenAI API 키 확인
    if not st.session_state.get("api_key"):
        st.warning("👈 왼쪽 사이드바 맨 위 'app'을 눌러서 메인 페이지로 돌아간 뒤, OpenAI API Key를 먼저 입력해라.")
        st.stop()

    youth_key = st.session_state.get("youth_api_key", "")
    fss_key   = st.session_state.get("fss_api_key", "")
    client    = OpenAI(api_key=st.session_state.api_key)

    # 2. 세션 키 설정
    CTX_KEY = f"ctx_{category}"
    MSG_KEY = f"msg_{category}"

    if CTX_KEY not in st.session_state:
        st.session_state[CTX_KEY] = None
    if MSG_KEY not in st.session_state:
        st.session_state[MSG_KEY] = []

    # 3. 초기화 버튼
    if st.button("🗑️ 대화 내역 초기화"):
        st.session_state[CTX_KEY] = None
        st.session_state[MSG_KEY] = []
        st.rerun()

    st.markdown("---")

    # 4. API 키 없음 안내
    if not youth_key and not fss_key:
        st.error("❌ 메인 페이지에서 **온통청년 API Key** 또는 **금융감독원 API Key** 중 최소 하나를 먼저 입력해라.")
        st.stop()

    # 5. 정책 데이터 로드 (세션당 최초 1회)
    if not st.session_state[CTX_KEY]:
        with st.spinner("🔍 정부 API에서 최신 정책 데이터를 실시간으로 불러오는 중..."):
            context_parts = []

            if youth_key:
                policies = youth_center_api.fetch_policies(youth_key, category)
                if policies:
                    context_parts.append(youth_center_api.format_for_context(policies))
                    st.toast(f"온통청년 정책 {len(policies)}건 로드 완료", icon="✅")
                else:
                    st.warning("⚠️ 온통청년 API에서 데이터를 불러오지 못했습니다. API 키를 확인하세요.")

            if fss_key:
                fss_ctx = fss_api.format_for_context(fss_key, category)
                if fss_ctx:
                    context_parts.append(fss_ctx)
                    st.toast("금융감독원 금융상품 로드 완료", icon="✅")
                else:
                    st.warning("⚠️ 금융감독원 API에서 데이터를 불러오지 못했습니다. API 키를 확인하세요.")

            if not context_parts:
                st.error("❌ 정책 데이터를 불러오지 못했습니다. API 키가 올바른지 확인하세요.")
                st.stop()

            st.session_state[CTX_KEY] = "\n\n".join(context_parts)

    # 6. 채팅 UI
    for msg in st.session_state[MSG_KEY]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(f"{category} 관련 정책을 물어보세요 (예: 월세 지원 조건이 어떻게 돼?)"):
        st.session_state[MSG_KEY].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("정책 찾는 중..."):
                try:
                    sys_content = (
                        f"너는 대한민국 정부 지원 정책 전문가 '청년지갑구조대'다. "
                        f"현재 질문하는 사용자는 '{category}'이다. "
                        f"아래 [정책 데이터]만을 근거로 답변해라. "
                        f"지원 조건·신청 자격·혜택 금액을 표나 번호 매기기로 알아듣기 쉽게 요약해라. "
                        f"데이터에 없는 내용은 절대 지어내지 말고 '제공된 데이터에 해당 정보가 없습니다'라고 솔직하게 말해라.\n\n"
                        f"=== 정책 데이터 ===\n{st.session_state[CTX_KEY]}"
                    )

                    messages = [{"role": "system", "content": sys_content}]
                    # 최근 12개 메시지(6턴)만 포함
                    for h in st.session_state[MSG_KEY][:-1][-12:]:
                        messages.append({"role": h["role"], "content": h["content"]})
                    messages.append({"role": "user", "content": prompt})

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    st.session_state[MSG_KEY].append({"role": "assistant", "content": answer})

                except Exception as e:
                    st.error(f"질문 처리 중 에러: {e}")
