"""Definition and setup of the SpaceX Binary Sensors for Home Assistant."""

import logging
import time

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import ATTR_NAME
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from . import SpaceXUpdateCoordinator
from .const import ATTR_IDENTIFIERS, ATTR_MANUFACTURER, ATTR_MODEL, DOMAIN, COORDINATOR

_LOGGER = logging.getLogger(__name__)

SENSOR_CONFIG = [
    {
        "name": "Next Launch Confirmed",
        "entity_id": "spacex_next_launch_confirmed",
        "icon": "mdi:check-circle",
        "device_identifier": "spacexlaunch",
    },
    {
        "name": "Launch within 24 Hours",
        "entity_id": "spacex_launch_24_hour_warning",
        "icon": "mdi:rocket",
        "device_identifier": "spacexlaunch",
    },
    {
        "name": "Launch within 20 Minutes",
        "entity_id": "spacex_launch_20_minute_warning",
        "icon": "mdi:rocket-launch",
        "device_identifier": "spacexlaunch",
    },
]

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary sensor platforms."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    sensors = [
        SpaceXBinarySensor(coordinator, **config) for config in SENSOR_CONFIG
    ]
    async_add_entities(sensors)


class SpaceXBinarySensor(BinarySensorEntity):
    """Defines a SpaceX Binary sensor."""

    def __init__(self, coordinator, name, entity_id, icon, device_identifier):
        """Initialize the entity."""
        self._name = name
        self._unique_id = f"spacex_{entity_id}"
        self._icon = icon
        self._kind = entity_id
        self._device_identifier = device_identifier
        self.coordinator = coordinator
        self.attrs = {}

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def unique_id(self):
        """Return the unique Home Assistant friendly identifier for this entity."""
        return self._unique_id

    @property
    def name(self):
        """Return the friendly name of this entity."""
        return self._name

    @property
    def icon(self):
        """Return the icon for this entity."""
        launch_data = self.coordinator.data["next_launch"]

        if self._kind == "spacex_next_launch_confirmed":
            return "mdi:check-circle" if not launch_data.get("tbd") else "mdi:do-not-disturb"
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the attributes."""
        return self.attrs

    @property
    def device_info(self):
        """Define the device based on device_identifier."""
        device_name = "SpaceX Launches" if self._device_identifier == "spacexlaunch" else "SpaceX Starman"
        device_model = "Launch" if self._device_identifier == "spacexlaunch" else "Starman"

        return {
            ATTR_IDENTIFIERS: {(DOMAIN, self._device_identifier)},
            ATTR_NAME: device_name,
            ATTR_MANUFACTURER: "SpaceX",
            ATTR_MODEL: device_model,
        }

    @property
    def is_on(self) -> bool:
        """Return the state."""
        launch_data = self.coordinator.data["next_launch"]
        current_time = time.time()

        if self._kind == "spacex_next_launch_confirmed":
            return not launch_data.get("tbd", True)

        time_delta = {
            "spacex_launch_24_hour_warning": 24 * 60 * 60,
            "spacex_launch_20_minute_warning": 20 * 60,
        }.get(self._kind)

        if time_delta:
            return current_time < launch_data["date_unix"] < (current_time + time_delta)

        return False

    async def async_update(self):
        """Update SpaceX Binary Sensor Entity."""
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
