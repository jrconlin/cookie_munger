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
            os.environ.get("PYTHON_LOG", "INFO").upper(), "INFO"
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
        dict(
            key="count",
            name="HammerCount",
            description="How many times to feed the munged cookies back to the site",
            source=dict(argv=["-c", "--count"]),
            default=1,
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
    log = get_logging()
    config = get_config()
    target = config.get("url")
    all_targets = get_includes(target)
    for target, cookies in all_targets.items():
        if len(cookies) == 0:
            next
        log.info(f"🎯 Targeting {target}")
        scanned = scan_cookies(cookies)
        for i in range(0, config.count):
            munged = munge_cookies(scanned)
            if len(munged):
                log.debug(f"🤢 munged: {munged}")
            if not config.get("dryrun"):
                log.info(f"🤮 Munging cookies to {target}")
                result = requests.get(target, cookies=munged)
                if result.status_code == 500:
                    wwcd += 1
    else:
        log.error("No cookies")
    if wwcd > 0:
        print("Winner! Winner! Chicken Dinner! {}".format(wwcd))


if __name__ == "__main__":
    main()
