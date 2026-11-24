"""Youfone integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from pathlib import Path
import random

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.storage import STORAGE_DIR, Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from requests.exceptions import ConnectionError  # type: ignore

from .client import YoufoneClient
from .const import COORDINATOR_MIN_UPDATE_INTERVAL, DOMAIN, PLATFORMS
from .exceptions import (
    BadCredentialsException,
    YoufoneException,
    YoufoneServiceException,
)
from .models import YoufoneItem

_LOGGER = logging.getLogger(__name__)


def get_coordinator_update_interval(minimum=COORDINATOR_MIN_UPDATE_INTERVAL):
    """Get the coordinator update interval."""
    minimum = max(
        minimum, COORDINATOR_MIN_UPDATE_INTERVAL
    )  # Ensure minimum is not lower than COORDINATOR_MIN_UPDATE_INTERVAL
    return timedelta(minutes=(minimum * 60 + random.uniform(5, 30)))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Youfone from a config entry."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {}

    for platform in PLATFORMS:
        hass.data[DOMAIN][entry.entry_id].setdefault(platform, set())

    client = YoufoneClient(
        email=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
    )

    storage_dir = Path(f"{hass.config.path(STORAGE_DIR)}/{DOMAIN}")
    if storage_dir.is_file():
        storage_dir.unlink()
    storage_dir.mkdir(exist_ok=True)
    store: Store = Store(hass, 1, f"{DOMAIN}/{entry.entry_id}")
    dev_reg = dr.async_get(hass)
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator = (
        YoufoneDataUpdateCoordinator(
            hass,
            config_entry=entry,
            dev_reg=dev_reg,
            client=client,
            store=store,
            scan_interval=entry.data[CONF_SCAN_INTERVAL],
            entry=entry,
        )
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    # Unload the platforms first
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

        # Define blocking file operations
        def remove_storage_files():
            storage = Path(f"{hass.config.path(STORAGE_DIR)}/{DOMAIN}/{entry.entry_id}")
            storage.unlink(missing_ok=True)  # Unlink (delete) the storage file

            storage_dir = Path(f"{hass.config.path(STORAGE_DIR)}/{DOMAIN}")
            # If the directory exists and is empty, remove it
            if storage_dir.is_dir() and not any(storage_dir.iterdir()):
                storage_dir.rmdir()

        # Offload the file system operations to a thread
        await asyncio.to_thread(remove_storage_files)

    return unload_ok


class YoufoneDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Youfone."""

    data: list[YoufoneItem]
    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        dev_reg: dr.DeviceRegistry,
        client: YoufoneClient,
        store: Store,
        scan_interval: int,
        entry: ConfigEntry,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=get_coordinator_update_interval(scan_interval),
            config_entry=config_entry,
        )
        self._debug = _LOGGER.isEnabledFor(logging.DEBUG)
        self._config_entry_id = config_entry.entry_id
        self._device_registry = dev_reg
        self.store = store
        self.client = client
        self.hass = hass
        self.entry = entry

    async def async_config_entry_first_refresh(self) -> None:
        """Refresh data for the first time when a config entry is setup."""
        self.data = await self.store.async_load() or {}
        if len(self.data) == 0 or "sim_roaming" not in self.data:
            await super().async_config_entry_first_refresh()

    async def get_data(self) -> dict | None:
        """Get the data from the Youfone client."""
        data = await self.client.fetch_data()
        if "error" in data:
            raise YoufoneServiceException(data["error"])
        self.data = data
        _LOGGER.debug(
            "Fetched data: %d SIM-only and %d roaming line(s)",
            len(self.data.get("sim_only", [])),
            len(self.data.get("sim_roaming", [])),
        )
        await self.store.async_save(self.data)

    async def _async_update_data(self) -> dict | None:
        """Update data."""
        if self._debug:
            await self.get_data()
        else:
            try:
                await self.get_data()
            except ConnectionError as exception:
                _LOGGER.warning(f"ConnectionError {exception}")
            except YoufoneServiceException as exception:
                _LOGGER.warning(f"YoufoneServiceException {exception}")
            except BadCredentialsException as exception:
                raise ConfigEntryAuthFailed(f"Login failed: {exception}") from exception
            except YoufoneException as exception:
                _LOGGER.warning(f"YoufoneException {exception}")
            except Exception as exception:
                _LOGGER.warning(f"Exception {exception}")

        if len(self.data):
            return self.data
        return {}


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    current_version = config_entry.version
    _LOGGER.info("Migrating from version %s", current_version)

    if config_entry.version < 2:
        new = {**config_entry.data}
        new[CONF_SCAN_INTERVAL] = COORDINATOR_MIN_UPDATE_INTERVAL
        hass.config_entries.async_update_entry(config_entry, data=new, version=2)
    if config_entry.version < 4:
        storage_file = Path(
            f"{hass.config.path(STORAGE_DIR)}/{DOMAIN}/{config_entry.entry_id}"
        )
        if storage_file.is_file():
            storage_file.unlink()
        hass.config_entries.async_update_entry(config_entry, version=4)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True
