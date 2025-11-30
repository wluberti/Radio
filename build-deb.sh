#!/bin/bash
# Build script for PyRadio
# Checks dependencies and builds the .deb package

set -e

echo "=========================================="
echo "PyRadio .deb Package Builder"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "debian" ]; then
    echo "Error: Please run this script from the pyradio source directory"
    exit 1
fi

# Check if build dependencies are installed
echo "Checking build dependencies..."
if ! dpkg-checkbuilddeps 2>/dev/null; then
    echo ""
    echo "Missing build dependencies detected."
    echo "Installing required packages..."
    echo ""

    sudo apt-get update
    sudo apt-get install -y \
        build-essential \
        debhelper \
        dh-python \
        python3-all \
        python3-setuptools \
        python3-gi \
        gir1.2-gtk-4.0

    echo ""
    echo "Build dependencies installed successfully."
fi

echo ""
echo "Building .deb package..."
echo ""

# Build the package
dpkg-buildpackage -us -uc -b

echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
echo ""
echo "The .deb package has been created in the parent directory:"
ls -lh ../*.deb 2>/dev/null || echo "Package file: ../pyradio_*.deb"
echo ""
echo "To install the package, run:"
echo "  sudo dpkg -i ../pyradio_*.deb"
echo "  sudo apt-get install -f"
echo ""
