# BPMN to PowerPoint - Design Reference

## Slide Generation Strategy

### Pyramid Principle Application

This skill applies Barbara Minto's Pyramid Principle to BPMN process documentation:

1. **Title Slide** - Process name and key metrics
2. **Overview Slide** - Chevron-style phase navigation (the "so what")
3. **Phase Detail Slides** - One per phase with SVG flow diagrams
4. **Decision Summary** (optional) - Key decision points consolidated

### Action Titles

Every slide includes a McKinsey-style "action title" that summarizes the key insight:

- **Overview**: "Process executes 5 phases including parallel workstreams to optimize throughput"
- **Phase Detail**: "Phase progresses from intake through validation with 2 decision gates"
- **Decision Summary**: "3 key decisions gate process progression and determine final outcome"

## Phase Detection Algorithm

The skill uses a priority-based approach:

### Priority 1: XML Comments
```xml
<!-- Phase 1: Intake -->
<bpmn:task id="Task_1" name="Receive Request"/>
```

### Priority 2: Subprocess Boundaries
Each expanded subprocess becomes its own phase automatically.

### Priority 3: Auto-Generation
When no explicit phases exist, the algorithm:
1. Performs topological sort of elements
2. Breaks at natural boundaries:
   - Parallel gateway splits
   - Major decision points (3+ outgoing flows)
   - Subprocess entries
   - Element count exceeds 8-10
3. Generates descriptive phase names from task verbs

## BPMN Element Mapping

| BPMN Element | Shape | Default Color |
|--------------|-------|---------------|
| Start Event | Oval (green border) | #C6F6D5 fill |
| End Event | Oval (thick red border) | #FED7D7 fill |
| Task | Rounded rectangle | #EBF8FF fill |
| User Task | Rounded rectangle + person icon | #EBF8FF fill |
| Service Task | Rounded rectangle + gear icon | #EBF8FF fill |
| Exclusive Gateway | Diamond with X | #FEFCBF fill |
| Parallel Gateway | Diamond with + | #E9D8FD fill |
| Inclusive Gateway | Diamond with O | #FEFCBF fill |
| Subprocess | Rounded rectangle (larger) | #F7FAFC fill |

## Brand Configuration

Brand configs are YAML files with three sections:

```yaml
colors:
  primary: "1A365D"      # Headers, titles
  secondary: "2B6CB0"    # Secondary elements
  accent: "ED8936"       # Highlights
  task_fill: "EBF8FF"    # Task backgrounds
  # ... element-specific colors

fonts:
  title: "Calibri Light"
  heading: "Calibri"
  body: "Calibri"
  sizes:
    slide_title: 28
    action_title: 16

layout:
  slide_width: 13.333    # 16:9 aspect ratio
  slide_height: 7.5
  margin_left: 0.5
  shape_width: 1.4
```

## HTML to PPTX Conversion

The skill generates intermediate HTML files, then uses the html2pptx library:

```
BPMN XML → ProcessModel → HTML Slides → html2pptx → PPTX
```

Each HTML slide is a self-contained document with:
- Inline CSS for styling
- SVG for flow diagrams
- Exact dimensions matching 16:9 slides (960×540 pixels)

## Cognitive Load Management

The 8-10 step limit per slide is based on cognitive science research:
- Miller's Law: 7±2 items in working memory
- Business audiences need quick comprehension
- Complex processes benefit from hierarchical navigation

## Integration with Other Skills

This skill complements the existing BPMN skills:

```
bpmn-xml-generator → Creates BPMN from descriptions
bpmn-diagram → Renders BPMN as PNG images
bpmn-to-pptx → Creates editable presentations (this skill)
```

Typical workflow:
1. Generate BPMN XML from natural language
2. Render as PNG for quick review
3. Convert to PPTX for stakeholder presentations
