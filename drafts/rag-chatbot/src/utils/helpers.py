from pydantic import BaseModel, Field, create_model



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
        "bool": bool
    }
    for field_name, field_info in schema.items():
        field_type = type_mapping.get(field_info.get("type"), str)
        default_value = field_info.get("default", ...)
        description = field_info.get("description", "")
        fields[field_name] = (field_type, Field(default_value, description=description))
    DynamicModel = create_model('DynamicModel', **fields)
    return DynamicModel