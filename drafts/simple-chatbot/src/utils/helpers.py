import yaml
from pydantic import BaseModel, Field, create_model
from .settings import *



def read_yml_file(file_path) -> dict:
    if not file_path.endswith('.yml') and not file_path.endswith('.yaml'):
        raise ValueError("The file must be a .yml or .yaml file")
    with open(file_path, 'r') as file:
        prompt_data = yaml.safe_load(file)
    return prompt_data



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

        field_type = type_mapping.get(type_key, str)
        fields[field_name] = (field_type, Field(default_value, description=description))
    DynamicModel = create_model('DynamicModel', **fields)
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