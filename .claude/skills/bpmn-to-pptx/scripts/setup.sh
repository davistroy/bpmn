#!/bin/bash
# Setup script for bpmn-to-pptx skill
# Installs required dependencies for BPMN to PowerPoint conversion

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "Setting up bpmn-to-pptx skill..."
echo "Skill directory: $SKILL_DIR"

# Check Python version
python3 --version || { echo "Python 3 is required"; exit 1; }

# Install Python dependencies (minimal - uses stdlib)
echo "Python dependencies: None required (uses stdlib only)"

# Check for Node.js (required for html2pptx conversion)
if command -v node &> /dev/null; then
    echo "Node.js found: $(node --version)"
else
    echo "Warning: Node.js not found. Required for final PPTX generation."
    echo "Install with: apt-get install nodejs npm"
fi

# Check for pptxgenjs
if npm list -g pptxgenjs &> /dev/null; then
    echo "pptxgenjs found"
else
    echo "Installing pptxgenjs globally..."
    npm install -g pptxgenjs || echo "Warning: Could not install pptxgenjs"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Usage:"
echo "  from src import generate_presentation"
echo "  generate_presentation('process.bpmn', 'output.pptx')"
echo ""
echo "Or with Claude Code:"
echo "  'Convert this BPMN file to a PowerPoint presentation'"
