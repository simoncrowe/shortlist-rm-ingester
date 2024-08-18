import pytest

# import scraping


@pytest.fixture
def to_rent_url():
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
