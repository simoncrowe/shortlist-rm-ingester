from os import path

import data
import pytest


@pytest.fixture(scope="session")
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
        "furnishTypes=unfurnished"
    )


@pytest.fixture(scope="session")
def results_page():
    test_dir = path.dirname(__file__)
    fixture_path = path.join(test_dir, "fixtures", "results-page.html")
    with open(fixture_path) as file_obj:
        return file_obj.read()


@pytest.fixture(scope="session")
def listing_one_page():
    test_dir = path.dirname(__file__)
    fixture_path = path.join(test_dir, "fixtures", "listing-one-page.html")
    with open(fixture_path) as file_obj:
        return file_obj.read()


@pytest.fixture(scope="session")
def listing_one_identifier():
    return 151625369


@pytest.fixture(scope="session")
def listing_one_profile():
    return data.Profile(
        text="Two Bedroom Top Floor Maisonette...",
        metadata=data.ProfileMetadata(
            url="https://www.rm.co.uk/properties/151625369",
            price="£1,700 pcm",
            location="St. Marks Road, Enfield",
            summary="2 bedroom maisonette",
        )
    )
