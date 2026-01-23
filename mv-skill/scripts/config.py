"""
MV Skill 配置模块
"""
import os
from pathlib import Path

# 路径配置
SKILL_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
SCHEMAS_DIR = SKILL_DIR / "schemas"
REMOTION_DIR = SKILL_DIR / "remotion"
OUTPUT_DIR = SKILL_DIR / "output"
CACHE_DIR = SKILL_DIR / ".cache"
SESSION_DIR = SKILL_DIR / ".sessions"

# 确保目录存在
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
SESSION_DIR.mkdir(exist_ok=True)

# API Keys
SUNO_API_KEY = os.environ.get("SUNO_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")

# 依赖 Skills 路径
CLAUDE_SKILLS_DIR = Path.home() / ".claude" / "skills"
ZIMAGE_SKILL_DIR = CLAUDE_SKILLS_DIR / "zimage-skill"
MEDIA_DOWNLOADER_DIR = CLAUDE_SKILLS_DIR / "media-downloader"

# 默认配置
DEFAULT_CONFIG = {
    "resolution": "1080x1920",  # 9:16 竖屏
    "fps": 30,
    "duration": 55,
    "style": "anime-hype",
}

# 质量要求
QUALITY_REQUIREMENTS = {
    "image": {
        "min_width": 1080,
        "min_height": 1920,
        "formats": ["jpg", "jpeg", "png", "webp"],
    },
    "video": {
        "min_width": 1080,
        "min_height": 1920,
        "min_fps": 24,
        "max_duration": 30,
        "formats": ["mp4", "mov", "webm"],
    },
}

# 超时配置（秒）
TIMEOUTS = {
    "music_generation": 180,
    "image_generation": 60,
    "asset_download": 30,
    "render_per_scene": 60,
    "total_render": 600,
}

# 素材源优先级
ASSET_SOURCES_PRIORITY = ["pexels", "pixabay", "ai_generate"]

# 可用风格
AVAILABLE_STYLES = ["anime-hype", "cyberpunk", "lyric"]

# 动画效果列表
ANIMATIONS = [
    "none", "zoom-in", "zoom-out", "pan-left", "pan-right",
    "pan-up", "pan-down", "shake", "flash", "ken-burns",
    "speed-lines", "rotate"
]

# 转场效果列表
TRANSITIONS = [
    "none", "fade", "cross-fade", "flash", "wipe-left",
    "wipe-right", "wipe-diagonal", "impact-frame", "glitch", "pixelate"
]
