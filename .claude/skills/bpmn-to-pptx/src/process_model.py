"""
Data structures for representing BPMN processes in a normalized format.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class ElementType(Enum):
    """Types of BPMN elements supported."""
    START = "start"
    END = "end"
    TASK = "task"
    USER_TASK = "user_task"
    SERVICE_TASK = "service_task"
    DECISION = "decision"           # exclusiveGateway
    PARALLEL_SPLIT = "parallel_split"  # parallelGateway (fork)
    PARALLEL_JOIN = "parallel_join"    # parallelGateway (merge)
    SUBPROCESS = "subprocess"
    MERGE = "merge"                 # Merging gateway
    GATEWAY = "gateway"             # Generic gateway


@dataclass
class SequenceFlow:
    """Represents a connection between two BPMN elements."""
    id: str
    source_ref: str
    target_ref: str
    name: Optional[str] = None
    condition: Optional[str] = None
    is_default: bool = False


@dataclass
class ProcessElement:
    """Represents a single BPMN element (task, gateway, event, etc.)."""
    id: str
    name: str
    element_type: ElementType
    phase_id: Optional[str] = None
    incoming_flows: List[str] = field(default_factory=list)
    outgoing_flows: List[str] = field(default_factory=list)
    # Layout coordinates from BPMN diagram (if available)
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    # Additional metadata
    documentation: Optional[str] = None
    is_expanded: bool = True  # For subprocesses
    
    @property
    def is_gateway(self) -> bool:
        """Check if this element is any type of gateway."""
        return self.element_type in [
            ElementType.DECISION,
            ElementType.PARALLEL_SPLIT,
            ElementType.PARALLEL_JOIN,
            ElementType.MERGE,
            ElementType.GATEWAY
        ]
    
    @property
    def is_branching(self) -> bool:
        """Check if this element creates branches (multiple outgoing flows)."""
        return len(self.outgoing_flows) > 1
    
    @property
    def is_merging(self) -> bool:
        """Check if this element merges branches (multiple incoming flows)."""
        return len(self.incoming_flows) > 1
    
    @property
    def display_name(self) -> str:
        """Get a clean display name for the element."""
        if self.name:
            return self.name
        # Generate from ID if no name
        return self.id.replace("_", " ").replace("-", " ").title()


@dataclass
class Phase:
    """Represents a logical phase/stage of the process."""
    id: str
    name: str
    order: int
    element_ids: List[str] = field(default_factory=list)
    description: Optional[str] = None
    
    @property
    def element_count(self) -> int:
        return len(self.element_ids)


@dataclass 
class ProcessModel:
    """Complete representation of a BPMN process."""
    id: str
    name: str
    elements: Dict[str, ProcessElement] = field(default_factory=dict)
    flows: Dict[str, SequenceFlow] = field(default_factory=dict)
    phases: List[Phase] = field(default_factory=list)
    # Raw XML for phase comment extraction
    raw_xml: Optional[str] = None
    # Metadata
    version: Optional[str] = None
    exporter: Optional[str] = None
    
    @property
    def element_count(self) -> int:
        return len(self.elements)
    
    @property
    def task_count(self) -> int:
        return sum(1 for e in self.elements.values() 
                   if e.element_type in [ElementType.TASK, ElementType.USER_TASK, ElementType.SERVICE_TASK])
    
    @property
    def decision_count(self) -> int:
        return sum(1 for e in self.elements.values() 
                   if e.element_type == ElementType.DECISION)
    
    @property
    def parallel_count(self) -> int:
        return sum(1 for e in self.elements.values() 
                   if e.element_type in [ElementType.PARALLEL_SPLIT, ElementType.PARALLEL_JOIN])
    
    def get_start_events(self) -> List[ProcessElement]:
        """Get all start events in the process."""
        return [e for e in self.elements.values() if e.element_type == ElementType.START]
    
    def get_end_events(self) -> List[ProcessElement]:
        """Get all end events in the process."""
        return [e for e in self.elements.values() if e.element_type == ElementType.END]
    
    def get_element_by_id(self, element_id: str) -> Optional[ProcessElement]:
        """Get an element by its ID."""
        return self.elements.get(element_id)
    
    def get_outgoing_elements(self, element_id: str) -> List[ProcessElement]:
        """Get all elements that this element connects to."""
        element = self.elements.get(element_id)
        if not element:
            return []
        
        result = []
        for flow_id in element.outgoing_flows:
            flow = self.flows.get(flow_id)
            if flow and flow.target_ref in self.elements:
                result.append(self.elements[flow.target_ref])
        return result
    
    def get_incoming_elements(self, element_id: str) -> List[ProcessElement]:
        """Get all elements that connect to this element."""
        element = self.elements.get(element_id)
        if not element:
            return []
        
        result = []
        for flow_id in element.incoming_flows:
            flow = self.flows.get(flow_id)
            if flow and flow.source_ref in self.elements:
                result.append(self.elements[flow.source_ref])
        return result
    
    def get_flow_label(self, source_id: str, target_id: str) -> Optional[str]:
        """Get the label for a flow between two elements."""
        for flow in self.flows.values():
            if flow.source_ref == source_id and flow.target_ref == target_id:
                return flow.name
        return None
    
    def get_elements_in_phase(self, phase_id: str) -> List[ProcessElement]:
        """Get all elements belonging to a specific phase."""
        phase = next((p for p in self.phases if p.id == phase_id), None)
        if not phase:
            return []
        return [self.elements[eid] for eid in phase.element_ids if eid in self.elements]
    
    def topological_sort(self) -> List[ProcessElement]:
        """
        Return elements in topological order (respecting flow direction).
        Uses Kahn's algorithm.
        """
        # Calculate in-degree for each element
        in_degree = {eid: 0 for eid in self.elements}
        for flow in self.flows.values():
            if flow.target_ref in in_degree:
                in_degree[flow.target_ref] += 1
        
        # Start with elements that have no incoming flows
        queue = [eid for eid, deg in in_degree.items() if deg == 0]
        result = []
        
        while queue:
            # Sort queue by x-coordinate if available for consistent ordering
            queue.sort(key=lambda eid: self.elements[eid].x or 0)
            current_id = queue.pop(0)
            result.append(self.elements[current_id])
            
            # Reduce in-degree for downstream elements
            for flow in self.flows.values():
                if flow.source_ref == current_id and flow.target_ref in in_degree:
                    in_degree[flow.target_ref] -= 1
                    if in_degree[flow.target_ref] == 0:
                        queue.append(flow.target_ref)
        
        return result


@dataclass
class SlideContent:
    """Represents content for a single PowerPoint slide."""
    slide_type: str  # "title", "overview", "phase_detail", "decision_summary"
    title: str
    action_title: Optional[str] = None  # McKinsey-style "so what" title
    elements: List[ProcessElement] = field(default_factory=list)
    flows: List[SequenceFlow] = field(default_factory=list)
    phase: Optional[Phase] = None
    # For overview slides
    phases_summary: List[Tuple[str, int]] = field(default_factory=list)  # (name, step_count)
    # For decision summary slides
    decisions: List[Tuple[str, List[str]]] = field(default_factory=list)  # (question, options)
    # Navigation
    overview_link: bool = False
    phase_number: Optional[int] = None
    total_phases: Optional[int] = None


@dataclass
class BrandConfig:
    """Brand configuration for styling the presentation."""
    name: str = "Default"
    
    # Colors (hex without #)
    primary: str = "1A365D"
    secondary: str = "2B6CB0"
    accent: str = "ED8936"
    background: str = "FFFFFF"
    text_primary: str = "1A202C"
    text_secondary: str = "4A5568"
    
    # Element colors
    task_fill: str = "EBF8FF"
    task_border: str = "3182CE"
    decision_fill: str = "FEFCBF"
    decision_border: str = "D69E2E"
    parallel_fill: str = "E9D8FD"
    parallel_border: str = "805AD5"
    start_fill: str = "C6F6D5"
    start_border: str = "38A169"
    end_fill: str = "FED7D7"
    end_border: str = "E53E3E"
    subprocess_fill: str = "F7FAFC"
    subprocess_border: str = "718096"
    merge_fill: str = "E2E8F0"
    merge_border: str = "718096"
    
    # Fonts
    title_font: str = "Calibri Light"
    heading_font: str = "Calibri"
    body_font: str = "Calibri"
    
    # Font sizes (pt)
    slide_title_size: int = 28
    action_title_size: int = 16
    phase_label_size: int = 14
    shape_text_size: int = 10
    footnote_size: int = 8
    
    # Layout (inches)
    slide_width: float = 13.333
    slide_height: float = 7.5
    margin_left: float = 0.5
    margin_right: float = 0.5
    margin_top: float = 0.75
    margin_bottom: float = 0.5
    
    # Shape dimensions (inches)
    shape_width: float = 1.4
    shape_height: float = 0.6
    shape_gap_h: float = 0.3
    shape_gap_v: float = 0.7
    
    # Logo
    logo_path: Optional[str] = None
    logo_width: float = 1.5
    logo_position: str = "top_right"
    
    def get_element_colors(self, element_type: ElementType) -> Tuple[str, str]:
        """Get fill and border colors for an element type."""
        color_map = {
            ElementType.START: (self.start_fill, self.start_border),
            ElementType.END: (self.end_fill, self.end_border),
            ElementType.TASK: (self.task_fill, self.task_border),
            ElementType.USER_TASK: (self.task_fill, self.task_border),
            ElementType.SERVICE_TASK: (self.parallel_fill, self.parallel_border),
            ElementType.DECISION: (self.decision_fill, self.decision_border),
            ElementType.PARALLEL_SPLIT: (self.parallel_fill, self.parallel_border),
            ElementType.PARALLEL_JOIN: (self.parallel_fill, self.parallel_border),
            ElementType.SUBPROCESS: (self.subprocess_fill, self.subprocess_border),
            ElementType.MERGE: (self.merge_fill, self.merge_border),
            ElementType.GATEWAY: (self.merge_fill, self.merge_border),
        }
        return color_map.get(element_type, (self.task_fill, self.task_border))
