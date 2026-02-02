import json
import functools
import yaml
from pydantic import BaseModel, Field, create_model
from .settings import *



@functools.lru_cache(maxsize=32)
def read_yml_file(file_path) -> dict:
    """Read a YAML file and cache results by file path.

    Caching avoids repeated disk reads during Streamlit reruns.
    """
    if not file_path.endswith('.yml') and not file_path.endswith('.yaml'):
        raise ValueError("The file must be a .yml or .yaml file")
    with open(file_path, 'r') as file:
        prompt_data = yaml.safe_load(file)
    return prompt_data


_pydantic_model_cache: dict[str, BaseModel] = {}


def map_dict_to_pydantic(schema: dict) -> BaseModel:
    """
        The dict schema should be in the format:
        {
            "field_name": {
                "type": "data_type_as_string",
                "default": default_value,
                "description": "Description of the field"
            },
            ...
        }
    """
    # Use a simple JSON-keyed cache to avoid rebuilding identical models
    try:
        cache_key = json.dumps(schema, sort_keys=True)
    except TypeError:
        cache_key = None
    if cache_key and cache_key in _pydantic_model_cache:
        return _pydantic_model_cache[cache_key]
    fields = {}
    type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
    }

    for field_name, field_info in schema.items():
        # Hỗ trợ 2 dạng:
        # 1. Đầy đủ: {"field": {"type": "str", "default": ..., "description": "..."}}
        # 2. Rút gọn: {"field": "str"}
        if isinstance(field_info, dict):
            type_key = field_info.get("type", "str")
            default_value = field_info.get("default", ...)
            description = field_info.get("description", "")
        else:
            # Dạng rút gọn: chỉ cung cấp kiểu dưới dạng string
            type_key = str(field_info)
            default_value = ...
            description = ""

        try:
            field_type = type_mapping[type_key]
        except KeyError:
            raise ValueError(f"Unsupported type '{type_key}' for field '{field_name}'")
        fields[field_name] = (field_type, Field(default_value, description=description))
    DynamicModel = create_model('DynamicModel', **fields)
    if cache_key is not None:
        _pydantic_model_cache[cache_key] = DynamicModel
    return DynamicModel



def define_api_base_url(provider: str) -> str:
    match provider:
        case "Ollama":
            return "http://localhost:11434/v1/"
        case "Groq":
            return "https://api.groq.com/openai/v1"
        case "Gemini":
            return "https://generativelanguage.googleapis.com/v1beta/openai/"
        case _:
            return "https://api.openai.com/v1/"