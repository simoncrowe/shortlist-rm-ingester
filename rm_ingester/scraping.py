import random
import re
import time
from typing import Iterator
from urllib import parse

import bs4
import requests

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",  # noqa
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", # noqa
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15" # noqa
]
MIN_WAIT_SECS = 1
MAX_WAIT_SECS = 3
LISTING_PATH_ID_REGEX = r"^\/properties\/([0-9]+)#/"


def iter_listings(first_page_url: str) -> Iterator[tuple[int, str]]:
    session = requests.Session()
    session.headers["User-Agent"] = random.choice(USER_AGENTS)

    for base_url, page_url in iter_page_urls(first_page_url):

        page_resp = session.get(page_url)
        if page_resp.status_code != 200:
            break

        time.sleep(random.randrange(MIN_WAIT_SECS, MAX_WAIT_SECS))

        for listing_id, listing_url in iter_listing_urls(page_resp.content,
                                                         base_url):
            listing_resp = session.get(listing_url)
            yield listing_id, listing_resp.content

            time.sleep(random.randrange(MIN_WAIT_SECS, MAX_WAIT_SECS))


def iter_page_urls(first_page_url: str) -> Iterator[tuple[str, str]]:
    url = parse.urlparse(first_page_url)
    base_url = f"{url.scheme}://{url.hostname}"
    query_map = parse.parse_qs(url.query)

    # Scrape up to the last page of 24 results (42)
    for index in range(0, 1008, 24):
        page_query = parse.urlencode({**query_map, "index": index}, doseq=True)
        yield base_url, f"{base_url}{url.path}?{page_query}"


def iter_listing_urls(result_page: str,
                      base_url: str) -> Iterator[tuple[int, str]]:

    soup = bs4.BeautifulSoup(result_page, "html.parser")

    for a in soup.find_all("a", class_="propertyCard-link"):
        relative_link = a.get("href")
        identifier = re.search(LISTING_PATH_ID_REGEX, relative_link).group(1)
        yield int(identifier), base_url + relative_link
