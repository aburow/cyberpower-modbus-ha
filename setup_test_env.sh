#!/bin/bash
# Setup script for Modbus test environment

set -e

echo "================================"
echo "Setting up Modbus Test Environment"
echo "================================"

# Check if venv exists
if [ -d "test_venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf test_venv
    else
        echo "Using existing venv"
    fi
fi

# Create virtual environment if needed
if [ ! -d "test_venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv test_venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source test_venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install pymodbus
echo "Installing pymodbus..."
pip install "pymodbus>=3.1.1"

# Show installed version
echo ""
echo "================================"
echo "Installation Complete"
echo "================================"
echo "Installed packages:"
pip list | grep pymodbus

echo ""
echo "================================"
echo "Ready to Test!"
echo "================================"
echo "Run the test script:"
echo "  source test_venv/bin/activate"
echo "  python test_modbus_blocks.py <UPS_IP> [unit_id]"
echo ""
echo "Example:"
echo "  python test_modbus_blocks.py 192.168.100.7 1"
echo ""
echo "When done, deactivate with:"
echo "  deactivate"
