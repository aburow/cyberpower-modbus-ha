"""Modbus data coordinator for APC UPS sensors."""

from __future__ import annotations

import functools
import logging
from typing import Any

from pymodbus.client import ModbusTcpClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, REGISTERS, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class APCModbusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls Modbus registers for the UPS."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: ModbusTcpClient,
        unit: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client
        self.unit = unit

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the UPS via Modbus."""
        data: dict[str, Any] = {}

        for descriptor in REGISTERS:
            read_request = functools.partial(
                self.client.read_holding_registers,
                descriptor["address"],
                count=descriptor["count"],
                device_id=self.unit,
            )
            result = await self.hass.async_add_executor_job(read_request)
            if result.isError():
                raise UpdateFailed(
                    f"Modbus read failure for {descriptor['key']}"
                )

            value = self._decode_register(result.registers, descriptor)
            if value is not None:
                data[descriptor["key"]] = value

        return data

    def _decode_register(
        self, registers: list[int], descriptor: dict[str, Any]
    ) -> float | int | None:
        """Decode register payloads to a numeric value."""
        dtype = descriptor.get("type")
        scale = descriptor.get("scale", 1)

        raw: int

        if dtype in ("uint16", "int16") and registers:
            raw = registers[0]
            if dtype == "int16" and raw >= 0x8000:
                raw -= 0x10000
        elif dtype in ("uint32", "int32") and len(registers) >= 2:
            raw = (registers[0] << 16) | registers[1]
            if dtype == "int32" and raw >= 0x80000000:
                raw -= 0x100000000
        elif dtype == "ascii" and registers:
            ascii_width = descriptor.get("ascii_width", 2)
            chars: list[str] = []
            for reg in registers:
                if ascii_width == 1:
                    chars.append(chr(reg & 0xFF))
                else:
                    chars.append(chr((reg >> 8) & 0xFF))
                    chars.append(chr(reg & 0xFF))
            return "".join(chars).rstrip()
        else:
            return None

        if scale and scale != 1:
            return raw / scale

        return raw
