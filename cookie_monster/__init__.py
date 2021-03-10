from config42 import ConfigManager
from datetime import date

import json
import base64
import os
import random
import re
import string
import requests

from typing import Any,Dict,AnyStr

def get_config() -> Dict[str, any]:
    env_config = ConfigManager(prefix="CM_")
    return env_config


def value_parser(value: Any) -> Dict[str, any]:
    if type(value) is bool:
        return {
            "type": "bool"
        }
    if type(value) is int:
        return {
            "type": "int",
            "len": len("{}".format(value))
        }
    if type(value) is bytes:
        return {
            "type": "bytes",
            "len": len(value)
        }
    if type(value) is dict:
        result = dict()
        for bit in value.keys():
            result[bit] = value_parser(value[bit])
        return {
            "type": dict,
            "value": result
        }
    if type(value) is list:
        result = []
        for item in value:
            result.append(value_parser(item))
        return {
            "type": "list",
            "value": result,
        }
    try:
        return {
            "type": "json",
            "value": value_parser(json.loads(value))
        }
    except ValueError:
        pass
    # try base64 first, because of "=" as padding
    try:
        bits = base64.urlsafe_b64decode(value)
        return {
            "type": "b64",
            "value": value_parser(bits)
        }
    except ValueError:
        pass

    if re.match("^[0-9\.]+$", value):
        return {
            "type": "ip4"
        }
    if re.match("\d{2}:\d{2}(:\d{2})?", value):
        return {
            "type": "time"
        }
    if re.match("^[0-9a-f\:]+$", value):
        return {
            "type": "ipv6"
        }
    if re.match("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(.{1,8})?Z", value):
        return {
            "type": "date-zulu"
        }
    if re.match("\d{2}/\d{2}/\d{2}", value):
        return {
            "type": "date"
        }
    # is this an array of things?
    if "&" in value:
        arr = dict()
        for bit in value.split('&'):
            (key, val) = bit.split('=')
            arr[key] = value_parser(val)
        return{
            "type": "array",
            "div": ";" if ";" in value else ",",
            "value": arr
        }
    # 🤷🏻‍♂️
    print(value)
    return {
        "type": "string",
        "len": len(value)
    }


def scan_cookies(cookies:Dict[str, str]) -> Dict[str, any]:
    result = dict()
    for cookie in cookies.keys():
        value = cookies.get(cookie)
        if value:
            result[cookie] = value_parser(value)
        else:
            result[cookie] = ""
    return result


def make_bool(**kwargs):
    return True


def make_int(len=10, **kwargs):
    return range(1,10**len)


def make_bytes(len=10, **kwargs):
    return os.urandom(len)


def encode_b64(value={}, **kwargs):
    return base64.urlsafe_b64encode(json.dumps(value))


def make_ip4(**kwargs):
    return "{}.{}.{}.{}".format(
        random.randint(1, 255),
        random.randint(1, 255),
        random.randint(1, 255),
        random.randint(1, 255),
        )


def make_ip6(**kwargs):
    hextets = []
    for i in range(1, 8):
        hextets.append(hex(random.randint(0,2**16))[2:].zfill(4))
    return hextets.join(":")


def make_date(**kwargs):
    return "{}/{}/{}".format(
        random.randint(1,12).zfill(2),
        random.randint(1,28).zfill(2),
        random.randint(1970, date.today().year)
    )


def make_zulu(**kwargs):
    return "{}/{}/{}T{}:{}:{}.{}Z".format(
        random.randint(1,12).zfill(2),
        random.randint(1,28).zfill(2),
        random.randint(1970, date.today().year),
        random.randint(0, 23).zfill(2),
        random.randint(0, 59).zfill(2),
        random.randint(0, 59).zfill(2),
        random.randint(0, 999999).zfill(6),
    )


def make_string(len=10, **kwargs):
    return "".join(
        random.choice(
            string.ascii_letters + string.digits
        ) for x in range(1, len))


def make_list(len=10, value=[], **kwargs):        
    return '["list"]'

def make_dict(value={}, **kwargs):
    return {"fake": "dict"}

def make_json(value={}, **kwargs):
    return {"fake": "json"}

def make_array(value={}, **kwargs):
    return "fake=array"


fake_vals = {
    "bool": make_bool,
    "int": make_int,
    "bytes": make_bytes,
    "dict": make_dict,
    "list": make_list,
    "array": make_array,
    "json": make_json,
    "b64": encode_b64,
    "ip4": make_ip4,
    "ip6": make_ip6,
    "date": make_date,
    "date_zulu": make_zulu,
    "string": make_string,
}


def get_cookies(config):
    if False:
        req = requests.get(config.get('url', 'http://example.com'))
        return req.cookies
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
	"userBehaviors": "[1014,222]"
    }


def bake_cookies(cookie_defs): 
    print("Pending...")

def main():
    config = get_config()
    cookies = get_cookies(config)
    if cookies:
        scanned = scan_cookies(cookies)
        print(scanned)
        print(bake_cookies(scanned))
    else:
        print("No cookies")


main()