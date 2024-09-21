import logging
import typing

import data
import protocols
import scraping

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def ingest_listings(listings: typing.Iterable[tuple[int, str]],
                    ingest_callback: typing.Callable[[data.Profile], None],
                    ingested: protocols.SetStore):

    for identifier, listing in listings:
        if identifier in ingested:
            logger.info(f"Listing {identifier} has already been ingested. "
                        "Exiting...")
            break

        profile = scraping.profile_from_listing_html(listing)

        ingest_callback(profile)
        ingested.add(identifier)
