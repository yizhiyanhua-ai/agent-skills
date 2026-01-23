"""
预览生成器
生成分镜预览图，供用户确认后再渲染
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from io import BytesIO

from .config import CACHE_DIR, OUTPUT_DIR
from .exceptions import MVSkillError


class PreviewGenerator:
    """预览生成器"""

    def __init__(self):
        self.preview_dir = CACHE_DIR / "previews"
        self.preview_dir.mkdir(exist_ok=True)

    def generate_storyboard_preview(
        self,
        storyboard: Dict,
        assets: Dict[str, str],
    ) -> str:
        """
        生成分镜预览板

        Args:
            storyboard: 分镜脚本
            assets: {scene_id: asset_path} 素材映射

        Returns:
            预览图路径或文本预览
        """
        scenes = storyboard.get("scenes", [])
        title = storyboard.get("meta", {}).get("title", "MV")

        # 生成文本预览
        text_preview = self._generate_text_preview(title, scenes, assets)

        # 尝试生成图像预览
        try:
            image_preview = self._generate_image_preview(title, scenes, assets)
            if image_preview:
                return image_preview
        except Exception as e:
            print(f"[PreviewGenerator] 图像预览生成失败: {e}")

        return text_preview

    def _generate_text_preview(
        self,
        title: str,
        scenes: List[Dict],
        assets: Dict[str, str],
    ) -> str:
        """生成文本格式的分镜预览"""
        lines = [
            f"┌{'─' * 60}┐",
            f"│  分镜预览 - {title:<46} │",
            f"├{'─' * 60}┤",
        ]

        # 场景行
        scene_headers = []
        scene_times = []
        scene_types = []
        scene_anims = []
        scene_sources = []

        for scene in scenes:
            scene_id = scene["id"]
            start = scene["start"]
            end = scene["end"]
            animation = scene.get("animation", "none")

            # 获取素材来源
            asset_path = assets.get(scene_id)
            if asset_path:
                source = "AI" if "_ai" in str(asset_path) else "Stock"
            else:
                source = "N/A"

            # 简化场景名称
            short_name = scene_id[:10] if len(scene_id) > 10 else scene_id

            scene_headers.append(f" {short_name:<10}")
            scene_times.append(f" {start:.0f}-{end:.0f}s".ljust(11))
            scene_types.append(f" {scene.get('type', 'action'):<10}")
            scene_anims.append(f" {animation[:10]:<10}")
            scene_sources.append(f" [{source}]".ljust(11))

        # 每行最多显示 5 个场景
        chunks = self._chunk_list(list(range(len(scenes))), 5)

        for chunk in chunks:
            lines.append("├" + "┬".join(["─" * 11] * len(chunk)) + "┤")
            lines.append("│" + "│".join([scene_headers[i] for i in chunk]) + "│")
            lines.append("│" + "│".join([scene_times[i] for i in chunk]) + "│")
            lines.append("│" + "│".join([scene_anims[i] for i in chunk]) + "│")
            lines.append("│" + "│".join([scene_sources[i] for i in chunk]) + "│")

        lines.append(f"└{'─' * 60}┘")
        lines.append("")
        lines.append("操作选项：")
        lines.append("  [确认] - 开始渲染")
        lines.append("  [修改 Scene X] - 修改指定场景")
        lines.append("  [重新生成 Scene X] - 重新生成指定场景素材")

        return "\n".join(lines)

    def _generate_image_preview(
        self,
        title: str,
        scenes: List[Dict],
        assets: Dict[str, str],
    ) -> Optional[str]:
        """生成图像格式的分镜预览"""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            return None

        # 设置尺寸
        thumb_width = 200
        thumb_height = 356  # 9:16 比例
        padding = 20
        cols = min(len(scenes), 6)
        rows = (len(scenes) + cols - 1) // cols

        canvas_width = cols * thumb_width + (cols + 1) * padding
        canvas_height = rows * (thumb_height + 60) + padding * 2 + 80  # 60 for labels, 80 for title

        # 创建画布
        canvas = Image.new("RGB", (canvas_width, canvas_height), "#1a1a1a")
        draw = ImageDraw.Draw(canvas)

        # 尝试加载字体
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 16)
            title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
        except:
            font = ImageFont.load_default()
            title_font = font

        # 绘制标题
        draw.text(
            (canvas_width // 2, 30),
            f"分镜预览 - {title}",
            fill="#ffffff",
            font=title_font,
            anchor="mm",
        )

        # 绘制场景缩略图
        for i, scene in enumerate(scenes):
            col = i % cols
            row = i // cols

            x = padding + col * (thumb_width + padding)
            y = 80 + row * (thumb_height + 60 + padding)

            # 绘制边框
            draw.rectangle(
                [x - 2, y - 2, x + thumb_width + 2, y + thumb_height + 2],
                outline="#444444",
                width=2,
            )

            # 加载并绘制缩略图
            asset_path = assets.get(scene["id"])
            if asset_path and Path(asset_path).exists():
                try:
                    img = Image.open(asset_path)
                    img = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                    canvas.paste(img, (x, y))
                except Exception as e:
                    # 绘制占位符
                    draw.rectangle([x, y, x + thumb_width, y + thumb_height], fill="#333333")
                    draw.text(
                        (x + thumb_width // 2, y + thumb_height // 2),
                        "加载失败",
                        fill="#666666",
                        font=font,
                        anchor="mm",
                    )
            else:
                # 绘制占位符
                draw.rectangle([x, y, x + thumb_width, y + thumb_height], fill="#333333")
                draw.text(
                    (x + thumb_width // 2, y + thumb_height // 2),
                    "待获取",
                    fill="#666666",
                    font=font,
                    anchor="mm",
                )

            # 绘制标签
            label_y = y + thumb_height + 5
            scene_id_short = scene["id"][:12]
            time_range = f"{scene['start']:.0f}-{scene['end']:.0f}s"
            animation = scene.get("animation", "none")[:10]

            draw.text((x, label_y), scene_id_short, fill="#ffffff", font=font)
            draw.text((x, label_y + 18), time_range, fill="#888888", font=font)
            draw.text((x, label_y + 36), animation, fill="#666666", font=font)

        # 保存预览图
        preview_path = self.preview_dir / f"{title}_preview.png"
        canvas.save(preview_path)

        return str(preview_path)

    def _chunk_list(self, lst: List, chunk_size: int) -> List[List]:
        """将列表分块"""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    def generate_asset_report(
        self,
        assets: Dict[str, str],
        storyboard: Dict,
    ) -> str:
        """生成素材质量报告"""
        scenes = storyboard.get("scenes", [])

        lines = [
            "┌─────────────────────────────────────────────────┐",
            "│  素材质量报告                                    │",
            "├──────────────┬──────────┬────────────────────────┤",
            "│ Scene        │ 来源     │ 状态                   │",
            "├──────────────┼──────────┼────────────────────────┤",
        ]

        success_count = 0
        fail_count = 0

        for scene in scenes:
            scene_id = scene["id"]
            asset_path = assets.get(scene_id)

            if asset_path and Path(asset_path).exists():
                source = "AI生成" if "_ai" in str(asset_path) else "素材库"
                status = "✅ 已获取"
                success_count += 1
            else:
                source = "-"
                status = "❌ 获取失败"
                fail_count += 1

            lines.append(
                f"│ {scene_id:<12} │ {source:<8} │ {status:<22} │"
            )

        lines.append("├──────────────┴──────────┴────────────────────────┤")
        lines.append(f"│  成功: {success_count}  失败: {fail_count}".ljust(49) + "│")
        lines.append("└─────────────────────────────────────────────────┘")

        return "\n".join(lines)


def generate_preview(storyboard: Dict, assets: Dict[str, str]) -> str:
    """
    便捷函数：生成预览

    Args:
        storyboard: 分镜脚本
        assets: 素材映射

    Returns:
        预览内容（路径或文本）
    """
    generator = PreviewGenerator()
    return generator.generate_storyboard_preview(storyboard, assets)
