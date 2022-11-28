import jsondiff


def diff(dict_1: dict, dict_2: dict) -> dict:
    return jsondiff.diff(
        dict_1,
        dict_2,
        marshal=True,
        syntax="explicit",
    )
