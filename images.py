import io
import os
from pathlib import Path
from typing import List, Dict

import streamlit as st


@st.cache_resource(ttl="1hr")
def get_image_data(directory: str = "images") -> List[Dict]:
    with st.spinner("Loading flowers..."):
        image_data_list = []

        # Create a Path object for the directory
        dir_path = Path(directory)

        # List all PNG, JPG, JPEG files in the directory
        for file_path in dir_path.iterdir():
            if file_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                filename = file_path.stem  # Gets the filename without the extension

                # Parse the filename
                parts = filename.split("_")
                if len(parts) != 3:
                    continue  # Skip files that don't match the expected format

                id_, latin, common = parts

                # Read the image and convert to BytesIO
                with open(file_path, "rb") as img_file:
                    image_bytes = io.BytesIO(img_file.read())

                # Create the dictionary
                image_dict = {
                    "id": id_,
                    "common": common.replace("-", " ").title(),
                    "latin": latin.replace("-", " ").title(),
                    "image": image_bytes,
                    "path": file_path
                }

                # Append the dictionary to the list
                image_data_list.append(image_dict)

        return image_data_list
