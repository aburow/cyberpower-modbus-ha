# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/apc-modbus-snmp-ha

"""Sensor platform for APC UPS data."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
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
        APCModbusSensor(coordinator, description, entry.entry_id) for description in SENSOR_DESCRIPTIONS
    )


class APCModbusSensor(CoordinatorEntity, SensorEntity):
    """Representation of an APC UPS Modbus sensor."""

    has_entity_name = True

    def __init__(self, coordinator: APCModbusCoordinator, description: APCModbusSensorDescription, entry_id: str) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=coordinator.device_name,
            manufacturer="APC",
            model=coordinator.hw_model or "Smart-UPS",
            serial_number=coordinator.serial_number,
            sw_version=f"{coordinator.fw_version} ({coordinator.fw_date})" if coordinator.fw_version and coordinator.fw_date else coordinator.fw_version,
        )

    @property
    def native_value(self):
        """Return the latest value from the coordinator."""
        return self.coordinator.data.get(self.entity_description.register_key)
