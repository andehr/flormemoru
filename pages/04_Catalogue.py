import base64
import random
import time
from io import BytesIO
from typing import Dict, List, Optional

import streamlit as st
import pandas as pd
from PIL import Image
from streamlithelpers import SessionObject

from images import get_image_data

st.set_page_config(page_title="Catalogue", page_icon=":blossom:", layout="centered")

image_data = get_image_data()


@st.cache_data()
def query(sort: str, filter: str):
    return [i for i in sorted(image_data, key=lambda i: i["common"].lower() if sort == "common name" else i["latin"].lower())
            if not filter or filter in i["common"].lower() or filter in i["latin"].lower()]


sort_col, filter_col, num_col = st.columns(3)
sort = sort_col.selectbox("Sort by", options=["common name", "latin name"])
filter = filter_col.text_input("Search")
filter = filter if filter is None else filter.lower()
num_col = num_col.slider("Columns", min_value=1, max_value=6, value=3)

image_cols = st.columns(num_col)

for i, image in enumerate(query(sort, filter)):
    col = image_cols[i % num_col]
    with col:
        st.write(image["common"])
        st.caption(image["latin"])
        st.image(image["image"])

