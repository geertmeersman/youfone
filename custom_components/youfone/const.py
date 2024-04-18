"""Constants used by Youfone."""
import json
from pathlib import Path
from typing import Final

from homeassistant.const import Platform

PLATFORMS: Final = [Platform.SENSOR, Platform.BINARY_SENSOR]

ATTRIBUTION: Final = "Data provided by Youfone"

BASE_HEADERS = {
    "Content-Type": "application/json",
}

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

COORDINATOR_MIN_UPDATE_INTERVAL = 2  # hours
WEBSITE = "https://my.youfone.nl/"

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
