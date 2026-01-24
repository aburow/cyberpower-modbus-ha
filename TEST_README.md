# Modbus Block Read Test Scripts

These scripts test the block read capabilities of your APC UPS to determine optimal configuration.

## Quick Start

### 1. Setup Test Environment

```bash
cd /home/dev/projects/apc-modbus-ha
./setup_test_env.sh
```

This will:
- Create a Python virtual environment (`test_venv/`)
- Install pymodbus 3.11.2 (matching Home Assistant version)
- Show installation summary

### 2. Run Block Read Tests

Activate the virtual environment and run the test:

```bash
source test_venv/bin/activate
python test_modbus_blocks.py <UPS_IP> [unit_id]
```

**Examples:**

```bash
# Test RT 2000 RM XL at 192.168.100.7 with unit ID 1 (default)
python test_modbus_blocks.py 192.168.100.7

# Test 600VA at 192.168.100.8 with explicit unit ID
python test_modbus_blocks.py 192.168.100.8 1
```

### 3. Deactivate When Done

```bash
deactivate
```

## What the Test Does

The script tests different block sizes:

1. **Single register** (1 register) - Baseline test
2. **Small block** (5 registers) - Conservative
3. **Medium block** (10 registers) - Balanced
4. **Large block** (24 registers) - Optimal if supported
5. **Block 2** (21 registers) - Second block from integration
6. **Isolated register** (0x004D) - Single battery current register

For each test, it:
- Attempts to read the specified block
- Measures read time
- Shows first 5 register values
- Reports success/failure

## Understanding Results

### ✅ All tests pass
Your UPS supports large block reads. Block read optimization will work perfectly.

### ⚠️ Only small/medium blocks pass
Your UPS has limitations. Consider using smaller block sizes in the integration.

### ❌ Only single register reads pass
Your UPS doesn't support block reads. Individual register reads are required.

## Sample Output

```
============================================================
APC UPS Modbus Block Read Test
============================================================
Target: 192.168.100.7:502
Unit ID: 1
Timeout: 5 seconds

Connecting to UPS...
✅ Connected successfully

============================================================
Testing: Large block (24 regs)
Address: 0x0000, Count: 24
============================================================
❌ EXCEPTION - BrokenPipeError: [Errno 32] Broken pipe

============================================================
Testing: Single register
Address: 0x0000, Count: 1
============================================================
✅ SUCCESS - Read 1 registers in 0.287s
   First 5 values: [8]
   Register 0x0000 = 8 (0x0008)

============================================================
TEST SUMMARY
============================================================
❌ FAIL - Large block (24 regs)
✅ PASS - Single register

Result: 1/6 tests passed

============================================================
RECOMMENDATIONS
============================================================
❌ Your UPS does not support block reads
   Use individual register reads only
```

## Troubleshooting

### Connection refused
- Verify UPS IP address is correct
- Check that Modbus TCP is enabled on the UPS
- Ensure port 502 is accessible (firewall)

### All tests fail
- Check unit ID (usually 1, but might be different)
- Verify UPS supports Modbus TCP (not just Modbus RTU)
- Try from a different machine to rule out network issues

### Broken pipe errors
- Normal for block reads if UPS doesn't support them
- Individual reads should still work

## Files

- `setup_test_env.sh` - Setup script to create venv and install dependencies
- `test_modbus_blocks.py` - Main test script
- `test_venv/` - Virtual environment (created by setup script)
- `TEST_README.md` - This file

## Cleanup

To remove the test environment:

```bash
rm -rf test_venv
```

The test scripts (`test_modbus_blocks.py`, `setup_test_env.sh`) can remain for future testing.
