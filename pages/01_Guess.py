import os
import io
import random

from PIL import Image
from streamlithelpers import SessionObject

import streamlit as st


@SessionObject("current_guess_image")
def current_image(img):
    return img


@st.cache_resource(ttl="1hr")
def get_image_data(directory: str = "images"):
    image_data_list = []

    # List all PNG files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            # Parse the filename
            parts = filename[:-4].split("_")  # Remove .png and split
            if len(parts) != 3:
                continue  # Skip files that don't match the expected format

            id_, common, latin = parts

            # Read the image and convert to BytesIO
            with open(os.path.join(directory, filename), "rb") as img_file:
                image_bytes = io.BytesIO(img_file.read())

            # Create the dictionary
            image_dict = {
                "id": id_,
                "common": common.replace("-", " ").title(),
                "latin": latin.replace("-", " ").title(),
                "image": image_bytes
            }

            # Append the dictionary to the list
            image_data_list.append(image_dict)

    return image_data_list


image_data = get_image_data()

if st.button("Guess!", use_container_width=True, type="primary"):
    current_image(random.choice(image_data))

if image_dict := current_image.get():

    st.image(image_dict["image"])

if st.toggle("Show answer"):
    st.write(image_dict["common"])
    st.caption(image_dict["latin"])

