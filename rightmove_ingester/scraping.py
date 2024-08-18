from typing import Callable, Iterator
from urllib import parse

import requests


def iter_new_listings(url: str,
                      id_is_new: Callable[[str], bool]) -> Iterator[str]:
    parsed_url = parse.urlparse(url)
    print(parsed_url.query)

    session = requests.Session()

    session.get(url)

    while False:
        yield None
