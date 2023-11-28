import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title="Setup",
    page_icon=":house:",
    layout="centered"
)


st.title("Welcome to Flormemoru")

st.subheader("Where we learn to remember flowers.")

st.image("./flormemoru_logo.jpg")

if st.button("Begin", use_container_width=True, type="primary"):
    switch_page("Multichoice")
