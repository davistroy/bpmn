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
        total_phases: int = 1
    ) -> str:
        """Generate a phase detail slide with process flow diagram."""
        
        if not action_title:
            action_title = f"Phase {phase_number} encompasses {len(elements)} activities"
        
        # Generate the process flow SVG
        flow_svg = self._generate_flow_svg(elements, flows)
        
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
            padding: 20px 32px;
            box-sizing: border-box;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
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
            margin: 0 0 16px 0;
            font-style: italic;
        }}
        .flow-container {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
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
        <div class="flow-container">
            {flow_svg}
        </div>
    </div>
</body>
</html>'''

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
