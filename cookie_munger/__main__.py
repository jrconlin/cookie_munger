from collections import OrderedDict
import pprint
import requests
from typing import Any,Dict,List,AnyStr

from config42 import ConfigManager
from config42.handlers import ArgParse

from cookie_munger import (get_cookies, munge_cookies, scan_cookies)

def get_config() -> Dict[str, any]:
    """Read environment config vars """
    schema = [
        dict(key="verbose",
             name="Verbose",
             source=dict(argv=["-v"], argv_options=dict(action="count")),
             description="Turn on verbose logging",
             default=0,
             required=False,
             ),
        dict(key="url", 
             name="URL",
             description="The target URL to, uh, test.",
             source=dict(argv=["-u"]),
             default="",
             required=False,
             type="string",
             ),
        dict(key="iter", 
             name="Iteration",
             description="How many times to send the cookies",
             source=dict(argv=["-i"]),
             type="integer",
             default=1,
             required=False,
             ),
        dict(key="dryrun", 
             name="DryRun",
             description="Just fetch the cookies",
             source=dict(argv=["-d"], argv_options=dict(action="count")),
             default=0,
             required=False,
             ),
    ]
    config = ConfigManager(
        schema=schema,
        defaults={"config42": OrderedDict(
            [
                ('argv', dict(handler=ArgParse, schema=schema)),
                ('env', dict(prefix="CM")),
            ]
        )}
    )
    return config


def main():
    wwcd = 0
    config = get_config()
    verbose = config.get("verbose")
    target = config.get("url")
    if verbose:
        print("Targeting {}".format(target))
    cookies = get_cookies(target)
    pp = pprint.PrettyPrinter(indent=2)
    if cookies:
        scanned = scan_cookies(cookies)
        if verbose:
            pp.pprint(scanned)
            print("====")
        for i in range(0, config.get('iter')):
            munged = munge_cookies(scanned)
            if verbose:
                pp.pprint(munged)
            if not config.get('dryrun'):
                result = requests.get(target, cookies=munged)
                if result.status_code == 500:
                    wwcd += 1
    else:
        print("No cookies")
    if wwcd > 0:
        print("Winner! Winner! Chicken Dinner! {}".format(wwcd))

if __name__ == "main":
    main()