import random
import time
from typing import Dict, List, Optional

import streamlit as st
from streamlithelpers import SessionObject

from images import get_image_data

st.set_page_config(layout="centered")

MODE_COMMON = "common name"
MODE_LATIN = "latin name"


@SessionObject("current_spelling_flower")
def current_flower(s: Dict) -> Dict:
    return s


@SessionObject("current_revealed")
def current_revealed(r: Optional[List[int]]) -> Optional[List[int]]:
    return r


def reveal_letter(name):
    revealed = current_revealed.get()
    if len(revealed) == len(name):
        return revealed
    options = [i for i in range(len(name)) if i not in revealed]
    choice = random.choice(options)
    return revealed + [choice]


current_revealed.init([])


image_data = get_image_data()

mode = st.selectbox("Mode", options=[MODE_COMMON, MODE_LATIN])

if st.button("Start", use_container_width=True):
    current_flower(random.choice(image_data))
    current_revealed([])

if flower := current_flower.get():
    st.header(f"How do you spell the {mode} of the following flower?")
    st.image(flower["image"])

    name = flower["common"] if mode == MODE_COMMON else flower["latin"]

    if st.sidebar.button("Hint", use_container_width=True):
        current_revealed(reveal_letter(name))

    revealed = current_revealed.get()
    letter_cols = st.columns(len(name))

    for i, (letter, col) in enumerate(zip(name, letter_cols)):
        with col:
            if letter == " ":
                st.header(" ")
            elif i in revealed:
                st.header(letter)
            else:
                st.header(":question:")

    answer = st.text_input("Answer")

    if st.button("Submit", disabled=not answer, use_container_width=True):
        if answer.strip().lower() == name.lower():
            st.toast("Correct! :white_check_mark:")
            time.sleep(0.7)
            current_flower(random.choice(image_data))
            current_revealed([])
            st.rerun()
        else:
            st.toast("Wrong! :repeat:")
