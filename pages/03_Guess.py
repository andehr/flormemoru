import random

import streamlit as st
from streamlithelpers import SessionObject

from images import get_image_data

st.set_page_config(layout="centered")


@SessionObject("current_guess_image")
def current_image(img):
    return img


image_data = get_image_data()

st.title("Guess the flower")

if st.button("Guess!", use_container_width=True, type="primary"):
    current_image(random.choice(image_data))

if image_dict := current_image.get():

    st.image(image_dict["image"])

if st.toggle("Show answer"):
    st.header(image_dict["common"])
    st.subheader(f"_{image_dict['latin']}_")

