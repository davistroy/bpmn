#!/usr/bin/env python3
"""
Example: Generate PowerPoint from BPMN

This script demonstrates how to use the bpmn-to-pptx skill to convert
a BPMN process diagram into a professional PowerPoint presentation.
"""

import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import (
    BPMNParser,
    build_hierarchy,
    ProcessPresentationGenerator,
    load_brand_config
)


def main():
    # Example BPMN file
    bpmn_file = "examples/rochester-2g-rebuild.bpmn"
    
    if not os.path.exists(bpmn_file):
        print(f"Error: BPMN file not found: {bpmn_file}")
        return 1
    
    print(f"Parsing BPMN file: {bpmn_file}")
    
    # Step 1: Parse the BPMN file
    parser = BPMNParser()
    process = parser.parse(bpmn_file)
    
    print(f"  Process: {process.name}")
    print(f"  Elements: {process.element_count}")
    print(f"  Tasks: {process.task_count}")
    print(f"  Decisions: {process.decision_count}")
    
    # Step 2: Build hierarchy (auto-detect phases)
    process = build_hierarchy(process, max_per_phase=10)
    
    print(f"  Phases detected: {len(process.phases)}")
    for phase in process.phases:
        print(f"    - {phase.name}: {phase.element_count} elements")
    
    # Step 3: Generate presentation
    print("\nGenerating PowerPoint presentation...")
    
    generator = ProcessPresentationGenerator(
        brand_config="default",  # or "stratfield" or path to YAML
        max_steps_per_slide=10,
        include_overview=True,
        include_decision_summary=True
    )
    
    output_file = "carburetor-rebuild-process.pptx"
    
    try:
        result = generator.generate(process, output_file)
        print(f"\nSuccess! Generated: {result}")
    except Exception as e:
        print(f"\nNote: Full generation requires html2pptx setup.")
        print(f"Error details: {e}")
        print("\nTo complete setup, ensure:")
        print("  1. Node.js and npm are installed")
        print("  2. pptxgenjs is installed: npm install -g pptxgenjs")
        print("  3. playwright is installed: npm install -g playwright")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
