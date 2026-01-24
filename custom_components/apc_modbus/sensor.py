"""Sensor platform for APC UPS data."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    APCModbusSensorDescription,
    DOMAIN,
    KEY_COORDINATOR,
    SENSOR_DESCRIPTIONS,
)
from .coordinator import APCModbusCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the APC UPS sensors for a config entry."""
    coordinator: APCModbusCoordinator = hass.data[DOMAIN][entry.entry_id][KEY_COORDINATOR]

    async_add_entities(
        APCModbusSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class APCModbusSensor(CoordinatorEntity, SensorEntity):
    """Representation of an APC UPS Modbus sensor."""

    def __init__(self, coordinator: APCModbusCoordinator, description: APCModbusSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_unique_id = f"{DOMAIN}_{description.key}"

    @property
    def native_value(self):
        """Return the latest value from the coordinator."""
        return self.coordinator.data.get(self.entity_description.register_key)
