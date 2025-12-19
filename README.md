# BPMN Skills for Claude Code

A collection of Claude Code skills for working with Business Process Model and Notation (BPMN) 2.0 workflows. These skills enable Claude to generate BPMN XML from natural language descriptions, render diagrams as PNG images, and create professional PowerPoint presentations.

## Overview

This project provides three skills that work together to create a complete BPMN documentation workflow:

| Skill | Version | Purpose | Input | Output |
|-------|---------|---------|-------|--------|
| **bpmn-xml-generator** | 1.1 | Generate BPMN XML from process descriptions | Natural language | BPMN 2.0 XML file |
| **bpmn-diagram** | 1.0 | Render BPMN diagrams as images | BPMN 2.0 XML | PNG image |
| **bpmn-to-pptx** | 2.0 | Convert BPMN to PowerPoint presentations | BPMN 2.0 XML | PowerPoint (.pptx) |

### Typical Workflow

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│  "Create an order   │     │  BPMN 2.0 XML       │     │  PNG Diagram    │
│   fulfillment       │ ──▶ │  (process.bpmn)     │ ──▶ │  (process.png)  │
│   workflow"         │     │                     │     │                 │
└─────────────────────┘     └─────────────────────┘     └─────────────────┘
     User Request          bpmn-xml-generator           bpmn-diagram
                                    │
                                    │
                                    ▼
                           ┌─────────────────────┐
                           │  PowerPoint Deck    │
                           │  (process.pptx)     │
                           └─────────────────────┘
                                bpmn-to-pptx
```

## Skills

### 1. BPMN XML Generator

Transforms natural language process descriptions into fully compliant BPMN 2.0 XML files with embedded documentation for downstream PowerPoint generation.

**Features:**
- Interactive question framework with 7 phases of clarification
- Automatic task type detection (User Task, Service Task, Script Task, etc.)
- Smart gateway selection (Exclusive, Parallel, Inclusive, Event-Based)
- Complete diagram interchange (DI) data for visual rendering
- **Task documentation elements** for detailed descriptions (critical for PowerPoint)
- **Phase comments** in XML for automatic hierarchy detection
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

### 3. BPMN to PowerPoint Generator (v2.0)

Transforms BPMN 2.0 process diagrams into professional, editable PowerPoint presentations following McKinsey/BCG consulting standards. Features a 3-tier hierarchical layout with automatic complexity management.

**Features:**
- **3-Tier Hierarchical Layout** on each phase slide:
  - Level 1 (Chevrons): Phase navigation showing all phases with current highlighted
  - Level 2 (White Rounded Boxes): Task group categories within the phase
  - Level 3 (Gray Square Boxes): Individual tasks with detailed bullet points
- McKinsey-style action titles (complete sentences stating the "so what")
- Automatic process chunking (8-10 steps per slide based on cognitive load research)
- Phase detection from XML comments, subprocess boundaries, or auto-chunking
- Consistent color coding for BPMN element types
- Customizable brand configurations (default, stratfield, or custom YAML)
- 20-25% whitespace for stakeholder annotations

**Trigger phrases:**
- "Convert this BPMN to PowerPoint"
- "Create a presentation from process.bpmn"
- "Generate slides for this workflow"
- "Make a stakeholder deck from this process"

**Example:**
```
User: Convert onboarding-process.bpmn to a PowerPoint presentation

Claude: [Parses BPMN, chunks into phases, generates multi-slide deck with:
        - Title slide
        - Overview slide (chevron diagram)
        - Phase detail slides (8-10 steps each)]
```

**Output Structure:**
1. **Title Slide** - Process name and metadata
2. **Overview Slide** - Phase-level chevron diagram (max 7 phases)
3. **Phase Detail Slides** - One per phase with full process flow
4. **Decision Summary** - (Optional) Key decision points listed

**Supported BPMN Elements:**
| Element | PowerPoint Shape | Color |
|---------|------------------|-------|
| Start Event | Green oval | #C6F6D5 |
| End Event | Red oval | #FED7D7 |
| User Task | Rounded rectangle | #EBF8FF (blue) |
| Service Task | Rounded rectangle | #E9D8FD (purple) |
| Exclusive Gateway | Diamond | #FEFCBF (yellow) |
| Parallel Gateway | Diamond with + | #E9D8FD (purple) |

## Installation

### Prerequisites

**For BPMN Diagram Renderer (Node.js):**
- Node.js 18.x or later
- System libraries for canvas rendering:
  - **Ubuntu/Debian:** `sudo apt-get install libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev`
  - **macOS:** `brew install cairo pango`

**For BPMN to PowerPoint (Python):**
- Python 3.8 or later
- Dependencies: lxml, pyyaml, python-pptx

### Setup

**Diagram Renderer Setup:**

```bash
cd .claude/skills/bpmn-diagram/scripts
./setup.sh
```

This installs:
- `bpmn-js` (^17.11.0) - BPMN 2.0 rendering toolkit
- `jsdom` (^25.0.0) - DOM implementation for Node.js
- `canvas` (^2.11.2) - Canvas implementation for PNG generation

**PowerPoint Generator Setup:**

```bash
cd .claude/skills/bpmn-to-pptx/scripts
./setup.sh
```

This installs:
- `lxml` - XML parsing for BPMN files
- `pyyaml` - Brand configuration loading
- `python-pptx` - PowerPoint generation (via html2pptx)

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
├── bpmn-diagram/                    # Diagram rendering skill (Node.js)
│   ├── SKILL.md                     # Skill definition and usage guide
│   ├── scripts/
│   │   ├── render-bpmn.js           # Main rendering script (bpmn-js + canvas)
│   │   ├── package.json             # Dependencies: bpmn-js ^17.11, jsdom ^25, canvas ^2.11
│   │   └── setup.sh                 # Installation script
│   ├── references/
│   │   └── bpmn-elements.md         # BPMN 2.0 elements reference
│   └── assets/
│       └── sample.bpmn              # Sample BPMN file for testing
│
├── bpmn-xml-generator/              # XML generation skill (Prompt-based)
│   ├── SKILL.md                     # Comprehensive skill definition with question framework
│   ├── templates/
│   │   ├── bpmn-skeleton.xml        # Base XML structure with namespaces
│   │   └── element-templates.xml    # Element snippets for all BPMN types
│   ├── examples/
│   │   ├── simple-approval.bpmn     # Simple approval workflow
│   │   ├── complex-order-process.bpmn
│   │   ├── parallel-processing.bpmn
│   │   └── subprocess-example.bpmn
│   └── references/
│       ├── bpmn-elements-reference.md  # Complete element catalog
│       ├── clarification-patterns.md   # Question templates by category
│       └── xml-namespaces.md           # Namespace documentation
│
└── bpmn-to-pptx/                    # PowerPoint generation skill (Python)
    ├── SKILL.md                     # Skill definition (v2.0.0)
    ├── scripts/
    │   └── setup.sh                 # Python dependencies setup
    ├── src/
    │   ├── __init__.py              # Package initialization
    │   ├── bpmn_parser.py           # BPMN XML parsing with lxml
    │   ├── process_model.py         # Data structures and type definitions
    │   ├── hierarchy_builder.py     # Phase detection & 3-tier chunking
    │   ├── slide_generator.py       # Main orchestration and html2pptx integration
    │   ├── html_templates.py        # HTML slide templates for each slide type
    │   └── brand_config.py          # YAML brand configuration loader
    ├── templates/
    │   └── brand_configs/
    │       ├── default.yaml         # Default brand colors and fonts
    │       └── stratfield.yaml      # Stratfield brand configuration
    ├── references/
    │   └── design-reference.md      # Design principles documentation
    └── examples/
        ├── rochester-2g-rebuild.bpmn  # Example BPMN file
        └── generate_example.py        # Example generation script
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

### PowerPoint Generator

- Maximum 50 elements recommended (larger processes should be decomposed)
- Swimlanes not yet supported (single-lane horizontal flow only)
- Collapsed subprocesses shown as single shape (not expanded)
- Complex nested gateways may require manual adjustment
- Requires the core `pptx` skill with html2pptx for conversion
- Max 7 phases displayed on overview slide

## Resources

- [BPMN 2.0 Specification (OMG)](https://www.omg.org/spec/BPMN/2.0/)
- [bpmn.io Toolkit](https://bpmn.io/toolkit/bpmn-js/)
- [bpmn-js GitHub](https://github.com/bpmn-io/bpmn-js)
- [BPMN Quick Guide](https://www.bpmn.org/)

## License

MIT
