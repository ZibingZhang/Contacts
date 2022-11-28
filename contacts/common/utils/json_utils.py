import jsondiff
from common.utils import dataclasses_utils


def diff(
    dict_1: dataclasses_utils.DataClassJsonMixin,
    dict_2: dataclasses_utils.DataClassJsonMixin,
) -> dict:
    return jsondiff.diff(
        dict_1.to_dict(),
        dict_2.to_dict(),
        marshal=True,
        syntax="explicit",
    )
