"""
Hierarchy Builder - Detects phases and chunks processes for slide generation.
"""

from typing import List, Dict, Optional, Set, Tuple
from .process_model import ProcessModel, ProcessElement, Phase, ElementType, SequenceFlow


class HierarchyBuilder:
    """
    Builds hierarchical structure from flat process elements.
    Detects or creates phases, ensures 8-10 elements per phase for slides.
    """
    
    def __init__(self, max_elements_per_phase: int = 10, min_elements_per_phase: int = 3):
        self.max_elements = max_elements_per_phase
        self.min_elements = min_elements_per_phase
    
    def build_hierarchy(self, model: ProcessModel) -> ProcessModel:
        """
        Build or refine the phase hierarchy for a process model.
        
        If phases exist, validates and potentially splits large phases.
        If no phases, auto-generates them based on process structure.
        
        Args:
            model: ProcessModel with elements and flows
            
        Returns:
            ProcessModel with updated phases
        """
        if model.phases and all(p.element_ids for p in model.phases):
            # Phases exist with assigned elements - validate and split if needed
            model.phases = self._validate_and_split_phases(model)
        else:
            # No phases or empty phases - auto-generate
            model.phases = self._auto_generate_phases(model)
        
        # Update element phase assignments
        for phase in model.phases:
            for element_id in phase.element_ids:
                if element_id in model.elements:
                    model.elements[element_id].phase_id = phase.id
        
        return model
    
    def _auto_generate_phases(self, model: ProcessModel) -> List[Phase]:
        """
        Auto-generate phases based on process structure.
        
        Uses these heuristics:
        1. Break at parallel gateway splits
        2. Break at major decision points (with multiple branches)
        3. Break at subprocess boundaries
        4. Chunk remaining linear sequences at max_elements
        """
        # Get topologically sorted elements
        sorted_elements = model.topological_sort()
        
        if not sorted_elements:
            return []
        
        phases = []
        current_phase_elements: List[str] = []
        phase_counter = 1
        
        # Track which elements we've processed
        processed: Set[str] = set()
        
        for element in sorted_elements:
            if element.id in processed:
                continue
            
            current_phase_elements.append(element.id)
            processed.add(element.id)
            
            # Check if we should break here
            should_break = self._should_break_phase(
                element, 
                current_phase_elements, 
                model
            )
            
            if should_break:
                # Create phase from current elements
                phase_name = self._generate_phase_name(current_phase_elements, model)
                phases.append(Phase(
                    id=f"phase_{phase_counter}",
                    name=phase_name,
                    order=phase_counter,
                    element_ids=current_phase_elements.copy()
                ))
                current_phase_elements = []
                phase_counter += 1
        
        # Handle remaining elements
        if current_phase_elements:
            phase_name = self._generate_phase_name(current_phase_elements, model)
            phases.append(Phase(
                id=f"phase_{phase_counter}",
                name=phase_name,
                order=phase_counter,
                element_ids=current_phase_elements
            ))
        
        # Merge very small phases
        phases = self._merge_small_phases(phases, model)
        
        # Ensure phase numbers are sequential
        for i, phase in enumerate(phases, 1):
            phase.order = i
            phase.id = f"phase_{i}"
        
        return phases
    
    def _should_break_phase(
        self, 
        element: ProcessElement, 
        current_elements: List[str],
        model: ProcessModel
    ) -> bool:
        """Determine if we should break the phase after this element."""
        
        # Always break after reaching max elements
        if len(current_elements) >= self.max_elements:
            return True
        
        # Break after parallel split gateways (natural parallelization boundary)
        if element.element_type == ElementType.PARALLEL_SPLIT:
            return True
        
        # Break after subprocesses
        if element.element_type == ElementType.SUBPROCESS:
            return True
        
        # Break after major decision points (if we have enough elements)
        if element.element_type == ElementType.DECISION:
            if len(current_elements) >= self.max_elements // 2:
                # Check if this decision has multiple meaningful branches
                outgoing_elements = model.get_outgoing_elements(element.id)
                if len(outgoing_elements) > 1:
                    return True
        
        # Break before merging parallel paths
        if element.element_type == ElementType.PARALLEL_JOIN:
            if len(current_elements) >= self.min_elements:
                return True
        
        # Break after end events (except if it's the only element)
        if element.element_type == ElementType.END and len(current_elements) > 1:
            return True
        
        return False
    
    def _generate_phase_name(self, element_ids: List[str], model: ProcessModel) -> str:
        """Generate a descriptive name for a phase based on its elements."""
        if not element_ids:
            return "Unknown Phase"
        
        elements = [model.elements[eid] for eid in element_ids if eid in model.elements]
        
        # Get task names (excluding gateways and events)
        task_names = [
            e.name for e in elements 
            if e.element_type in [ElementType.TASK, ElementType.USER_TASK, 
                                  ElementType.SERVICE_TASK, ElementType.SUBPROCESS]
            and e.name
        ]
        
        if not task_names:
            # Fall back to first and last element names
            first_elem = elements[0] if elements else None
            last_elem = elements[-1] if elements else None
            
            if first_elem and first_elem.name:
                return first_elem.name
            return "Process Phase"
        
        # Extract common verbs or nouns
        first_task = task_names[0]
        
        # Try to find a common theme
        if len(task_names) == 1:
            return task_names[0]
        
        # Look for common prefixes or actions
        common_words = self._find_common_theme(task_names)
        if common_words:
            return common_words
        
        # Default: use first task name or create range description
        if len(task_names) <= 2:
            return " & ".join(task_names)
        
        return f"{task_names[0]} through {task_names[-1]}"
    
    def _find_common_theme(self, names: List[str]) -> Optional[str]:
        """Find common theme among task names."""
        if not names:
            return None
        
        # Common action verbs that indicate phase themes
        theme_verbs = {
            'prepare': 'Preparation',
            'setup': 'Setup',
            'initialize': 'Initialization',
            'configure': 'Configuration',
            'validate': 'Validation',
            'verify': 'Verification',
            'review': 'Review',
            'approve': 'Approval',
            'clean': 'Cleaning',
            'inspect': 'Inspection',
            'test': 'Testing',
            'assemble': 'Assembly',
            'disassemble': 'Disassembly',
            'remove': 'Removal',
            'install': 'Installation',
            'adjust': 'Adjustment',
            'finalize': 'Finalization',
            'complete': 'Completion',
        }
        
        # Check if names share a common verb
        for verb, theme in theme_verbs.items():
            matching = sum(1 for name in names if verb in name.lower())
            if matching >= len(names) * 0.5:  # At least half match
                return theme
        
        # Check for common first words
        first_words = [name.split()[0].lower() if name.split() else '' for name in names]
        if first_words:
            most_common = max(set(first_words), key=first_words.count)
            count = first_words.count(most_common)
            if count >= len(names) * 0.5 and most_common:
                return most_common.title()
        
        return None
    
    def _validate_and_split_phases(self, model: ProcessModel) -> List[Phase]:
        """Validate existing phases and split any that are too large."""
        result_phases = []
        phase_counter = 1
        
        for phase in model.phases:
            if len(phase.element_ids) <= self.max_elements:
                # Phase is fine
                phase.order = phase_counter
                phase.id = f"phase_{phase_counter}"
                result_phases.append(phase)
                phase_counter += 1
            else:
                # Split the phase
                sub_phases = self._split_large_phase(phase, model)
                for sub_phase in sub_phases:
                    sub_phase.order = phase_counter
                    sub_phase.id = f"phase_{phase_counter}"
                    result_phases.append(sub_phase)
                    phase_counter += 1
        
        return result_phases
    
    def _split_large_phase(self, phase: Phase, model: ProcessModel) -> List[Phase]:
        """Split a large phase into smaller phases."""
        elements = phase.element_ids
        sub_phases = []
        
        # Get elements in order
        sorted_ids = self._sort_elements_by_flow(elements, model)
        
        current_elements: List[str] = []
        sub_counter = 1
        
        for element_id in sorted_ids:
            current_elements.append(element_id)
            
            element = model.elements.get(element_id)
            if element and self._should_break_phase(element, current_elements, model):
                sub_phases.append(Phase(
                    id=f"{phase.id}_{sub_counter}",
                    name=f"{phase.name} (Part {sub_counter})",
                    order=sub_counter,
                    element_ids=current_elements.copy()
                ))
                current_elements = []
                sub_counter += 1
        
        # Handle remaining
        if current_elements:
            if sub_phases:
                # Append to last phase if small
                if len(current_elements) < self.min_elements:
                    sub_phases[-1].element_ids.extend(current_elements)
                else:
                    sub_phases.append(Phase(
                        id=f"{phase.id}_{sub_counter}",
                        name=f"{phase.name} (Part {sub_counter})",
                        order=sub_counter,
                        element_ids=current_elements
                    ))
            else:
                sub_phases.append(Phase(
                    id=phase.id,
                    name=phase.name,
                    order=1,
                    element_ids=current_elements
                ))
        
        return sub_phases
    
    def _sort_elements_by_flow(self, element_ids: List[str], model: ProcessModel) -> List[str]:
        """Sort elements by their position in the process flow."""
        # Build a mini-graph for just these elements
        elements = {eid: model.elements[eid] for eid in element_ids if eid in model.elements}
        
        # Use x-coordinate if available, otherwise use flow order
        if all(e.x is not None for e in elements.values()):
            return sorted(element_ids, key=lambda eid: elements[eid].x or 0)
        
        # Fall back to topological sort within subset
        in_degree = {eid: 0 for eid in element_ids}
        for flow in model.flows.values():
            if flow.target_ref in in_degree and flow.source_ref in element_ids:
                in_degree[flow.target_ref] += 1
        
        queue = [eid for eid, deg in in_degree.items() if deg == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for flow in model.flows.values():
                if flow.source_ref == current and flow.target_ref in in_degree:
                    in_degree[flow.target_ref] -= 1
                    if in_degree[flow.target_ref] == 0:
                        queue.append(flow.target_ref)
        
        # Add any remaining elements not reached
        for eid in element_ids:
            if eid not in result:
                result.append(eid)
        
        return result
    
    def _merge_small_phases(self, phases: List[Phase], model: ProcessModel) -> List[Phase]:
        """Merge phases that are too small."""
        if len(phases) <= 1:
            return phases
        
        result = []
        i = 0
        
        while i < len(phases):
            current = phases[i]
            
            # If current phase is too small and there's a next phase
            if len(current.element_ids) < self.min_elements and i + 1 < len(phases):
                next_phase = phases[i + 1]
                
                # Merge if combined would still be under max
                combined_count = len(current.element_ids) + len(next_phase.element_ids)
                if combined_count <= self.max_elements:
                    merged = Phase(
                        id=current.id,
                        name=f"{current.name} & {next_phase.name}",
                        order=current.order,
                        element_ids=current.element_ids + next_phase.element_ids
                    )
                    result.append(merged)
                    i += 2  # Skip both phases
                    continue
            
            result.append(current)
            i += 1
        
        return result


def build_hierarchy(model: ProcessModel, max_per_phase: int = 10) -> ProcessModel:
    """
    Convenience function to build hierarchy for a process model.
    
    Args:
        model: ProcessModel to process
        max_per_phase: Maximum elements per phase (default: 10)
        
    Returns:
        ProcessModel with updated phases
    """
    builder = HierarchyBuilder(max_elements_per_phase=max_per_phase)
    return builder.build_hierarchy(model)
