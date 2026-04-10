# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/cyberpower-modbus-ha

"""Icon mapping helpers for CyberPower entities."""

from __future__ import annotations

from collections.abc import Sequence


def _match_icon(register_key: str, mapping: Sequence[tuple[tuple[str, ...], str]], default_icon: str) -> str:
    """Resolve icon by first matching key-pattern set."""
    for patterns, icon in mapping:
        if any(pattern in register_key for pattern in patterns):
            return icon
    return default_icon


SENSOR_ICON_MAPPING: tuple[tuple[tuple[str, ...], str], ...] = (
    (("temperature", "temp"), "mdi:thermometer"),
    (("humidity",), "mdi:water-percent"),
    (("frequency",), "mdi:sine-wave"),
    (("voltage", "volt"), "mdi:lightning-bolt"),
    (("current", "amp"), "mdi:current-ac"),
    (("active_power", "apparent_power", "reactive_power", "power"), "mdi:flash"),
    (("energy",), "mdi:meter-electric"),
    (("runtime",), "mdi:timer-outline"),
    (("load",), "mdi:gauge"),
    (("battery_capacity", "state_of_charge", "soc"), "mdi:battery-high"),
    (("battery",), "mdi:battery"),
    (("status", "result", "state", "source"), "mdi:state-machine"),
)

SENSOR_DEFAULT_ICON = "mdi:gauge"

BINARY_SENSOR_ICON_MAPPING: tuple[tuple[tuple[str, ...], str], ...] = (
    (("fault", "fail", "problem", "error"), "mdi:alert-circle"),
    (("overload",), "mdi:car-brake-alert"),
    (("over_temperature", "temperature"), "mdi:thermometer-alert"),
    (("battery_eod", "battery_not_present", "battery_volt_low", "battery_low"), "mdi:battery-alert"),
    (("battery_charging",), "mdi:battery-charging"),
    (("battery_fully_charged",), "mdi:battery-check"),
    (("battery_discharging",), "mdi:battery-arrow-down"),
    (("battery",), "mdi:battery"),
    (("bypass",), "mdi:transit-detour"),
    (("online", "load_on_source"), "mdi:power-plug"),
    (("no_output", "output_off"), "mdi:power-plug-off"),
    (("output_shorted",), "mdi:flash-alert"),
    (("inverter_off",), "mdi:power"),
    (("buzzer_muted",), "mdi:volume-off"),
    (("runtime_low",), "mdi:timer-alert"),
)

BINARY_SENSOR_DEFAULT_ICON = "mdi:help-circle-outline"


def resolve_sensor_icon(register_key: str) -> str:
    """Resolve a deterministic mdi icon for a sensor register key."""
    return _match_icon(register_key.lower(), SENSOR_ICON_MAPPING, SENSOR_DEFAULT_ICON)


def resolve_binary_sensor_icon(register_key: str) -> str:
    """Resolve a deterministic mdi icon for a binary sensor register key."""
    return _match_icon(register_key.lower(), BINARY_SENSOR_ICON_MAPPING, BINARY_SENSOR_DEFAULT_ICON)
