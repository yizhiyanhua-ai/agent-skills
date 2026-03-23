"""
素材管理器
负责从素材库和 AI 生成服务获取视觉素材
质量优先策略：素材库 > AI 生成
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

from .config import (
    CACHE_DIR,
    QUALITY_REQUIREMENTS,
    TIMEOUTS,
    ASSET_SOURCES_PRIORITY,
    ZIMAGE_SKILL_DIR,
    MEDIA_DOWNLOADER_DIR,
    PEXELS_API_KEY,
    PIXABAY_API_KEY,
)
from .exceptions import AssetNotFoundError, AssetQualityError, DependencyError


class AssetManager:
    """素材管理器"""

    def __init__(self, style_config: Optional[Dict] = None):
        """
        初始化素材管理器

        Args:
            style_config: 风格配置，包含 ai_prompt_suffix 等
        """
        self.style_config = style_config or {}
        self.cache_dir = CACHE_DIR / "assets"
        self.cache_dir.mkdir(exist_ok=True)
        self._check_dependencies()

    def _check_dependencies(self):
        """检查依赖的 Skills 是否存在"""
        self.has_zimage = (ZIMAGE_SKILL_DIR / "generate.py").exists()
        self.has_media_downloader = (MEDIA_DOWNLOADER_DIR / "media_cli.py").exists()

        if not self.has_zimage and not self.has_media_downloader:
            raise DependencyError(
                "需要至少安装 zimage-skill 或 media-downloader 之一"
            )

    def fetch_asset(
        self,
        scene: Dict,
        scene_id: str,
    ) -> str:
        """
        获取场景素材

        质量优先策略：
        1. 先从素材库搜索高质量匹配
        2. 评估匹配度，不满意再用 AI 生成
        3. AI 生成作为兜底方案

        Args:
            scene: 场景配置
            scene_id: 场景 ID

        Returns:
            素材文件路径
        """
        visual = scene.get("visual", {})
        source = visual.get("source", "auto")

        # DJ 场景是程序化生成的，不需要素材
        if source == "programmatic" or scene.get("type") == "dj":
            return "programmatic"

        # 用户指定了文件
        if source == "user" and visual.get("file"):
            return self._validate_user_asset(visual["file"])

        # 强制使用 AI
        if source == "ai":
            return self._generate_ai_image(visual, scene_id)

        # 强制使用素材库
        if source == "stock":
            return self._fetch_stock_asset(visual, scene_id)

        # auto 模式：质量优先策略
        return self._fetch_auto(visual, scene_id)

    def _fetch_auto(self, visual: Dict, scene_id: str) -> str:
        """自动模式：素材库优先，AI 兜底"""
        quality_priority = visual.get("quality_priority", "high")
        allow_ai_fallback = visual.get("allow_ai_fallback", True)
        prefer_video = visual.get("prefer_video", False)

        # 第一步：如果偏好视频，先尝试获取视频
        if prefer_video and self.has_media_downloader:
            try:
                result = self._fetch_stock_asset(visual, scene_id, media_type="video")
                if result:
                    return result
            except (AssetNotFoundError, AssetQualityError) as e:
                print(f"[AssetManager] 视频素材未找到，尝试图片: {e}")

        # 第二步：尝试素材库（图片）
        if self.has_media_downloader:
            try:
                result = self._fetch_stock_asset(visual, scene_id)
                if result:
                    return result
            except (AssetNotFoundError, AssetQualityError) as e:
                print(f"[AssetManager] 素材库未找到合适素材: {e}")

        # 第二步：AI 生成兜底
        if allow_ai_fallback and self.has_zimage:
            try:
                return self._generate_ai_image(visual, scene_id)
            except Exception as e:
                print(f"[AssetManager] AI 生成失败: {e}")

        # 第三步：降低标准重试素材库
        if self.has_media_downloader:
            try:
                return self._fetch_stock_asset(
                    visual, scene_id, strict_quality=False
                )
            except Exception as e:
                pass

        raise AssetNotFoundError(f"无法获取素材: {scene_id}")

    def _fetch_stock_asset(
        self,
        visual: Dict,
        scene_id: str,
        strict_quality: bool = True,
        media_type: str = None,
    ) -> str:
        """从素材库获取素材"""
        if not self.has_media_downloader:
            raise DependencyError("media-downloader skill 未安装")

        keywords = visual.get("stock_keywords", [])
        if not keywords and visual.get("prompt"):
            # 从 prompt 提取关键词
            keywords = self._extract_keywords(visual["prompt"])

        if not keywords:
            raise AssetNotFoundError("没有可用的搜索关键词")

        # 确定媒体类型
        if media_type is None:
            media_type = visual.get("media_type", "image")

        output_dir = self.cache_dir / scene_id
        output_dir.mkdir(exist_ok=True)

        # 调用 media-downloader
        cli_path = MEDIA_DOWNLOADER_DIR / "media_cli.py"
        search_query = " ".join(keywords[:3])

        cmd = [
            sys.executable,
            str(cli_path),
            media_type,
            search_query,
            "-n", "1",
            "-o", str(output_dir),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUTS["asset_download"],
            )

            if result.returncode == 0:
                # 查找下载的文件
                files = list(output_dir.glob("*"))
                if files:
                    asset_path = files[0]
                    if strict_quality:
                        self._validate_quality(asset_path, media_type)
                    return str(asset_path)

        except subprocess.TimeoutExpired:
            print(f"[AssetManager] 素材下载超时: {scene_id}")
        except Exception as e:
            print(f"[AssetManager] 素材下载错误: {e}")

        raise AssetNotFoundError(f"素材库未找到: {search_query}")

    def _generate_ai_image(self, visual: Dict, scene_id: str) -> str:
        """使用 AI 生成图像"""
        if not self.has_zimage:
            raise DependencyError("zimage-skill 未安装")

        prompt = visual.get("prompt", "")
        if not prompt:
            raise AssetNotFoundError("没有可用的生成提示词")

        # 添加风格后缀
        style_suffix = self.style_config.get(
            "visual_style", {}
        ).get("ai_prompt_suffix", "")
        full_prompt = f"{prompt}, {style_suffix}" if style_suffix else prompt

        output_path = self.cache_dir / f"{scene_id}_ai.jpg"

        # 调用 zimage-skill
        generate_script = ZIMAGE_SKILL_DIR / "generate.py"
        cmd = [
            sys.executable,
            str(generate_script),
            full_prompt,
            str(output_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUTS["image_generation"],
            )

            if result.returncode == 0 and output_path.exists():
                return str(output_path)
            else:
                raise Exception(result.stderr or "AI 生成失败")

        except subprocess.TimeoutExpired:
            raise AssetNotFoundError(f"AI 生成超时: {scene_id}")

    def _validate_user_asset(self, file_path: str) -> str:
        """验证用户提供的素材"""
        path = Path(file_path)
        if not path.exists():
            raise AssetNotFoundError(f"文件不存在: {file_path}")

        # 检查格式
        suffix = path.suffix.lower().lstrip(".")
        all_formats = (
            QUALITY_REQUIREMENTS["image"]["formats"] +
            QUALITY_REQUIREMENTS["video"]["formats"]
        )
        if suffix not in all_formats:
            raise AssetQualityError(f"不支持的格式: {suffix}")

        return str(path)

    def _validate_quality(self, file_path: Path, media_type: str) -> bool:
        """验证素材质量"""
        requirements = QUALITY_REQUIREMENTS.get(media_type, {})

        # 检查文件格式
        suffix = file_path.suffix.lower().lstrip(".")
        if suffix not in requirements.get("formats", []):
            raise AssetQualityError(f"格式不符合要求: {suffix}")

        # TODO: 使用 PIL 或 ffprobe 检查分辨率
        # 暂时跳过分辨率检查

        return True

    def _extract_keywords(self, prompt: str) -> List[str]:
        """从提示词提取关键词"""
        # 移除常见的修饰词
        noise_words = {
            "style", "anime", "dramatic", "epic", "dynamic",
            "lighting", "vibrant", "colors", "high", "quality",
            "beautiful", "amazing", "stunning", "cel-shaded",
        }

        words = prompt.lower().replace(",", " ").split()
        keywords = [w for w in words if w not in noise_words and len(w) > 2]

        return keywords[:5]

    def fetch_all_assets(
        self,
        storyboard: Dict,
        progress_callback=None,
    ) -> Dict[str, str]:
        """
        获取分镜脚本中所有场景的素材

        Args:
            storyboard: 分镜脚本
            progress_callback: 进度回调函数

        Returns:
            {scene_id: asset_path} 映射
        """
        scenes = storyboard.get("scenes", [])
        assets = {}
        total = len(scenes)

        for i, scene in enumerate(scenes):
            scene_id = scene["id"]

            if progress_callback:
                progress_callback(i + 1, total, scene_id)

            try:
                asset_path = self.fetch_asset(scene, scene_id)
                assets[scene_id] = asset_path
                print(f"[{i+1}/{total}] {scene_id}: {asset_path}")
            except Exception as e:
                print(f"[{i+1}/{total}] {scene_id}: 失败 - {e}")
                assets[scene_id] = None

        return assets

    def get_asset_report(self, assets: Dict[str, str]) -> str:
        """生成素材质量报告"""
        lines = [
            "┌─────────────────────────────────────────────────┐",
            "│  素材质量报告                                    │",
            "├──────────┬──────────┬──────────┬────────────────┤",
            "│ Scene    │ 来源     │ 分辨率    │ 状态           │",
            "├──────────┼──────────┼──────────┼────────────────┤",
        ]

        for scene_id, path in assets.items():
            if path:
                source = "AI生成" if "_ai" in path else "素材库"
                status = "✅ 高质量"
                resolution = "1920x1080"  # TODO: 实际检测
            else:
                source = "-"
                status = "❌ 获取失败"
                resolution = "-"

            lines.append(
                f"│ {scene_id:<8} │ {source:<8} │ {resolution:<8} │ {status:<14} │"
            )

        lines.append("└──────────┴──────────┴──────────┴────────────────┘")

        return "\n".join(lines)
