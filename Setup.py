import streamlit as st
from openai import AuthenticationError
from streamlit_extras.switch_page_button import switch_page

from chat import OpenAiCompletionParameters, list_models
from settings import api_key, model_params, model

st.set_page_config(
    page_title="Setup",
    page_icon=":house:",
    layout="centered"
)


try:
    if st.secrets.load_if_toml_exists() and "openai_key" in st.secrets:
        api_key(st.secrets["openai_key"])
except:
    pass  # Fails if no secrets file specified


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

