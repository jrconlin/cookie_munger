from bs4 import BeautifulSoup
from collections import OrderedDict
from config42 import ConfigManager
from config42.handlers import ArgParse
from datetime import date

import json
import base64
import logging
import os
import random
import re
import string
import requests

import traceback

from typing import Any, Dict, List, AnyStr


def value_parser(value: Any) -> Dict[str, any]:
    """Try to determine what the cookie ingredients are"""
    if type(value) is bool:
        return {"type": "bool"}
    if type(value) is int:
        return {"type": "int", "len": len("{}".format(value))}
    if type(value) is bytes:
        return {"type": "bytes", "len": len(value)}
    if type(value) is dict:
        result = dict()
        for bit in value.keys():
            result[bit] = value_parser(value[bit])
        return {"type": "dict", "value": result}
    if type(value) is list:
        result = []
        for item in value:
            result.append(value_parser(item))
        return {
            "type": "list",
            "value": result,
        }
    try:
        return {"type": "json", "value": value_parser(json.loads(value))}
    except ValueError:
        pass
    if re.match(r"^[0-9\.]+$", value):
        return {"type": "ip4"}
    if re.match(r"\d{2}:\d{2}(:\d{2})?", value):
        return {"type": "time"}
    if re.match(r"^[0-9a-f\:]+$", value):
        return {"type": "ipv6"}
    if re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(.{1,8})?Z", value):
        return {"type": "date_zulu"}
    if re.match(r"\d{2}/\d{2}/\d{2}", value):
        return {"type": "date"}
    # is this an array of things?
    if "&" in value and "=" in value:
        arr = dict()
        for bit in value.split("&"):
            bits = bit.split("=")
            if len(bits) > 1:
                arr[bits[0]] = value_parser(bits[1])
            else:
                arr[bits[0]] = ""
        return {"type": "array", "div": ";" if ";" in value else ",", "value": arr}
    # try base64 first, because of "=" as padding
    if re.match(r"^[a-zA-Z0-9\-\+/_]+=?$", value):
        try:
            bits = base64.urlsafe_b64decode(value)
            try:
                bits = bits.decode("utf-8")
            except ValueError:
                pass
            return {"type": "b64", "value": value_parser(bits)}
        except ValueError:
            pass
    # 🤷🏻‍♂️
    return {"type": "string", "len": len(value)}


def scan_cookies(cookies: Dict[str, str]) -> Dict[str, any]:
    """Scan each cookie, and determine what it's made of"""
    result = dict()
    for cookie in cookies.keys():
        value = cookies.get(cookie)
        if value:
            result[cookie] = value_parser(value)
        else:
            result[cookie] = ""
    return result


# Various generic mungers
def make_bool(**kwargs) -> bool:
    return True


def make_int(len: int = 10, **kwargs) -> int:
    return random.choice(range(1, 10**len))


def make_bytes(len: int = 10, **kwargs) -> bytes:
    return os.urandom(len)


def encode_b64(value: Dict[str, any] = {}, **kwargs) -> str:
    val = derive(value)
    if type(val) is str:
        val = val.encode("utf-8")
    return base64.urlsafe_b64encode(val).decode()


def make_ipv4(**kwargs) -> str:
    return "{}.{}.{}.{}".format(
        random.randint(1, 255),
        random.randint(1, 255),
        random.randint(1, 255),
        random.randint(1, 255),
    )


def make_ipv6(**kwargs) -> str:
    hextets = []
    for i in range(1, 8):
        hextets.append(hex(random.randint(0, 2**16))[2:].zfill(4))
    return ":".join(hextets)


def make_date(**kwargs) -> str:
    return "{:02d}/{:02d}/{:04d}".format(
        random.randint(1, 12),
        random.randint(1, 28),
        random.randint(1970, date.today().year),
    )


def make_zulu(**kwargs) -> str:
    return "{:02d}/{:02d}/{:04d}T{:02d}:{:02d}:{:02d}.{:06d}Z".format(
        random.randint(1, 12),
        random.randint(1, 28),
        random.randint(1970, date.today().year),
        random.randint(0, 23),
        random.randint(0, 59),
        random.randint(0, 59),
        random.randint(0, 999999),
    )


def make_string(len: int = 10, **kwargs) -> str:
    return "".join(
        random.choice(string.ascii_letters + string.digits) for x in range(1, len)
    )


def make_list(len: int = 10, value: Dict = [], **kwargs) -> List[any]:
    result = []
    for item in value:
        val = derive(value=item)
        result.append(val)
    return result


def make_dict(value: Dict = {}, **kwargs) -> Dict[str, any]:
    result = dict()
    if type(value) is not dict:
        return value
    for key, val in value.items():
        result[key] = derive(val)
    return result


def make_json(value: Dict = {}, **kwargs):
    return json.dumps(derive(value))


def make_array(value: Dict = {}, **kwargs) -> str:
    result = []
    for key, val in value.items():
        result.append("{}={}".format(key, derive(val)))
    return "&".join(result)


# Pretty sure there's a smarter way to do this...
fake_vals = {
    "bool": make_bool,
    "int": make_int,
    "bytes": make_bytes,
    "dict": make_dict,
    "list": make_list,
    "array": make_array,
    "json": make_json,
    "b64": encode_b64,
    "ipv4": make_ipv4,
    "ipv6": make_ipv6,
    "date": make_date,
    "date_zulu": make_zulu,
    "string": make_string,
}


def get_cookies(req=[None | requests.Response]) -> Dict[str, any]:
    """Eventually fetch some cookies. For now, use a stock set from Ace"""
    if req:
        return req.cookies.get_dict()
    else:
        return {
            "_mzPc": "eyJjb3JyZWxhdGlvbklkIjoiNDYwODQ1MWY5MWVjNDlmNDgxYzFmYzRmZWZiMTk1ODkiLCJpcEFkZHJlc3MiOiIyNjAwOjE3MDA6MTE1MDo4YTZmOjM1ODY6ZjgzYjpiMWE4OmJiNGIiLCJpc0RlYnVnTW9kZSI6ZmFsc2UsImlzQ3Jhd2xlciI6ZmFsc2UsImlzTW9iaWxlIjpmYWxzZSwiaXNUYWJsZXQiOmZhbHNlLCJpc0Rlc2t0b3AiOnRydWUsInZpc2l0Ijp7InZpc2l0SWQiOiJzcUpKT2pmT2lFQ0h1NTd2NzNnNUdnIiwidmlzaXRvcklkIjoiWGFaS0NydnpRa2VTSmQ5Y1ZkTEtwUSIsImlzVHJhY2tlZCI6ZmFsc2UsImlzVXNlclRyYWNrZWQiOmZhbHNlfSwidXNlciI6eyJpc0F1dGhlbnRpY2F0ZWQiOmZhbHNlLCJ1c2VySWQiOiJjZmJlMTFmNzk4MjI0ZGFmOGFjNjc1ZWY2ZWRjNjFhYiIsImZpcnN0TmFtZSI6IiIsImxhc3ROYW1lIjoiIiwiZW1haWwiOiIiLCJpc0Fub255bW91cyI6dHJ1ZSwiYmVoYXZpb3JzIjpbMTAxNCwyMjJdfSwidXNlclByb2ZpbGUiOnsidXNlcklkIjoiY2ZiZTExZjc5ODIyNGRhZjhhYzY3NWVmNmVkYzYxYWIiLCJmaXJzdE5hbWUiOiIiLCJsYXN0TmFtZSI6IiIsImVtYWlsQWRkcmVzcyI6IiIsInVzZXJOYW1lIjoiIn0sImlzRWRpdE1vZGUiOmZhbHNlLCJpc0FkbWluTW9kZSI6ZmFsc2UsIm5vdyI6IjIwMjEtMDMtMDlUMjM6NTM6NDMuMzg3ODMyMloiLCJjcmF3bGVySW5mbyI6eyJpc0NyYXdsZXIiOmZhbHNlLCJjYW5vbmljYWxVcmwiOiIvaG9tZSJ9LCJjdXJyZW5jeVJhdGVJbmZvIjp7fX0=",
            "_mzvr": "XaZKCrvzQkeSJd9cVdLKpQ",
            "_mzvs": "nn",
            "_mzvt": "sqJJOjfOiECHu57v73g5Gg",
            "closestStoreCode": "16192",
            "recentlyViewed": "7502578",
            "sb-sf-at-prod": "pt=&at=MAXacwhjRLX0xo4rmKZNQnAThzX1V2TmcvRXFI+cyJDs+Kf78Rc/ivPEsTC9drWxVmq2gKI6Dl1oWJ/HdJY+2BhkyBV+r5fM9YJRsuTXlUGWheI6SNS8IKj9KI4w2tY8d96njLuTyTuozRK0D5tvmfBQ5qWfp8fFq+EZRIKG7wXZ7xwfGLIlgBBhiqUpevq8Wgy94pkIQSKvj8oPYfCw33MqO/VORvTqYNOdH4+mzaIa9L4CLFR+dzJItWmRmkOgEk0k5ctRNtMXK2gVuTKwjxMcVEHAsjBY1IuB/fXk8xuZ+hWBpkQqcKkYPTtfDg7H",
            "sb-sf-at-prod-s": "pt=&at=MAXacwhjRLX0xo4rmKZNQnAThzX1V2TmcvRXFI+cyJDs+Kf78Rc/ivPEsTC9drWxVmq2gKI6Dl1oWJ/HdJY+2BhkyBV+r5fM9YJRsuTXlUGWheI6SNS8IKj9KI4w2tY8d96njLuTyTuozRK0D5tvmfBQ5qWfp8fFq+EZRIKG7wXZ7xwfGLIlgBBhiqUpevq8Wgy94pkIQSKvj8oPYfCw33MqO/VORvTqYNOdH4+mzaIa9L4CLFR+dzJItWmRmkOgEk0k5ctRNtMXK2gVuTKwjxMcVEHAsjBY1IuB/fXk8xuZ+hWBpkQqcKkYPTtfDg7H&dt=2021-03-09T23:29:10.9286050Z",
            "userBehaviors": "[1014,222]",
        }


def get_includes(target: str = None) -> Dict[str, Dict[str, any]]:
    log = logging.getLogger("cookie_munger")
    results = {}
    if target:
        log.debug(f"Scanning {target}")
        # First get the list of includes
        resp = requests.get(target).content
        results[target] = requests.get(target).cookies.get_dict()
        parsed = BeautifulSoup(resp, "html.parser")
        items = parsed.find_all("script")
        log.debug(f".. {len(items)} scripts...")
        for item in items:
            domain = item.attrs.get("src")
            if domain and not domain.startswith("/"):
                if domain not in results:
                    try:
                        results[domain] = requests.get(domain).cookies.get_dict()
                        log.debug(f".... {domain} {len(results[domain])} cookies")
                    except requests.exceptions.MissingSchema:
                        import pdb

                        pdb.set_trace()
                        print(domain)

        items = parsed.find_all("img")
        log.debug(f".. {len(items)} imgs...")
        for item in items:
            domain: str = item.attrs.get("href")
            if domain and not domain.startswith("/"):
                if domain not in results:
                    try:
                        results[domain] = requests.get(domain).cookies.get_dict()
                        log.debug(f".... {domain} {len(results[domain])} cookies")
                    except requests.exceptions.MissingSchema:
                        import pdb

                        pdb.set_trace()
                        print(domain)
    return results


def derive(value: Dict[str, any]) -> Any:
    """Make a fake version of whatever we think should go into the cookie"""
    if value == "":
        return ""
    if type(value) is list:
        return make_list(value)
    func = fake_vals.get(value.get("type"))
    if func is None:
        return make_dict(value=value)
    val = value.get("value")
    return func(value=val, len=value.get("len"))


def munge_cookies(cookie_defs):
    result = dict()
    for key, value in cookie_defs.items():
        try:
            result[key] = derive(value)
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            exit()
    return result
