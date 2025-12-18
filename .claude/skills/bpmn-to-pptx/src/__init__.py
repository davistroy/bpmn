"""
BPMN to PowerPoint Skill

Transform BPMN 2.0 process diagrams into professional, editable PowerPoint presentations.
"""

from .process_model import (
    ProcessModel,
    ProcessElement,
    Phase,
    SequenceFlow,
    ElementType,
    BrandConfig,
    SlideContent
)

from .bpmn_parser import BPMNParser, parse_bpmn_file
from .hierarchy_builder import HierarchyBuilder, build_hierarchy
from .slide_generator import ProcessPresentationGenerator, generate_presentation
from .brand_config import load_brand_config, save_brand_config

__version__ = "1.0.0"
__all__ = [
    # Data models
    "ProcessModel",
    "ProcessElement", 
    "Phase",
    "SequenceFlow",
    "ElementType",
    "BrandConfig",
    "SlideContent",
    # Parser
    "BPMNParser",
    "parse_bpmn_file",
    # Hierarchy
    "HierarchyBuilder",
    "build_hierarchy",
    # Generator
    "ProcessPresentationGenerator",
    "generate_presentation",
    # Brand config
    "load_brand_config",
    "save_brand_config",
]
