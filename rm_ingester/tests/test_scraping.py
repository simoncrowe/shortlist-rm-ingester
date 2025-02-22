import pytest
import requests

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

    results = set(scraping.iter_listing_urls(results_page, base_url))

    assert len(results) == 24
    assert results == {
        (27487032, 'https://rm.co.uk/properties/27487032#/?channel=RES_LET'),
        (157252958, 'https://rm.co.uk/properties/157252958#/?channel=RES_LET'),
        (157971347, 'https://rm.co.uk/properties/157971347#/?channel=RES_LET'),
        (158159990, 'https://rm.co.uk/properties/158159990#/?channel=RES_LET'),
        (158435789, 'https://rm.co.uk/properties/158435789#/?channel=RES_LET'),
        (158528063, 'https://rm.co.uk/properties/158528063#/?channel=RES_LET'),
        (158561030, 'https://rm.co.uk/properties/158561030#/?channel=RES_LET'),
        (158591858, 'https://rm.co.uk/properties/158591858#/?channel=RES_LET'),
        (158592008, 'https://rm.co.uk/properties/158592008#/?channel=RES_LET'),
        (158592122, 'https://rm.co.uk/properties/158592122#/?channel=RES_LET'),
        (158592149, 'https://rm.co.uk/properties/158592149#/?channel=RES_LET'),
        (158592308, 'https://rm.co.uk/properties/158592308#/?channel=RES_LET'),
        (158592314, 'https://rm.co.uk/properties/158592314#/?channel=RES_LET'),
        (158592644, 'https://rm.co.uk/properties/158592644#/?channel=RES_LET'),
        (158592677, 'https://rm.co.uk/properties/158592677#/?channel=RES_LET'),
        (158592707, 'https://rm.co.uk/properties/158592707#/?channel=RES_LET'),
        (158592917, 'https://rm.co.uk/properties/158592917#/?channel=RES_LET'),
        (158593142, 'https://rm.co.uk/properties/158593142#/?channel=RES_LET'),
        (158593172, 'https://rm.co.uk/properties/158593172#/?channel=RES_LET'),
        (158593412, 'https://rm.co.uk/properties/158593412#/?channel=RES_LET'),
        (158593427, 'https://rm.co.uk/properties/158593427#/?channel=RES_LET'),
        (158593526, 'https://rm.co.uk/properties/158593526#/?channel=RES_LET'),
        (158593592, 'https://rm.co.uk/properties/158593592#/?channel=RES_LET'),
        (158593811, 'https://rm.co.uk/properties/158593811#/?channel=RES_LET')
    }


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
            return mocker.Mock(content=results_page,
                               status_code=200,
                               headers={})
        elif url.startswith("https://www.rm.co.uk/properties/"):
            return mocker.Mock(content=dummy_listing,
                               status_code=200,
                               headers={})

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
            return mocker.Mock(content=results_page,
                               status_code=200,
                               headers={})
        elif url.startswith("https://www.rm.co.uk/properties/"):
            resp = mocker.Mock(status_code=400, headers={})
            resp.raise_for_status.side_effect = (
                requests.exceptions.RequestException
            )
            return resp

    mock_session.get.side_effect = get_stub

    with pytest.raises(requests.exceptions.RequestException):
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
