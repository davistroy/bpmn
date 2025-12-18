"""
BPMN 2.0 XML Parser - Converts BPMN XML to ProcessModel.
"""

import re
from typing import Dict, List, Optional, Tuple
from lxml import etree
from .process_model import (
    ProcessModel, ProcessElement, SequenceFlow, Phase, ElementType
)


# BPMN 2.0 Namespaces
NAMESPACES = {
    'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
    'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
    'dc': 'http://www.omg.org/spec/DD/20100524/DC',
    'di': 'http://www.omg.org/spec/DD/20100524/DI',
}


class BPMNParser:
    """Parser for BPMN 2.0 XML files."""
    
    def __init__(self):
        self.namespaces = NAMESPACES
    
    def parse(self, file_path: str) -> ProcessModel:
        """
        Parse a BPMN file and return a ProcessModel.
        
        Args:
            file_path: Path to the .bpmn file
            
        Returns:
            ProcessModel with all elements, flows, and detected phases
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_xml = f.read()
        
        tree = etree.parse(file_path)
        root = tree.getroot()
        
        # Find the process element
        process_elem = root.find('.//bpmn:process', self.namespaces)
        if process_elem is None:
            raise ValueError("No BPMN process found in file")
        
        process_id = process_elem.get('id', 'unknown')
        process_name = process_elem.get('name', process_id)
        
        # Extract exporter info
        exporter = root.get('exporter')
        
        # Parse all elements and flows
        elements = self._parse_elements(process_elem)
        flows = self._parse_flows(process_elem, elements)
        
        # Parse diagram information for coordinates
        self._parse_diagram_info(root, elements)
        
        # Create the process model
        model = ProcessModel(
            id=process_id,
            name=process_name,
            elements=elements,
            flows=flows,
            raw_xml=raw_xml,
            exporter=exporter
        )
        
        # Detect phases from comments or auto-generate
        phases = self._detect_phases(raw_xml, model)
        model.phases = phases
        
        # Assign elements to phases
        self._assign_elements_to_phases(model)
        
        return model
    
    def _parse_elements(self, process_elem: etree.Element) -> Dict[str, ProcessElement]:
        """Parse all BPMN elements from the process."""
        elements = {}
        
        # Element type mapping
        element_types = {
            'startEvent': ElementType.START,
            'endEvent': ElementType.END,
            'task': ElementType.TASK,
            'userTask': ElementType.USER_TASK,
            'serviceTask': ElementType.SERVICE_TASK,
            'manualTask': ElementType.TASK,
            'scriptTask': ElementType.TASK,
            'businessRuleTask': ElementType.TASK,
            'sendTask': ElementType.TASK,
            'receiveTask': ElementType.TASK,
            'subProcess': ElementType.SUBPROCESS,
            'callActivity': ElementType.SUBPROCESS,
        }
        
        # Parse standard elements
        for tag, elem_type in element_types.items():
            for elem in process_elem.findall(f'.//bpmn:{tag}', self.namespaces):
                element = self._create_element(elem, elem_type)
                elements[element.id] = element
        
        # Parse gateways (need special handling for type detection)
        for gateway in process_elem.findall('.//bpmn:exclusiveGateway', self.namespaces):
            element = self._create_gateway_element(gateway, process_elem)
            elements[element.id] = element
        
        for gateway in process_elem.findall('.//bpmn:parallelGateway', self.namespaces):
            element = self._create_parallel_gateway_element(gateway, process_elem)
            elements[element.id] = element
        
        for gateway in process_elem.findall('.//bpmn:inclusiveGateway', self.namespaces):
            element = self._create_gateway_element(gateway, process_elem)
            elements[element.id] = element
        
        for gateway in process_elem.findall('.//bpmn:eventBasedGateway', self.namespaces):
            element = self._create_element(gateway, ElementType.GATEWAY)
            elements[element.id] = element
        
        return elements
    
    def _create_element(self, elem: etree.Element, elem_type: ElementType) -> ProcessElement:
        """Create a ProcessElement from an XML element."""
        element_id = elem.get('id', '')
        name = elem.get('name', '')
        
        # Get incoming and outgoing flow references
        incoming = [flow.text for flow in elem.findall('bpmn:incoming', self.namespaces) if flow.text]
        outgoing = [flow.text for flow in elem.findall('bpmn:outgoing', self.namespaces) if flow.text]
        
        # Get documentation if present
        doc_elem = elem.find('bpmn:documentation', self.namespaces)
        documentation = doc_elem.text if doc_elem is not None else None
        
        # Check if subprocess is expanded
        is_expanded = True
        if elem_type == ElementType.SUBPROCESS:
            # Collapsed subprocesses typically have no child elements
            child_elements = list(elem)
            is_expanded = len([c for c in child_elements 
                              if c.tag != f"{{{self.namespaces['bpmn']}}}incoming" 
                              and c.tag != f"{{{self.namespaces['bpmn']}}}outgoing"]) > 0
        
        return ProcessElement(
            id=element_id,
            name=name,
            element_type=elem_type,
            incoming_flows=incoming,
            outgoing_flows=outgoing,
            documentation=documentation,
            is_expanded=is_expanded
        )
    
    def _create_gateway_element(self, gateway: etree.Element, process_elem: etree.Element) -> ProcessElement:
        """Create a gateway element, determining if it's a decision or merge."""
        element_id = gateway.get('id', '')
        name = gateway.get('name', '')
        
        incoming = [flow.text for flow in gateway.findall('bpmn:incoming', self.namespaces) if flow.text]
        outgoing = [flow.text for flow in gateway.findall('bpmn:outgoing', self.namespaces) if flow.text]
        
        # Determine gateway type based on flow counts
        if len(outgoing) > 1:
            elem_type = ElementType.DECISION
        elif len(incoming) > 1:
            elem_type = ElementType.MERGE
        else:
            elem_type = ElementType.GATEWAY
        
        return ProcessElement(
            id=element_id,
            name=name,
            element_type=elem_type,
            incoming_flows=incoming,
            outgoing_flows=outgoing
        )
    
    def _create_parallel_gateway_element(self, gateway: etree.Element, process_elem: etree.Element) -> ProcessElement:
        """Create a parallel gateway element."""
        element_id = gateway.get('id', '')
        name = gateway.get('name', '')
        
        incoming = [flow.text for flow in gateway.findall('bpmn:incoming', self.namespaces) if flow.text]
        outgoing = [flow.text for flow in gateway.findall('bpmn:outgoing', self.namespaces) if flow.text]
        
        # Determine if fork or join
        if len(outgoing) > 1:
            elem_type = ElementType.PARALLEL_SPLIT
        elif len(incoming) > 1:
            elem_type = ElementType.PARALLEL_JOIN
        else:
            elem_type = ElementType.GATEWAY
        
        return ProcessElement(
            id=element_id,
            name=name,
            element_type=elem_type,
            incoming_flows=incoming,
            outgoing_flows=outgoing
        )
    
    def _parse_flows(self, process_elem: etree.Element, elements: Dict[str, ProcessElement]) -> Dict[str, SequenceFlow]:
        """Parse all sequence flows."""
        flows = {}
        
        for flow_elem in process_elem.findall('.//bpmn:sequenceFlow', self.namespaces):
            flow_id = flow_elem.get('id', '')
            source_ref = flow_elem.get('sourceRef', '')
            target_ref = flow_elem.get('targetRef', '')
            name = flow_elem.get('name')
            
            # Check for condition expression
            condition_elem = flow_elem.find('bpmn:conditionExpression', self.namespaces)
            condition = condition_elem.text if condition_elem is not None else None
            
            flow = SequenceFlow(
                id=flow_id,
                source_ref=source_ref,
                target_ref=target_ref,
                name=name,
                condition=condition
            )
            flows[flow_id] = flow
        
        return flows
    
    def _parse_diagram_info(self, root: etree.Element, elements: Dict[str, ProcessElement]):
        """Parse diagram information to get element coordinates."""
        # Find all BPMNShape elements
        for shape in root.findall('.//bpmndi:BPMNShape', self.namespaces):
            bpmn_element = shape.get('bpmnElement')
            if bpmn_element and bpmn_element in elements:
                bounds = shape.find('dc:Bounds', self.namespaces)
                if bounds is not None:
                    elements[bpmn_element].x = float(bounds.get('x', 0))
                    elements[bpmn_element].y = float(bounds.get('y', 0))
                    elements[bpmn_element].width = float(bounds.get('width', 100))
                    elements[bpmn_element].height = float(bounds.get('height', 80))
    
    def _detect_phases(self, raw_xml: str, model: ProcessModel) -> List[Phase]:
        """
        Detect phases from BPMN XML.
        
        Priority:
        1. Explicit XML comments (<!-- Phase N: Name -->)
        2. Subprocess boundaries
        3. Return empty list (will be auto-generated later)
        """
        phases = []
        
        # Strategy 1: Look for phase comments
        phase_pattern = r'<!--\s*Phase\s+(\d+)\s*:\s*([^-]+?)\s*-->'
        matches = re.findall(phase_pattern, raw_xml, re.IGNORECASE)
        
        if matches:
            for order_str, name in matches:
                order = int(order_str)
                phase_id = f"phase_{order}"
                phases.append(Phase(
                    id=phase_id,
                    name=name.strip(),
                    order=order
                ))
            # Sort by order
            phases.sort(key=lambda p: p.order)
            return phases
        
        # Strategy 2: Use subprocesses as phases
        subprocesses = [e for e in model.elements.values() 
                       if e.element_type == ElementType.SUBPROCESS]
        if subprocesses:
            for idx, sp in enumerate(sorted(subprocesses, key=lambda e: e.x or 0), 1):
                phases.append(Phase(
                    id=f"phase_{idx}",
                    name=sp.name or f"Phase {idx}",
                    order=idx,
                    element_ids=[sp.id]
                ))
            return phases
        
        # Return empty - hierarchy_builder will auto-generate
        return []
    
    def _assign_elements_to_phases(self, model: ProcessModel):
        """
        Assign elements to their respective phases based on position in XML.
        """
        if not model.phases:
            return
        
        # Get topologically sorted elements
        sorted_elements = model.topological_sort()
        
        # If phases were detected from comments, assign based on position
        if model.phases and not model.phases[0].element_ids:
            # Find phase boundaries in the raw XML
            phase_positions = self._find_phase_positions_in_xml(model.raw_xml, model.phases)
            
            # Assign elements to phases based on their position
            for element in sorted_elements:
                if element.x is not None:
                    # Find which phase this element belongs to based on x coordinate
                    assigned = False
                    for i, phase in enumerate(model.phases):
                        start_x = phase_positions.get(phase.id, {}).get('start', 0)
                        end_x = phase_positions.get(phase.id, {}).get('end', float('inf'))
                        
                        if start_x <= element.x < end_x:
                            phase.element_ids.append(element.id)
                            element.phase_id = phase.id
                            assigned = True
                            break
                    
                    # If not assigned, put in first phase without end
                    if not assigned and model.phases:
                        model.phases[-1].element_ids.append(element.id)
                        element.phase_id = model.phases[-1].id
    
    def _find_phase_positions_in_xml(self, raw_xml: str, phases: List[Phase]) -> Dict[str, Dict[str, float]]:
        """
        Estimate phase boundaries based on comment positions and element coordinates.
        This is a heuristic approach.
        """
        positions = {}
        
        # For now, divide space evenly among phases
        # A more sophisticated approach would parse the actual XML positions
        for i, phase in enumerate(phases):
            positions[phase.id] = {
                'start': i * 500,  # Rough estimate
                'end': (i + 1) * 500 if i < len(phases) - 1 else float('inf')
            }
        
        return positions


def parse_bpmn_file(file_path: str) -> ProcessModel:
    """
    Convenience function to parse a BPMN file.
    
    Args:
        file_path: Path to the .bpmn file
        
    Returns:
        ProcessModel with all elements, flows, and detected phases
    """
    parser = BPMNParser()
    return parser.parse(file_path)
