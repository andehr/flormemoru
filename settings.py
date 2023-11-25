from streamlithelpers import SessionObject

from chat import OpenAiCompletionParameters


@SessionObject("api_key")
def api_key(key: str) -> str:
    return key


@SessionObject("model_params")
def model_params(params: OpenAiCompletionParameters) -> OpenAiCompletionParameters:
    return params


@SessionObject("model")
def model(m: str) -> str:
    return m