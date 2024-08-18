import pytest
import scraping


@pytest.fixture
def rightmove_url():
    return (
        "https://www.rightmove.co.uk/property-to-rent/find.html?"
        "locationIdentifier=REGION%5E87490&"
        "maxBedrooms=2&"
        "minBedrooms=1&"
        "maxPrice=2000&"
        "index=24&"
        "propertyTypes=bungalow%2Cdetached%2Cflat&"
        "includeLetAgreed=false&"
        "mustHave=&"
        "dontShow=houseShare%2Cretirement%2Cstudent&"
        "furnishTypes=unfurnished&"
        "keywords="
    )


def test_no_new_results(rightmove_url):
    def always_not_new(_):
        return False

    listings = list(scraping.iter_new_listings(rightmove_url, always_not_new))

    assert listings == []
