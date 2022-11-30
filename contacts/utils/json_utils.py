import json

import jsondiff


def diff(dict_1: dict, dict_2: dict) -> dict:
    return jsondiff.diff(
        dict_1,
        dict_2,
        marshal=True,
        syntax="explicit",
    )


def dumps(dct: dict) -> str:
    return json.dumps(dct, ensure_ascii=False, indent=2)
