import streamlit as st
from openai import OpenAI
import time
import os

# 타겟 카테고리 설정
CATEGORY = "사회초년생" 

st.set_page_config(page_title=f"{CATEGORY} 정책 챗봇", page_icon="💡")
st.title(f"💡 {CATEGORY} 맞춤형 정책 챗봇")

# 1. API 키 확인
if not st.session_state.get("api_key"):
    st.warning("👈 왼쪽 사이드바 맨 위 'app'을 눌러서 메인 페이지로 돌아간 뒤, OpenAI API Key를 먼저 입력해라.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# 2. 독립적인 세션 메모리 구축
VS_ID = f"vs_{CATEGORY}"
ASST_ID = f"asst_{CATEGORY}"
TH_ID = f"th_{CATEGORY}"
MSG = f"msg_{CATEGORY}"

if VS_ID not in st.session_state: st.session_state[VS_ID] = None
if ASST_ID not in st.session_state: st.session_state[ASST_ID] = None
if TH_ID not in st.session_state: st.session_state[TH_ID] = None
if MSG not in st.session_state: st.session_state[MSG] = []

# 3. 데이터 폴더 경로 설정 (깃허브에 미리 올려둔 PDF 파일 위치)
data_folder = f"data/{CATEGORY}"

# 4. 초기화 버튼
if st.button("🗑️ 대화 내역 초기화"):
    if st.session_state[VS_ID]:
        try:
            client.beta.vector_stores.delete(st.session_state[VS_ID])
        except:
            pass
    st.session_state[VS_ID] = None
    st.session_state[ASST_ID] = None
    st.session_state[TH_ID] = None
    st.session_state[MSG] = []
    st.rerun()

st.markdown("---")

# 5. 로컬 PDF 파일 자동 로드 및 AI 뇌(Vector Store)에 쑤셔 박기
if not st.session_state[VS_ID]:
    # 폴더가 없거나 비어있으면 경고 띄우고 정지
    if not os.path.exists(data_folder) or not any(f.endswith('.pdf') for f in os.listdir(data_folder)):
        st.error(f"❌ 서버 에러: '{data_folder}' 경로에 PDF 파일이 없습니다. 개발자(조장)에게 문의하세요.")
        st.stop()

    with st.spinner("서버에 저장된 정책 데이터를 AI 뇌에 자동 장전하는 중..."):
        file_streams = []
        try:
            vector_store = client.beta.vector_stores.create(name=f"DB_{CATEGORY}")
            
            # 폴더 안에 있는 모든 PDF 파일을 열어서 리스트에 담기
            pdf_files = [f for f in os.listdir(data_folder) if f.endswith('.pdf')]
            file_streams = [open(os.path.join(data_folder, f), "rb") for f in pdf_files]
            
            # OpenAI 서버로 일괄 업로드
            client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id,
                files=file_streams
            )
            st.session_state[VS_ID] = vector_store.id
            
            # 환각 방지 프롬프트
            sys_prompt = (
                f"너는 대한민국 정부 지원 정책 전문가 '청년지갑구조대'다. "
                f"현재 질문하는 사용자는 '{CATEGORY}'이다. "
                f"반드시 업로드된 문서의 내용만을 기반으로 답변해라. "
                f"지원 조건, 신청 자격, 혜택 금액을 표나 번호 매기기로 알아듣기 쉽게 요약하고, 문서에 없는 내용은 절대 지어내지 마라."
            )
            
            assistant = client.beta.assistants.create(
                name=f"{CATEGORY} 챗봇",
                instructions=sys_prompt,
                model="gpt-4o-mini",
                tools=[{"type": "file_search"}],
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
            )
            st.session_state[ASST_ID] = assistant.id
            
            thread = client.beta.threads.create()
            st.session_state[TH_ID] = thread.id
            
        except Exception as e:
            st.error(f"데이터 자동 로드 중 에러 발생: {e}")
        finally:
            # 메모리 누수 방지용 파일 닫기
            for f in file_streams:
                f.close()

# 6. 채팅 UI 및 질의응답 로직
if st.session_state[VS_ID]:
    for msg in st.session_state[MSG]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input(f"{CATEGORY} 정책에 대해 물어보세요 (예: 월세 지원 조건이 어떻게 돼?)"):
        st.session_state[MSG].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("규정집 뒤지는 중..."):
                try:
                    client.beta.threads.messages.create(
                        thread_id=st.session_state[TH_ID],
                        role="user",
                        content=prompt
                    )
                    
                    run = client.beta.threads.runs.create(
                        thread_id=st.session_state[TH_ID],
                        assistant_id=st.session_state[ASST_ID]
                    )
                    
                    while run.status in ['queued', 'in_progress']:
                        time.sleep(1)
                        run = client.beta.threads.runs.retrieve(
                            thread_id=st.session_state[TH_ID],
                            run_id=run.id
                        )
                    
                    if run.status == 'completed':
                        messages = client.beta.threads.messages.list(
                            thread_id=st.session_state[TH_ID]
                        )
                        answer = messages.data[0].content[0].text.value
                        st.markdown(answer)
                        st.session_state[MSG].append({"role": "assistant", "content": answer})
                    else:
                        st.error(f"답변 생성 실패. 상태 코드: {run.status}")
                except Exception as e:
                    st.error(f"질문 처리 중 에러: {e}")