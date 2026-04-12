# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/cyberpower-modbus-ha

"""Button entities for CyberPower UPS Modbus."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, KEY_COORDINATOR
from .coordinator import CyberPowerModbusCoordinator
from .sensor_availability_unified import entity_enabled_default

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CyberPower UPS button entities for a config entry."""
    coordinator: CyberPowerModbusCoordinator = hass.data[DOMAIN][entry.entry_id][
        KEY_COORDINATOR
    ]
    async_add_entities(
        [CyberPowerModbusResetMonitoringButton(coordinator, entry.entry_id)]
    )


class CyberPowerModbusResetMonitoringButton(CoordinatorEntity, ButtonEntity):
    """Button to reset entity monitoring defaults for one config entry."""

    has_entity_name = True
    _attr_name = "Set or Reset Monitors"
    _attr_icon = "mdi:tune-variant"

    def __init__(self, coordinator: CyberPowerModbusCoordinator, entry_id: str) -> None:
        """Initialize reset monitoring button."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_set_or_reset_monitors"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=coordinator.device_name,
            manufacturer="CyberPower",
            model=coordinator.hw_model or "CyberPower UPS",
            serial_number=coordinator.serial_number,
            sw_version=(
                f"{coordinator.fw_version} ({coordinator.fw_date})"
                if coordinator.fw_version and coordinator.fw_date
                else coordinator.fw_version
            ),
        )

    async def async_press(self) -> None:
        """Enable core monitoring entities and disable non-core entities."""
        registry = er.async_get(self.hass)
        unique_id_prefix = f"{DOMAIN}_{self._entry_id}_"
        updated = 0
        enabled = 0
        disabled = 0
        skipped = 0

        for entry in er.async_entries_for_config_entry(registry, self._entry_id):
            if entry.domain not in ("sensor", "binary_sensor"):
                continue
            if not entry.unique_id or not entry.unique_id.startswith(unique_id_prefix):
                continue

            local_key = entry.unique_id.removeprefix(unique_id_prefix)
            should_enable = entity_enabled_default(local_key)
            desired_disabled_by = (
                None if should_enable else er.RegistryEntryDisabler.INTEGRATION
            )

            if entry.disabled_by == desired_disabled_by:
                skipped += 1
                continue

            registry.async_update_entity(
                entry.entity_id,
                disabled_by=desired_disabled_by,
            )
            updated += 1
            if should_enable:
                enabled += 1
            else:
                disabled += 1

        _LOGGER.info(
            "Set/reset monitors complete: updated=%d enabled=%d disabled=%d unchanged=%d [entry_id=%s]",
            updated,
            enabled,
            disabled,
            skipped,
            self._entry_id,
        )
