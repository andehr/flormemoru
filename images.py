import io
import os
from typing import List, Dict

import streamlit as st


@st.cache_resource(ttl="1hr")
def get_image_data(directory: str = "images") -> List[Dict]:
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
