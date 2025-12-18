# BPMN Skills for Claude Code

A collection of Claude Code skills for working with Business Process Model and Notation (BPMN) 2.0 workflows. These skills enable Claude to generate BPMN XML from natural language descriptions and render the diagrams as PNG images.

## Overview

This project provides two complementary skills that work together to create a complete BPMN workflow:

| Skill | Purpose | Input | Output |
|-------|---------|-------|--------|
| **bpmn-xml-generator** | Generate BPMN XML from process descriptions | Natural language | BPMN 2.0 XML file |
| **bpmn-diagram** | Render BPMN diagrams as images | BPMN 2.0 XML | PNG image |

### Typical Workflow

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│  "Create an order   │     │  BPMN 2.0 XML       │     │  PNG Diagram    │
│   fulfillment       │ ──▶ │  (process.bpmn)     │ ──▶ │  (process.png)  │
│   workflow"         │     │                     │     │                 │
└─────────────────────┘     └─────────────────────┘     └─────────────────┘
     User Request          bpmn-xml-generator           bpmn-diagram
```

## Skills

### 1. BPMN XML Generator

Transforms natural language process descriptions into fully compliant BPMN 2.0 XML files.

**Features:**
- Interactive question framework to clarify requirements
- Automatic task type detection (User Task, Service Task, etc.)
- Smart gateway selection (Exclusive, Parallel, Inclusive)
- Complete diagram interchange (DI) data for visual rendering
- Compatible with Camunda, Flowable, bpmn.io, and other BPMN tools

**Trigger phrases:**
- "Create a BPMN workflow for..."
- "Generate BPMN XML for..."
- "Model this process..."
- "Convert to BPMN 2.0..."
- "Build a workflow diagram..."

**Example:**
```
User: Create a BPMN workflow for an employee onboarding process

Claude: I'll help you create a BPMN workflow. Let me ask a few questions to
        understand your requirements...

        Question 1: What triggers the onboarding process?
        A) [Recommended] HR receives signed offer letter (Message Start Event)
        B) New employee start date arrives (Timer Start Event)
        C) Manual initiation
        D) Provide your own answer
        E) Accept recommended answers for all remaining questions
```

### 2. BPMN Diagram Renderer

Converts BPMN 2.0 XML files into PNG diagram images using the bpmn-js rendering toolkit.

**Features:**
- Full BPMN 2.0 element support
- Configurable output dimensions and scale
- Pure Node.js implementation (no browser required)
- Validates BPMN XML structure before rendering

**Usage:**
```
User: Render the onboarding.bpmn file as a diagram
User: Create a PNG from this BPMN XML: [XML content]
User: Visualize the process diagram
```

## Installation

### Prerequisites

- Node.js 16.x or later
- System libraries for canvas rendering:
  - **Ubuntu/Debian:** `sudo apt-get install libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev`
  - **macOS:** `brew install cairo pango`

### Setup

Run the setup script to install Node.js dependencies for the diagram renderer:

```bash
cd .claude/skills/bpmn-diagram/scripts
./setup.sh
```

This installs:
- `bpmn-js` - BPMN 2.0 rendering toolkit
- `jsdom` - DOM implementation for Node.js
- `canvas` - Canvas implementation for PNG generation

## Usage

### With Claude Code

Once the skills are installed, Claude automatically uses them based on your requests:

**Generate BPMN XML:**
```
You: Create a BPMN workflow for a document approval process

Claude: [Asks clarifying questions, then generates a .bpmn file]
```

**Render as Image:**
```
You: Create a diagram from approval-process.bpmn

Claude: [Renders the BPMN XML to a PNG image]
```

**Combined Workflow:**
```
You: Create a BPMN workflow for order processing and render it as a diagram

Claude: [Generates XML and then renders it to PNG]
```

### Command Line (Diagram Renderer)

The diagram renderer can also be used directly from the command line:

```bash
node .claude/skills/bpmn-diagram/scripts/render-bpmn.js <input.bpmn> <output.png> [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--scale=N` | Image scale factor (e.g., 2 for 2x resolution) | 1 |
| `--min-dimensions=WxH` | Minimum output dimensions in pixels | 800x600 |
| `--padding=N` | Padding around diagram | 20 |

**Example:**
```bash
node .claude/skills/bpmn-diagram/scripts/render-bpmn.js order-process.bpmn order-process.png --scale=2
```

## BPMN 2.0 Support

Both skills support the full BPMN 2.0 specification:

### Events

| Type | Elements |
|------|----------|
| **Start** | None, Message, Timer, Signal, Conditional |
| **End** | None, Message, Error, Terminate, Signal, Escalation |
| **Intermediate** | Message (catch/throw), Timer, Signal, Link, Conditional |
| **Boundary** | Timer, Error, Message, Escalation (interrupting/non-interrupting) |

### Activities

| Type | Description |
|------|-------------|
| Task | Generic activity |
| User Task | Performed by a human |
| Service Task | Automated service call |
| Script Task | Executes a script |
| Send Task | Sends a message |
| Receive Task | Waits for a message |
| Business Rule Task | Executes business rules |
| Manual Task | Manual work outside the system |
| Sub-Process | Embedded sub-process |
| Call Activity | Calls external process |

### Gateways

| Type | Symbol | Use Case |
|------|--------|----------|
| Exclusive (XOR) | X | One path based on condition |
| Parallel (AND) | + | All paths simultaneously |
| Inclusive (OR) | O | One or more paths |
| Event-Based | ⬠ | Path based on which event occurs first |
| Complex | * | Complex merge conditions |

### Other Elements

- **Swimlanes:** Pools, Lanes
- **Data:** Data Objects, Data Stores, Data Input/Output
- **Artifacts:** Text Annotations, Groups
- **Flows:** Sequence Flow, Message Flow, Association

## Project Structure

```
.claude/skills/
├── bpmn-diagram/                    # Diagram rendering skill
│   ├── SKILL.md                     # Skill definition
│   ├── scripts/
│   │   ├── render-bpmn.js           # Main rendering script
│   │   ├── package.json             # Node.js dependencies
│   │   └── setup.sh                 # Setup script
│   ├── references/
│   │   └── bpmn-elements.md         # BPMN 2.0 elements reference
│   └── assets/
│       └── sample.bpmn              # Sample BPMN file
│
└── bpmn-xml-generator/              # XML generation skill
    ├── SKILL.md                     # Skill definition
    ├── templates/
    │   ├── bpmn-skeleton.xml        # Base XML structure
    │   └── element-templates.xml    # Element snippets
    ├── examples/
    │   ├── simple-approval.bpmn     # Simple approval workflow
    │   ├── complex-order-process.bpmn
    │   ├── parallel-processing.bpmn
    │   └── subprocess-example.bpmn
    └── references/
        ├── bpmn-elements-reference.md
        ├── clarification-patterns.md
        └── xml-namespaces.md
```

## Examples

### Simple Approval Process

**Input:** "Create a document approval workflow"

**Generated BPMN XML structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI">

    <bpmn:process id="Process_Approval" name="Document Approval" isExecutable="true">
        <bpmn:startEvent id="Start_1" name="Request Received"/>
        <bpmn:userTask id="Task_Submit" name="Submit Request"/>
        <bpmn:userTask id="Task_Review" name="Review Request"/>
        <bpmn:exclusiveGateway id="Gateway_Decision" name="Approved?"/>
        <bpmn:sendTask id="Task_NotifyApproved" name="Send Approval"/>
        <bpmn:sendTask id="Task_NotifyRejected" name="Send Rejection"/>
        <bpmn:endEvent id="End_1" name="Process Complete"/>
        <!-- Sequence flows and diagram interchange... -->
    </bpmn:process>

    <bpmndi:BPMNDiagram id="BPMNDiagram_1">
        <!-- Visual layout definitions... -->
    </bpmndi:BPMNDiagram>

</bpmn:definitions>
```

### Sample BPMN Files

The `bpmn-xml-generator` skill includes several example files in the `examples/` directory:

| File | Description |
|------|-------------|
| `simple-approval.bpmn` | Basic approval workflow with one decision point |
| `complex-order-process.bpmn` | Order fulfillment with error handling |
| `parallel-processing.bpmn` | Parallel gateway demonstration |
| `subprocess-example.bpmn` | Embedded subprocess example |

## Compatibility

Generated BPMN files are compatible with:

- [bpmn.io](https://bpmn.io/) - Web-based BPMN modeler
- [Camunda](https://camunda.com/) - Process automation platform
- [Flowable](https://flowable.com/) - Business process engine
- [Activiti](https://www.activiti.org/) - Open source BPM platform
- Any BPMN 2.0 compliant tool

## Limitations

### Diagram Renderer

The Node.js-based renderer has some limitations compared to browser-based rendering:

1. **SVG Transform Positioning:** Complex transforms may not render perfectly
2. **Text Rendering:** Depends on system fonts available
3. **Complex Diagrams:** Very large diagrams may have rendering artifacts

For production use with complex diagrams, consider using `bpmn-to-image` with Puppeteer.

### XML Generator

- Requires user interaction for complex processes (clarifying questions)
- Generated layouts are optimized for readability but may need manual adjustment for very complex processes

## Resources

- [BPMN 2.0 Specification (OMG)](https://www.omg.org/spec/BPMN/2.0/)
- [bpmn.io Toolkit](https://bpmn.io/toolkit/bpmn-js/)
- [bpmn-js GitHub](https://github.com/bpmn-io/bpmn-js)
- [BPMN Quick Guide](https://www.bpmn.org/)

## License

MIT
