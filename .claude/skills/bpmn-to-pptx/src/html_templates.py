"""
HTML Templates for PowerPoint slide generation.
Uses the html2pptx workflow from the core pptx skill.
"""

from typing import List, Dict, Optional, Tuple
from .process_model import ProcessElement, Phase, ElementType, BrandConfig, SlideContent


class HTMLTemplates:
    """Generates HTML slides for conversion to PowerPoint."""
    
    def __init__(self, brand: BrandConfig):
        self.brand = brand
        # Slide dimensions for 16:9
        self.width = 960
        self.height = 540
    
    def generate_title_slide(self, process_name: str, subtitle: Optional[str] = None) -> str:
        """Generate the title slide HTML."""
        subtitle_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else ''
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {self._get_base_css()}
        .title-slide {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            background: linear-gradient(135deg, #{self.brand.primary} 0%, #{self.brand.secondary} 100%);
            color: white;
            text-align: center;
            padding: 40px;
        }}
        .title-slide h1 {{
            font-family: "{self.brand.title_font}", sans-serif;
            font-size: 48px;
            font-weight: 300;
            margin: 0 0 20px 0;
            letter-spacing: 1px;
        }}
        .title-slide .subtitle {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: 20px;
            opacity: 0.9;
            margin: 0;
        }}
    </style>
</head>
<body style="width: {self.width}px; height: {self.height}px; margin: 0; padding: 0;">
    <div class="title-slide">
        <h1>{process_name}</h1>
        {subtitle_html}
    </div>
</body>
</html>'''

    def generate_overview_slide(
        self, 
        process_name: str,
        phases: List[Tuple[str, int]],  # (name, step_count)
        action_title: Optional[str] = None
    ) -> str:
        """Generate the process overview slide with chevron phases."""
        
        if not action_title:
            action_title = f"{process_name} follows {len(phases)} phases from start to completion"
        
        # Generate chevron arrows for each phase
        chevrons_html = self._generate_chevrons(phases)
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {self._get_base_css()}
        .overview-slide {{
            display: flex;
            flex-direction: column;
            height: 100%;
            padding: 20px 32px;
            box-sizing: border-box;
        }}
        .slide-title {{
            font-family: "{self.brand.heading_font}", sans-serif;
            font-size: {self.brand.slide_title_size}px;
            font-weight: 600;
            color: #{self.brand.primary};
            margin: 0 0 8px 0;
        }}
        .action-title {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: {self.brand.action_title_size}px;
            color: #{self.brand.text_secondary};
            margin: 0 0 24px 0;
            font-style: italic;
        }}
        .chevron-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            flex: 1;
            gap: 0;
        }}
        .chevron {{
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-width: 120px;
            height: 80px;
            background: #{self.brand.secondary};
            color: white;
            padding: 10px 20px 10px 30px;
            clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 50%, calc(100% - 20px) 100%, 0 100%, 20px 50%);
            margin-left: -10px;
        }}
        .chevron:first-child {{
            clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 50%, calc(100% - 20px) 100%, 0 100%);
            margin-left: 0;
            padding-left: 20px;
        }}
        .chevron:nth-child(odd) {{
            background: #{self.brand.primary};
        }}
        .chevron-number {{
            font-family: "{self.brand.heading_font}", sans-serif;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .chevron-name {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: 11px;
            text-align: center;
            line-height: 1.2;
        }}
        .chevron-count {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: 9px;
            opacity: 0.8;
            margin-top: 4px;
        }}
    </style>
</head>
<body style="width: {self.width}px; height: {self.height}px; margin: 0; padding: 0;">
    <div class="overview-slide">
        <h1 class="slide-title">Process Overview</h1>
        <p class="action-title">{action_title}</p>
        <div class="chevron-container">
            {chevrons_html}
        </div>
    </div>
</body>
</html>'''

    def _generate_chevrons(self, phases: List[Tuple[str, int]]) -> str:
        """Generate HTML for chevron phase indicators."""
        html_parts = []
        for i, (name, count) in enumerate(phases, 1):
            # Truncate long names
            display_name = name if len(name) <= 20 else name[:17] + "..."
            html_parts.append(f'''
            <div class="chevron">
                <span class="chevron-number">{i}</span>
                <span class="chevron-name">{display_name}</span>
                <span class="chevron-count">{count} steps</span>
            </div>''')
        return '\n'.join(html_parts)

    def generate_phase_detail_slide(
        self,
        phase: Phase,
        elements: List[ProcessElement],
        flows: List[Tuple[str, str, Optional[str]]],  # (from_id, to_id, label)
        action_title: Optional[str] = None,
        phase_number: int = 1,
        total_phases: int = 1,
        all_phases: Optional[List[Tuple[str, int]]] = None  # (name, step_count) for chevron row
    ) -> str:
        """Generate a phase detail slide with 3-tier hierarchical layout.

        Layout:
        - Row 1 (Level 1): Chevrons showing all phases, current phase highlighted
        - Row 2 (Level 2): White rounded boxes showing task groups
        - Row 3 (Level 3): Gray square boxes showing individual tasks
        - Below Row 3: Bullet points with task details
        """

        if not action_title:
            action_title = f"Phase {phase_number} encompasses {len(elements)} activities"

        # Build phase chevrons (Level 1)
        if all_phases:
            chevrons_html = self._generate_phase_chevrons(all_phases, phase_number)
        else:
            # Fallback: just show current phase
            chevrons_html = self._generate_phase_chevrons([(phase.name, len(elements))], 1)

        # Group elements into Level 2 categories and Level 3 tasks
        task_groups = self._group_elements_for_hierarchy(elements, flows)

        # Generate Level 2 (white rounded boxes) and Level 3 (gray square boxes)
        level2_html = self._generate_level2_boxes(task_groups)

        # Generate bullet points for task details
        bullets_html = self._generate_task_bullets(task_groups)

        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {self._get_base_css()}
        .phase-slide {{
            display: flex;
            flex-direction: column;
            height: 100%;
            padding: 16px 28px;
            box-sizing: border-box;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 6px;
        }}
        .slide-title {{
            font-family: "{self.brand.heading_font}", sans-serif;
            font-size: {self.brand.slide_title_size}px;
            font-weight: 600;
            color: #{self.brand.primary};
            margin: 0;
        }}
        .phase-indicator {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: 12px;
            color: #{self.brand.text_secondary};
            background: #f0f0f0;
            padding: 4px 12px;
            border-radius: 12px;
        }}
        .action-title {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: {self.brand.action_title_size}px;
            color: #{self.brand.text_secondary};
            margin: 0 0 12px 0;
            font-style: italic;
        }}

        /* Level 1: Phase Chevrons */
        .level1-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 16px;
            gap: 0;
        }}
        .phase-chevron {{
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-width: 100px;
            height: 50px;
            background: #{self.brand.text_secondary};
            color: white;
            padding: 6px 16px 6px 24px;
            clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 50%, calc(100% - 15px) 100%, 0 100%, 15px 50%);
            margin-left: -8px;
            opacity: 0.5;
        }}
        .phase-chevron:first-child {{
            clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 50%, calc(100% - 15px) 100%, 0 100%);
            margin-left: 0;
            padding-left: 16px;
        }}
        .phase-chevron.active {{
            background: #{self.brand.primary};
            opacity: 1;
        }}
        .phase-chevron-number {{
            font-family: "{self.brand.heading_font}", sans-serif;
            font-size: 14px;
            font-weight: 700;
        }}
        .phase-chevron-name {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: 9px;
            text-align: center;
            line-height: 1.1;
            max-width: 80px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        /* Level 2: White Rounded Boxes (Task Groups) */
        .level2-container {{
            display: flex;
            align-items: stretch;
            justify-content: center;
            gap: 20px;
            margin-bottom: 12px;
        }}
        .level2-box {{
            background: #FFFFFF;
            border: 2px solid #{self.brand.primary};
            border-radius: 12px;
            padding: 10px 16px;
            min-width: 140px;
            max-width: 200px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .level2-title {{
            font-family: "{self.brand.heading_font}", sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #{self.brand.primary};
            margin: 0;
        }}

        /* Level 3: Gray Square Boxes (Individual Tasks) */
        .level3-container {{
            display: flex;
            align-items: flex-start;
            justify-content: center;
            gap: 20px;
            margin-bottom: 16px;
        }}
        .level3-group {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }}
        .level3-tasks {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .level3-box {{
            background: #E8E8E8;
            border: 1px solid #A0A0A0;
            border-radius: 0;
            padding: 8px 12px;
            min-width: 100px;
            max-width: 140px;
            text-align: center;
        }}
        .level3-title {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: 10px;
            font-weight: 500;
            color: #{self.brand.text_primary};
            margin: 0;
            line-height: 1.2;
        }}

        /* Connector lines between levels */
        .connector-container {{
            display: flex;
            justify-content: center;
            margin: 4px 0;
        }}
        .connector-line {{
            width: 2px;
            height: 12px;
            background: #{self.brand.text_secondary};
        }}

        /* Bullet Points Section */
        .bullets-container {{
            flex: 1;
            background: #F8F9FA;
            border-radius: 8px;
            padding: 12px 16px;
            overflow-y: auto;
        }}
        .bullets-title {{
            font-family: "{self.brand.heading_font}", sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #{self.brand.primary};
            margin: 0 0 8px 0;
        }}
        .task-bullet-group {{
            margin-bottom: 10px;
        }}
        .task-bullet-header {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: 11px;
            font-weight: 600;
            color: #{self.brand.text_primary};
            margin: 0 0 4px 0;
        }}
        .task-bullet-list {{
            margin: 0;
            padding-left: 20px;
        }}
        .task-bullet-item {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: 10px;
            color: #{self.brand.text_secondary};
            margin: 2px 0;
            line-height: 1.3;
        }}
    </style>
</head>
<body style="width: {self.width}px; height: {self.height}px; margin: 0; padding: 0;">
    <div class="phase-slide">
        <div class="header">
            <h1 class="slide-title">{phase.name}</h1>
            <span class="phase-indicator">Phase {phase_number} of {total_phases}</span>
        </div>
        <p class="action-title">{action_title}</p>

        <!-- Level 1: Phase Chevrons -->
        <div class="level1-container">
            {chevrons_html}
        </div>

        <!-- Level 2 & 3: Task Groups and Individual Tasks -->
        {level2_html}

        <!-- Task Details Bullets -->
        <div class="bullets-container">
            <div class="bullets-title">Activity Details</div>
            {bullets_html}
        </div>
    </div>
</body>
</html>'''

    def _generate_phase_chevrons(self, phases: List[Tuple[str, int]], active_phase: int) -> str:
        """Generate chevron HTML for Level 1 (phase overview row)."""
        html_parts = []
        for i, (name, count) in enumerate(phases, 1):
            active_class = "active" if i == active_phase else ""
            display_name = name if len(name) <= 15 else name[:12] + "..."
            html_parts.append(f'''
            <div class="phase-chevron {active_class}">
                <span class="phase-chevron-number">{i}</span>
                <span class="phase-chevron-name">{display_name}</span>
            </div>''')
        return '\n'.join(html_parts)

    def _group_elements_for_hierarchy(
        self,
        elements: List[ProcessElement],
        flows: List[Tuple[str, str, Optional[str]]]
    ) -> List[Dict]:
        """Group elements into Level 2 categories containing Level 3 tasks.

        Returns list of groups, each with:
        - name: group name
        - tasks: list of ProcessElement objects
        """
        # Filter to only task-like elements (not gateways, events)
        tasks = [e for e in elements if e.element_type in [
            ElementType.TASK, ElementType.USER_TASK,
            ElementType.SERVICE_TASK, ElementType.SUBPROCESS
        ]]

        if not tasks:
            return []

        # Group tasks into logical clusters of 3-4 tasks each
        groups = []
        group_size = 3  # Target 3 tasks per group for good visual balance

        for i in range(0, len(tasks), group_size):
            group_tasks = tasks[i:i + group_size]

            # Generate group name from first task or common theme
            group_name = self._generate_group_name(group_tasks)

            groups.append({
                'name': group_name,
                'tasks': group_tasks
            })

        return groups

    def _generate_group_name(self, tasks: List[ProcessElement]) -> str:
        """Generate a descriptive name for a group of tasks."""
        if not tasks:
            return "Activities"

        if len(tasks) == 1:
            return tasks[0].display_name

        # Try to find common theme from task names
        names = [t.display_name for t in tasks]

        # Check for common first word
        first_words = [n.split()[0].lower() if n.split() else '' for n in names]
        if first_words and len(set(first_words)) == 1 and first_words[0]:
            return first_words[0].title() + " Activities"

        # Check for common action verbs
        common_verbs = ['prepare', 'setup', 'configure', 'validate', 'review',
                       'clean', 'inspect', 'test', 'assemble', 'install', 'remove']
        for verb in common_verbs:
            if all(verb in n.lower() for n in names):
                return verb.title() + " Steps"

        # Default: use first task name as group indicator
        first_name = tasks[0].display_name
        if len(first_name) > 20:
            first_name = first_name[:17] + "..."
        return first_name

    def _generate_level2_boxes(self, task_groups: List[Dict]) -> str:
        """Generate HTML for Level 2 (white rounded boxes) and Level 3 (gray square boxes)."""
        if not task_groups:
            return '<div class="level2-container"><div class="level2-box"><p class="level2-title">No activities</p></div></div>'

        # Build Level 2 boxes
        level2_parts = []
        for group in task_groups:
            level2_parts.append(f'''
            <div class="level2-box">
                <p class="level2-title">{group['name']}</p>
            </div>''')

        level2_html = f'''
        <div class="level2-container">
            {''.join(level2_parts)}
        </div>
        <div class="connector-container">
            <div class="connector-line"></div>
        </div>'''

        # Build Level 3 groups with tasks
        level3_parts = []
        for group in task_groups:
            task_boxes = []
            for task in group['tasks']:
                task_name = task.display_name
                if len(task_name) > 20:
                    task_name = task_name[:17] + "..."
                task_boxes.append(f'''
                <div class="level3-box">
                    <p class="level3-title">{task_name}</p>
                </div>''')

            level3_parts.append(f'''
            <div class="level3-group">
                <div class="level3-tasks">
                    {''.join(task_boxes)}
                </div>
            </div>''')

        level3_html = f'''
        <div class="level3-container">
            {''.join(level3_parts)}
        </div>'''

        return level2_html + level3_html

    def _generate_task_bullets(self, task_groups: List[Dict]) -> str:
        """Generate bullet points HTML for task details."""
        if not task_groups:
            return '<p class="task-bullet-item">No activity details available</p>'

        html_parts = []
        for group in task_groups:
            bullets = []
            for task in group['tasks']:
                # Use documentation if available, otherwise generate description
                if task.documentation:
                    description = task.documentation
                else:
                    description = self._generate_task_description(task)

                bullets.append(f'<li class="task-bullet-item">{description}</li>')

            html_parts.append(f'''
            <div class="task-bullet-group">
                <p class="task-bullet-header">{group['name']}</p>
                <ul class="task-bullet-list">
                    {''.join(bullets)}
                </ul>
            </div>''')

        return '\n'.join(html_parts)

    def _generate_task_description(self, task: ProcessElement) -> str:
        """Generate a description for a task based on its name and type."""
        name = task.display_name

        # Generate contextual description based on task type
        if task.element_type == ElementType.USER_TASK:
            return f"Manual activity: {name} - requires user input and verification"
        elif task.element_type == ElementType.SERVICE_TASK:
            return f"Automated step: {name} - system performs this action automatically"
        elif task.element_type == ElementType.SUBPROCESS:
            return f"Sub-process: {name} - contains nested activities (see detailed breakdown)"
        else:
            return f"{name} - execute this step to progress the workflow"

    def _generate_flow_svg(
        self, 
        elements: List[ProcessElement],
        flows: List[Tuple[str, str, Optional[str]]]
    ) -> str:
        """Generate SVG for process flow diagram."""
        
        if not elements:
            return '<p>No elements to display</p>'
        
        # Layout parameters
        shape_w = 120
        shape_h = 50
        gap_h = 40
        gap_v = 60
        padding = 20
        
        # Calculate positions
        positions = self._calculate_layout(elements, flows, shape_w, shape_h, gap_h, gap_v)
        
        # Determine SVG dimensions
        max_x = max(pos['x'] + shape_w for pos in positions.values()) if positions else 400
        max_y = max(pos['y'] + shape_h for pos in positions.values()) if positions else 200
        svg_width = max_x + padding * 2
        svg_height = max_y + padding * 2
        
        # Scale to fit container (max 896 x 340)
        scale_x = min(1, 896 / svg_width)
        scale_y = min(1, 340 / svg_height)
        scale = min(scale_x, scale_y)
        
        # Generate SVG elements
        svg_elements = []
        
        # Draw connectors first (behind shapes)
        for from_id, to_id, label in flows:
            if from_id in positions and to_id in positions:
                connector = self._draw_connector(
                    positions[from_id], positions[to_id],
                    shape_w, shape_h, label
                )
                svg_elements.append(connector)
        
        # Draw shapes
        for element in elements:
            if element.id in positions:
                shape = self._draw_shape(element, positions[element.id], shape_w, shape_h)
                svg_elements.append(shape)
        
        return f'''<svg width="{svg_width * scale}" height="{svg_height * scale}" 
                       viewBox="0 0 {svg_width} {svg_height}" 
                       style="max-width: 100%; max-height: 100%;">
            <g transform="translate({padding}, {padding})">
                {''.join(svg_elements)}
            </g>
        </svg>'''

    def _calculate_layout(
        self,
        elements: List[ProcessElement],
        flows: List[Tuple[str, str, Optional[str]]],
        shape_w: int,
        shape_h: int,
        gap_h: int,
        gap_v: int
    ) -> Dict[str, Dict[str, int]]:
        """Calculate x,y positions for each element."""
        
        positions = {}
        
        # Build adjacency for layout
        outgoing = {e.id: [] for e in elements}
        incoming = {e.id: [] for e in elements}
        element_ids = {e.id for e in elements}
        
        for from_id, to_id, _ in flows:
            if from_id in element_ids and to_id in element_ids:
                outgoing[from_id].append(to_id)
                incoming[to_id].append(from_id)
        
        # Find start elements (no incoming from within this set)
        starts = [e for e in elements if not incoming[e.id]]
        if not starts:
            starts = [elements[0]]
        
        # BFS to assign columns
        visited = set()
        queue = [(e.id, 0) for e in starts]
        columns: Dict[str, int] = {}
        
        while queue:
            elem_id, col = queue.pop(0)
            if elem_id in visited:
                # Update column if we found a longer path
                if col > columns.get(elem_id, -1):
                    columns[elem_id] = col
                continue
            
            visited.add(elem_id)
            columns[elem_id] = max(col, columns.get(elem_id, 0))
            
            for next_id in outgoing[elem_id]:
                if next_id in element_ids:
                    queue.append((next_id, col + 1))
        
        # Assign rows within each column
        col_rows: Dict[int, List[str]] = {}
        for elem_id, col in columns.items():
            if col not in col_rows:
                col_rows[col] = []
            col_rows[col].append(elem_id)
        
        # Calculate positions
        for col, elem_ids in col_rows.items():
            # Sort by y-coordinate if available, otherwise by original order
            elem_ids.sort(key=lambda eid: next((e.y or 0 for e in elements if e.id == eid), 0))
            
            for row, elem_id in enumerate(elem_ids):
                # Center vertically if single row
                total_height = len(elem_ids) * shape_h + (len(elem_ids) - 1) * gap_v
                start_y = (340 - total_height) // 2 if total_height < 340 else 0
                
                positions[elem_id] = {
                    'x': col * (shape_w + gap_h),
                    'y': start_y + row * (shape_h + gap_v),
                    'col': col,
                    'row': row
                }
        
        return positions

    def _draw_shape(
        self, 
        element: ProcessElement, 
        pos: Dict[str, int],
        width: int,
        height: int
    ) -> str:
        """Draw a single BPMN shape as SVG."""
        
        x, y = pos['x'], pos['y']
        fill, stroke = self.brand.get_element_colors(element.element_type)
        
        # Get display text (truncate if needed)
        text = element.display_name
        if len(text) > 25:
            text = text[:22] + "..."
        
        # Split text into lines if too long
        lines = self._wrap_text(text, 18)
        
        if element.element_type in [ElementType.START, ElementType.END]:
            # Oval shape
            cx, cy = x + width // 2, y + height // 2
            rx, ry = width // 3, height // 2.5
            text_y = cy + 4
            
            return f'''
            <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" 
                     fill="#{fill}" stroke="#{stroke}" stroke-width="2"/>
            <text x="{cx}" y="{text_y}" text-anchor="middle" 
                  font-family="{self.brand.body_font}" font-size="10" fill="#{self.brand.text_primary}">
                {element.display_name[:12]}
            </text>'''
        
        elif element.element_type in [ElementType.DECISION, ElementType.PARALLEL_SPLIT, 
                                       ElementType.PARALLEL_JOIN, ElementType.MERGE, ElementType.GATEWAY]:
            # Diamond shape
            cx, cy = x + width // 2, y + height // 2
            size = min(width, height) * 0.7
            
            points = f"{cx},{cy - size/2} {cx + size/2},{cy} {cx},{cy + size/2} {cx - size/2},{cy}"
            
            # Add + symbol for parallel gateways
            symbol = ''
            if element.element_type in [ElementType.PARALLEL_SPLIT, ElementType.PARALLEL_JOIN]:
                symbol = f'''
                <line x1="{cx - 8}" y1="{cy}" x2="{cx + 8}" y2="{cy}" 
                      stroke="#{stroke}" stroke-width="2"/>
                <line x1="{cx}" y1="{cy - 8}" x2="{cx}" y2="{cy + 8}" 
                      stroke="#{stroke}" stroke-width="2"/>'''
            elif element.element_type == ElementType.DECISION:
                symbol = f'''
                <text x="{cx}" y="{cy + 4}" text-anchor="middle" 
                      font-family="{self.brand.body_font}" font-size="12" 
                      font-weight="bold" fill="#{stroke}">?</text>'''
            
            return f'''
            <polygon points="{points}" fill="#{fill}" stroke="#{stroke}" stroke-width="2"/>
            {symbol}'''
        
        elif element.element_type == ElementType.SUBPROCESS:
            # Rounded rectangle with border
            rx = 8
            
            text_elements = self._generate_text_lines(lines, x + width // 2, y + height // 2)
            
            return f'''
            <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{rx}" 
                  fill="#{fill}" stroke="#{stroke}" stroke-width="2"/>
            <rect x="{x + 4}" y="{y + 4}" width="{width - 8}" height="{height - 8}" rx="{rx - 2}" 
                  fill="none" stroke="#{stroke}" stroke-width="1" stroke-dasharray="3,2"/>
            {text_elements}'''
        
        else:
            # Default: Rounded rectangle (task)
            rx = 8
            
            text_elements = self._generate_text_lines(lines, x + width // 2, y + height // 2)
            
            return f'''
            <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{rx}" 
                  fill="#{fill}" stroke="#{stroke}" stroke-width="2"/>
            {text_elements}'''

    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        """Wrap text into multiple lines."""
        if len(text) <= max_chars:
            return [text]
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines[:3]  # Max 3 lines

    def _generate_text_lines(self, lines: List[str], cx: int, cy: int) -> str:
        """Generate SVG text elements for multiple lines."""
        if not lines:
            return ''
        
        line_height = 12
        start_y = cy - (len(lines) - 1) * line_height // 2
        
        text_elements = []
        for i, line in enumerate(lines):
            y = start_y + i * line_height
            text_elements.append(
                f'<text x="{cx}" y="{y}" text-anchor="middle" '
                f'font-family="{self.brand.body_font}" font-size="10" '
                f'fill="#{self.brand.text_primary}">{line}</text>'
            )
        
        return '\n'.join(text_elements)

    def _draw_connector(
        self,
        from_pos: Dict[str, int],
        to_pos: Dict[str, int],
        shape_w: int,
        shape_h: int,
        label: Optional[str] = None
    ) -> str:
        """Draw a connector arrow between two shapes."""
        
        # Calculate connection points
        from_x = from_pos['x'] + shape_w
        from_y = from_pos['y'] + shape_h // 2
        to_x = to_pos['x']
        to_y = to_pos['y'] + shape_h // 2
        
        # Different column = horizontal connection
        if from_pos['col'] != to_pos['col']:
            # Simple horizontal with optional vertical jog
            if abs(from_y - to_y) < 10:
                # Straight horizontal
                path = f"M {from_x} {from_y} L {to_x} {to_y}"
            else:
                # Elbow connector
                mid_x = (from_x + to_x) // 2
                path = f"M {from_x} {from_y} L {mid_x} {from_y} L {mid_x} {to_y} L {to_x} {to_y}"
        else:
            # Same column - vertical connection
            from_y = from_pos['y'] + shape_h
            to_y = to_pos['y']
            from_x = from_pos['x'] + shape_w // 2
            to_x = to_pos['x'] + shape_w // 2
            path = f"M {from_x} {from_y} L {to_x} {to_y}"
        
        # Arrow marker
        arrow_id = f"arrow_{from_pos['col']}_{from_pos['row']}_{to_pos['col']}_{to_pos['row']}"
        
        label_element = ''
        if label:
            mid_x = (from_x + to_x) // 2
            mid_y = (from_y + to_y) // 2 - 8
            label_element = f'''
            <text x="{mid_x}" y="{mid_y}" text-anchor="middle" 
                  font-family="{self.brand.body_font}" font-size="9" 
                  fill="#{self.brand.text_secondary}">{label[:15]}</text>'''
        
        return f'''
        <defs>
            <marker id="{arrow_id}" markerWidth="10" markerHeight="7" 
                    refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#{self.brand.text_secondary}"/>
            </marker>
        </defs>
        <path d="{path}" fill="none" stroke="#{self.brand.text_secondary}" 
              stroke-width="1.5" marker-end="url(#{arrow_id})"/>
        {label_element}'''

    def generate_decision_summary_slide(
        self,
        decisions: List[Tuple[str, List[str]]],  # (question, [options])
        action_title: Optional[str] = None
    ) -> str:
        """Generate a decision points summary slide."""
        
        if not action_title:
            action_title = f"The process contains {len(decisions)} key decision points"
        
        # Generate decision cards
        cards_html = self._generate_decision_cards(decisions)
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {self._get_base_css()}
        .decision-slide {{
            display: flex;
            flex-direction: column;
            height: 100%;
            padding: 20px 32px;
            box-sizing: border-box;
        }}
        .slide-title {{
            font-family: "{self.brand.heading_font}", sans-serif;
            font-size: {self.brand.slide_title_size}px;
            font-weight: 600;
            color: #{self.brand.primary};
            margin: 0 0 8px 0;
        }}
        .action-title {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: {self.brand.action_title_size}px;
            color: #{self.brand.text_secondary};
            margin: 0 0 20px 0;
            font-style: italic;
        }}
        .decisions-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            flex: 1;
        }}
        .decision-card {{
            background: #{self.brand.decision_fill};
            border: 2px solid #{self.brand.decision_border};
            border-radius: 8px;
            padding: 12px 16px;
            width: calc(50% - 8px);
            box-sizing: border-box;
        }}
        .decision-number {{
            font-family: "{self.brand.heading_font}", sans-serif;
            font-size: 14px;
            font-weight: 700;
            color: #{self.brand.decision_border};
            margin-bottom: 4px;
        }}
        .decision-question {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: #{self.brand.text_primary};
            margin-bottom: 8px;
        }}
        .decision-options {{
            font-family: "{self.brand.body_font}", sans-serif;
            font-size: 10px;
            color: #{self.brand.text_secondary};
        }}
        .decision-option {{
            margin: 2px 0;
        }}
    </style>
</head>
<body style="width: {self.width}px; height: {self.height}px; margin: 0; padding: 0;">
    <div class="decision-slide">
        <h1 class="slide-title">Key Decision Points</h1>
        <p class="action-title">{action_title}</p>
        <div class="decisions-container">
            {cards_html}
        </div>
    </div>
</body>
</html>'''

    def _generate_decision_cards(self, decisions: List[Tuple[str, List[str]]]) -> str:
        """Generate HTML for decision cards."""
        cards = []
        for i, (question, options) in enumerate(decisions, 1):
            options_html = '\n'.join(
                f'<div class="decision-option">→ {opt}</div>' 
                for opt in options[:3]  # Max 3 options
            )
            cards.append(f'''
            <div class="decision-card">
                <div class="decision-number">Decision {i}</div>
                <div class="decision-question">{question}</div>
                <div class="decision-options">{options_html}</div>
            </div>''')
        return '\n'.join(cards)

    def _get_base_css(self) -> str:
        """Return base CSS used across all slides."""
        return f'''
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: "{self.brand.body_font}", Arial, sans-serif;
            background: #{self.brand.background};
            color: #{self.brand.text_primary};
        }}
        '''
