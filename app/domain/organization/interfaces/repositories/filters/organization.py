from dataclasses import dataclass


@dataclass
class OrganizationFilter:
    name: str | None = None
    address: str | None = None
    activity_name: str | None = None
    limit: int = 10
    offset: int = 0
