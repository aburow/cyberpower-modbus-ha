#!/usr/bin/env python3
"""
Test script to verify Modbus block read capabilities of APC UPS.
Tests different block sizes to determine optimal configuration.

Usage:
    python test_modbus_blocks.py <ups_ip> [unit_id]
"""

import sys
import time
from pymodbus.client import ModbusTcpClient

# Test configurations
TEST_BLOCKS = [
    {"name": "Single register", "start": 0x0000, "count": 1},
    {"name": "Small block (5 regs)", "start": 0x0000, "count": 5},
    {"name": "Medium block (10 regs)", "start": 0x0000, "count": 10},
    {"name": "Large block (24 regs)", "start": 0x0000, "count": 24},
    {"name": "Block 2 (21 regs)", "start": 0x001A, "count": 21},
    {"name": "Single isolated (0x004D)", "start": 0x004D, "count": 1},
]


def test_block_read(client, unit_id, block):
    """Test a single block read."""
    print(f"\n{'='*60}")
    print(f"Testing: {block['name']}")
    print(f"Address: 0x{block['start']:04X}, Count: {block['count']}")
    print(f"{'='*60}")

    try:
        start_time = time.time()

        # Use the same parameter as Home Assistant coordinator
        result = client.read_holding_registers(
            block['start'],
            count=block['count'],
            device_id=unit_id
        )

        elapsed = time.time() - start_time

        # Check if result is valid (pymodbus 3.x)
        if not hasattr(result, 'registers') or result.registers is None:
            print(f"❌ FAILED - Invalid response")
            print(f"   Response: {result}")
            return False

        print(f"✅ SUCCESS - Read {len(result.registers)} registers in {elapsed:.3f}s")
        print(f"   First 5 values: {result.registers[:5]}")

        # Decode first register as example
        if result.registers:
            print(f"   Register 0x{block['start']:04X} = {result.registers[0]} (0x{result.registers[0]:04X})")

        return True

    except Exception as e:
        print(f"❌ EXCEPTION - {type(e).__name__}: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_modbus_blocks.py <ups_ip> [unit_id]")
        print("Example: python test_modbus_blocks.py 192.168.100.7 1")
        sys.exit(1)

    ups_ip = sys.argv[1]
    unit_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    print("="*60)
    print("APC UPS Modbus Block Read Test")
    print("="*60)
    print(f"Target: {ups_ip}:502")
    print(f"Unit ID: {unit_id}")
    print(f"Timeout: 5 seconds")

    # Create client
    print("\nConnecting to UPS...")
    client = ModbusTcpClient(host=ups_ip, port=502, timeout=5)

    if not client.connect():
        print("❌ FAILED to connect to UPS")
        sys.exit(1)

    print("✅ Connected successfully")

    # Run tests
    results = {}
    for block in TEST_BLOCKS:
        success = test_block_read(client, unit_id, block)
        results[block['name']] = success
        time.sleep(0.5)  # Small delay between tests

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nResult: {passed}/{total} tests passed")

    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)

    if results.get("Large block (24 regs)"):
        print("✅ Your UPS supports large block reads (24 registers)")
        print("   Block read optimization will work well")
    elif results.get("Medium block (10 regs)"):
        print("⚠️  Your UPS supports medium blocks (10 registers)")
        print("   Consider splitting blocks into smaller sizes")
    elif results.get("Small block (5 regs)"):
        print("⚠️  Your UPS only supports small blocks (5 registers)")
        print("   Use smaller block sizes for optimization")
    else:
        print("❌ Your UPS does not support block reads")
        print("   Use individual register reads only")

    client.close()
    print("\nConnection closed")


if __name__ == "__main__":
    main()
