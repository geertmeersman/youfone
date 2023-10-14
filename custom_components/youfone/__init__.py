"""Youfone integration."""
from __future__ import annotations

import logging
import random
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_COUNTRY, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from requests.exceptions import ConnectionError

from .client import YoufoneClient
from .const import COORDINATOR_UPDATE_INTERVAL, DOMAIN, PLATFORMS
from .exceptions import (
    BadCredentialsException,
    YoufoneException,
    YoufoneServiceException,
)
from .models import YoufoneItem

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Youfone from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = YoufoneClient(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        country=entry.data[CONF_COUNTRY],
    )

    dev_reg = dr.async_get(hass)
    hass.data[DOMAIN][entry.entry_id] = coordinator = YoufoneDataUpdateCoordinator(
        hass,
        config_entry_id=entry.entry_id,
        dev_reg=dev_reg,
        client=client,
    )

    # sleep random number of seconds, trying to avoid IP blacklisting
    time.sleep(random.uniform(1, 10))

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class YoufoneDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Youfone."""

    data: list[YoufoneItem]
    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry_id: str,
        dev_reg: dr.DeviceRegistry,
        client: YoufoneClient,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=COORDINATOR_UPDATE_INTERVAL,
        )
        self._debug = _LOGGER.isEnabledFor(logging.DEBUG)
        self._config_entry_id = config_entry_id
        self._device_registry = dev_reg
        self.client = client
        self.hass = hass

    async def _async_update_data(self) -> dict | None:
        """Update data."""
        if self._debug:
            items = await self.hass.async_add_executor_job(self.client.fetch_data)
        else:
            try:
                items = await self.hass.async_add_executor_job(self.client.fetch_data)
            except ConnectionError as exception:
                raise UpdateFailed(f"ConnectionError {exception}") from exception
            except YoufoneServiceException as exception:
                raise UpdateFailed(
                    f"YoufoneServiceException {exception}"
                ) from exception
            except BadCredentialsException as exception:
                raise UpdateFailed(f"Login failed: {exception}") from exception
            except YoufoneException as exception:
                raise UpdateFailed(f"YoufoneException {exception}") from exception
            except Exception as exception:
                raise UpdateFailed(f"Exception {exception}") from exception

        items: list[YoufoneItem] = items

        current_items = {
            list(device.identifiers)[0][1]
            for device in dr.async_entries_for_config_entry(
                self._device_registry, self._config_entry_id
            )
        }

        if items is not None and len(items) > 0:
            fetched_items = {str(items[item].device_key) for item in items}
            _LOGGER.debug(
                f"[init|YoufoneDataUpdateCoordinator|_async_update_data|fetched_items] {fetched_items}"
            )
            if stale_items := current_items - fetched_items:
                for device_key in stale_items:
                    if device := self._device_registry.async_get_device(
                        {(DOMAIN, device_key)}
                    ):
                        _LOGGER.debug(
                            f"[init|YoufoneDataUpdateCoordinator|_async_update_data|async_remove_device] {device_key}",
                            True,
                        )
                        self._device_registry.async_remove_device(device.id)

            # If there are new items, we should reload the config entry so we can
            # create new devices and entities.
            if self.data and fetched_items - {
                str(self.data[item].device_key) for item in self.data
            }:
                # _LOGGER.debug(f"[init|YoufoneDataUpdateCoordinator|_async_update_data|async_reload] {product.product_name}")
                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(self._config_entry_id)
                )
                return None
            return items
        return []
