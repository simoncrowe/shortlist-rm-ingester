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

    assert len(results) == 25
    assert results == {
        (87135699, 'https://rm.co.uk/properties/87135699#/?channel=RES_LET'),
        (114626912, 'https://rm.co.uk/properties/114626912#/?channel=RES_LET'),
        (125788652, 'https://rm.co.uk/properties/125788652#/?channel=RES_LET'),
        (157381913, 'https://rm.co.uk/properties/157381913#/?channel=RES_LET'),
        (158937452, 'https://rm.co.uk/properties/158937452#/?channel=RES_LET'),
        (159234344, 'https://rm.co.uk/properties/159234344#/?channel=RES_LET'),
        (159462437, 'https://rm.co.uk/properties/159462437#/?channel=RES_LET'),
        (159719024, 'https://rm.co.uk/properties/159719024#/?channel=RES_LET'),
        (159766613, 'https://rm.co.uk/properties/159766613#/?channel=RES_LET'),
        (159893033, 'https://rm.co.uk/properties/159893033#/?channel=RES_LET'),
        (159989135, 'https://rm.co.uk/properties/159989135#/?channel=RES_LET'),
        (159989972, 'https://rm.co.uk/properties/159989972#/?channel=RES_LET'),
        (159990008, 'https://rm.co.uk/properties/159990008#/?channel=RES_LET'),
        (159992048, 'https://rm.co.uk/properties/159992048#/?channel=RES_LET'),
        (159992444, 'https://rm.co.uk/properties/159992444#/?channel=RES_LET'),
        (159992603, 'https://rm.co.uk/properties/159992603#/?channel=RES_LET'),
        (159992699, 'https://rm.co.uk/properties/159992699#/?channel=RES_LET'),
        (159993188, 'https://rm.co.uk/properties/159993188#/?channel=RES_LET'),
        (159993224, 'https://rm.co.uk/properties/159993224#/?channel=RES_LET'),
        (159994016, 'https://rm.co.uk/properties/159994016#/?channel=RES_LET'),
        (159994241, 'https://rm.co.uk/properties/159994241#/?channel=RES_LET'),
        (159994874, 'https://rm.co.uk/properties/159994874#/?channel=RES_LET'),
        (159994979, 'https://rm.co.uk/properties/159994979#/?channel=RES_LET'),
        (159995372, 'https://rm.co.uk/properties/159995372#/?channel=RES_LET'),
        (159995486, 'https://rm.co.uk/properties/159995486#/?channel=RES_LET')
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
