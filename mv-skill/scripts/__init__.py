"""
MV Skill - 动感短视频生成器
"""

from .storyboard_generator import StoryboardGenerator, generate_storyboard
from .asset_manager import AssetManager
from .music_generator import MusicGenerator, analyze_music
from .preview_generator import PreviewGenerator, generate_preview
from .renderer import Renderer, render_mv
from .config import AVAILABLE_STYLES, DEFAULT_CONFIG
from .exceptions import (
    MVSkillError,
    MusicGenerationError,
    AssetNotFoundError,
    RenderError,
    TemplateNotFoundError,
)

__all__ = [
    "StoryboardGenerator",
    "generate_storyboard",
    "AssetManager",
    "MusicGenerator",
    "analyze_music",
    "PreviewGenerator",
    "generate_preview",
    "Renderer",
    "render_mv",
    "AVAILABLE_STYLES",
    "DEFAULT_CONFIG",
    "MVSkillError",
    "MusicGenerationError",
    "AssetNotFoundError",
    "RenderError",
    "TemplateNotFoundError",
]

__version__ = "1.0.0"
