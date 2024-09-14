import service


def test_ingest_single_listing(mocker,
                               to_rent_url,
                               listing_one_page,
                               listing_one_identifier,
                               listing_one_profile):

    mocker.patch("scraping.BASE_LISTING_URL",
                 "https://www.rm.co.uk/properties")
    ingested = set()
    results = []

    listings = [(listing_one_identifier, listing_one_page)]

    service.ingest_listings(url=to_rent_url,
                            ingested=ingested,
                            listings=listings,
                            ingest_callback=results.append)

    assert results == [listing_one_profile]
    assert ingested == {listing_one_identifier}


def test_ingest_two_listings(mocker,
                             to_rent_url,
                             listing_one_page,
                             listing_one_identifier,
                             listing_one_profile,
                             listing_two_page,
                             listing_two_identifier,
                             listing_two_profile):

    mocker.patch("scraping.BASE_LISTING_URL",
                 "https://www.rm.co.uk/properties")
    ingested = set()
    results = []

    listings = [(listing_one_identifier, listing_one_page),
                (listing_two_identifier, listing_two_page)]

    service.ingest_listings(url=to_rent_url,
                            ingested=ingested,
                            listings=listings,
                            ingest_callback=results.append)

    assert results == [listing_one_profile, listing_two_profile]
    assert ingested == {listing_one_identifier, listing_two_identifier}


def test_ingest_skips_ingested(mocker,
                               to_rent_url,
                               listing_one_page,
                               listing_one_identifier,
                               listing_two_page,
                               listing_two_identifier,
                               listing_two_profile):

    mocker.patch("scraping.BASE_LISTING_URL",
                 "https://www.rm.co.uk/properties")
    ingested = {listing_one_identifier}
    results = []

    listings = [(listing_one_identifier, listing_one_page),
                (listing_two_identifier, listing_two_page)]

    service.ingest_listings(url=to_rent_url,
                            ingested=ingested,
                            listings=listings,
                            ingest_callback=results.append)

    assert results == [listing_two_profile]
    assert ingested == {listing_one_identifier, listing_two_identifier}
