# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/cyberpower-modbus-ha

"""CyberPower UPS Modbus integration entry point."""

from __future__ import annotations

import asyncio
import logging

try:
    import pymodbus
    PYMODBUS_VERSION = pymodbus.__version__
except (ImportError, AttributeError):
    PYMODBUS_VERSION = "unknown"

from pymodbus.client import ModbusTcpClient
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import (
    CONF_DEVICE_NAME,
    CONF_SNMP_COMMUNITY,
    CONF_UNIT,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SNMP_COMMUNITY,
    DEFAULT_UNIT,
    DOMAIN,
    KEY_COORDINATOR,
    SUPPORTED_PLATFORMS,
)
from .coordinator import CyberPowerModbusCoordinator
from .device_types import CyberPowerDeviceType
from .register_factory import get_registers_for_device
from .snmp_helper import detect_device_type_sync, get_device_metadata_sync

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CyberPower Modbus from a config entry."""
    _LOGGER.info("CyberPower UPS Modbus integration starting (pymodbus %s)", PYMODBUS_VERSION)
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    unit = entry.data.get(CONF_UNIT, DEFAULT_UNIT)
    device_name = entry.data.get(CONF_DEVICE_NAME, DEFAULT_NAME)
    snmp_community = entry.data.get(CONF_SNMP_COMMUNITY, DEFAULT_SNMP_COMMUNITY)
    locks = hass.data[DOMAIN].setdefault("locks", {})
    lock_key = f"{host}:{port}"
    io_lock = locks.setdefault(lock_key, asyncio.Lock())

    def client_factory() -> ModbusTcpClient:
        # Create client with timeout to prevent hung connections
        return ModbusTcpClient(host=host, port=port, timeout=5)

    client = client_factory()
    connected = await hass.async_add_executor_job(client.connect)
    if not connected:
        raise ConfigEntryNotReady("Unable to connect to CyberPower UPS")

    coordinator = CyberPowerModbusCoordinator(
        hass,
        client,
        unit,
        device_name,
        host,
        port,
        entry.entry_id,
        io_lock,
        client_factory,
        snmp_community,
    )

    # Query SNMP for device metadata (async, non-blocking)
    try:
        _LOGGER.debug("Querying SNMP metadata from %s", host)
        metadata = await hass.async_add_executor_job(get_device_metadata_sync, host, snmp_community)
        if metadata and any([metadata.get("model"), metadata.get("serial_number"), metadata.get("firmware_version")]):
            _LOGGER.info("SNMP metadata retrieved: model=%s, serial=%s", metadata.get("model"), metadata.get("serial_number"))
            coordinator.set_device_metadata(
                hw_model=metadata.get("model"),
                serial_number=metadata.get("serial_number"),
                fw_version=metadata.get("firmware_version"),
                fw_date=metadata.get("firmware_date"),
            )
        else:
            _LOGGER.debug("SNMP query returned empty metadata")
    except (OSError, RuntimeError, ValueError) as err:
        _LOGGER.warning("Failed to query SNMP metadata from %s: %s", host, err)
        # Continue without metadata - Modbus sensors still work

    # Detect device type via SNMP (fallback to single-phase)
    try:
        model_hint = coordinator.hw_model
        device_type = await hass.async_add_executor_job(
            detect_device_type_sync,
            host,
            snmp_community,
            model_hint,
        )
    except (OSError, RuntimeError, ValueError) as err:
        _LOGGER.warning("Failed to detect device type from SNMP: %s", err)
        device_type = CyberPowerDeviceType.SINGLE_PHASE

    coordinator.set_device_type(device_type)

    # Load registers for detected device type
    registers, blocks, reg_map = get_registers_for_device(coordinator.device_type)
    coordinator.set_registers(registers, blocks, reg_map)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Failed to fetch initial data from CyberPower device: %s", err)
        raise ConfigEntryNotReady(f"Failed to fetch initial data: {err}") from err

    hass.data[DOMAIN][entry.entry_id] = {KEY_COORDINATOR: coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, SUPPORTED_PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a CyberPower Modbus config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, SUPPORTED_PLATFORMS)

    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data[KEY_COORDINATOR].async_close()

    return unload_ok
