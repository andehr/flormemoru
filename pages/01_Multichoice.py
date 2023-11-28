import random
import time

import streamlit as st
from streamlithelpers import SessionObject

from images import get_image_data

st.set_page_config(layout="wide")

MODE_IMAGE_COMMON = "image (by common name)"
MODE_IMAGE_LATIN = "image (by latin name)"
MODE_TEXT_COMMON = "common name"
MODE_TEXT_LATIN = "latin name"


@SessionObject("setup")
def current_setup(image_data):
    answers = random.sample(image_data, choice_size)
    correct_answer_idx = random.choice(range(len(answers)))
    return answers, correct_answer_idx


image_data = get_image_data()
n = len(image_data)

st.title("Choose the correct flower")

mode_col, options_n_col = st.columns(2, gap="large")

with mode_col:
    mode = st.selectbox("Mode", options=[MODE_IMAGE_COMMON, MODE_IMAGE_LATIN, MODE_TEXT_COMMON, MODE_TEXT_LATIN])

with options_n_col:
    choice_size = st.slider("Choices", value=min(n, 4), min_value=2, max_value=n)

if st.button("Start", use_container_width=True, type="primary"):
    current_setup(image_data)

if setup := current_setup.get():
    answers, correct_answer_idx = setup
    correct_answer = answers[correct_answer_idx]

    if mode == MODE_IMAGE_COMMON:
        st.subheader(f"Which image is a {correct_answer['common']}?")
    elif mode == MODE_IMAGE_LATIN:
        st.subheader(f"Which image is a {correct_answer['latin']}?")
    elif mode == MODE_TEXT_COMMON:
        st.subheader(f"What's the common name of this flower?")
    elif mode == MODE_TEXT_LATIN:
        st.subheader(f"What's the latin name of this flower?")

    num_cols = min(5, choice_size) if mode in [MODE_IMAGE_COMMON, MODE_IMAGE_LATIN] else 2
    choice_cols = st.columns(num_cols)

    if mode in [MODE_TEXT_COMMON, MODE_TEXT_LATIN]:
        with choice_cols[1]:
            st.image(correct_answer["image"])

    status = st.empty()

    for i, answer in enumerate(answers):
        col = choice_cols[i % num_cols] if mode in [MODE_IMAGE_COMMON, MODE_IMAGE_LATIN] else choice_cols[0]
        with col:
            if mode == MODE_IMAGE_COMMON or mode == MODE_IMAGE_LATIN:
                st.image(answer["image"])

            name = answer["latin"] if mode == MODE_TEXT_LATIN else answer["common"]

            button_name = "Choose" if mode in [MODE_IMAGE_COMMON, MODE_IMAGE_LATIN] else name

            if st.button(button_name, key=f"choice_button_{i}", use_container_width=True):
                if i == correct_answer_idx:
                    st.toast("Correct! :white_check_mark:")
                    status.success("Well done!")
                    current_setup(image_data)
                    time.sleep(0.7)
                    st.rerun()
                else:
                    status.warning("Try again!")
                    st.toast("Wrong! :repeat:")

