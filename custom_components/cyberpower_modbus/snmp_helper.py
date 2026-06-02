# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/cyberpower-modbus-ha

"""SNMP helper for CyberPower UPS device metadata and type detection."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pysnmp.error import PySnmpError
from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
)

from .device_types import CyberPowerDeviceType

_LOGGER = logging.getLogger(__name__)

# UPS-MIB OIDs
UPS_OID_MANUFACTURER = "1.3.6.1.2.1.33.1.1.1.0"
UPS_OID_MODEL = "1.3.6.1.2.1.33.1.1.2.0"
UPS_OID_UPS_FIRMWARE = "1.3.6.1.2.1.33.1.1.3.0"
UPS_OID_AGENT_FIRMWARE = "1.3.6.1.2.1.33.1.1.4.0"
UPS_OID_NAME = "1.3.6.1.2.1.33.1.1.5.0"
UPS_OID_INPUT_LINES = "1.3.6.1.2.1.33.1.3.2.0"

# CyberPower enterprise OIDs (3808) observed on RMCARD205
CYBERPOWER_OID_MODEL = "1.3.6.1.4.1.3808.1.1.1.1.1.1.0"
CYBERPOWER_OID_CARD_MODEL = "1.3.6.1.4.1.3808.1.1.1.1.1.2.0"
CYBERPOWER_OID_UPS_FIRMWARE = "1.3.6.1.4.1.3808.1.1.1.1.2.1.0"
CYBERPOWER_OID_SERIAL = "1.3.6.1.4.1.3808.1.1.1.1.2.3.0"
CYBERPOWER_OID_CARD_FIRMWARE = "1.3.6.1.4.1.3808.1.1.1.1.2.4.0"
CYBERPOWER_OID_OUTPUT_POWER = "1.3.6.1.4.1.3808.1.1.1.4.2.5.0"
CYBERPOWER_OID_OUTPUT_ENERGY = "1.3.6.1.4.1.3808.1.1.1.4.2.6.0"

SNMP_TELEMETRY_DESCRIPTORS = (
    {
        "key": "output_power",
        "oid": CYBERPOWER_OID_OUTPUT_POWER,
        "scale": 1,
    },
    {
        "key": "output_energy",
        "oid": CYBERPOWER_OID_OUTPUT_ENERGY,
        "scale": 10,
    },
)


async def async_get_snmp_value(
    host: str,
    oid: str,
    community: str = "public",
    timeout: int = 5,
    retries: int = 3,
) -> str | None:
    """Query single SNMP OID and return string value."""
    try:
        _LOGGER.debug("SNMP query to %s OID %s (timeout=%ds)", host, oid, timeout)

        target = await UdpTransportTarget.create((host, 161), timeout=timeout, retries=retries)

        error_indication, error_status, error_index, var_binds = await get_cmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),  # SNMPv2c
            target,
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )

        if error_indication:
            _LOGGER.debug("SNMP error from %s (OID %s): %s", host, oid, error_indication)
            return None
        if error_status:
            _LOGGER.debug(
                "SNMP error status from %s (OID %s): %s at index %s",
                host,
                oid,
                error_status.prettyPrint(),
                error_index,
            )
            return None

        for var_bind in var_binds:
            value = str(var_bind[1])
            _LOGGER.debug("SNMP query succeeded: %s=%s", oid, value[:50] if len(value) > 50 else value)
            return value

        _LOGGER.debug("SNMP query returned no value for OID %s", oid)
        return None

    except asyncio.TimeoutError:
        _LOGGER.warning("SNMP query to %s timed out after %ds for OID %s", host, timeout, oid)
        return None
    except (PySnmpError, OSError, RuntimeError, ValueError) as err:
        _LOGGER.debug("SNMP query failed for %s (OID %s): %s (%s)", host, oid, err, type(err).__name__)
        return None


async def async_get_device_metadata(
    host: str,
    community: str = "public",
    device_type: CyberPowerDeviceType | None = None,
) -> dict[str, Any]:
    """Query CyberPower device metadata via SNMP.

    device_type is accepted for compatibility with the APC integration call pattern.
    """
    _LOGGER.debug("Querying SNMP metadata from %s (community: %s)", host, community)

    results = await asyncio.gather(
        async_get_snmp_value(host, UPS_OID_MODEL, community),
        async_get_snmp_value(host, UPS_OID_UPS_FIRMWARE, community),
        async_get_snmp_value(host, UPS_OID_AGENT_FIRMWARE, community),
        async_get_snmp_value(host, CYBERPOWER_OID_MODEL, community),
        async_get_snmp_value(host, CYBERPOWER_OID_UPS_FIRMWARE, community),
        async_get_snmp_value(host, CYBERPOWER_OID_CARD_MODEL, community),
        async_get_snmp_value(host, CYBERPOWER_OID_SERIAL, community),
        async_get_snmp_value(host, CYBERPOWER_OID_CARD_FIRMWARE, community),
        return_exceptions=True,
    )

    (
        ups_model,
        ups_fw,
        agent_fw,
        cyber_model,
        cyber_ups_fw,
        card_model,
        serial,
        card_fw,
    ) = [r if not isinstance(r, Exception) else None for r in results]

    model = ups_model or cyber_model
    firmware = ups_fw or cyber_ups_fw or agent_fw or card_fw

    metadata = {
        "model": model,
        "serial_number": serial,
        "firmware_version": firmware,
        "firmware_date": None,
        "card_model": card_model,
    }

    _LOGGER.debug("SNMP metadata retrieved: %s", metadata)
    return metadata


async def async_get_snmp_telemetry(
    host: str,
    community: str = "public",
) -> dict[str, float | int]:
    """Query CyberPower SNMP telemetry values used during regular polling."""
    telemetry: dict[str, float | int] = {}

    results = await asyncio.gather(
        *(
            async_get_snmp_value(
                host,
                descriptor["oid"],
                community,
                timeout=1,
                retries=1,
            )
            for descriptor in SNMP_TELEMETRY_DESCRIPTORS
        ),
        return_exceptions=True,
    )

    for descriptor, result in zip(SNMP_TELEMETRY_DESCRIPTORS, results, strict=True):
        if isinstance(result, Exception) or result is None:
            continue
        try:
            raw_value = int(result)
        except ValueError:
            _LOGGER.debug(
                "SNMP telemetry value for %s is not numeric: %s",
                descriptor["key"],
                result,
            )
            continue

        scale = descriptor["scale"]
        telemetry[descriptor["key"]] = raw_value / scale if scale != 1 else raw_value

    return telemetry


def _detect_device_type_from_model(model_string: str | None) -> CyberPowerDeviceType:
    """Infer device type from model string when UPS-MIB line count is unavailable."""
    if not model_string:
        return CyberPowerDeviceType.SINGLE_PHASE

    model_upper = model_string.upper()
    if "3PH" in model_upper or "3-PH" in model_upper or "3 PH" in model_upper:
        return CyberPowerDeviceType.THREE_PHASE

    return CyberPowerDeviceType.SINGLE_PHASE


async def async_detect_device_type(
    host: str, community: str = "public", model_hint: str | None = None
) -> CyberPowerDeviceType:
    """Detect CyberPower device type via SNMP UPS-MIB."""
    line_count = await async_get_snmp_value(host, UPS_OID_INPUT_LINES, community)
    if line_count is not None:
        try:
            lines = int(line_count)
            if lines == 3:
                return CyberPowerDeviceType.THREE_PHASE
            if lines == 1:
                return CyberPowerDeviceType.SINGLE_PHASE
        except ValueError:
            _LOGGER.debug("Unexpected UPS input line count value: %s", line_count)

    return _detect_device_type_from_model(model_hint)


def get_device_metadata_sync(host: str, community: str = "public") -> dict[str, Any]:
    """Sync wrapper for SNMP metadata (safe to run in executor)."""
    return asyncio.run(async_get_device_metadata(host, community))


def get_snmp_telemetry_sync(host: str, community: str = "public") -> dict[str, float | int]:
    """Sync wrapper for SNMP telemetry (safe to run in executor)."""
    return asyncio.run(async_get_snmp_telemetry(host, community))


def detect_device_type_sync(
    host: str, community: str = "public", model_hint: str | None = None
) -> CyberPowerDeviceType:
    """Sync wrapper for device type detection (safe to run in executor)."""
    return asyncio.run(async_detect_device_type(host, community, model_hint))
