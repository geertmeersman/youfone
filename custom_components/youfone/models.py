"""Models used by Youfone."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict


class YoufoneConfigEntryData(TypedDict):
    """Config entry for the Youfone integration."""

    username: str | None
    password: str | None
    scan_interval: int | None


@dataclass
class YoufoneEnvironment:
    """Class to describe a Youfone environment."""

    api_endpoint: str
    base_url: str


@dataclass
class YoufoneItem:
    """Youfone item model."""

    name: str = ""
    key: str = ""
    type: str = ""
    state: str = ""
    device_key: str = ""
    device_name: str = ""
    device_model: str = ""
    data: dict = field(default_factory=dict)
    extra_attributes: dict = field(default_factory=dict)
    native_unit_of_measurement: str = None
