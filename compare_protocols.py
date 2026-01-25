#!/usr/bin/env python3
"""
Compare SNMP and Modbus performance and capabilities for APC UPS monitoring.

Usage:
    python compare_protocols.py <ups_ip> [unit_id]
"""

import sys
import time
import subprocess
from pymodbus.client import ModbusTcpClient


def test_modbus_performance(ip, unit_id, iterations=5):
    """Test Modbus block read performance."""
    print("\n" + "="*70)
    print("MODBUS PERFORMANCE TEST")
    print("="*70)

    client = ModbusTcpClient(host=ip, port=502, timeout=5)
    if not client.connect():
        print("❌ Failed to connect")
        return None

    times = []

    # Test block reads
    blocks = [
        (0x0000, 24, "Block 1"),
        (0x001A, 21, "Block 2"),
        (0x004D, 1, "Block 3"),
    ]

    total_start = time.time()

    for iteration in range(iterations):
        print(f"\nIteration {iteration+1}:")
        iter_start = time.time()

        for start, count, name in blocks:
            block_start = time.time()
            try:
                result = client.read_holding_registers(start, count=count, device_id=unit_id)
                block_time = time.time() - block_start
                if hasattr(result, 'registers') and result.registers:
                    print(f"  ✅ {name}: {block_time*1000:.1f}ms ({count} regs)")
                else:
                    print(f"  ❌ {name}: FAILED")
            except Exception as e:
                block_time = time.time() - block_start
                print(f"  ❌ {name}: {type(e).__name__}")

        iter_time = time.time() - iter_start
        times.append(iter_time)
        print(f"  Total iteration time: {iter_time*1000:.1f}ms")

    total_time = time.time() - total_start
    client.close()

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"\nModbus Summary ({iterations} iterations):")
    print(f"  Average per cycle:     {avg_time*1000:.1f}ms")
    print(f"  Min:                   {min_time*1000:.1f}ms")
    print(f"  Max:                   {max_time*1000:.1f}ms")
    print(f"  Total time:            {total_time:.2f}s")
    print(f"  Network calls:         {iterations * 3} (3 block reads)")

    return {
        "avg": avg_time,
        "min": min_time,
        "max": max_time,
        "calls": iterations * 3,
    }


def test_snmp_performance(ip, iterations=5):
    """Test SNMP walk performance."""
    print("\n" + "="*70)
    print("SNMP PERFORMANCE TEST")
    print("="*70)

    times = []

    total_start = time.time()

    for iteration in range(iterations):
        print(f"\nIteration {iteration+1}:")
        iter_start = time.time()

        try:
            result = subprocess.run(
                ["snmpwalk", "-v", "2c", "-c", "public", ip, "1.3.6.1.4.1.318.1.1.1"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            iter_time = time.time() - iter_start
            times.append(iter_time)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print(f"  ✅ Retrieved {len(lines)} OIDs in {iter_time*1000:.1f}ms")
            else:
                print(f"  ❌ SNMP walk failed: {result.stderr[:100]}")

        except subprocess.TimeoutExpired:
            print(f"  ❌ SNMP walk timeout")
        except Exception as e:
            print(f"  ❌ Exception: {type(e).__name__}")

    total_time = time.time() - total_start

    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\nSNMP Summary ({iterations} iterations):")
        print(f"  Average per cycle:     {avg_time*1000:.1f}ms")
        print(f"  Min:                   {min_time*1000:.1f}ms")
        print(f"  Max:                   {max_time*1000:.1f}ms")
        print(f"  Total time:            {total_time:.2f}s")
        print(f"  Network calls:         {iterations} (1 walk per cycle)")

        return {
            "avg": avg_time,
            "min": min_time,
            "max": max_time,
            "calls": iterations,
        }

    return None


def test_snmp_targeted(ip, iterations=5):
    """Test targeted SNMP gets instead of walk."""
    print("\n" + "="*70)
    print("SNMP TARGETED GETS (OID-specific queries)")
    print("="*70)

    oids = [
        "1.3.6.1.4.1.318.1.1.1.1.1.1.0",  # Model
        "1.3.6.1.4.1.318.1.1.1.1.1.2.0",  # Device name
        "1.3.6.1.4.1.318.1.1.1.2.2.1.0",  # Battery SoC
        "1.3.6.1.4.1.318.1.1.1.2.2.2.0",  # Temperature
        "1.3.6.1.4.1.318.1.1.1.3.2.1.0",  # Output voltage
    ]

    times = []
    total_start = time.time()

    for iteration in range(iterations):
        print(f"\nIteration {iteration+1}:")
        iter_start = time.time()

        for oid in oids:
            oid_start = time.time()
            try:
                result = subprocess.run(
                    ["snmpget", "-v", "2c", "-c", "public", ip, oid],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                oid_time = time.time() - oid_start

                if result.returncode == 0:
                    print(f"  ✅ OID {oid[-3:]}: {oid_time*1000:.1f}ms")
                else:
                    print(f"  ❌ OID {oid[-3:]}: FAILED")

            except subprocess.TimeoutExpired:
                print(f"  ❌ OID {oid[-3:]}: timeout")

        iter_time = time.time() - iter_start
        times.append(iter_time)
        print(f"  Total iteration time: {iter_time*1000:.1f}ms")

    total_time = time.time() - total_start

    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\nSNMP Targeted Summary ({iterations} iterations):")
        print(f"  Average per cycle:     {avg_time*1000:.1f}ms")
        print(f"  Min:                   {min_time*1000:.1f}ms")
        print(f"  Max:                   {max_time*1000:.1f}ms")
        print(f"  Total time:            {total_time:.2f}s")
        print(f"  Network calls:         {iterations * len(oids)} ({len(oids)} OIDs per cycle)")

        return {
            "avg": avg_time,
            "min": min_time,
            "max": max_time,
            "calls": iterations * len(oids),
        }

    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python compare_protocols.py <ups_ip> [unit_id]")
        print("Example: python compare_protocols.py 192.168.100.7 1")
        sys.exit(1)

    ups_ip = sys.argv[1]
    unit_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    print("="*70)
    print("APC UPS: MODBUS vs SNMP COMPARISON")
    print("="*70)
    print(f"Target: {ups_ip}:502 (Modbus) / {ups_ip}:161 (SNMP)")
    print()

    # Run tests
    modbus_results = test_modbus_performance(ups_ip, unit_id, iterations=5)
    snmp_results = test_snmp_performance(ups_ip, iterations=5)
    snmp_targeted = test_snmp_targeted(ups_ip, iterations=5)

    # Summary
    print("\n" + "="*70)
    print("PERFORMANCE COMPARISON SUMMARY")
    print("="*70)

    if modbus_results and snmp_results and snmp_targeted:
        print("\n{:<25} {:<15} {:<15} {:<15}".format(
            "Protocol", "Avg (ms)", "Min (ms)", "Max (ms)"
        ))
        print("-" * 70)
        print("{:<25} {:<15.1f} {:<15.1f} {:<15.1f}".format(
            "Modbus (3 blocks)",
            modbus_results["avg"] * 1000,
            modbus_results["min"] * 1000,
            modbus_results["max"] * 1000,
        ))
        print("{:<25} {:<15.1f} {:<15.1f} {:<15.1f}".format(
            "SNMP Walk",
            snmp_results["avg"] * 1000,
            snmp_results["min"] * 1000,
            snmp_results["max"] * 1000,
        ))
        print("{:<25} {:<15.1f} {:<15.1f} {:<15.1f}".format(
            "SNMP Targeted (5 OIDs)",
            snmp_targeted["avg"] * 1000,
            snmp_targeted["min"] * 1000,
            snmp_targeted["max"] * 1000,
        ))

        # Calculate ratios
        snmp_walk_ratio = snmp_results["avg"] / modbus_results["avg"]
        snmp_targeted_ratio = snmp_targeted["avg"] / modbus_results["avg"]

        print("\nRelative Performance (Modbus = 1.0x baseline):")
        print(f"  Modbus:           1.0x (baseline)")
        print(f"  SNMP Walk:        {snmp_walk_ratio:.1f}x slower")
        print(f"  SNMP Targeted:    {snmp_targeted_ratio:.1f}x slower")


if __name__ == "__main__":
    main()
