"""Constants used by Youfone."""
from datetime import timedelta
import json
from pathlib import Path
import random
from typing import Final

from homeassistant.const import Platform

from .models import YoufoneEnvironment

PLATFORMS: Final = [Platform.SENSOR, Platform.BINARY_SENSOR]

ATTRIBUTION: Final = "Data provided by Youfone"

DEFAULT_YOUFONE_ENVIRONMENT = YoufoneEnvironment(
    api_endpoint="https://my.youfone.be/prov/MyYoufone/MyYOufone.Wcf/v2.0/Service.svc/json",
    base_url="https://my.youfone.be",
)

BASE_HEADERS = {
    "Content-Type": "application/json",
}

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DEFAULT_COUNTRY = "be"
COUNTRY_CHOICES = ["be", "nl"]

COORDINATOR_UPDATE_INTERVAL = timedelta(minutes=110 + random.uniform(10, 20))
WEBSITE = "https://my.youfone.be/"

manifestfile = Path(__file__).parent / "manifest.json"
with open(manifestfile) as json_file:
    manifest_data = json.load(json_file)

DOMAIN = manifest_data.get("domain")
NAME = manifest_data.get("name")
VERSION = manifest_data.get("version")
ISSUEURL = manifest_data.get("issue_tracker")
STARTUP = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom component
If you have any issues with this you need to open an issue here:
{ISSUEURL}
-------------------------------------------------------------------
"""
