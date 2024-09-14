import dataclasses


@dataclasses.dataclass(frozen=True)
class ProfileMetadata:
    url: str
    price: str
    location: str
    summary: str


@dataclasses.dataclass(frozen=True)
class Profile:
    text: str
    metadata: ProfileMetadata
