import typing

import protocols
import scraping


def ingest_listings(url: str,
                    ingested: protocols.SetStore,
                    listings: typing.Iterable[tuple[int, str]],
                    runner_callback: typing.Callable):

    for identifier, listing in listings:
        if identifier in ingested:
            continue

        profile = scraping.profile_from_listing_html(listing)

        runner_callback(identifier, profile)
