"""Read APC Smart-UPS registers via Modbus TCP for validation."""

from __future__ import annotations

import argparse
import logging
from typing import Any

from pymodbus.client import ModbusTcpClient

from apc_modbus_registers import REGISTERS

_LOGGER = logging.getLogger(__name__)


def decode_register(registers: list[int], descriptor: dict[str, Any]) -> float | int | None:
    dtype = descriptor.get("type")
    scale = descriptor.get("scale", 1)

    if dtype in ("uint16", "int16") and registers:
        raw = registers[0]
        if dtype == "int16" and raw >= 0x8000:
            raw -= 0x10000
    elif dtype in ("uint32", "int32") and len(registers) >= 2:
        raw = (registers[0] << 16) | registers[1]
        if dtype == "int32" and raw >= 0x80000000:
            raw -= 0x100000000
    elif dtype == "ascii" and registers:
        chars: list[str] = []
        for reg in registers:
            chars.append(chr((reg >> 8) & 0xFF))
            chars.append(chr(reg & 0xFF))
        return "".join(chars).rstrip()
    else:
        return None

    if scale and scale != 1:
        return raw / scale

    return raw


def main() -> None:
    parser = argparse.ArgumentParser(description="Read APC UPS registers over Modbus TCP")
    parser.add_argument("host", nargs="?", default="192.168.100.8", help="Modbus TCP host")
    parser.add_argument("--port", type=int, default=502, help="Modbus TCP port")
    parser.add_argument("--unit", type=int, default=1, help="Modbus slave/unit ID")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    client = ModbusTcpClient(host=args.host, port=args.port)
    if not client.connect():
        raise SystemExit("Unable to connect to Modbus host")

    print(f"Connected to {args.host}:{args.port} (unit {args.unit})")
    try:
        for descriptor in REGISTERS:
            name = descriptor["key"]
            result = client.read_holding_registers(
                descriptor["address"],
                count=descriptor["count"],
                device_id=args.unit,
            )
            if result.isError():
                _LOGGER.error("Failed to read %s (%s)", name, result)
                continue

            value = decode_register(result.registers, descriptor)
            print(f"{name:30} => {value}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
