from dataclasses import dataclass


@dataclass
class ActivityFilter:
    name: str | None = None
    parent_id: str | None = None
