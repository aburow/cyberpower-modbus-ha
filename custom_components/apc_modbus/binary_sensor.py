"""Binary sensor definitions for APC UPS Modbus."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    APCModbusBinarySensorDescription,
    BINARY_SENSOR_DESCRIPTIONS,
    DOMAIN,
    KEY_COORDINATOR,
)
from .coordinator import APCModbusCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the APC UPS binary sensors."""
    coordinator: APCModbusCoordinator = hass.data[DOMAIN][entry.entry_id][KEY_COORDINATOR]
    async_add_entities(
        APCModbusBinarySensor(coordinator, description, entry.entry_id) for description in BINARY_SENSOR_DESCRIPTIONS
    )


class APCModbusBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for APC UPS status bits."""

    has_entity_name = True

    def __init__(self, coordinator: APCModbusCoordinator, description: APCModbusBinarySensorDescription, entry_id: str) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=coordinator.device_name,
            manufacturer="APC",
            model="Smart-UPS",
        )

    @property
    def is_on(self) -> bool | None:
        """Return the current state of the binary sensor."""
        value = self.coordinator.data.get(self.entity_description.register_key)
        if value is None:
            return None
        return bool(int(value) & (1 << self.entity_description.bit_index))
