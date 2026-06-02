# SPDX-FileCopyrightText: 2026 github.com/aburow
# SPDX-License-Identifier: GPL-3.0-only

"""Unified capability profiles for UPS Unified bridge interop."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "2.0.0"
contract_version = CONTRACT_VERSION

DEFAULT_POLL_GROUPS: dict[str, dict[str, int]] = {
    "fast": {"interval_s": 10},
    "slow": {"interval_s": 60},
}

_SINGLE_FAST_KEYS = {
    "runtime_remaining",
    "battery_capacity",
    "utility_voltage",
    "output_voltage",
    "output_load_percent",
    "battery_discharging",
}

_THREE_FAST_PREFIXES = (
    "input_voltage_",
    "output_voltage_",
    "load_percent_",
)
_THREE_FAST_KEYS = {
    "battery_runtime_remaining",
    "battery_capacity",
    "load_on_source",
}


def _parse_register_data(file_name: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Parse REGISTERS and REGISTER_BLOCKS from register definition modules."""
    source = (Path(__file__).parent / file_name).read_text()
    match = re.search(
        r"REGISTERS\s*=\s*(\[.*?\])\n\nREGISTER_BLOCKS\s*=\s*(\[.*?\])\n\nREGISTER_MAP",
        source,
        re.S,
    )
    if not match:
        return ([], [])
    registers = ast.literal_eval(match.group(1))
    blocks = ast.literal_eval(match.group(2))
    return (registers, blocks)


def _register_poll_group(profile_id: str, metric_key: str) -> str:
    """Resolve poll group for a metric key."""
    if profile_id == "cyberpower_modbus_single_phase":
        return "fast" if metric_key in _SINGLE_FAST_KEYS else "slow"
    if metric_key in _THREE_FAST_KEYS:
        return "fast"
    if any(metric_key.startswith(prefix) for prefix in _THREE_FAST_PREFIXES):
        return "fast"
    return "slow"


def _block_poll_group(block_name: str) -> str:
    """Resolve poll group for a register block."""
    name = block_name.lower()
    if "measurement" in name or "battery" in name:
        return "fast"
    return "slow"


def _build_modbus_profile(profile_id: str, file_name: str) -> dict[str, Any]:
    """Build modbus capability profile from register source file."""
    registers, register_blocks = _parse_register_data(file_name)

    profile_registers: list[dict[str, Any]] = []
    for register in registers:
        normalized = dict(register)
        normalized["poll_group"] = _register_poll_group(profile_id, register["key"])
        if "word_order" not in normalized:
            normalized["word_order"] = "big"
        profile_registers.append(normalized)

    profile_blocks: list[dict[str, Any]] = []
    for block in register_blocks:
        normalized = {
            "name": block["name"],
            "start_address": block["start_address"],
            "count": block["count"],
            "poll_group": _block_poll_group(block["name"]),
        }
        profile_blocks.append(normalized)

    return {
        "profile_id": profile_id,
        "protocol": "modbus",
        "registers": profile_registers,
        "register_blocks": profile_blocks,
        "poll_groups": dict(DEFAULT_POLL_GROUPS),
    }


CAPABILITY_PROFILES: tuple[dict[str, Any], ...] = (
    _build_modbus_profile(
        "cyberpower_modbus_single_phase", "registers_single_phase.py"
    ),
    _build_modbus_profile("cyberpower_modbus_three_phase", "registers_three_phase.py"),
)
