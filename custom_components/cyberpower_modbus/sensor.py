# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/cyberpower-modbus-ha

"""Sensor platform for CyberPower UPS data."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CyberPowerModbusSensorDescription,
    DOMAIN,
    KEY_COORDINATOR,
)
from .coordinator import CyberPowerModbusCoordinator
from .device_types import CyberPowerDeviceType
from .icons_unified import resolve_sensor_icon
from .sensor_availability_unified import is_sensor_enabled_by_default

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the CyberPower UPS sensors for a config entry."""
    coordinator: CyberPowerModbusCoordinator = hass.data[DOMAIN][entry.entry_id][KEY_COORDINATOR]

    if coordinator.device_type == CyberPowerDeviceType.THREE_PHASE:
        from . import registers_three_phase
        sensor_descriptions = registers_three_phase.get_sensor_descriptions()
    else:
        from . import registers_single_phase
        sensor_descriptions = registers_single_phase.get_sensor_descriptions()

    _LOGGER.debug("Setting up %d sensors for device type %s", len(sensor_descriptions), coordinator.device_type.value)

    async_add_entities(
        CyberPowerModbusSensor(coordinator, description, entry.entry_id) for description in sensor_descriptions
    )


class CyberPowerModbusSensor(CoordinatorEntity, SensorEntity):
    """Representation of a CyberPower UPS Modbus sensor."""

    has_entity_name = True

    def __init__(self, coordinator: CyberPowerModbusCoordinator, description: CyberPowerModbusSensorDescription, entry_id: str) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{description.key}"
        self._attr_icon = resolve_sensor_icon(description.register_key)
        self._attr_entity_registry_enabled_default = is_sensor_enabled_by_default(
            description.register_key,
            coordinator.device_type.value,
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=coordinator.device_name,
            manufacturer="CyberPower",
            model=coordinator.hw_model or "CyberPower UPS",
            serial_number=coordinator.serial_number,
            sw_version=f"{coordinator.fw_version} ({coordinator.fw_date})" if coordinator.fw_version and coordinator.fw_date else coordinator.fw_version,
        )

    @property
    def native_value(self):
        """Return the latest value from the coordinator."""
        return self.coordinator.data.get(self.entity_description.register_key)
