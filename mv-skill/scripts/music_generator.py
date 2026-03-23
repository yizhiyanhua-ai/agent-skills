"""
音乐生成器
集成 Suno API 生成音乐，支持本地音乐分析
"""
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests

from .config import CACHE_DIR, SUNO_API_KEY, TIMEOUTS
from .exceptions import MusicGenerationError, DependencyError


class MusicGenerator:
    """音乐生成器"""

    def __init__(self):
        self.cache_dir = CACHE_DIR / "music"
        self.cache_dir.mkdir(exist_ok=True)
        self.api_key = SUNO_API_KEY

    def generate(
        self,
        prompt: str,
        duration: int = 55,
        title: str = "mv_music",
    ) -> Dict:
        """
        生成音乐

        Args:
            prompt: 音乐描述提示词
            duration: 目标时长（秒）
            title: 音乐标题

        Returns:
            {
                "file": 音乐文件路径,
                "bpm": 检测到的 BPM,
                "beats": 节拍时间点列表,
                "duration": 实际时长
            }
        """
        if not self.api_key:
            raise MusicGenerationError(
                "SUNO_API_KEY 未配置。请设置环境变量或使用本地音乐文件。"
            )

        try:
            # 调用 Suno API
            music_file = self._call_suno_api(prompt, duration, title)

            # 分析节拍
            bpm, beats = self._analyze_beats(music_file)

            return {
                "file": str(music_file),
                "bpm": bpm,
                "beats": beats,
                "duration": self._get_duration(music_file),
            }

        except Exception as e:
            raise MusicGenerationError(f"音乐生成失败: {e}")

    def _call_suno_api(
        self,
        prompt: str,
        duration: int,
        title: str,
    ) -> Path:
        """调用 Suno API 生成音乐"""
        # TODO: 实现真正的 Suno API 调用
        # 目前 Suno 没有官方公开 API，可能需要使用第三方封装

        # 占位实现：提示用户使用本地文件
        raise MusicGenerationError(
            "Suno API 调用暂未实现。请使用本地音乐文件：\n"
            "  - 提供音乐路径：'使用这个音乐 /path/to/music.mp3'\n"
            "  - 或配置 SUNO_API_KEY 环境变量"
        )

    def analyze_local_music(self, music_path: str) -> Dict:
        """
        分析本地音乐文件

        Args:
            music_path: 音乐文件路径

        Returns:
            {
                "file": 音乐文件路径,
                "bpm": 检测到的 BPM,
                "beats": 节拍时间点列表,
                "duration": 时长
            }
        """
        path = Path(music_path).resolve()
        if not path.exists():
            raise MusicGenerationError(f"音乐文件不存在: {music_path}")

        # 检查格式
        valid_formats = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
        if path.suffix.lower() not in valid_formats:
            raise MusicGenerationError(
                f"不支持的音乐格式: {path.suffix}，支持: {valid_formats}"
            )

        # 分析节拍
        bpm, beats = self._analyze_beats(path)
        duration = self._get_duration(path)

        return {
            "file": str(path),
            "bpm": bpm,
            "beats": beats,
            "duration": duration,
        }

    def _analyze_beats(self, music_path: Path) -> Tuple[int, List[float]]:
        """
        分析音乐节拍

        使用 librosa 进行节拍检测

        Returns:
            (bpm, [beat_times])
        """
        try:
            import librosa
            import numpy as np

            # 加载音频
            y, sr = librosa.load(str(music_path), sr=22050)

            # 检测节拍
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)

            # tempo 可能是数组
            bpm = int(float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo))

            return bpm, beat_times.tolist()

        except ImportError:
            print("[MusicGenerator] librosa 未安装，使用估算 BPM")
            return self._estimate_bpm_fallback(music_path)

        except Exception as e:
            print(f"[MusicGenerator] 节拍分析错误: {e}")
            return self._estimate_bpm_fallback(music_path)

    def _estimate_bpm_fallback(self, music_path: Path) -> Tuple[int, List[float]]:
        """
        备用 BPM 估算方法

        当 librosa 不可用时使用
        """
        duration = self._get_duration(music_path)
        # 假设 120 BPM
        default_bpm = 120
        beat_interval = 60.0 / default_bpm

        beats = []
        t = 0.0
        while t < duration:
            beats.append(round(t, 3))
            t += beat_interval

        return default_bpm, beats

    def _get_duration(self, music_path: Path) -> float:
        """获取音乐时长（秒）"""
        try:
            # 使用 ffprobe 获取时长
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "json",
                str(music_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return float(data["format"]["duration"])

        except Exception as e:
            print(f"[MusicGenerator] ffprobe 错误: {e}")

        # 备用方案：使用 pydub
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(music_path))
            return len(audio) / 1000.0
        except ImportError:
            pass

        # 最后备用：假设 60 秒
        return 60.0

    def align_scenes_to_beats(
        self,
        scenes: List[Dict],
        beats: List[float],
        beat_sync_ratio: float = 0.7,
    ) -> List[Dict]:
        """
        将场景切点对齐到节拍

        Args:
            scenes: 场景列表
            beats: 节拍时间点
            beat_sync_ratio: 需要对齐的场景比例

        Returns:
            调整后的场景列表
        """
        if not beats:
            return scenes

        aligned_scenes = []

        for i, scene in enumerate(scenes):
            scene = scene.copy()

            # 根据 beat_sync 标记决定是否对齐
            if scene.get("beat_sync", False):
                # 找最近的节拍点
                scene["start"] = self._find_nearest_beat(scene["start"], beats)

                if i < len(scenes) - 1:
                    # 调整结束时间为下一场景开始
                    pass  # 在下一轮处理

            aligned_scenes.append(scene)

        # 修正结束时间
        for i in range(len(aligned_scenes) - 1):
            aligned_scenes[i]["end"] = aligned_scenes[i + 1]["start"]

        return aligned_scenes

    def _find_nearest_beat(self, time: float, beats: List[float]) -> float:
        """找到最近的节拍点"""
        if not beats:
            return time

        nearest = min(beats, key=lambda b: abs(b - time))
        return nearest


def analyze_music(music_path: str) -> Dict:
    """
    便捷函数：分析本地音乐

    Args:
        music_path: 音乐文件路径

    Returns:
        音乐分析结果
    """
    generator = MusicGenerator()
    return generator.analyze_local_music(music_path)
