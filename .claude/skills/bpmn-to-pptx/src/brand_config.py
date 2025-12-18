"""
Brand Configuration Loader - Loads and validates brand settings.
"""

import os
from typing import Optional, Union
import yaml
from .process_model import BrandConfig


# Default brand configurations
DEFAULT_BRANDS = {
    'default': {
        'name': 'Default',
        'colors': {
            'primary': '1A365D',
            'secondary': '2B6CB0',
            'accent': 'ED8936',
            'background': 'FFFFFF',
            'text_primary': '1A202C',
            'text_secondary': '4A5568',
            'task_fill': 'EBF8FF',
            'task_border': '3182CE',
            'decision_fill': 'FEFCBF',
            'decision_border': 'D69E2E',
            'parallel_fill': 'E9D8FD',
            'parallel_border': '805AD5',
            'start_fill': 'C6F6D5',
            'start_border': '38A169',
            'end_fill': 'FED7D7',
            'end_border': 'E53E3E',
            'subprocess_fill': 'F7FAFC',
            'subprocess_border': '718096',
            'merge_fill': 'E2E8F0',
            'merge_border': '718096',
        },
        'fonts': {
            'title': 'Calibri Light',
            'heading': 'Calibri',
            'body': 'Calibri',
            'sizes': {
                'slide_title': 28,
                'action_title': 16,
                'phase_label': 14,
                'shape_text': 10,
                'footnote': 8,
            }
        },
        'layout': {
            'slide_width': 13.333,
            'slide_height': 7.5,
            'margin_left': 0.5,
            'margin_right': 0.5,
            'margin_top': 0.75,
            'margin_bottom': 0.5,
            'shape_width': 1.4,
            'shape_height': 0.6,
            'shape_gap_h': 0.3,
            'shape_gap_v': 0.7,
        }
    },
    'stratfield': {
        'name': 'Stratfield Consulting',
        'colors': {
            'primary': '0D2137',      # Deep navy
            'secondary': '1E4976',    # Medium navy
            'accent': 'D4A84B',       # Gold
            'background': 'FFFFFF',
            'text_primary': '1A202C',
            'text_secondary': '4A5568',
            'task_fill': 'E8F4FC',
            'task_border': '1E4976',
            'decision_fill': 'FDF6E3',
            'decision_border': 'D4A84B',
            'parallel_fill': 'F0E6F6',
            'parallel_border': '6B4C7A',
            'start_fill': 'D4EDDA',
            'start_border': '28A745',
            'end_fill': 'F8D7DA',
            'end_border': 'DC3545',
            'subprocess_fill': 'F8F9FA',
            'subprocess_border': '6C757D',
            'merge_fill': 'E9ECEF',
            'merge_border': '6C757D',
        },
        'fonts': {
            'title': 'Calibri Light',
            'heading': 'Calibri',
            'body': 'Calibri',
            'sizes': {
                'slide_title': 28,
                'action_title': 16,
                'phase_label': 14,
                'shape_text': 10,
                'footnote': 8,
            }
        },
        'layout': {
            'slide_width': 13.333,
            'slide_height': 7.5,
            'margin_left': 0.5,
            'margin_right': 0.5,
            'margin_top': 0.75,
            'margin_bottom': 0.5,
            'shape_width': 1.4,
            'shape_height': 0.6,
            'shape_gap_h': 0.3,
            'shape_gap_v': 0.7,
        }
    }
}


def load_brand_config(brand: Union[str, dict, None] = None) -> BrandConfig:
    """
    Load brand configuration from various sources.
    
    Args:
        brand: Can be:
            - None: Use default brand
            - "default" or "stratfield": Use built-in brand
            - Path to YAML file: Load from file
            - Dict: Use directly
            
    Returns:
        BrandConfig object
    """
    if brand is None:
        brand = 'default'
    
    # If it's a string, could be a preset name or file path
    if isinstance(brand, str):
        # Check if it's a preset
        if brand.lower() in DEFAULT_BRANDS:
            config_dict = DEFAULT_BRANDS[brand.lower()]
        # Check if it's a file path
        elif os.path.isfile(brand):
            with open(brand, 'r') as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError(f"Unknown brand '{brand}'. Use 'default', 'stratfield', or provide a path to a YAML file.")
    elif isinstance(brand, dict):
        config_dict = brand
    else:
        raise ValueError(f"Invalid brand type: {type(brand)}")
    
    return _dict_to_brand_config(config_dict)


def _dict_to_brand_config(config: dict) -> BrandConfig:
    """Convert a configuration dictionary to a BrandConfig object."""
    
    # Start with defaults
    result = BrandConfig()
    
    # Apply name
    if 'name' in config:
        result.name = config['name']
    elif 'brand' in config and 'name' in config['brand']:
        result.name = config['brand']['name']
    
    # Apply colors
    colors = config.get('colors', {})
    for key in ['primary', 'secondary', 'accent', 'background', 
                'text_primary', 'text_secondary',
                'task_fill', 'task_border', 'decision_fill', 'decision_border',
                'parallel_fill', 'parallel_border', 'start_fill', 'start_border',
                'end_fill', 'end_border', 'subprocess_fill', 'subprocess_border',
                'merge_fill', 'merge_border']:
        if key in colors:
            # Remove # prefix if present
            value = colors[key].lstrip('#')
            setattr(result, key, value)
    
    # Apply fonts
    fonts = config.get('fonts', {})
    if 'title' in fonts:
        result.title_font = fonts['title']
    if 'heading' in fonts:
        result.heading_font = fonts['heading']
    if 'body' in fonts:
        result.body_font = fonts['body']
    
    # Apply font sizes
    sizes = fonts.get('sizes', {})
    if 'slide_title' in sizes:
        result.slide_title_size = sizes['slide_title']
    if 'action_title' in sizes:
        result.action_title_size = sizes['action_title']
    if 'phase_label' in sizes:
        result.phase_label_size = sizes['phase_label']
    if 'shape_text' in sizes:
        result.shape_text_size = sizes['shape_text']
    if 'footnote' in sizes:
        result.footnote_size = sizes['footnote']
    
    # Apply layout
    layout = config.get('layout', {})
    for key in ['slide_width', 'slide_height', 'margin_left', 'margin_right',
                'margin_top', 'margin_bottom', 'shape_width', 'shape_height',
                'shape_gap_h', 'shape_gap_v']:
        if key in layout:
            setattr(result, key, layout[key])
    
    # Apply logo settings
    if 'logo' in config:
        logo = config['logo']
        if 'path' in logo:
            result.logo_path = logo['path']
        if 'width' in logo:
            result.logo_width = logo['width']
        if 'position' in logo:
            result.logo_position = logo['position']
    
    return result


def save_brand_config(config: BrandConfig, file_path: str):
    """Save a brand configuration to a YAML file."""
    
    config_dict = {
        'brand': {
            'name': config.name
        },
        'colors': {
            'primary': config.primary,
            'secondary': config.secondary,
            'accent': config.accent,
            'background': config.background,
            'text_primary': config.text_primary,
            'text_secondary': config.text_secondary,
            'task_fill': config.task_fill,
            'task_border': config.task_border,
            'decision_fill': config.decision_fill,
            'decision_border': config.decision_border,
            'parallel_fill': config.parallel_fill,
            'parallel_border': config.parallel_border,
            'start_fill': config.start_fill,
            'start_border': config.start_border,
            'end_fill': config.end_fill,
            'end_border': config.end_border,
            'subprocess_fill': config.subprocess_fill,
            'subprocess_border': config.subprocess_border,
            'merge_fill': config.merge_fill,
            'merge_border': config.merge_border,
        },
        'fonts': {
            'title': config.title_font,
            'heading': config.heading_font,
            'body': config.body_font,
            'sizes': {
                'slide_title': config.slide_title_size,
                'action_title': config.action_title_size,
                'phase_label': config.phase_label_size,
                'shape_text': config.shape_text_size,
                'footnote': config.footnote_size,
            }
        },
        'layout': {
            'slide_width': config.slide_width,
            'slide_height': config.slide_height,
            'margin_left': config.margin_left,
            'margin_right': config.margin_right,
            'margin_top': config.margin_top,
            'margin_bottom': config.margin_bottom,
            'shape_width': config.shape_width,
            'shape_height': config.shape_height,
            'shape_gap_h': config.shape_gap_h,
            'shape_gap_v': config.shape_gap_v,
        }
    }
    
    if config.logo_path:
        config_dict['logo'] = {
            'path': config.logo_path,
            'width': config.logo_width,
            'position': config.logo_position,
        }
    
    with open(file_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
