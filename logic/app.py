# app.py
import streamlit as st
from chat import main as chat_main
from dashboard_reviews import main as dashboard_reviews_main
from dashboard_surveys import main as dashboard_surveys_main
from rag_chat import main as rag_chat_main

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", 
    ["Chat", "Dashboard Reviews", "Dashboard Surveys", "Rag Chat"])

if page == "Chat":
    chat_main()
elif page == "Dashboard Reviews":
    dashboard_reviews_main()
elif page == "Dashboard Surveys":
    dashboard_surveys_main()
elif page == "Rag Chat":
    rag_chat_main()
