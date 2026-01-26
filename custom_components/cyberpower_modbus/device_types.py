# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/cyberpower-modbus-ha

"""Device type definitions for CyberPower devices."""

from enum import Enum


class CyberPowerDeviceType(Enum):
    """Enumeration of supported CyberPower UPS device types."""

    SINGLE_PHASE = "single_phase"
    THREE_PHASE = "three_phase"
    UNKNOWN = "unknown"
