from dataclasses import dataclass


@dataclass
class BuildingFilter:
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    radius: float | None = None
    lat_min: float | None = None
    lat_max: float | None = None
    lon_min: float | None = None
    lon_max: float | None = None
