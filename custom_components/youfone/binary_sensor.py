"""Binary sensor platform for Youfone."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import YoufoneDataUpdateCoordinator
from .const import DOMAIN
from .entity import YoufoneEntity
from .models import YoufoneItem

_LOGGER = logging.getLogger(__name__)


@dataclass
class YoufoneSensorDescription(SensorEntityDescription):
    """Class to describe a Youfone sensor."""

    value_fn: Callable[[Any], StateType] | None = None
    name_suffix: str | None = None
    unique_id_fn: Callable | None = None


SENSOR_DESCRIPTIONS: list[SensorEntityDescription] = [
    YoufoneSensorDescription(
        key="usage_percentage_data",
        icon="mdi:signal-4g",
        device_class=BinarySensorDeviceClass.SAFETY,
        unique_id_fn=lambda customer: customer.get("customer_id"),
        name_suffix="Alarm",
        value_fn=lambda data: data.state
        > data.extra_attributes.get("period_percentage_completed"),
    ),
    YoufoneSensorDescription(
        key="usage_percentage_voice_sms",
        icon="mdi:phone",
        device_class=BinarySensorDeviceClass.SAFETY,
        unique_id_fn=lambda customer: customer.get("customer_id"),
        name_suffix="Alarm",
        value_fn=lambda data: data.state
        > data.extra_attributes.get("period_percentage_completed"),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Youfone binary sensors."""
    """
    _LOGGER.debug("[binary_sensor|async_setup_entry|async_add_entities|start]")
    coordinator: YoufoneDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    entities: list[YoufoneBinarySensor] = []

    SUPPORTED_KEYS = {
        description.key: description for description in SENSOR_DESCRIPTIONS
    }

    if entry.data[CONF_COUNTRY] == "be":
        if coordinator.data is not None:
            for _, item in coordinator.data.items():
                if description := SUPPORTED_KEYS.get(item.type):
                    _LOGGER.debug(f"[sensor|async_setup_entry|adding] {item.name}")
                    entities.append(
                        YoufoneBinarySensor(
                            coordinator=coordinator,
                            description=description,
                            item=item,
                        )
                    )
                else:
                    _LOGGER.debug(
                        f"[sensor|async_setup_entry|no support type found] {item.name}, type: {item.type}, keys: {SUPPORTED_KEYS.get(item.type)}",
                        True,
                    )

            async_add_entities(entities)
"""


class YoufoneBinarySensor(YoufoneEntity, BinarySensorEntity):
    """Representation of a Youfone binary sensor."""

    entity_description: YoufoneSensorDescription

    def __init__(
        self,
        coordinator: YoufoneDataUpdateCoordinator,
        description: EntityDescription,
        item: YoufoneItem,
    ) -> None:
        """Set entity ID."""
        super().__init__(coordinator, description, item)
        self.entity_id = f"binary_sensor.{DOMAIN}_{self.item.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.item)

        return self._attr_is_on

    @property
    def extra_state_attributes(self):
        """Return attributes for sensor."""
        if not self.coordinator.data:
            return {}
        attributes = {
            "last_synced": self.last_synced,
        }
        if len(self.item.extra_attributes) > 0:
            for attr in self.item.extra_attributes:
                attributes[attr] = self.item.extra_attributes[attr]
        return attributes
