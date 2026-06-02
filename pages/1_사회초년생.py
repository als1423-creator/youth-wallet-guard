import streamlit as st
from utils.chat_page import render_chat_page

CATEGORY = "사회초년생"

st.set_page_config(page_title=f"{CATEGORY} 정책 챗봇", page_icon="💼")
st.title(f"💼 {CATEGORY} 맞춤형 정책 챗봇")

render_chat_page(CATEGORY)
