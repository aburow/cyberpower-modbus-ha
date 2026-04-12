# SPDX-FileCopyrightText: 2026 github.com/aburow
# SPDX-License-Identifier: GPL-3.0-only

"""Unified default entity availability profiles (dependency-free)."""

from __future__ import annotations


UPS_DEVICE_FAMILIES = ("single_phase", "three_phase", "unknown")

STANDARD_ENABLED_CANONICAL_KEYS: tuple[str, ...] = (
    "runtime_remaining",
    "battery_state_of_charge",
    "input_voltage",
    "output_voltage",
    "output_load_percent",
    "online_state",
    "on_battery_state",
)

STANDARD_ENABLED_CANONICAL_SET = set(STANDARD_ENABLED_CANONICAL_KEYS)

SENSOR_CANONICAL_PATTERNS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("runtime",), "runtime_remaining"),
    (("state_of_charge", "battery_charge", "battery_capacity"), "battery_state_of_charge"),
    (("input_voltage", "utility_voltage"), "input_voltage"),
    (("output_voltage",), "output_voltage"),
    (("output_load_percent", "load_percent", "output_load"), "output_load_percent"),
    (("load_on_source",), "online_state"),
)

BINARY_CANONICAL_PATTERNS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("battery_discharging",), "on_battery_state"),
    (("online", "ac_power", "mains"), "online_state"),
)


def _match_pattern_key(
    local_key: str, patterns: tuple[tuple[tuple[str, ...], str], ...]
) -> str | None:
    key_lower = local_key.lower()
    for fragments, canonical_key in patterns:
        if any(fragment in key_lower for fragment in fragments):
            return canonical_key
    return None


def resolve_sensor_canonical_key(local_key: str) -> str | None:
    """Resolve a local sensor key to its canonical sensor key."""
    return _match_pattern_key(local_key, SENSOR_CANONICAL_PATTERNS)


def resolve_binary_canonical_key(local_key: str) -> str | None:
    """Resolve a local binary sensor key to its canonical binary key."""
    return _match_pattern_key(local_key, BINARY_CANONICAL_PATTERNS)


def is_sensor_enabled_by_default(local_key: str, device_family: str) -> bool:
    """Return whether a sensor should be entity-registry enabled by default."""
    if device_family not in UPS_DEVICE_FAMILIES:
        return True
    canonical_key = resolve_sensor_canonical_key(local_key)
    return canonical_key in STANDARD_ENABLED_CANONICAL_SET


def is_binary_sensor_enabled_by_default(local_key: str, device_family: str) -> bool:
    """Return whether a binary sensor should be entity-registry enabled by default."""
    if device_family not in UPS_DEVICE_FAMILIES:
        return True
    canonical_key = resolve_binary_canonical_key(local_key)
    return canonical_key in STANDARD_ENABLED_CANONICAL_SET


def entity_enabled_default(local_entity_key: str) -> bool:
    """Return whether this entity key should be enabled by default.

    This external API is consumed by ups-docker-ha without device-family context.
    """
    try:
        if resolve_sensor_canonical_key(local_entity_key) is not None:
            return is_sensor_enabled_by_default(local_entity_key, "unknown")
        return is_binary_sensor_enabled_by_default(local_entity_key, "unknown")
    except (AttributeError, TypeError, ValueError):
        return True
