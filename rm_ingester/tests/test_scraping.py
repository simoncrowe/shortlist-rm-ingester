import pytest

import data
import scraping


def test_iter_page_urls(to_rent_url):
    urls = list(scraping.iter_page_urls(to_rent_url))

    for page, (base_url, page_url) in enumerate(urls, start=0):
        url, query = page_url.split("?")
        query_map = dict(pair.split("=") for pair in query.split("&"))

        assert url == "https://www.rm.co.uk/property-to-rent/find.html"
        assert len(query_map) == 9
        expected_index = str(page * 24)
        assert query_map["index"] == expected_index

    assert base_url == "https://www.rm.co.uk"


def test_iter_listing_urls(results_page):
    base_url = "https://rm.co.uk"

    results = list(scraping.iter_listing_urls(results_page, base_url))

    assert len(results) == 25  # 24 normal results + 1 featured
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


def test_iter_listings(mocker, to_rent_url, results_page):
    mock_iter_page_urls = mocker.patch("scraping.iter_page_urls")
    first_page_url = f"{to_rent_url}&index=0"
    mock_iter_page_urls.return_value = [
        ("https://www.rm.co.uk", first_page_url)
    ]
    mock_sleep = mocker.patch("scraping.time.sleep")
    mock_session_cls = mocker.patch("scraping.requests.Session")
    mock_session = mock_session_cls.return_value
    mock_session.headers = {}
    dummy_listing = (
        b"<html><head><title>foo</title></head><body><p>bar</p></body></html>"
    )

    def get_stub(url):
        if url == first_page_url:
            return mocker.Mock(content=results_page, status_code=200)
        elif url.startswith("https://www.rm.co.uk/properties/"):
            return mocker.Mock(content=dummy_listing, status_code=200)

    mock_session.get.side_effect = get_stub

    for _, listing in scraping.iter_listings(to_rent_url):
        assert listing == dummy_listing.decode()

    assert mock_session.headers["User-Agent"] in scraping.USER_AGENTS
    assert mock_session.get.call_count == 26
    assert mock_sleep.call_count == 26


def test_iter_listings_bad_page_resp(mocker, to_rent_url, results_page):
    mock_session_cls = mocker.patch("scraping.requests.Session")
    mock_session = mock_session_cls.return_value

    def get_stub(url):
        resp = mocker.Mock(status_code=400)
        resp.raise_for_status.side_effect = Exception
        return resp

    mock_session.get.side_effect = get_stub

    with pytest.raises(Exception):
        list(scraping.iter_listings(to_rent_url))

    assert mock_session.get.call_count == 1


def test_iter_listings_bad_list_resp(mocker, to_rent_url, results_page):
    mock_iter_page_urls = mocker.patch("scraping.iter_page_urls")
    first_page_url = f"{to_rent_url}&index=0"
    mock_iter_page_urls.return_value = [
        ("https://www.rm.co.uk", first_page_url)
    ]
    mock_sleep = mocker.patch("scraping.time.sleep")
    mock_session_cls = mocker.patch("scraping.requests.Session")
    mock_session = mock_session_cls.return_value
    mock_session.headers = {}

    def get_stub(url):
        if url == first_page_url:
            return mocker.Mock(content=results_page, status_code=200)
        elif url.startswith("https://www.rm.co.uk/properties/"):
            resp = mocker.Mock(status_code=400)
            resp.raise_for_status.side_effect = Exception
            return resp

    mock_session.get.side_effect = get_stub

    with pytest.raises(Exception):
        list(scraping.iter_listings(to_rent_url))

    assert mock_session.get.call_count == 2
    assert mock_sleep.call_count == 1


def test_profile_from_listing_html(mocker, listing_one_page):
    mocker.patch("scraping.BASE_LISTING_URL",
                 "https://www.rm.co.uk/properties")

    result = scraping.profile_from_listing_html(listing_one_page)

    assert result == data.Profile(
        text="Two Bedroom Top Floor Maisonette...",
        metadata=data.ProfileMetadata(
            url="https://www.rm.co.uk/properties/151625369",
            price="£1,700 pcm",
            location="St. Marks Road, Enfield",
            summary="2 bedroom maisonette",
        )
    )
