"""Definition and setup of the SpaceX Binary Sensors for Home Assistant."""

import logging
import time
import datetime
from homeassistant.util.dt import as_local, utc_from_timestamp
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    LENGTH_KILOMETERS,
    SPEED_KILOMETERS_PER_HOUR,
    ATTR_NAME,
)
from .const import ATTR_IDENTIFIERS, ATTR_MANUFACTURER, ATTR_MODEL, DOMAIN, COORDINATOR

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platforms."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    sensor_definitions = [
        ("Next Launch Mission", "spacex_next_launch_mission", "mdi:information-outline", "spacexlaunch"),
        ("Next Launch Day", "spacex_next_launch_day", "mdi:calendar", "spacexlaunch"),
        ("Next Launch Time", "spacex_next_launch_time", "mdi:clock-outline", "spacexlaunch"),
        ("Next Launch Countdown", "spacex_next_launch_countdown", "mdi:clock-outline", "spacexlaunch"),
        ("Next Launch Site", "spacex_next_launch_site", "mdi:map-marker", "spacexlaunch"),
        ("Next Launch Rocket", "spacex_next_launch_rocket", "mdi:rocket", "spacexlaunch"),
        ("Next Launch Payload", "spacex_next_launch_payload", "mdi:package", "spacexlaunch"),
        ("Next Confirmed Launch Day", "spacex_next_confirmed_launch_day", "mdi:calendar", "spacexlaunch"),
        ("Next Confirmed Launch Time", "spacex_next_confirmed_launch_time", "mdi:clock-outline", "spacexlaunch"),
        ("Latest Launch Mission", "spacex_latest_launch_mission", "mdi:information-outline", "spacexlaunch"),
        ("Latest Launch Day", "spacex_latest_launch_day", "mdi:calendar", "spacexlaunch"),
        ("Latest Launch Time", "spacex_latest_launch_time", "mdi:clock-outline", "spacexlaunch"),
        ("Latest Launch Site", "spacex_latest_launch_site", "mdi:map-marker", "spacexlaunch"),
        ("Latest Launch Rocket", "spacex_latest_launch_rocket", "mdi:rocket", "spacexlaunch"),
        ("Latest Launch Payload", "spacex_latest_launch_payload", "mdi:package", "spacexlaunch"),
        ("Starman Speed", "spacex_starman_speed", "mdi:account-star", "spacexstarman"),
        ("Starman Distance", "spacex_starman_distance", "mdi:map-marker-distance", "spacexstarman"),
    ]

    sensors = [
        SpaceXSensor(coordinator, name, entity_id, icon, device_identifier)
        for name, entity_id, icon, device_identifier in sensor_definitions
    ]
    async_add_entities(sensors)


class SpaceXSensor(CoordinatorEntity):
    """Defines a SpaceX Binary sensor."""

    def __init__(self, coordinator, name, entity_id, icon, device_identifier):
        """Initialize Entities."""
        super().__init__(coordinator)
        self._name = name
        self._unique_id = f"spacex_{entity_id}"
        self._icon = icon
        self._device_identifier = device_identifier
        self._unit_of_measurement = self._set_unit_of_measurement(entity_id)
        self.attrs = {}

    @staticmethod
    def _set_unit_of_measurement(entity_id):
        """Set the unit of measurement based on the entity type."""
        if entity_id == "spacex_starman_speed":
            return SPEED_KILOMETERS_PER_HOUR
        if entity_id == "spacex_starman_distance":
            return LENGTH_KILOMETERS
        return None

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        """Return additional attributes for the sensor."""
        self.attrs = self._generate_attributes()
        return self.attrs

    def _generate_attributes(self):
        """Generate attributes dynamically based on the sensor type."""
        coordinator_data = self.coordinator.data
        starman_data = coordinator_data.get("starman", {})
        launch_data = coordinator_data.get("next_launch", {})
        latest_launch_data = coordinator_data.get("latest_launch", {})
        attributes = {}

        if "next_launch" in self._unique_id:
            self._populate_launch_attributes(launch_data, attributes)
        elif "latest_launch" in self._unique_id:
            self._populate_launch_attributes(latest_launch_data, attributes)
        elif "starman" in self._unique_id:
            self._populate_starman_attributes(starman_data, attributes)

        return attributes

    def _populate_launch_attributes(self, launch_data, attributes):
        """Populate launch-specific attributes."""
        # Example for one kind of launch data attribute.
        if self._unique_id.endswith("mission"):
            attributes["mission_patch"] = launch_data.get("links", {}).get("patch", {}).get("large", "N/A")
            attributes["details"] = launch_data.get("details", "No details available")[:255]

    def _populate_starman_attributes(self, starman_data, attributes):
        """Populate Starman-specific attributes."""
        if self._unique_id.endswith("speed"):
            attributes["mach_speed"] = float(starman_data.get("speed_kph", 0)) / 1235
        elif self._unique_id.endswith("distance"):
            attributes["au_distance"] = float(starman_data.get("earth_distance_km", 0)) / (1.496 * 10**8)

    @property
    def device_info(self):
        """Define the device info."""
        device_name = "SpaceX Starman" if self._device_identifier != "spacexlaunch" else "SpaceX Launches"
        device_model = "Starman" if self._device_identifier != "spacexlaunch" else "Launch"
        return {
            ATTR_IDENTIFIERS: {(DOMAIN, self._device_identifier)},
            ATTR_NAME: device_name,
            ATTR_MANUFACTURER: "SpaceX",
            ATTR_MODEL: device_model,
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._generate_state()

    def _generate_state(self):
        """Generate the state dynamically based on the sensor type."""
        # Simplified logic for demonstration.
        return "State logic here."
