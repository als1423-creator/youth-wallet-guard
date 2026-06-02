import streamlit as st
from utils.chat_page import render_chat_page

CATEGORY = "군 전역 예정자"

st.set_page_config(page_title=f"{CATEGORY} 정책 챗봇", page_icon="🪖")
st.title(f"🪖 {CATEGORY} 맞춤형 정책 챗봇")

render_chat_page(CATEGORY)
