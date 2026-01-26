# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/cyberpower-modbus-ha

"""Constants for the CyberPower UPS Modbus integration."""

from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import SensorEntityDescription

DOMAIN = "cyberpower_modbus"
DEFAULT_NAME = "CyberPower UPS"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_UNIT = 1
DEFAULT_SNMP_COMMUNITY = "public"
CONF_UNIT = "unit"
CONF_DEVICE_NAME = "device_name"
CONF_SNMP_COMMUNITY = "snmp_community"

KEY_CLIENT = "modbus_client"
KEY_COORDINATOR = "coordinator"

SUPPORTED_PLATFORMS = ["sensor", "binary_sensor"]


@dataclass
class CyberPowerModbusSensorDescription(SensorEntityDescription):
    """Describe a CyberPower Modbus sensor."""

    register_key: str = ""


@dataclass
class CyberPowerModbusBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a CyberPower Modbus binary sensor."""

    register_key: str = ""
    bit_index: int | None = None


SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
