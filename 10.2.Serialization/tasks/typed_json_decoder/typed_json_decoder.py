import typing as tp
import json

from decimal import Decimal

def decode(value: tp.Any) -> tp.Any:
    if value is None:
        return None
    if isinstance(value, dict) and "__custom_key_type__" in value.keys():
        to_type = value.get("__custom_key_type__")
        answer_dict = {}
        for key, inside in value.items():
            value = decode(inside)
            if key == "__custom_key_type__":
                continue
            match to_type:
                case "int":
                    answer_dict[int(key)] = inside
                case "float":
                    answer_dict[float(key)] = inside
                case "decimal":
                    answer_dict[Decimal(key)] = inside
        return answer_dict
    else:
        if isinstance(value, list):
            for i in range(len(value)):
                value[i] = decode(value[i])
        if isinstance(value, dict):
            for k, v in value.items():
                value[k] = decode(v)
        return value


def decode_typed_json(json_value: str) -> tp.Any:
    """
    Returns deserialized object from json string.
    Checks __custom_key_type__ in object's keys to choose appropriate type.

    :param json_value: serialized object in json format
    :return: deserialized object
    """
    dict_value = json.loads(json_value)
    print(dict_value)

    return decode(dict_value)


