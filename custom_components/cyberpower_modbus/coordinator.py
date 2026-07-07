# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/cyberpower-modbus-ha

"""Modbus data coordinator for CyberPower UPS sensors.

Note: pymodbus API compatibility
- pymodbus 2.x: result.isError() (camelCase)
- pymodbus 3.0-3.5: result.is_error() (snake_case)
- pymodbus 3.6+: Check hasattr(result, 'registers') instead
"""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from typing import Any, Callable

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL
from .device_types import CyberPowerDeviceType
from . import registers_single_phase
from .snmp_helper import get_snmp_telemetry_sync

_LOGGER = logging.getLogger(__name__)


def _build_configuration_url(host: str) -> str | None:
    """Return a device web UI URL for the configured host."""
    host = host.strip()
    if not host:
        return None
    if host.startswith("http://") or host.startswith("https://"):
        return host
    return f"http://{host}"


class CyberPowerModbusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls Modbus registers for the UPS."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: ModbusTcpClient,
        unit: int,
        device_name: str,
        host: str,
        port: int,
        entry_id: str,
        io_lock: asyncio.Lock,
        client_factory: Callable[[], ModbusTcpClient],
        snmp_community: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self._client = client
        self._client_factory = client_factory
        self._io_lock = io_lock
        self._host = host
        self._port = port
        self._entry_id = entry_id
        self._snmp_community = snmp_community
        self.configuration_url = _build_configuration_url(host)
        self.unit = unit
        self.device_name = device_name
        self._device_context = (
            f"{self.device_name} {self._host}:{self._port} unit {self.unit} entry {self._entry_id}"
        )
        # Initialize data as empty dict to ensure it's always present
        self.data: dict[str, Any] = {}
        # Device metadata (populated via SNMP at startup)
        self.hw_model: str | None = None
        self.serial_number: str | None = None
        self.fw_version: str | None = None
        self.fw_date: str | None = None
        # Default to single-phase; may be updated via SNMP detection.
        self.device_type: CyberPowerDeviceType = CyberPowerDeviceType.SINGLE_PHASE
        # Registers and blocks (loaded from factory based on device type)
        self.registers: list[dict[str, Any]] = registers_single_phase.REGISTERS
        self.register_blocks: list[dict[str, Any]] = registers_single_phase.REGISTER_BLOCKS
        self.register_map: dict[int, dict[str, Any]] = registers_single_phase.REGISTER_MAP
        self._backoff_until: float | None = None
        self._backoff_seconds: float = 0.0
        self._backoff_max_seconds: float = 60.0
        self._reconnect_count: int = 0
        self._post_connect_delay: float = 0.05
        self._inter_block_delay: float = 0.05

    def set_device_metadata(
        self,
        hw_model: str | None,
        serial_number: str | None,
        fw_version: str | None,
        fw_date: str | None,
    ) -> None:
        """Set device metadata from SNMP query."""
        self.hw_model = hw_model
        self.serial_number = serial_number
        self.fw_version = fw_version
        self.fw_date = fw_date
        _LOGGER.debug(
            "Device metadata set: model=%s, serial=%s, firmware=%s [%s]",
            hw_model,
            serial_number,
            fw_version,
            self._device_context,
        )

    def set_device_type(self, device_type: CyberPowerDeviceType) -> None:
        """Update device type and adjust read timing."""
        self.device_type = device_type
        if device_type == CyberPowerDeviceType.THREE_PHASE:
            self._post_connect_delay = 0.1
            self._inter_block_delay = 0.1
        else:
            self._post_connect_delay = 0.05
            self._inter_block_delay = 0.05
        _LOGGER.info(
            "Device type set to: %s (post_connect_delay=%.0fms, inter_block_delay=%.0fms) [%s]",
            device_type.value,
            self._post_connect_delay * 1000,
            self._inter_block_delay * 1000,
            self._device_context,
        )

    def set_registers(
        self,
        registers: list[dict[str, Any]],
        register_blocks: list[dict[str, Any]],
        register_map: dict[int, dict[str, Any]],
    ) -> None:
        """Set registers, blocks, and map for the device type."""
        self.registers = registers
        self.register_blocks = register_blocks
        self.register_map = register_map
        _LOGGER.debug(
            "Registers updated: %d registers, %d blocks [%s]",
            len(registers),
            len(register_blocks),
            self._device_context,
        )

    async def async_close(self) -> None:
        """Close the current Modbus client."""
        await self._close_client()

    @staticmethod
    def _is_error_response(result) -> bool:
        """Check if a Modbus response indicates an error (pymodbus 3.6+ compatible)."""
        # For pymodbus 3.6+: Check if registers attribute exists and is not None
        if not hasattr(result, 'registers'):
            return True
        if result.registers is None:
            return True
        return False

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the UPS via Modbus (block reads with fallback to individual reads)."""
        data: dict[str, Any] = {}
        errors: list[str] = []
        poll_start = time.monotonic()
        lock_wait = 0.0
        connect_elapsed = 0.0
        block_reads_elapsed = 0.0
        individual_reads_elapsed = 0.0
        close_elapsed = 0.0
        modbus_cycle_elapsed = 0.0
        reconnects_at_start = self._reconnect_count

        now = time.monotonic()
        if self._backoff_until and now < self._backoff_until:
            remaining = self._backoff_until - now
            raise UpdateFailed(f"Backoff active for {remaining:.1f}s")

        _LOGGER.info("Starting update cycle [%s]", self._device_context)

        lock_start = time.monotonic()
        async with self._io_lock:
            lock_wait = time.monotonic() - lock_start
            if lock_wait > 0:
                _LOGGER.debug("Waited %.3fs for Modbus lock [%s]", lock_wait, self._device_context)

            cycle_start = time.monotonic()
            connect_start = time.monotonic()
            connected = await self._connect_client()
            connect_elapsed = time.monotonic() - connect_start
            if not connected:
                self._apply_backoff()
                raise UpdateFailed("Unable to connect to Modbus device")

            if self._post_connect_delay:
                await asyncio.sleep(self._post_connect_delay)

            try:
                # Try block reads first (optimized) with reconnection logic
                _LOGGER.debug("Attempting block reads [%s]", self._device_context)
                block_reads_start = time.monotonic()
                block_read_ok = await self._try_block_reads(data, errors)
                block_reads_elapsed = time.monotonic() - block_reads_start
                _LOGGER.debug(
                    "Block reads result: %s (data keys: %s) [%s]",
                    "success" if block_read_ok else "failed",
                    list(data.keys()),
                    self._device_context,
                )

                # If block reads failed, fall back to individual reads with reconnection
                if not block_read_ok:
                    _LOGGER.info(
                        "Block reads failed or incomplete, falling back to individual register reads [%s]",
                        self._device_context,
                    )
                    # Don't clear data - preserve any partial data from successful block reads
                    individual_reads_start = time.monotonic()
                    await self._try_individual_reads(data, errors)
                    individual_reads_elapsed = time.monotonic() - individual_reads_start
                    _LOGGER.debug(
                        "Individual reads fallback complete (data keys: %s) [%s]",
                        list(data.keys()),
                        self._device_context,
                    )

                if not data:
                    self._apply_backoff()
                    raise UpdateFailed(f"Unable to read any registers: {', '.join(errors)}")

                if errors:
                    _LOGGER.debug(
                        "Failed to read %d registers: %s [%s]",
                        len(errors),
                        ", ".join(errors),
                        self._device_context,
                    )

                # Log successful data keys for debugging
                _LOGGER.debug(
                    "Successfully read %d registers: %s [%s]",
                    len(data),
                    ", ".join(sorted(data.keys())),
                    self._device_context,
                )
                self._reset_backoff()
            finally:
                close_start = time.monotonic()
                await self._close_client()
                close_elapsed = time.monotonic() - close_start
                modbus_cycle_elapsed = time.monotonic() - cycle_start
                _LOGGER.info(
                    "Update cycle complete in %.3fs [%s]",
                    modbus_cycle_elapsed,
                    self._device_context,
                )
                _LOGGER.info(
                    "Poll timing breakdown: total=%.3fs, lock_wait=%.3fs, modbus=%.3fs, "
                    "connect=%.3fs, block_reads=%.3fs, individual_reads=%.3fs, close=%.3fs, reconnects=%d [%s]",
                    time.monotonic() - poll_start,
                    lock_wait,
                    modbus_cycle_elapsed,
                    connect_elapsed,
                    block_reads_elapsed,
                    individual_reads_elapsed,
                    close_elapsed,
                    self._reconnect_count - reconnects_at_start,
                    self._device_context,
                )

        await self._merge_snmp_telemetry(data)
        return data

    async def _merge_snmp_telemetry(self, data: dict[str, Any]) -> None:
        """Merge optional SNMP telemetry without affecting Modbus polling success."""
        try:
            telemetry = await self.hass.async_add_executor_job(
                get_snmp_telemetry_sync,
                self._host,
                self._snmp_community,
            )
        except (OSError, RuntimeError, ValueError) as err:
            _LOGGER.debug("SNMP telemetry polling failed: %s [%s]", err, self._device_context)
            return

        if telemetry:
            data.update(telemetry)
            _LOGGER.debug(
                "SNMP telemetry merged: %s [%s]",
                ", ".join(sorted(telemetry.keys())),
                self._device_context,
            )

    async def _try_block_reads(self, data: dict[str, Any], errors: list[str]) -> bool:
        """Try to read data using block reads. Returns True if any blocks succeed, False if all fail."""
        block_success_count = 0

        for block in self.register_blocks:
            try:
                _LOGGER.debug(
                    "Reading block %s (addr 0x%04X, count %d) [%s]",
                    block["name"],
                    block["start_address"],
                    block["count"],
                    self._device_context,
                )
                block_start = time.monotonic()
                read_request = functools.partial(
                    self._client.read_holding_registers,
                    block["start_address"],
                    count=block["count"],
                    device_id=self.unit,
                )
                result = await self.hass.async_add_executor_job(read_request)
                block_duration = time.monotonic() - block_start

                # Check if result is an error
                if self._is_error_response(result):
                    _LOGGER.warning(
                        "Block read returned error %s (0x%04X, %d registers): %s [%s]",
                        block["name"],
                        block["start_address"],
                        block["count"],
                        result,
                        self._device_context,
                    )
                    # Mark all registers in this block as failed, but continue to next block
                    for addr in block["registers"]:
                        if addr in self.register_map:
                            errors.append(self.register_map[addr]["key"])
                    if self._inter_block_delay:
                        await asyncio.sleep(self._inter_block_delay)
                    continue

                # Block read successful, increment counter
                _LOGGER.debug(
                    "Block read succeeded: %s (%.1fms) [%s]",
                    block["name"],
                    block_duration * 1000,
                    self._device_context,
                )
                block_success_count += 1

                # Decode each register in the block
                for addr in block["registers"]:
                    if addr not in self.register_map:
                        continue

                    descriptor = self.register_map[addr]
                    offset = addr - block["start_address"]
                    reg_count = descriptor["count"]
                    reg_slice = result.registers[offset : offset + reg_count]

                    if len(reg_slice) < reg_count:
                        _LOGGER.debug(
                            "Insufficient registers for %s at offset %d [%s]",
                            descriptor["key"],
                            offset,
                            self._device_context,
                        )
                        errors.append(descriptor["key"])
                        continue

                    try:
                        value = self._decode_register(reg_slice, descriptor)
                        if value is not None:
                            data[descriptor["key"]] = value
                    except (ValueError, TypeError, IndexError) as err:
                        errors.append(descriptor["key"])
                        _LOGGER.debug(
                            "Error decoding register %s: %s [%s]",
                            descriptor["key"],
                            err,
                            self._device_context,
                        )

            except (ModbusException, OSError, RuntimeError) as err:
                _LOGGER.warning(
                    "Exception in block read %s: %s (type: %s) [%s]",
                    block["name"],
                    err,
                    type(err).__name__,
                    self._device_context,
                )

                # Try to reconnect on connection errors (same as individual reads)
                if self._is_connection_error(err):
                    _LOGGER.debug(
                        "Connection error in block read, attempting to reconnect and retry [%s]",
                        self._device_context,
                    )
                    try:
                        if not await self._rebuild_and_connect():
                            raise RuntimeError("Reconnect failed")

                        # Retry the block read
                        read_request = functools.partial(
                            self._client.read_holding_registers,
                            block["start_address"],
                            count=block["count"],
                            device_id=self.unit,
                        )
                        result = await self.hass.async_add_executor_job(read_request)

                        if not self._is_error_response(result):
                            _LOGGER.debug(
                                "Block read succeeded after reconnect: %s [%s]",
                                block["name"],
                                self._device_context,
                            )
                            block_success_count += 1
                            # Decode the registers from this successful block
                            for addr in block["registers"]:
                                if addr not in self.register_map:
                                    continue

                                descriptor = self.register_map[addr]
                                offset = addr - block["start_address"]
                                reg_count = descriptor["count"]
                                reg_slice = result.registers[offset : offset + reg_count]

                                if len(reg_slice) < reg_count:
                                    errors.append(descriptor["key"])
                                    continue

                                try:
                                    value = self._decode_register(reg_slice, descriptor)
                                    if value is not None:
                                        data[descriptor["key"]] = value
                                except (ValueError, TypeError, IndexError) as decode_err:
                                    errors.append(descriptor["key"])
                                    _LOGGER.debug(
                                        "Error decoding register %s: %s [%s]",
                                        descriptor["key"],
                                        decode_err,
                                        self._device_context,
                                    )
                            continue  # Skip the error marking below
                    except (ModbusException, OSError, RuntimeError) as reconnect_err:
                        _LOGGER.debug(
                            "Failed to reconnect and retry block: %s [%s]",
                            reconnect_err,
                            self._device_context,
                        )

                # Mark all registers in this block as failed
                for addr in block["registers"]:
                    if addr in self.register_map:
                        errors.append(self.register_map[addr]["key"])
            finally:
                if self._inter_block_delay:
                    await asyncio.sleep(self._inter_block_delay)

        # Return True if at least one block succeeded
        return block_success_count > 0

    async def _try_individual_reads(self, data: dict[str, Any], errors: list[str]) -> None:
        """Try to read data using individual registers with reconnection logic."""
        consecutive_failures = 0

        for descriptor in self.registers:
            try:
                # Try to read register with automatic reconnection if needed
                result = await self._read_register_with_reconnect(descriptor)

                if result is None:
                    # Connection error, already logged
                    errors.append(descriptor["key"])
                    consecutive_failures += 1

                    # If too many consecutive failures, abort
                    if consecutive_failures >= 5:
                        _LOGGER.warning(
                            "Too many consecutive read failures, aborting update cycle [%s]",
                            self._device_context,
                        )
                        break
                    continue

                # Reset failure counter on successful read
                consecutive_failures = 0

                # Check if result is an error
                if self._is_error_response(result):
                    errors.append(descriptor["key"])
                    _LOGGER.debug(
                        "Failed to read register %s (address 0x%04X): %s [%s]",
                        descriptor["key"],
                        descriptor["address"],
                        result,
                        self._device_context,
                    )
                    continue

                value = self._decode_register(result.registers, descriptor)
                if value is not None:
                    data[descriptor["key"]] = value
            except (ModbusException, OSError, RuntimeError, ValueError, TypeError, IndexError) as err:
                errors.append(descriptor["key"])
                consecutive_failures += 1
                _LOGGER.debug(
                    "Exception reading register %s (address 0x%04X): %s [%s]",
                    descriptor["key"],
                    descriptor["address"],
                    err,
                    self._device_context,
                )

                if consecutive_failures >= 5:
                    _LOGGER.warning(
                        "Too many consecutive read failures, aborting update cycle [%s]",
                        self._device_context,
                    )
                    break
            finally:
                if self._inter_block_delay:
                    await asyncio.sleep(self._inter_block_delay)

    async def _read_register_with_reconnect(self, descriptor: dict[str, Any]):
        """Read a register with automatic reconnection on failure."""
        # Attempt read with current connection
        try:
            read_request = functools.partial(
                self._client.read_holding_registers,
                descriptor["address"],
                count=descriptor["count"],
                device_id=self.unit,
            )
            result = await self.hass.async_add_executor_job(read_request)
            return result
        except (ModbusException, OSError, RuntimeError) as err:
            # Connection likely dropped, attempt to reconnect and retry
            _LOGGER.debug(
                "Read error for %s (address 0x%04X): %s (type: %s) [%s]",
                descriptor["key"],
                descriptor["address"],
                err,
                type(err).__name__,
                self._device_context,
            )

            if self._is_connection_error(err):
                _LOGGER.debug(
                    "Connection error detected, attempting reconnect for %s [%s]",
                    descriptor["key"],
                    self._device_context,
                )

                if not await self._rebuild_and_connect():
                    return None

                try:
                    # Retry the read
                    read_request = functools.partial(
                        self._client.read_holding_registers,
                        descriptor["address"],
                        count=descriptor["count"],
                        device_id=self.unit,
                    )
                    result = await self.hass.async_add_executor_job(read_request)
                    _LOGGER.debug(
                        "Successfully reconnected and read register %s [%s]",
                        descriptor["key"],
                        self._device_context,
                    )
                    return result
                except (ModbusException, OSError, RuntimeError) as reconnect_err:
                    _LOGGER.debug(
                        "Failed to reconnect and read register %s: %s [%s]",
                        descriptor["key"],
                        reconnect_err,
                        self._device_context,
                    )
                    return None
            else:
                # Not a connection error, re-raise
                raise

    async def _connect_client(self) -> bool:
        """Connect the Modbus client for this update cycle."""
        start = time.monotonic()
        connect_request = functools.partial(self._client.connect)
        connected = await self.hass.async_add_executor_job(connect_request)
        duration = (time.monotonic() - start) * 1000
        _LOGGER.debug(
            "Modbus connect %s in %.1fms [%s]",
            "ok" if connected else "failed",
            duration,
            self._device_context,
        )
        return connected

    async def _close_client(self) -> None:
        """Close the Modbus client."""
        start = time.monotonic()
        close_request = functools.partial(self._client.close)
        await self.hass.async_add_executor_job(close_request)
        duration = (time.monotonic() - start) * 1000
        _LOGGER.debug("Modbus close completed in %.1fms [%s]", duration, self._device_context)

    async def _rebuild_and_connect(self) -> bool:
        """Rebuild the Modbus client after socket errors and reconnect."""
        self._reconnect_count += 1
        await self._close_client()
        self._client = self._client_factory()
        connected = await self._connect_client()
        if connected and self._post_connect_delay:
            await asyncio.sleep(self._post_connect_delay)
        return connected

    def _is_connection_error(self, err: Exception) -> bool:
        err_str = str(err).lower()
        return "broken pipe" in err_str or "connection" in err_str or "reset" in err_str

    def _apply_backoff(self) -> None:
        if self._backoff_seconds <= 0:
            self._backoff_seconds = 5.0
        else:
            self._backoff_seconds = min(self._backoff_max_seconds, self._backoff_seconds * 2)
        self._backoff_until = time.monotonic() + self._backoff_seconds
        _LOGGER.warning(
            "Applying backoff: %.0fs [%s]",
            self._backoff_seconds,
            self._device_context,
        )

    def _reset_backoff(self) -> None:
        if self._backoff_seconds or self._backoff_until:
            _LOGGER.debug("Backoff reset [%s]", self._device_context)
        self._backoff_seconds = 0.0
        self._backoff_until = None

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
            word_order = descriptor.get("word_order", "big")
            if word_order == "little":
                raw = (registers[1] << 16) | registers[0]
            else:
                raw = (registers[0] << 16) | registers[1]
            if dtype == "int32" and raw >= 0x80000000:
                raw -= 0x100000000
        elif dtype == "ascii" and registers:
            ascii_width = descriptor.get("ascii_width", 2)
            chars: list[str] = []
            for reg in registers:
                if ascii_width == 1:
                    # One char per register: character is in lower byte (LSB)
                    # Upper byte is typically 0x00 padding
                    chars.append(chr(reg & 0xFF))
                else:
                    # Two chars per register: MSB first (big-endian)
                    chars.append(chr((reg >> 8) & 0xFF))
                    chars.append(chr(reg & 0xFF))
            return "".join(chars).rstrip()
        else:
            return None

        if scale and scale != 1:
            return raw / scale

        return raw
