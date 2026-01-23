"""
分镜脚本生成器
根据用户输入和风格模板生成完整的分镜脚本
"""
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

from .config import TEMPLATES_DIR, SCHEMAS_DIR, DEFAULT_CONFIG
from .exceptions import TemplateNotFoundError, StoryboardValidationError


class StoryboardGenerator:
    """分镜脚本生成器"""

    def __init__(self, style: str = "anime-hype"):
        self.style = style
        self.template = self._load_template(style)

    def _load_template(self, style: str) -> Dict:
        """加载风格模板"""
        template_path = TEMPLATES_DIR / style / "template.yaml"
        if not template_path.exists():
            raise TemplateNotFoundError(f"模板不存在: {style}")

        with open(template_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def generate(
        self,
        title: str,
        theme: str,
        lyrics: Optional[List[str]] = None,
        duration: int = 55,
        custom_prompts: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """
        生成分镜脚本

        Args:
            title: MV 标题
            theme: 主题描述
            lyrics: 歌词列表
            duration: 总时长（秒）
            custom_prompts: 自定义场景提示词

        Returns:
            完整的分镜脚本字典
        """
        # 基础元数据
        storyboard = {
            "meta": {
                "title": title,
                "style": self.style,
                "duration": duration,
                "resolution": DEFAULT_CONFIG["resolution"],
                "fps": DEFAULT_CONFIG["fps"],
            },
            "music": {
                "source": "suno",
                "prompt": self._generate_music_prompt(theme),
                "file": None,
                "bpm": None,
                "beats": [],
            },
            "scenes": [],
        }

        # 根据模板结构生成场景
        scenes = self._generate_scenes(
            title=title,
            theme=theme,
            lyrics=lyrics or [],
            duration=duration,
            custom_prompts=custom_prompts or {},
        )
        storyboard["scenes"] = scenes

        return storyboard

    def _generate_music_prompt(self, theme: str) -> str:
        """生成音乐提示词"""
        template = self.template.get("rhythm", {}).get(
            "music_prompt_template",
            "epic {mood} music, {bpm}bpm"
        )
        bpm_range = self.template.get("rhythm", {}).get("bpm_range", {"ideal": 128})
        ideal_bpm = bpm_range.get("ideal", 128)

        # 根据主题推断情绪
        mood = self._infer_mood(theme)

        return template.format(mood=mood, bpm=ideal_bpm)

    def _infer_mood(self, theme: str) -> str:
        """从主题推断情绪"""
        # 关键词映射
        mood_keywords = {
            "epic": ["战斗", "战士", "英雄", "battle", "hero", "warrior", "fight"],
            "emotional": ["爱", "思念", "回忆", "love", "memory", "miss"],
            "energetic": ["燃", "热血", "奔跑", "energy", "run", "fire"],
            "mysterious": ["神秘", "黑暗", "宇宙", "mystery", "dark", "cosmos"],
            "triumphant": ["胜利", "觉醒", "崛起", "victory", "awaken", "rise"],
        }

        theme_lower = theme.lower()
        for mood, keywords in mood_keywords.items():
            if any(kw in theme_lower for kw in keywords):
                return mood

        return "epic"  # 默认

    def _generate_scenes(
        self,
        title: str,
        theme: str,
        lyrics: List[str],
        duration: int,
        custom_prompts: Dict[str, str],
    ) -> List[Dict]:
        """根据模板结构生成场景列表"""
        scenes = []
        structure = self.template.get("structure", {})
        sections = structure.get("sections", [])

        # 计算时间比例
        total_template_duration = structure.get("total_duration", 55)
        time_scale = duration / total_template_duration

        current_time = 0
        scene_index = 0
        lyric_index = 0

        for section in sections:
            section_duration = section["duration"] * time_scale
            section_type = section["type"]
            scene_count = section.get("scene_count", 1)

            # 分配场景时长
            scene_duration = section_duration / scene_count

            for i in range(scene_count):
                scene_id = f"{section_type}_{scene_index}"
                start_time = current_time
                end_time = current_time + scene_duration

                # 生成场景
                scene = self._create_scene(
                    scene_id=scene_id,
                    start=round(start_time, 2),
                    end=round(end_time, 2),
                    section=section,
                    theme=theme,
                    title=title if section.get("scene_type") == "title" else None,
                    lyrics=lyrics[lyric_index] if lyric_index < len(lyrics) else None,
                    custom_prompt=custom_prompts.get(scene_id),
                    scene_index_in_section=i,
                )
                scenes.append(scene)

                current_time = end_time
                scene_index += 1

                # 推进歌词
                if section.get("scene_type") == "action" and lyric_index < len(lyrics):
                    lyric_index += 1

        return scenes

    def _create_scene(
        self,
        scene_id: str,
        start: float,
        end: float,
        section: Dict,
        theme: str,
        title: Optional[str],
        lyrics: Optional[str],
        custom_prompt: Optional[str],
        scene_index_in_section: int,
    ) -> Dict:
        """创建单个场景"""
        scene_type = section.get("scene_type", "action")

        # 选择动画
        animations = section.get("animations", [section.get("animation", "none")])
        animation = animations[scene_index_in_section % len(animations)] if animations else "none"

        # 选择转场
        transitions = section.get("transitions", [section.get("transition", "none")])
        transition = transitions[scene_index_in_section % len(transitions)] if transitions else "none"

        # 生成视觉提示词
        visual_prompt = custom_prompt or self._generate_visual_prompt(
            section_type=section["type"],
            theme=theme,
        )

        # 生成搜索关键词
        stock_keywords = self._generate_stock_keywords(section["type"], theme)

        scene = {
            "id": scene_id,
            "start": start,
            "end": end,
            "type": scene_type,
            "visual": {
                "source": "auto",
                "prompt": visual_prompt,
                "stock_keywords": stock_keywords,
                "quality_priority": "high",
                "allow_ai_fallback": True,
                "file": None,
            },
            "animation": animation,
            "transition": transition,
            "beat_sync": section.get("beat_sync", False),
        }

        # 添加内容
        content = {}
        if title and scene_type == "title":
            content["text"] = title
            content["subtitle"] = self._generate_subtitle(title)
        if lyrics:
            content["lyrics"] = lyrics

        if content:
            scene["content"] = content

        return scene

    def _generate_visual_prompt(self, section_type: str, theme: str) -> str:
        """生成视觉提示词"""
        scene_prompts = self.template.get("scene_prompts", {})
        style_suffix = self.template.get("visual_style", {}).get("ai_prompt_suffix", "")

        # 映射 section_type 到 prompt 类别
        prompt_category_map = {
            "intro": "intro",
            "buildup": "hero",
            "climax": "battle",
            "bridge": "emotional",
            "finale": "victory",
        }
        category = prompt_category_map.get(section_type, "hero")

        # 从模板选择基础提示词
        prompts = scene_prompts.get(category, [])
        base_prompt = random.choice(prompts) if prompts else f"{theme}, dramatic scene"

        # 组合最终提示词
        return f"{base_prompt}, {theme}, {style_suffix}"

    def _generate_stock_keywords(self, section_type: str, theme: str) -> List[str]:
        """生成素材库搜索关键词"""
        base_keywords = self.template.get("visual_style", {}).get("stock_keywords", [])

        # 根据 section_type 添加特定关键词
        section_keywords = {
            "intro": ["cosmos", "galaxy", "title", "opening"],
            "buildup": ["hero", "warrior", "rising", "energy"],
            "climax": ["battle", "explosion", "action", "impact"],
            "bridge": ["peaceful", "stars", "emotional", "hope"],
            "finale": ["victory", "sunrise", "triumphant", "ending"],
        }

        specific_keywords = section_keywords.get(section_type, [])

        # 合并并去重
        all_keywords = list(set(base_keywords[:3] + specific_keywords[:3]))
        return all_keywords[:5]

    def _generate_subtitle(self, title: str) -> str:
        """生成英文副标题"""
        # 简单的中文到英文关键词映射
        translations = {
            "觉醒": "AWAKENING",
            "战斗": "BATTLE",
            "宇宙": "COSMOS",
            "星": "STAR",
            "火": "FIRE",
            "光": "LIGHT",
            "力量": "POWER",
            "英雄": "HERO",
            "梦": "DREAM",
        }

        for cn, en in translations.items():
            if cn in title:
                return en

        return "THE BEGINNING"

    def to_yaml(self, storyboard: Dict) -> str:
        """将分镜脚本转换为 YAML 字符串"""
        return yaml.dump(storyboard, allow_unicode=True, default_flow_style=False)

    def to_json(self, storyboard: Dict) -> str:
        """将分镜脚本转换为 JSON 字符串"""
        return json.dumps(storyboard, ensure_ascii=False, indent=2)

    def save(self, storyboard: Dict, output_path: Path, format: str = "yaml") -> Path:
        """保存分镜脚本到文件"""
        if format == "yaml":
            content = self.to_yaml(storyboard)
            suffix = ".yaml"
        else:
            content = self.to_json(storyboard)
            suffix = ".json"

        output_file = output_path.with_suffix(suffix)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        return output_file


def generate_storyboard(
    title: str,
    theme: str,
    style: str = "anime-hype",
    lyrics: Optional[List[str]] = None,
    duration: int = 55,
) -> Dict:
    """
    便捷函数：生成分镜脚本

    Args:
        title: MV 标题
        theme: 主题描述
        style: 风格模板名称
        lyrics: 歌词列表
        duration: 总时长

    Returns:
        分镜脚本字典
    """
    generator = StoryboardGenerator(style=style)
    return generator.generate(
        title=title,
        theme=theme,
        lyrics=lyrics,
        duration=duration,
    )
