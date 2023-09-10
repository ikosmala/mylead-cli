import models
from pydantic import ValidationError
import orjson


def validate_data(data: list) -> list:
    valid_data = []
    for item in data:
        try:
            valid_item = models.Lead(**item)
            valid_data.append(valid_item.model_dump())
        except ValidationError as e:
            print(e)

    return valid_data


def data_to_file(file_name: str, data: list):
    valid_data = validate_data(data)
    with open(file_name, "wb") as f:
        json_str = orjson.dumps(valid_data, option=orjson.OPT_INDENT_2)
        f.write(json_str)


def data_from_file(file_name: str):
    with open(file_name, "rb") as f:
        json_bytes = f.read()
    print(type(json_bytes))
    # Deserialize using orjson
    data_from_json = orjson.loads(json_bytes)
    valid_data = validate_data(data_from_json)
    print(type(valid_data))
    return data_from_json
