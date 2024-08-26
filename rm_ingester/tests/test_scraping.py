from os import path
from urllib import parse

import pytest
import scraping


@pytest.fixture
def to_rent_url():
    return (
        "https://www.rm.co.uk/property-to-rent/find.html?"
        "locationIdentifier=REGION%5E87490&"
        "maxBedrooms=2&"
        "minBedrooms=1&"
        "maxPrice=2000&"
        "propertyTypes=bungalow%2Cdetached%2Cflat&"
        "includeLetAgreed=false&"
        "dontShow=houseShare%2Cretirement%2Cstudent&"
        "furnishTypes=unfurnished&"
    )


@pytest.fixture(scope="module")
def results_page():
    test_dir = path.dirname(__file__)
    fixture_path = path.join(test_dir, "fixtures", "results-page.html")
    with open(fixture_path) as file_obj:
        return file_obj.read()


def test_iter_page_urls(to_rent_url):
    urls = list(scraping.iter_page_urls(to_rent_url))

    for page, (base_url, page_url) in enumerate(urls, start=0):
        parsed_url = parse.urlparse(page_url)

        assert parsed_url.scheme == "https"
        assert parsed_url.hostname == "www.rm.co.uk"

        parsed_qs = parse.parse_qs(parsed_url.query)
        assert len(parsed_qs) == 9

        expected_index = str(page * 24)
        assert parsed_qs["index"] == [expected_index]

    assert base_url == "https://www.rm.co.uk"


def test_iter_listing_urls(results_page):
    base_url = "https://rm.co.uk"

    results = list(scraping.iter_listing_urls(results_page, base_url))

    assert results == [
        (151268708, "https://rm.co.uk/properties/151268708#/?channel=RES_LET"),
        (151626689, "https://rm.co.uk/properties/151626689#/?channel=RES_LET"),
        (151626230, "https://rm.co.uk/properties/151626230#/?channel=RES_LET"),
        (151625894, "https://rm.co.uk/properties/151625894#/?channel=RES_LET"),
        (151625804, "https://rm.co.uk/properties/151625804#/?channel=RES_LET"),
        (120819272, "https://rm.co.uk/properties/120819272#/?channel=RES_LET"),
        (151625567, "https://rm.co.uk/properties/151625567#/?channel=RES_LET"),
        (151625369, "https://rm.co.uk/properties/151625369#/?channel=RES_LET"),
        (151625381, "https://rm.co.uk/properties/151625381#/?channel=RES_LET"),
        (151329554, "https://rm.co.uk/properties/151329554#/?channel=RES_LET"),
        (151625171, "https://rm.co.uk/properties/151625171#/?channel=RES_LET"),
        (150066716, "https://rm.co.uk/properties/150066716#/?channel=RES_LET"),
        (151625024, "https://rm.co.uk/properties/151625024#/?channel=RES_LET"),
        (151624967, "https://rm.co.uk/properties/151624967#/?channel=RES_LET"),
        (151624928, "https://rm.co.uk/properties/151624928#/?channel=RES_LET"),
        (151624880, "https://rm.co.uk/properties/151624880#/?channel=RES_LET"),
        (151624841, "https://rm.co.uk/properties/151624841#/?channel=RES_LET"),
        (151624832, "https://rm.co.uk/properties/151624832#/?channel=RES_LET"),
        (151624775, "https://rm.co.uk/properties/151624775#/?channel=RES_LET"),
        (151624742, "https://rm.co.uk/properties/151624742#/?channel=RES_LET"),
        (151624670, "https://rm.co.uk/properties/151624670#/?channel=RES_LET"),
        (58973337, "https://rm.co.uk/properties/58973337#/?channel=RES_LET"),
        (151624205, "https://rm.co.uk/properties/151624205#/?channel=RES_LET"),
        (151624097, "https://rm.co.uk/properties/151624097#/?channel=RES_LET"),
        (151624082, "https://rm.co.uk/properties/151624082#/?channel=RES_LET"),
    ]
