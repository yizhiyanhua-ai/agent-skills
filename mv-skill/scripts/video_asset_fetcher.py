"""
视频素材获取器 - 严格筛选演唱会/DJ/Club 视频
使用 media-downloader skill 下载高质量视频素材
"""
import subprocess
import sys
import random
from pathlib import Path
from typing import Dict, List, Optional

from .config import CACHE_DIR, MEDIA_DOWNLOADER_DIR


class VideoAssetFetcher:
    """视频素材获取器 - 严格限制为演唱会、DJ、Club 场景"""

    # 严格筛选的视频关键词 - 只保留演唱会/DJ/Club 相关
    DJ_VIDEO_KEYWORDS = {
        # 演唱会场景 - 最高优先级
        "concert": [
            "concert",
            "live concert",
            "rock concert",
            "music concert",
            "stage performance",
            "live music",
            "live show",
            "concert crowd",
            "concert stage",
        ],
        # DJ 打碟场景 - 最高优先级
        "dj": [
            "dj",
            "dj set",
            "dj mixing",
            "dj booth",
            "turntable",
            "edm dj",
            "electronic dj",
            "club dj",
        ],
        # 夜店 Club 场景 - 最高优先级
        "club": [
            "nightclub",
            "club",
            "night club",
            "dance club",
            "club party",
            "club dancing",
            "disco club",
            "club lights",
        ],
        # 音乐节场景
        "festival": [
            "music festival",
            "edm festival",
            "rave",
            "festival crowd",
            "festival stage",
            "outdoor concert",
        ],
        # 舞台灯光（演唱会/Club 相关）
        "stage_lights": [
            "stage lights",
            "concert lights",
            "club lights",
            "disco lights",
            "stage lighting",
            "concert lighting",
        ],
        # 激光秀（演唱会/Club 相关）
        "laser": [
            "laser show",
            "concert laser",
            "club laser",
            "laser lights",
            "stage laser",
        ],
        # 人群（演唱会/Club 相关）
        "crowd": [
            "concert crowd",
            "club crowd",
            "festival crowd",
            "dancing crowd",
            "party crowd",
            "rave crowd",
        ],
        # 舞池/舞蹈
        "dancing": [
            "dance floor",
            "club dancing",
            "party dancing",
            "disco dancing",
            "rave dancing",
        ],
    }

    # 备用关键词 - 仍然限制在演唱会/DJ/Club 范围
    FALLBACK_KEYWORDS = [
        "concert",
        "dj",
        "nightclub",
        "club",
        "live music",
        "stage",
        "festival",
        "disco",
        "rave",
        "party",
    ]

    def __init__(self):
        self.cache_dir = CACHE_DIR / "video_assets"
        self.cache_dir.mkdir(exist_ok=True)
        self.downloaded_videos: Dict[str, str] = {}
        self.failed_keywords: set = set()
        self._check_dependencies()

    def _check_dependencies(self):
        """检查 media-downloader 是否可用"""
        self.cli_path = MEDIA_DOWNLOADER_DIR / "media_cli.py"
        if not self.cli_path.exists():
            raise RuntimeError("media-downloader skill 未安装")

    def fetch_video(
        self,
        category: str,
        scene_id: str,
        duration: float = 10,
        retry_count: int = 5,  # 增加重试次数
    ) -> Optional[str]:
        """
        获取指定类别的视频素材，带重试机制

        Args:
            category: 视频类别
            scene_id: 场景 ID
            duration: 期望的视频时长（秒）
            retry_count: 重试次数

        Returns:
            视频文件路径，失败返回 None
        """
        # 获取关键词列表
        keywords = self.DJ_VIDEO_KEYWORDS.get(category, []).copy()
        if not keywords:
            keywords = self.FALLBACK_KEYWORDS.copy()

        # 过滤掉已失败的关键词
        available_keywords = [k for k in keywords if k not in self.failed_keywords]
        if not available_keywords:
            # 如果所有关键词都失败了，从备用列表中选择
            available_keywords = [k for k in self.FALLBACK_KEYWORDS if k not in self.failed_keywords]
        if not available_keywords:
            available_keywords = self.FALLBACK_KEYWORDS.copy()

        # 随机打乱顺序
        random.shuffle(available_keywords)

        output_dir = self.cache_dir / scene_id
        output_dir.mkdir(exist_ok=True)

        # 尝试多个关键词
        for attempt, keyword in enumerate(available_keywords[:retry_count]):
            # 检查缓存
            cache_key = f"{keyword.replace(' ', '_')}"
            if cache_key in self.downloaded_videos:
                cached = self.downloaded_videos[cache_key]
                if Path(cached).exists():
                    print(f"[VideoFetcher] 使用缓存: {Path(cached).name}")
                    return cached

            print(f"[VideoFetcher] 搜索 ({attempt+1}/{retry_count}): {keyword}")

            video_path = self._download_video(keyword, output_dir, duration)
            if video_path:
                self.downloaded_videos[cache_key] = video_path
                return video_path
            else:
                self.failed_keywords.add(keyword)

        return None

    def _download_video(
        self,
        keyword: str,
        output_dir: Path,
        duration: float,
    ) -> Optional[str]:
        """执行视频下载"""
        cmd = [
            sys.executable,
            str(self.cli_path),
            "video",
            keyword,
            "-n", "1",
            "-o", str(output_dir),
            "-d", str(int(duration + 10)),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                video_files = list(output_dir.glob("*.mp4")) + list(output_dir.glob("*.webm"))
                if video_files:
                    video_path = str(max(video_files, key=lambda p: p.stat().st_mtime))
                    print(f"[VideoFetcher] ✅ 下载成功: {Path(video_path).name}")
                    return video_path

            return None

        except subprocess.TimeoutExpired:
            print(f"[VideoFetcher] ⏱️ 超时: {keyword}")
            return None
        except Exception as e:
            print(f"[VideoFetcher] ❌ 错误: {e}")
            return None

    def fetch_videos_for_scenes(
        self,
        scenes: List[Dict],
        progress_callback=None,
    ) -> Dict[str, str]:
        """为多个场景获取视频素材"""
        results = {}
        total = len(scenes)

        # 严格的场景类别轮换 - 只使用演唱会/DJ/Club 相关
        category_rotation = [
            "concert",      # 演唱会
            "dj",           # DJ 打碟
            "club",         # 夜店
            "stage_lights", # 舞台灯光
            "crowd",        # 人群
            "laser",        # 激光秀
            "festival",     # 音乐节
            "dancing",      # 舞池
        ]

        for i, scene in enumerate(scenes):
            scene_id = scene.get("id", f"scene_{i}")

            if progress_callback:
                progress_callback(i + 1, total, scene_id)

            # 按顺序轮换类别
            category = category_rotation[i % len(category_rotation)]

            duration = scene.get("end", 10) - scene.get("start", 0)

            video_path = self.fetch_video(
                category=category,
                scene_id=scene_id,
                duration=duration,
                retry_count=5,
            )

            if video_path:
                results[scene_id] = video_path
                print(f"[{i+1}/{total}] {scene_id}: ✅ {Path(video_path).name}")
            else:
                # 如果失败，尝试使用已下载的视频
                if self.downloaded_videos:
                    fallback = random.choice(list(self.downloaded_videos.values()))
                    results[scene_id] = fallback
                    print(f"[{i+1}/{total}] {scene_id}: 🔄 使用备用视频")
                else:
                    results[scene_id] = None
                    print(f"[{i+1}/{total}] {scene_id}: ❌ 获取失败")

        # 统计成功率
        success_count = sum(1 for v in results.values() if v)
        print(f"\n[VideoFetcher] 视频获取完成: {success_count}/{total} 成功")

        return results
