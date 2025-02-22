import json
import os
import random
import re
import time
from typing import Iterator
from urllib import parse

import bs4
import requests
import structlog

import data

BASE_LISTING_URL = os.getenv("BASE_LISTING_URL", "")
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
PAGE_MODEL_ASSIGNMENT_JS = "window.PAGE_MODEL = "

logger = structlog.getLogger(__name__)


def iter_listings(first_page_url: str) -> Iterator[tuple[int, str]]:
    session = requests.Session()
    session.headers["User-Agent"] = random.choice(USER_AGENTS)

    for base_url, page_url in iter_page_urls(first_page_url):
        page_resp = session.get(page_url)
        page_resp.raise_for_status()
        logger.debug("Got results page", response_headers=page_resp.headers)

        time.sleep(random.randrange(MIN_WAIT_SECS, MAX_WAIT_SECS))

        page = page_resp.content.decode()

        if not (urls := list(iter_listing_urls(page, base_url))):
            return

        for listing_id, listing_url in urls:
            listing_resp = session.get(listing_url)

            listing_resp.raise_for_status()
            logger.debug("Got listing page",
                         url=listing_url,
                         response_headers=listing_resp.headers)

            yield listing_id, listing_resp.content.decode()

            time.sleep(random.randrange(MIN_WAIT_SECS, MAX_WAIT_SECS))


def iter_page_urls(first_page_url: str) -> Iterator[tuple[str, str]]:
    url = parse.urlparse(first_page_url)
    base_url = f"{url.scheme}://{url.hostname}"
    query_map = parse.parse_qs(url.query)

    # Scrape up to the last page of 24 results (page 42)
    for index in range(0, 1008, 24):
        page_query = parse.urlencode({**query_map, "index": index}, doseq=True)
        yield base_url, f"{base_url}{url.path}?{page_query}"


def iter_listing_urls(result_page: str,
                      base_url: str) -> Iterator[tuple[int, str]]:

    soup = bs4.BeautifulSoup(result_page, "html.parser")
    if not (search := soup.find("div", {"id": "propertySearch"})):
        return
    query = {"data-test": "property-details"}
    for a in search.find_all("a", attrs=query):  # type: ignore
        relative_link = a.get("href")
        if not (match := re.search(LISTING_PATH_ID_REGEX, relative_link)):
            continue
        identifier = match.group(1)
        yield (int(identifier), base_url + relative_link)


def profile_from_listing_html(page: str) -> data.Profile:
    model_line = next(line for line in page.splitlines()
                      if line.strip().startswith(PAGE_MODEL_ASSIGNMENT_JS))
    model_json = model_line.split(PAGE_MODEL_ASSIGNMENT_JS)[-1]
    model_data = json.loads(model_json)

    return data.Profile(
        text=model_data["propertyData"]["text"]["description"],
        metadata=data.ProfileMetadata(
            price=model_data["propertyData"]["prices"]["primaryPrice"],
            location=model_data["propertyData"]["address"]["displayAddress"],
            summary=model_data["propertyData"]["text"]["propertyPhrase"],
            url=f"{BASE_LISTING_URL}/{model_data['propertyData']['id']}"
        )
    )
