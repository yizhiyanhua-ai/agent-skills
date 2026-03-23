"""
音乐合并器
合并多个音乐片段为单个文件，支持交叉淡化
"""
import subprocess
from pathlib import Path
from typing import List, Optional

from .config import CACHE_DIR
from .exceptions import MusicGenerationError


class MusicMerger:
    """音乐合并器"""

    def __init__(self):
        self.cache_dir = CACHE_DIR / "merged"
        self.cache_dir.mkdir(exist_ok=True)

    def merge(
        self,
        segments: List[str],
        output_name: str = "medley",
        crossfade: float = 0.5,
    ) -> str:
        """
        合并多个音乐片段

        Args:
            segments: 音乐片段文件路径列表
            output_name: 输出文件名
            crossfade: 交叉淡化时长（秒）

        Returns:
            合并后的文件路径
        """
        if not segments:
            raise MusicGenerationError("没有音乐片段可合并")

        if len(segments) == 1:
            # 只有一个片段，直接返回
            return segments[0]

        output_path = self.cache_dir / f"{output_name}.mp3"

        # 使用 ffmpeg 的 concat 滤镜合并
        # 构建复杂滤镜图
        filter_complex = self._build_crossfade_filter(len(segments), crossfade)

        # 构建输入参数
        input_args = []
        for seg in segments:
            input_args.extend(["-i", str(seg)])

        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-acodec", "libmp3lame",
            "-q:a", "2",
            str(output_path),
        ]

        try:
            print(f"[MusicMerger] 合并 {len(segments)} 个片段...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                print(f"[MusicMerger] ffmpeg 错误: {result.stderr}")
                # 尝试简单拼接
                return self._simple_concat(segments, output_path)

            print(f"[MusicMerger] 合并完成: {output_path}")
            return str(output_path)

        except subprocess.TimeoutExpired:
            raise MusicGenerationError("音乐合并超时")

    def _build_crossfade_filter(self, count: int, crossfade: float) -> str:
        """
        构建交叉淡化滤镜

        对于 3 个输入:
        [0][1]acrossfade=d=0.5[a01];[a01][2]acrossfade=d=0.5[out]
        """
        if count == 2:
            return f"[0][1]acrossfade=d={crossfade}[out]"

        parts = []
        prev_label = "0"

        for i in range(1, count):
            next_input = str(i)
            if i == 1:
                out_label = f"a{i-1}{i}"
                parts.append(f"[{prev_label}][{next_input}]acrossfade=d={crossfade}[{out_label}]")
                prev_label = out_label
            elif i == count - 1:
                parts.append(f"[{prev_label}][{next_input}]acrossfade=d={crossfade}[out]")
            else:
                out_label = f"a{i-1}{i}"
                parts.append(f"[{prev_label}][{next_input}]acrossfade=d={crossfade}[{out_label}]")
                prev_label = out_label

        return ";".join(parts)

    def _simple_concat(self, segments: List[str], output_path: Path) -> str:
        """简单拼接（不使用交叉淡化）"""
        # 创建临时文件列表
        list_file = self.cache_dir / "concat_list.txt"
        with open(list_file, "w") as f:
            for seg in segments:
                f.write(f"file '{seg}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-acodec", "libmp3lame",
            "-q:a", "2",
            str(output_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                raise MusicGenerationError(f"简单拼接失败: {result.stderr}")

            return str(output_path)

        finally:
            # 清理临时文件
            if list_file.exists():
                list_file.unlink()

    def get_total_duration(self, segments: List[str], crossfade: float = 0.5) -> float:
        """
        计算合并后的总时长

        Args:
            segments: 片段路径列表
            crossfade: 交叉淡化时长

        Returns:
            总时长（秒）
        """
        total = 0.0

        for seg in segments:
            duration = self._get_duration(seg)
            total += duration

        # 减去交叉淡化重叠部分
        if len(segments) > 1:
            total -= crossfade * (len(segments) - 1)

        return total

    def _get_duration(self, music_path: str) -> float:
        """获取音乐时长"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "csv=p=0",
                str(music_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception:
            pass
        return 10.0  # 默认


def merge_music(segments: List[str], output_name: str = "medley") -> str:
    """便捷函数：合并音乐"""
    merger = MusicMerger()
    return merger.merge(segments, output_name)
