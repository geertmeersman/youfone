"""Youfone sensor platform."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_COUNTRY, CURRENCY_EURO, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import YoufoneDataUpdateCoordinator
from .const import DOMAIN
from .entity import YoufoneBeEntity, YoufoneEntity
from .models import YoufoneItem

_LOGGER = logging.getLogger(__name__)


@dataclass
class YoufoneSensorDescription(SensorEntityDescription):
    """Sensor entity description for Youfone."""

    available_fn: Callable | None = None
    value_fn: Callable | None = None
    attributes_fn: Callable | None = None
    entity_picture_fn: Callable | None = None
    unique_id_fn: Callable | None = None
    translation_key: str | None = None
    native_unit_of_measurement_fn: Callable | None = None


SENSOR_TYPES: tuple[YoufoneSensorDescription, ...] = (
    YoufoneSensorDescription(
        key="customer",
        icon="mdi:face-man",
        translation_key="customer",
        unique_id_fn=lambda customer: customer.get("customer_id"),
        available_fn=lambda customer: customer.get("customer_id") is not None,
        value_fn=lambda customer: customer.get("name"),
        attributes_fn=lambda customer: customer,
    ),
    YoufoneSensorDescription(
        key="sim_only",
        icon="mdi:sim",
        translation_key="sim_subscription",
        unique_id_fn=lambda sim: sim.get("msisdn"),
        available_fn=lambda sim: sim.get("msisdn") is not None,
        value_fn=lambda sim: sim.get("subscription_info").get("subscriptions")[0],
        attributes_fn=lambda sim: sim.get("subscription_info"),
    ),
    YoufoneSensorDescription(
        key="sim_only",
        icon="mdi:signal-5g",
        translation_key="data",
        unique_id_fn=lambda sim: sim.get("msisdn"),
        available_fn=lambda sim: sim.get("msisdn") is not None,
        native_unit_of_measurement_fn=lambda sim: None
        if sim.get("usage").get("data").get("percentage") is None
        else PERCENTAGE,
        value_fn=lambda sim: "∞"
        if sim.get("usage").get("data").get("percentage") is None
        else sim.get("usage").get("data").get("percentage"),
        attributes_fn=lambda sim: {
            "usage": sim.get("usage").get("data"),
            "msisdn": f"+{sim.get('msisdn')}",
        },
    ),
    YoufoneSensorDescription(
        key="sim_only",
        icon="mdi:phone",
        translation_key="voice",
        unique_id_fn=lambda sim: sim.get("msisdn"),
        available_fn=lambda sim: sim.get("msisdn") is not None,
        native_unit_of_measurement_fn=lambda sim: None
        if sim.get("usage").get("data").get("percentage") is None
        else PERCENTAGE,
        value_fn=lambda sim: "∞"
        if sim.get("usage").get("voice").get("percentage") is None
        else sim.get("usage").get("voice").get("percentage"),
        attributes_fn=lambda sim: {
            "usage": sim.get("usage").get("voice"),
            "msisdn": f"+{sim.get('msisdn')}",
        },
    ),
)


@dataclass
class YoufoneBeSensorDescription(SensorEntityDescription):
    """Class to describe a Youfone sensor."""

    name_suffix: str | None = None
    available_fn: Callable | None = None
    value_fn: Callable | None = None
    attributes_fn: Callable | None = None
    unique_id_fn: Callable | None = None
    translation_key: str | None = None


SENSOR_DESCRIPTIONS: list[SensorEntityDescription] = [
    YoufoneBeSensorDescription(key="profile", icon="mdi:face-man"),
    YoufoneBeSensorDescription(key="subscription", icon="mdi:sim"),
    YoufoneBeSensorDescription(
        key="euro",
        icon="mdi:currency-eur",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
        suggested_display_precision=0,
    ),
    YoufoneBeSensorDescription(
        key="usage_percentage_data",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:signal-4g",
        suggested_display_precision=0,
    ),
    YoufoneBeSensorDescription(
        key="usage_percentage_voice_sms",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:phone",
        suggested_display_precision=0,
    ),
    YoufoneBeSensorDescription(
        key="data",
        icon="mdi:signal-4g",
    ),
    YoufoneBeSensorDescription(
        key="voice_sms",
        icon="mdi:phone",
    ),
    YoufoneBeSensorDescription(
        key="remaining_days",
        icon="mdi:calendar-end-outline",
    ),
    YoufoneBeSensorDescription(
        key="coins",
        icon="mdi:hand-coin",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    YoufoneBeSensorDescription(
        key="coins_pending",
        icon="mdi:timer-sand",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    YoufoneBeSensorDescription(
        key="coins_proposition",
        icon="mdi:offer",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    YoufoneBeSensorDescription(key="sim", icon="mdi:sim"),
    YoufoneBeSensorDescription(key="address", icon="mdi:home"),
    YoufoneBeSensorDescription(key="voice", icon="mdi:phone"),
    YoufoneBeSensorDescription(key="sms", icon="mdi:message-processing"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Youfone sensors."""
    _LOGGER.debug("[sensor|async_setup_entry|async_add_entities|start]")
    coordinator: YoufoneDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    # _LOGGER.debug(f"[sensor|async_setup_entry|async_add_entities|SUPPORTED_KEYS] {SUPPORTED_KEYS}")

    if entry.data[CONF_COUNTRY] == "be":
        entities: list[YoufoneBeSensor] = []

        SUPPORTED_KEYS = {
            description.key: description for description in SENSOR_DESCRIPTIONS
        }
        if coordinator.data is not None:
            for _, item in coordinator.data.items():
                if description := SUPPORTED_KEYS.get(item.type):
                    if item.native_unit_of_measurement is not None:
                        native_unit_of_measurement = item.native_unit_of_measurement
                    else:
                        native_unit_of_measurement = (
                            description.native_unit_of_measurement
                        )
                    sensor_description = YoufoneBeSensorDescription(
                        key=str(item.key),
                        name=item.name,
                        value_fn=description.value_fn,
                        native_unit_of_measurement=native_unit_of_measurement,
                        icon=description.icon,
                    )

                    _LOGGER.debug(f"[sensor|async_setup_entry|adding] {item.name}")
                    entities.append(
                        YoufoneBeSensor(
                            coordinator=coordinator,
                            description=sensor_description,
                            item=item,
                        )
                    )
                else:
                    _LOGGER.debug(
                        f"[sensor|async_setup_entry|no support type found] {item.name}, type: {item.type}, keys: {SUPPORTED_KEYS.get(item.type)}",
                        True,
                    )
        async_add_entities(entities)
    else:
        entities: list[YoufoneSensor] = []
        device_name = ""
        for sensor_type in SENSOR_TYPES:
            _LOGGER.debug(
                f"Searching for {sensor_type.key}-{sensor_type.translation_key}"
            )
            if sensor_type.key in coordinator.data:
                item_id = None
                if sensor_type.key == "customer":
                    device_name = coordinator.data[sensor_type.key].get("email")
                    entities.append(
                        YoufoneSensor(coordinator, sensor_type, device_name, item_id)
                    )
                elif sensor_type.key in ["sim_only"]:
                    for index in range(len(coordinator.data[sensor_type.key])):
                        entities.append(
                            YoufoneSensor(coordinator, sensor_type, device_name, index)
                        )
        async_add_entities(entities)


class YoufoneSensor(YoufoneEntity, RestoreSensor, SensorEntity):
    """Representation of an Youfone sensor."""

    entity_description: YoufoneSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: YoufoneDataUpdateCoordinator,
        description: EntityDescription,
        device_name: str,
        item_id: str,
    ) -> None:
        """Set entity ID."""
        super().__init__(coordinator, description, device_name, item_id)
        self.entity_id = f"sensor.{DOMAIN}_{self.entity_description.translation_key}_{self.entity_description.unique_id_fn(self.item)}"
        _LOGGER.debug(f"Adding {self.entity_id}")
        self._value: StateType = None

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        if self.coordinator.data is not None:
            return self.entity_description.value_fn(self.item)
        return self._value

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if self.coordinator.data is None:
            sensor_data = await self.async_get_last_sensor_data()
            if sensor_data is not None:
                _LOGGER.debug(f"Restoring latest data for {self.entity_id}")
                self._value = sensor_data.native_value
            else:
                _LOGGER.debug(
                    f"Restoring latest - waiting for coordinator refresh {self.entity_id}"
                )
                await self.coordinator.async_request_refresh()
        else:
            self._value = self.entity_description.value_fn(self.item)

    @property
    def extra_state_attributes(self):
        """Return attributes for sensor."""
        if not self.coordinator.data:
            return {}
        attributes = {
            "last_synced": self.last_synced,
        }
        if (
            self.entity_description.attributes_fn
            and self.entity_description.attributes_fn(self.item) is not None
        ):
            return attributes | self.entity_description.attributes_fn(self.item)
        return attributes


class YoufoneBeSensor(YoufoneBeEntity, SensorEntity):
    """Representation of a Youfone sensor."""

    entity_description: YoufoneBeSensorDescription

    def __init__(
        self,
        coordinator: YoufoneDataUpdateCoordinator,
        description: EntityDescription,
        item: YoufoneItem,
    ) -> None:
        """Set entity ID."""
        super().__init__(coordinator, description, item)
        self.entity_id = f"sensor.{DOMAIN}_{self.item.key}"

    @property
    def native_value(self) -> str:
        """Return the status of the sensor."""
        state = self.item.state

        if self.entity_description.value_fn:
            return self.entity_description.value_fn(state)

        return state

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return native unit of mesurement of the sensor."""
        if self.entity_description.native_unit_of_measurement:
            return self.entity_description.native_unit_of_measurement
        if self.entity_description.native_unit_of_measurement_fn:
            return self.entity_description.native_unit_of_measurement_fn(self.item)
        return None

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
