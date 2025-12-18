#!/bin/bash

# BPMN Diagram Skill - Setup Script
#
# This script installs all dependencies required for the BPMN diagram skill.
# Run this once before first use.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================="
echo "BPMN Diagram Skill - Setup"
echo "=================================="
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed."
    echo "Please install Node.js 16.x or later from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "Warning: Node.js version $NODE_VERSION detected."
    echo "This skill requires Node.js 16.x or later for best compatibility."
fi

echo "Node.js version: $(node -v)"
echo "npm version: $(npm -v)"
echo ""

# Check for required system libraries for canvas
echo "Checking system dependencies for canvas..."
if command -v pkg-config &> /dev/null; then
    # Check for cairo (required by canvas)
    if ! pkg-config --exists cairo 2>/dev/null; then
        echo "Warning: cairo library not found."
        echo "You may need to install it:"
        echo "  Ubuntu/Debian: sudo apt-get install libcairo2-dev"
        echo "  MacOS: brew install cairo"
        echo "  RHEL/CentOS: sudo yum install cairo-devel"
    fi
fi

# Install npm dependencies
echo "Installing npm dependencies..."
npm install

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "You can now use the BPMN diagram skill."
echo ""
echo "Test with:"
echo "  node render-bpmn.js ../assets/sample.bpmn output.png"
echo ""
