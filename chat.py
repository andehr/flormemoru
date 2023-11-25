import base64
from io import BytesIO
from typing import Literal, List, Dict
import json

import streamlit as st
from json_repair import repair_json
from openai import OpenAI

ShapeLiteral = Literal["square", "portrait", "landscape"]
QualityLiteral = Literal["standard", "hd"]
StyleLiteral = Literal["vivid", "natural"]


class OpenAiCompletionParameters:
    def __init__(self, name):
        self.name = name
        self.top_p = st.slider("top_p", value=1.0, min_value=0.0, max_value=1.0, key=f"top_p:{self.name}", help="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass. So `0.1` means only the tokens comprising the top `10%` probability mass are considered. We generally recommend altering this or `temperature` but not both. Defaults to `1.0`")
        self.temperature = st.slider("temperature", value=1.0, min_value=0.0, max_value=2.0, key=f"temperature:{self.name}", help="What sampling temperature to use, between `0` and `2`. Higher values like `0.8` will make the output more random, while lower values like `0.2` will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both. Defaults to `1.0`")
        self.presence_penalty = st.slider("presence_penalty", value=0.0, min_value=-2.0, max_value=2.0, key=f"presence_penalty:{self.name}", help="Number between `-2.0` and `2.0`. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Defaults to `0.0`")
        self.frequency_penalty = st.slider("frequency_penalty", value=0.0, min_value=-2.0, max_value=2.0, key=f"frequency_penalty:{self.name}", help="Number between `-2.0` and `2.0`. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Defaults to `0.0`")
        self.max_tokens = st.number_input("max_tokens", value=2048, min_value=100, max_value=8192, key=f"max_tokens:{self.name}", help="The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. Defaults to `512`")

    def create_chat_completion(self, model: str, messages: List[Dict], api_key: str, stream=True, functions=None, tools=None):
        if functions:  # annoying that we can't just pass None without error (at least pre-v1 anyways)
            return chat_client(api_key).chat.completions.create(messages=messages, model=model, stream=stream, functions=functions,
                                                                top_p=self.top_p, temperature=self.temperature, presence_penalty=self.presence_penalty,
                                                                frequency_penalty=self.frequency_penalty, max_tokens=self.max_tokens)
        elif tools:
            return chat_client(api_key).chat.completions.create(messages=messages, model=model, stream=stream, tools=[{"type": "function", "function": f} for f in tools],
                                                                top_p=self.top_p, temperature=self.temperature,
                                                                presence_penalty=self.presence_penalty, frequency_penalty=self.frequency_penalty, max_tokens=self.max_tokens)
        else:
            return chat_client(api_key).chat.completions.create(model=model, messages=messages, stream=stream,
                                                                top_p=self.top_p, temperature=self.temperature, presence_penalty=self.presence_penalty,
                                                                frequency_penalty=self.frequency_penalty, max_tokens=self.max_tokens)


@st.cache_resource()
def chat_client(api_key: str):
    return OpenAI(api_key=api_key)


@st.cache_data(ttl="1h")
def list_models(api_key: str) -> List[str]:
    return [m.id for m in chat_client(api_key).models.list().data]


def stream_json(prompt: str, model: str, api_key: str, model_params=None, existing_messages: List[Dict] = None, container=None):
    """
    Stream the JSON from a chat model response into a streamlit container. When stream completes, repair the JSON, strip any
    markdown ```json``` syntax, then return the parsed object from the json.
    TODO: Doesn't yet use the force JSON parameter.
    """
    json_placeholder = st.empty() if container is None else container
    full_json = ""
    messages = [{"role": "system", "content": prompt}]
    if existing_messages:
        messages += content_role_only_list(existing_messages)
    for response in model_params.create_chat_completion(model, messages, api_key) if model_params is not None else default_chat_completion(model, messages, api_key):
        if content := response.choices[0].delta.content:
            full_json += content
        json_placeholder.code(full_json + "▌", language="json")
    json_placeholder.code(full_json, language="json")
    return json.loads(repair_json(strip_json_markdown_tag(full_json)))


def strip_json_markdown_tag(json_string: str):
    """
    Strips triple backtick json markdown markers if present.
    """
    if json_string.startswith("```json") and json_string.endswith("```"):
        print(json_string[7:-3].strip())
        return json_string[7:-3].strip()
    else:
        return json_string


def content_role_only_list(msgs):
    return [extract_only_api_props(m) for m in msgs if m is not None]


def extract_only_api_props(msg):
    valid = {}
    for prop in ["role", "name", "content", "tool_calls", "function_call", "tool_call_id"]:
        if prop in msg:
            valid[prop] = msg[prop]
    return valid



def generate_images(prompt: str, n: int, api_key: str, model="dall-e-2", shape: ShapeLiteral = "square", quality: QualityLiteral = "standard", style: StyleLiteral = "vivid"):
    if model == "dall-e-2":
        response = chat_client(api_key).images.generate(prompt=prompt, model=model, n=n, size=image_size(model, shape), response_format="b64_json")
        return [b64_json_image_to_bytes_io(encoded) for encoded in response.data]
    elif model == "dall-e-3":
        images = []
        for i in range(n):
            response = chat_client(api_key).images.generate(prompt=prompt, model=model, n=1, size=image_size(model, shape), response_format="b64_json", quality=quality, style=style)
            images.append(b64_json_image_to_bytes_io(response.data[0]))
        return images
    else:
        raise ValueError(f"Unknown image model {model}")


def b64_json_image_to_bytes_io(b64_image):
    return BytesIO(base64.b64decode(b64_image.b64_json))


def image_size(model: str = "dall-e-2", shape: ShapeLiteral = "square") -> Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]:

    if model == "dall-e-2":
        return "1024x1024"
    elif model == "dall-e-3":
        match shape:
            case "square":
                return "1024x1024"
            case "landscape":
                return "1792x1024"
            case "portrait":
                return "1024x1792"
            case _:
                raise ValueError(f"Unknown shape: {shape}")
    else:
        raise ValueError(f"Unknown model: {model}")
