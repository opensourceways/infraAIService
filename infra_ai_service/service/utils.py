#!/usr/bin/python3

import json
from collections import OrderedDict


def _get_and_check_name(info: dict):
    try:
        return info["name"]
    except Exception:
        # TODO: log the exception
        return ""


def _update_json(xml, spec):
    res = {}
    all_keys = set(xml.keys()).union(set(spec.keys()))
    for key in all_keys:
        if key in xml and key in spec:
            # dont process other type
            if isinstance(spec[key], list) and isinstance(xml[key], list):
                res[key] = spec[key] + xml[key]
            else:
                res[key] = spec[key]
        elif key in xml:
            res[key] = xml[key]
        else:
            res[key] = spec[key]

    return res


def update_json(j_xml: dict, j_spec: dict):
    """
    The API /feature-insert/ only process one spec, so the j_spec
    must be one length.
    """
    if not j_xml:
        return j_spec

    spec_info = j_spec[1]
    spec_name = _get_and_check_name(spec_info)

    for i, info in j_xml.items():
        xml_name = _get_and_check_name(info)
        if spec_name != "" and xml_name == spec_name:
            j_spec[1] = _update_json(info, spec_info)
            break

    return j_spec


def write_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def convert_to_str(data: dict):
    ordered_keys = [
        "name",
        "version",
        "summary",
        "description",
        "url",
        "requires",
        "binaryList",
        "provides",
        "buildRequires",
        "source0",
        "macro_names",
        "email_names",
        "class_names",
        "path_names",
        "url_names",
    ]
    ordered_dict = OrderedDict()
    for key in ordered_keys:
        if key in data:
            ordered_dict[key] = data[key]

    return json.dumps(ordered_dict)
