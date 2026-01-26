# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/cyberpower-modbus-ha

"""Factory pattern for selecting device-type-specific registers."""

from __future__ import annotations

import logging
from typing import Any

from .device_types import CyberPowerDeviceType
from . import registers_single_phase

_LOGGER = logging.getLogger(__name__)


def get_registers_for_device(device_type: CyberPowerDeviceType) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[int, dict[str, Any]]]:
    """Get registers, blocks, and map for the specified device type.

    Args:
        device_type: The detected or configured device type

    Returns:
        Tuple of (REGISTERS, REGISTER_BLOCKS, REGISTER_MAP)
    """
    if device_type == CyberPowerDeviceType.SINGLE_PHASE:
        return (
            registers_single_phase.REGISTERS,
            registers_single_phase.REGISTER_BLOCKS,
            registers_single_phase.REGISTER_MAP,
        )
    elif device_type == CyberPowerDeviceType.THREE_PHASE:
        # Import here to avoid circular imports and lazy-load three-phase registers
        try:
            from . import registers_three_phase
            return (
                registers_three_phase.REGISTERS,
                registers_three_phase.REGISTER_BLOCKS,
                registers_three_phase.REGISTER_MAP,
            )
        except ImportError:
            _LOGGER.warning("Three-phase register module not available, falling back to single-phase")
            return (
                registers_single_phase.REGISTERS,
                registers_single_phase.REGISTER_BLOCKS,
                registers_single_phase.REGISTER_MAP,
            )
    else:
        # Unknown type defaults to single-phase
        _LOGGER.debug("Unknown device type %s, defaulting to single-phase", device_type)
        return (
            registers_single_phase.REGISTERS,
            registers_single_phase.REGISTER_BLOCKS,
            registers_single_phase.REGISTER_MAP,
        )
