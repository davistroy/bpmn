# BPMN Diagram Skill

A Claude Code skill that converts BPMN 2.0 XML files to PNG diagram images.

## Overview

This skill enables Claude to render Business Process Model and Notation (BPMN) 2.0 diagrams from XML input, producing PNG images that visualize the process flows.

## Features

- Converts BPMN 2.0 XML to PNG images
- Supports all standard BPMN 2.0 elements (events, tasks, gateways, flows)
- Configurable output dimensions and scale
- Pure Node.js implementation (no browser required)
- Validates BPMN XML structure before rendering

## Installation

1. Navigate to the skill's scripts directory:
   ```bash
   cd .claude/skills/bpmn-diagram/scripts
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

   This installs the required Node.js dependencies:
   - `bpmn-js` - BPMN 2.0 rendering toolkit
   - `jsdom` - DOM implementation for Node.js
   - `canvas` - Canvas implementation for PNG generation

### System Requirements

- Node.js 16.x or later
- System libraries for canvas (automatically checked by setup.sh):
  - Ubuntu/Debian: `libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev`
  - macOS: `cairo pango`

## Usage

### As a Claude Skill

When the skill is active, Claude will automatically use it when you:
- Provide BPMN XML content and ask for a diagram
- Ask to visualize or render a BPMN process

### Command Line

```bash
node render-bpmn.js <input.bpmn> <output.png> [options]
```

**Options:**
- `--scale=N` - Image scale factor (default: 1)
- `--min-dimensions=WxH` - Minimum dimensions in pixels (default: 800x600)
- `--padding=N` - Padding around diagram (default: 20)

**Example:**
```bash
node render-bpmn.js diagram.bpmn output.png --scale=2
```

## Project Structure

```
.claude/skills/bpmn-diagram/
├── SKILL.md                    # Skill definition and instructions
├── scripts/
│   ├── render-bpmn.js          # Main rendering script
│   ├── package.json            # Node.js dependencies
│   └── setup.sh                # Setup script
├── references/
│   └── bpmn-elements.md        # BPMN 2.0 elements reference
└── assets/
    └── sample.bpmn             # Sample BPMN file
```

## BPMN 2.0 Support

The skill supports the full BPMN 2.0 specification including:

- **Events**: Start, End, Intermediate (Timer, Message, Signal, Error)
- **Activities**: Task, User Task, Service Task, Script Task, Sub-Process
- **Gateways**: Exclusive (XOR), Parallel (AND), Inclusive (OR), Event-Based
- **Flows**: Sequence Flow, Message Flow, Association
- **Swimlanes**: Pool, Lane
- **Artifacts**: Data Object, Data Store, Text Annotation

## Resources

- [bpmn.io Toolkit](https://bpmn.io/toolkit/bpmn-js/)
- [BPMN 2.0 Specification (OMG)](https://www.omg.org/spec/BPMN/2.0/)
- [bpmn-js GitHub](https://github.com/bpmn-io/bpmn-js)

## License

MIT
