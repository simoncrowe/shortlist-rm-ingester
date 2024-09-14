import service


def test_ingest_single_listing(mocker,
                               to_rent_url,
                               listing_one_page,
                               listing_one_identifier,
                               listing_one_profile):

    mocker.patch("scraping.BASE_LISTING_URL",
                 "https://www.rm.co.uk/properties")
    results = []

    def callback_stub(identifier, profile):
        results.append((identifier, profile))

    listings = [(listing_one_identifier, listing_one_page)]

    service.ingest_listings(url=to_rent_url,
                            ingested=set(),
                            listings=listings,
                            runner_callback=callback_stub)

    assert results == [(listing_one_identifier, listing_one_profile)]
