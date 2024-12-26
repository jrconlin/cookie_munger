from collections import OrderedDict
import os
import requests
from typing import Any, Dict, List, AnyStr
import logging


from config42 import ConfigManager
from config42.handlers import ArgParse

from cookie_munger import get_includes, munge_cookies, scan_cookies


def get_logging() -> logging.Logger:
    log = logging.basicConfig(
        level=logging.getLevelNamesMapping().get(
            os.environ.get("PYTHON_LOG", "debug").upper(), "DEBUG"
        )
    )
    return logging.getLogger("cookie_munger")


def get_config() -> Dict[str, any]:
    """Read environment config vars"""
    schema = [
        dict(
            key="url",
            name="URL",
            description="The target URL to, uh, test.",
            source=dict(argv=["-u"]),
            default="",
            required=False,
            type="string",
        ),
        dict(
            key="iter",
            name="Iteration",
            description="How many times to send the cookies",
            source=dict(argv=["-i"]),
            type="integer",
            default=1,
            required=False,
        ),
        dict(
            key="dryrun",
            name="DryRun",
            description="Just fetch the cookies",
            source=dict(argv=["-d"], argv_options=dict(action="count")),
            default=0,
            required=False,
        ),
    ]
    config = ConfigManager(
        schema=schema,
        defaults={
            "config42": OrderedDict(
                [
                    ("argv", dict(handler=ArgParse, schema=schema)),
                    ("env", dict(prefix="CM")),
                ]
            )
        },
    )
    return config


def main():
    wwcd = 0
    print("here")
    logging = get_logging()
    config = get_config()
    target = config.get("url")
    all_targets = get_includes(target)
    import pdb

    pdb.set_trace()
    for loaded in all_targets.items():
        logging.info("Targeting {}".format(target))
        scanned = scan_cookies(loaded)
        munged = munge_cookies(scanned)elements
        logging.debug(munged)
        if not config.get("dryrun"):
            result = requests.get(target, cookies=munged)
            if result.status_code == 500:
                wwcd += 1
    else:
        logging.error("No cookies")
    if wwcd > 0:
        print("Winner! Winner! Chicken Dinner! {}".format(wwcd))


if __name__ == "__main__":
    main()
