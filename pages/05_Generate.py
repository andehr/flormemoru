import os
import zipfile
from typing import Dict, List

import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
from streamlithelpers import SessionObject

from chat import stream_json, generate_images, OpenAiCompletionParameters, list_models
from settings import api_key, model, model_params

st.set_page_config(page_title="Generate", page_icon=":blossom:", layout="centered")


@SessionObject("flower_names")
def flower_names(n: int = 20) -> List[Dict[str, str]]:
    with st.status(f"Generating flower names..."):
        return stream_json(f"""
        Generate a JSON array of {n} JSON objects, where each JSON object represents a random flower.
        Each of the {n} JSON objects should have the following 3 properties:
        1. "latin" (string): the latin name of the flower
        2. "common" (string): the common name of the flower.
        3. "description" (string): a short visual description of an example of this flower.
        Ensure that your response contains only valid JSON.
        """, chat_model, key, chat_model_params)


@SessionObject("flower_images")
def flower_images(flowers: List[Dict[str, str]]):
    images = []
    for flower in flowers:
        try:
            with st.spinner(f"Generating image for: {flower['common']} ({flower['latin']})..."):
                generated = generate_images(f"""
                A high quality photograph of a bunch of the following flower: 
                {flower['common']} (latin name: {flower['latin']}). Description: {flower['description']}
                """, 1, key, "dall-e-3")
                images.append((generated[0], flower))
        except:
            st.warning(f"Error generating for: {flower['common']}. Skipped")
            continue

    return images


def clean_name(name: str) -> str:
    return name.replace(" ", "-").lower().strip()


try:
    if st.secrets.load_if_toml_exists() and "openai_key" in st.secrets:
        api_key(st.secrets["openai_key"])
except:
    pass  # Fails if no secrets file specified

with st.sidebar:
    if api_key_val := st.text_input("OpenAI API key", value=api_key.get() or "", key="api_key_widget", type="password", help="Specify your OpenAI API key here to access the app's tools. Visit [here](https://openai.com/blog/openai-api) to sign up for access to OpenAI's API and get your API key."):
        api_key(api_key_val)

    all_models = list_models(api_key_val) if api_key_val else []
    models = [m for m in all_models if "gpt" in m]

    current_model = model.get()
    if current_model is not None and current_model in models:
        default_model_idx = models.index(current_model)
    else:
        default_model_idx = models.index("gpt-4") if models and "gpt-4" in models else 0
    m = st.selectbox("Model", options=models, index=default_model_idx, key="model_select", help="This app was developed using GPT-4; older models may not perform sufficiently well")
    if m:
        model(m)

    with st.expander("Model parameters"):
        model_params(OpenAiCompletionParameters("model_params"))


chat_model_params = model_params.get()
chat_model = model.get()
key = api_key.get()


st.header("Generate flowers")
if key and chat_model:

    flower_n = st.number_input("Number of flowers to generate", value=20)

    if st.button("Generate flowers", use_container_width=True):
        flower_names(flower_n)

    if flowers := flower_names.get():
        for flower in flowers:
            st.markdown(f"**{flower['common']}** ({flower['latin']}): {flower['description']}")
        if st.button("Generate images", use_container_width=True):
            flower_images(flowers)

    if images := flower_images.get():
        img_cols = st.columns(min(len(images), 5))
        for i, (image, flower) in enumerate(images):
            with img_cols[i % len(img_cols)]:
                st.image(image, caption=flower["common"] + f" ({flower['latin']})")

        if st.button("Get download link", use_container_width=True):
            temp_dir = 'temp_images'
            os.makedirs(temp_dir, exist_ok=True)
            zip_filename = "flowers.zip"

            for i, (image, flower) in enumerate(images):
                filename = f'{i}_{clean_name(flower["common"])}_{clean_name(flower["latin"])}.png'
                img = Image.open(image)
                img.save(os.path.join(temp_dir, filename))

            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file),
                                   os.path.relpath(os.path.join(root, file), os.path.join(temp_dir, '..')))

            with open(zip_filename, 'rb') as f:
                st.download_button(label='Download Images', data=f, file_name=zip_filename, mime='application/zip', use_container_width=True)

else:
    st.write("Enter your Open AI API key in the sidebar to use GPT to generate your flowers.")

