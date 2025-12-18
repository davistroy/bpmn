"""
Slide Generator - Main orchestration for BPMN to PowerPoint conversion.
Uses html2pptx workflow from the core pptx skill.
"""

import os
import subprocess
import tempfile
from typing import List, Optional, Tuple, Dict
from .process_model import (
    ProcessModel, ProcessElement, Phase, ElementType, 
    BrandConfig, SlideContent, SequenceFlow
)
from .bpmn_parser import BPMNParser
from .hierarchy_builder import HierarchyBuilder
from .html_templates import HTMLTemplates
from .brand_config import load_brand_config


class ActionTitleGenerator:
    """Generates McKinsey-style action titles for slides."""
    
    def generate_overview_title(self, process: ProcessModel) -> str:
        """Generate action title for overview slide."""
        phase_count = len(process.phases)
        task_count = process.task_count
        decision_count = process.decision_count
        
        if decision_count > 3:
            return f"Process spans {phase_count} phases with {decision_count} critical decision points determining outcome paths"
        elif process.parallel_count > 0:
            return f"Process executes {phase_count} phases including parallel workstreams to optimize throughput"
        else:
            return f"Process follows {phase_count} sequential phases encompassing {task_count} activities from initiation to completion"
    
    def generate_phase_title(
        self, 
        phase: Phase, 
        elements: List[ProcessElement],
        phase_number: int,
        total_phases: int
    ) -> str:
        """Generate action title for a phase detail slide."""
        
        # Analyze phase composition
        tasks = [e for e in elements if e.element_type in [ElementType.TASK, ElementType.USER_TASK, ElementType.SERVICE_TASK]]
        decisions = [e for e in elements if e.element_type == ElementType.DECISION]
        parallels = [e for e in elements if e.element_type in [ElementType.PARALLEL_SPLIT, ElementType.PARALLEL_JOIN]]
        
        # Get first and last task names
        first_task = tasks[0].display_name if tasks else None
        last_task = tasks[-1].display_name if tasks else None
        
        # Generate based on composition
        if len(decisions) >= 2:
            return f"Phase contains {len(decisions)} decision points that determine downstream processing paths"
        
        if parallels:
            parallel_count = len([p for p in parallels if p.element_type == ElementType.PARALLEL_SPLIT])
            if parallel_count > 0:
                return f"Phase executes {parallel_count} parallel workstream{'s' if parallel_count > 1 else ''} to optimize cycle time"
        
        if len(tasks) <= 3 and first_task and last_task and first_task != last_task:
            return f"Phase progresses from {first_task} through {last_task}"
        
        if len(tasks) > 0:
            return f"Phase encompasses {len(tasks)} activities requiring sequential execution"
        
        return f"Phase {phase_number} contains {len(elements)} process steps"
    
    def generate_decision_summary_title(self, decision_count: int) -> str:
        """Generate action title for decision summary slide."""
        if decision_count == 1:
            return "Single critical decision point determines process outcome"
        elif decision_count <= 3:
            return f"{decision_count} key decisions gate process progression and determine final outcome"
        else:
            return f"Process contains {decision_count} decision points requiring stakeholder input"


class ProcessPresentationGenerator:
    """
    Main generator class for converting BPMN processes to PowerPoint.
    """
    
    def __init__(
        self,
        brand_config: str = "default",
        max_steps_per_slide: int = 10,
        include_overview: bool = True,
        include_decision_summary: bool = False,
        feedback_mode: bool = False
    ):
        """
        Initialize the generator.
        
        Args:
            brand_config: Brand name ("default", "stratfield") or path to YAML
            max_steps_per_slide: Maximum elements per phase detail slide
            include_overview: Whether to include the overview slide
            include_decision_summary: Whether to include decision summary slide
            feedback_mode: Whether to add annotation zones for feedback
        """
        self.brand = load_brand_config(brand_config)
        self.max_steps = max_steps_per_slide
        self.include_overview = include_overview
        self.include_decision_summary = include_decision_summary
        self.feedback_mode = feedback_mode
        
        self.templates = HTMLTemplates(self.brand)
        self.title_generator = ActionTitleGenerator()
        self.hierarchy_builder = HierarchyBuilder(max_elements_per_phase=max_steps_per_slide)
    
    def generate(
        self, 
        process: ProcessModel, 
        output_path: str,
        working_dir: Optional[str] = None
    ) -> str:
        """
        Generate a PowerPoint presentation from a ProcessModel.
        
        Args:
            process: The parsed and structured ProcessModel
            output_path: Path for the output .pptx file
            working_dir: Working directory for intermediate files (temp if None)
            
        Returns:
            Path to the generated .pptx file
        """
        # Ensure hierarchy is built
        process = self.hierarchy_builder.build_hierarchy(process)
        
        # Create working directory
        if working_dir is None:
            working_dir = tempfile.mkdtemp(prefix="bpmn_pptx_")
        os.makedirs(working_dir, exist_ok=True)
        
        # Generate slide content
        slides = self._generate_slide_content(process)
        
        # Generate HTML files
        html_files = self._generate_html_files(slides, working_dir)
        
        # Generate JavaScript conversion script
        js_script = self._generate_conversion_script(html_files, output_path, working_dir)
        
        # Run the conversion
        self._run_conversion(js_script, working_dir)
        
        return output_path
    
    def generate_from_file(self, bpmn_path: str, output_path: str) -> str:
        """
        Convenience method to generate from a BPMN file path.
        
        Args:
            bpmn_path: Path to the .bpmn file
            output_path: Path for the output .pptx file
            
        Returns:
            Path to the generated .pptx file
        """
        parser = BPMNParser()
        process = parser.parse(bpmn_path)
        return self.generate(process, output_path)
    
    def _generate_slide_content(self, process: ProcessModel) -> List[SlideContent]:
        """Generate the content structure for all slides."""
        slides = []

        # 1. Title slide
        slides.append(SlideContent(
            slide_type="title",
            title=process.name,
            action_title=f"Process Documentation • {process.task_count} Steps • {len(process.phases)} Phases"
        ))

        # 2. Overview slide (if enabled)
        phases_summary = [
            (phase.name, len(phase.element_ids))
            for phase in process.phases
        ]

        if self.include_overview and process.phases:
            slides.append(SlideContent(
                slide_type="overview",
                title="Process Overview",
                action_title=self.title_generator.generate_overview_title(process),
                phases_summary=phases_summary[:7]  # Max 7 phases on overview
            ))

        # 3. Phase detail slides
        total_phases = len(process.phases)
        for i, phase in enumerate(process.phases, 1):
            elements = process.get_elements_in_phase(phase.id)
            flows = self._get_flows_for_elements(process, [e.id for e in elements])

            slides.append(SlideContent(
                slide_type="phase_detail",
                title=phase.name,
                action_title=self.title_generator.generate_phase_title(
                    phase, elements, i, total_phases
                ),
                elements=elements,
                flows=flows,
                phase=phase,
                phase_number=i,
                total_phases=total_phases,
                overview_link=self.include_overview,
                phases_summary=phases_summary  # Pass all phases for chevron row
            ))
        
        # 4. Decision summary slide (if enabled)
        if self.include_decision_summary:
            decisions = self._extract_decisions(process)
            if decisions:
                slides.append(SlideContent(
                    slide_type="decision_summary",
                    title="Key Decision Points",
                    action_title=self.title_generator.generate_decision_summary_title(len(decisions)),
                    decisions=decisions
                ))
        
        return slides
    
    def _get_flows_for_elements(
        self, 
        process: ProcessModel, 
        element_ids: List[str]
    ) -> List[Tuple[str, str, Optional[str]]]:
        """Get flows between the specified elements."""
        element_set = set(element_ids)
        flows = []
        
        for flow in process.flows.values():
            if flow.source_ref in element_set and flow.target_ref in element_set:
                flows.append((flow.source_ref, flow.target_ref, flow.name))
        
        return flows
    
    def _extract_decisions(
        self, 
        process: ProcessModel
    ) -> List[Tuple[str, List[str]]]:
        """Extract decision points with their options."""
        decisions = []
        
        for element in process.elements.values():
            if element.element_type == ElementType.DECISION:
                question = element.name or "Decision Point"
                
                # Get outgoing flow labels as options
                options = []
                for flow_id in element.outgoing_flows:
                    flow = process.flows.get(flow_id)
                    if flow:
                        label = flow.name or f"Path to {flow.target_ref}"
                        target = process.elements.get(flow.target_ref)
                        if target and not flow.name:
                            label = target.display_name
                        options.append(label)
                
                if not options:
                    options = ["Yes", "No"]  # Default binary decision
                
                decisions.append((question, options))
        
        return decisions
    
    def _generate_html_files(
        self, 
        slides: List[SlideContent], 
        working_dir: str
    ) -> List[str]:
        """Generate HTML files for each slide."""
        html_files = []
        
        for i, slide in enumerate(slides):
            html_content = self._render_slide_html(slide)
            file_path = os.path.join(working_dir, f"slide_{i:02d}.html")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            html_files.append(file_path)
        
        return html_files
    
    def _render_slide_html(self, slide: SlideContent) -> str:
        """Render a single slide to HTML."""
        if slide.slide_type == "title":
            return self.templates.generate_title_slide(
                slide.title, 
                slide.action_title
            )
        
        elif slide.slide_type == "overview":
            return self.templates.generate_overview_slide(
                slide.title,
                slide.phases_summary,
                slide.action_title
            )
        
        elif slide.slide_type == "phase_detail":
            flows_tuples = [(f[0], f[1], f[2] if len(f) > 2 else None) for f in slide.flows]
            return self.templates.generate_phase_detail_slide(
                slide.phase,
                slide.elements,
                flows_tuples,
                slide.action_title,
                slide.phase_number,
                slide.total_phases,
                all_phases=slide.phases_summary  # Pass all phases for chevron row
            )
        
        elif slide.slide_type == "decision_summary":
            return self.templates.generate_decision_summary_slide(
                slide.decisions,
                slide.action_title
            )
        
        else:
            raise ValueError(f"Unknown slide type: {slide.slide_type}")
    
    def _generate_conversion_script(
        self, 
        html_files: List[str], 
        output_path: str,
        working_dir: str
    ) -> str:
        """Generate the JavaScript conversion script."""
        
        # Build slide conversion calls
        slide_calls = []
        for i, html_file in enumerate(html_files):
            # Use relative path from working dir
            rel_path = os.path.basename(html_file)
            slide_calls.append(f'  await html2pptx("{rel_path}", pptx);')
        
        slides_code = '\n'.join(slide_calls)
        
        # Determine output path (absolute or relative)
        if os.path.isabs(output_path):
            output_file = output_path
        else:
            output_file = os.path.join(os.getcwd(), output_path)
        
        script = f'''const pptxgen = require("pptxgenjs");
const {{ html2pptx }} = require("./html2pptx");

async function main() {{
  const pptx = new pptxgen();
  pptx.layout = "LAYOUT_16x9";
  pptx.title = "Process Presentation";
  pptx.author = "BPMN to PPTX Skill";
  
  // Convert each HTML slide
{slides_code}

  // Save the presentation
  await pptx.writeFile("{output_file}");
  console.log("Generated: {output_file}");
}}

main().catch(err => {{
  console.error("Error:", err);
  process.exit(1);
}});
'''
        
        script_path = os.path.join(working_dir, "convert.js")
        with open(script_path, 'w') as f:
            f.write(script)
        
        return script_path
    
    def _run_conversion(self, script_path: str, working_dir: str):
        """Run the JavaScript conversion script."""
        
        # Extract html2pptx library if not present
        html2pptx_dir = os.path.join(working_dir, "html2pptx")
        if not os.path.exists(html2pptx_dir):
            # Find the html2pptx.tgz in the pptx skill
            tgz_path = "/mnt/skills/public/pptx/html2pptx.tgz"
            if os.path.exists(tgz_path):
                os.makedirs(html2pptx_dir, exist_ok=True)
                subprocess.run(
                    ["tar", "-xzf", tgz_path, "-C", html2pptx_dir],
                    check=True
                )
        
        # Run the conversion script
        env = os.environ.copy()
        env["NODE_PATH"] = subprocess.check_output(
            ["npm", "root", "-g"], 
            text=True
        ).strip()
        
        result = subprocess.run(
            ["node", script_path],
            cwd=working_dir,
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Conversion failed: {result.stderr}")
        
        print(result.stdout)


def generate_presentation(
    bpmn_path: str,
    output_path: str,
    brand: str = "default",
    max_steps: int = 10,
    include_overview: bool = True,
    include_decisions: bool = False
) -> str:
    """
    Convenience function to generate a presentation from a BPMN file.
    
    Args:
        bpmn_path: Path to the .bpmn file
        output_path: Path for the output .pptx file
        brand: Brand configuration name or path
        max_steps: Maximum steps per phase slide
        include_overview: Include overview slide
        include_decisions: Include decision summary slide
        
    Returns:
        Path to the generated presentation
    """
    generator = ProcessPresentationGenerator(
        brand_config=brand,
        max_steps_per_slide=max_steps,
        include_overview=include_overview,
        include_decision_summary=include_decisions
    )
    
    return generator.generate_from_file(bpmn_path, output_path)
