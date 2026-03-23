"""
音乐结构分析器
分析歌曲结构，识别副歌/高潮部分，选择最佳片段
确保截取的片段有实际音乐内容
"""
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import CACHE_DIR
from .exceptions import MusicGenerationError


class MusicAnalyzer:
    """音乐结构分析器"""

    def __init__(self):
        self.cache_dir = CACHE_DIR / "segments"
        self.cache_dir.mkdir(exist_ok=True)

    def get_duration(self, music_path: str) -> float:
        """获取音乐时长（秒）"""
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
        except Exception as e:
            print(f"[MusicAnalyzer] 获取时长失败: {e}")
        return 60.0  # 默认 60 秒

    def detect_silence(self, music_path: str) -> Tuple[float, float]:
        """
        检测音频开头和结尾的静音部分

        Returns:
            (开头静音结束时间, 结尾静音开始时间)
        """
        duration = self.get_duration(music_path)

        try:
            # 使用 ffmpeg 检测静音
            cmd = [
                "ffmpeg",
                "-i", str(music_path),
                "-af", "silencedetect=noise=-40dB:d=0.5",
                "-f", "null", "-"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # 解析静音检测结果
            silence_start = 0.0
            silence_end = duration

            for line in result.stderr.split('\n'):
                if 'silence_end' in line:
                    # 找到第一个静音结束点（开头静音结束）
                    try:
                        parts = line.split('silence_end:')
                        if len(parts) > 1:
                            end_time = float(parts[1].split()[0])
                            if end_time < 10:  # 只考虑前10秒的静音
                                silence_start = end_time
                                break
                    except:
                        pass

            return (silence_start, silence_end)

        except Exception as e:
            print(f"[MusicAnalyzer] 静音检测失败: {e}")
            return (0.0, duration)

    def get_audio_loudness(self, music_path: str, start: float, duration: float) -> float:
        """
        获取指定片段的响度

        Returns:
            响度值（dB），越高越响
        """
        try:
            cmd = [
                "ffmpeg",
                "-ss", str(start),
                "-t", str(duration),
                "-i", str(music_path),
                "-af", "volumedetect",
                "-f", "null", "-"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # 解析响度
            for line in result.stderr.split('\n'):
                if 'mean_volume' in line:
                    try:
                        parts = line.split('mean_volume:')
                        if len(parts) > 1:
                            return float(parts[1].split()[0])
                    except:
                        pass

            return -20.0  # 默认响度

        except Exception:
            return -20.0

    def analyze_energy(self, music_path: str) -> List[Dict]:
        """
        分析音乐能量分布，找到高能量段落

        Returns:
            [{"start": float, "end": float, "energy": float}, ...]
        """
        try:
            import librosa
            import numpy as np

            # 加载音频
            y, sr = librosa.load(str(music_path), sr=22050)
            duration = len(y) / sr

            # 计算 RMS 能量
            hop_length = 512
            rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

            # 将能量分成 1 秒的段落
            frames_per_second = sr / hop_length
            segment_duration = 1.0  # 1 秒一段
            frames_per_segment = int(frames_per_second * segment_duration)

            segments = []
            for i in range(0, len(rms), frames_per_segment):
                segment_rms = rms[i:i + frames_per_segment]
                if len(segment_rms) > 0:
                    start_time = i / frames_per_second
                    end_time = min((i + frames_per_segment) / frames_per_second, duration)
                    avg_energy = float(np.mean(segment_rms))
                    segments.append({
                        "start": round(start_time, 2),
                        "end": round(end_time, 2),
                        "energy": round(avg_energy, 4),
                    })

            return segments

        except ImportError:
            print("[MusicAnalyzer] librosa 未安装，使用简化分析")
            return self._simple_energy_analysis(music_path)
        except Exception as e:
            print(f"[MusicAnalyzer] 能量分析失败: {e}")
            return self._simple_energy_analysis(music_path)

    def _simple_energy_analysis(self, music_path: str) -> List[Dict]:
        """简化的能量分析（不依赖 librosa）- 使用 ffmpeg 检测"""
        duration = self.get_duration(music_path)

        # 检测开头静音
        silence_start, _ = self.detect_silence(music_path)

        # 跳过开头静音和可能的人声朗读部分
        # EDM/舞曲前奏通常有 15-30 秒，我们跳过更多以避免朗读部分
        min_skip = max(duration * 0.25, 30.0)  # 至少跳过 25% 或 30 秒
        actual_start = max(silence_start, min_skip)

        segments = []

        # EDM/舞曲通常结构（从跳过前奏后开始）：
        # 我们从歌曲的 25% 位置开始，这通常是第一个 Drop 或副歌
        # Buildup -> Drop/高潮 -> Break -> Drop2/高潮2 -> Outro
        # 重点选择 Drop 部分（高能量、有节奏感的部分）

        effective_duration = duration - actual_start - 5.0  # 留 5 秒结尾余量

        # 从 25% 位置开始的结构，优先选择中后段高潮
        structure = [
            (0.0, 0.15, 0.7),    # 第一个 Buildup
            (0.15, 0.40, 1.0),   # Drop 1 / 副歌 (最高能量) ★ 优先选择
            (0.40, 0.50, 0.5),   # Break / 间奏
            (0.50, 0.75, 0.95),  # Drop 2 / 副歌2 (高能量) ★ 优先选择
            (0.75, 0.90, 0.6),   # 渐出段
            (0.90, 1.0, 0.3),    # Outro
        ]

        for start_ratio, end_ratio, energy in structure:
            seg_start = actual_start + effective_duration * start_ratio
            seg_end = actual_start + effective_duration * end_ratio
            segments.append({
                "start": round(seg_start, 2),
                "end": round(seg_end, 2),
                "energy": energy,
            })

        return segments

    def find_best_segment(
        self,
        music_path: str,
        target_duration: float,
        prefer_position: str = "chorus",
    ) -> Tuple[float, float]:
        """
        找到最佳片段 - 确保有实际音乐内容，避免人声朗读部分

        Args:
            music_path: 音乐文件路径
            target_duration: 目标片段时长
            prefer_position: 偏好位置 ("chorus" 副歌/Drop, "intro" 开头, "middle" 中间)

        Returns:
            (start_time, end_time)
        """
        duration = self.get_duration(music_path)

        # 检测静音，确保不截取静音部分
        silence_end, _ = self.detect_silence(music_path)

        # 跳过前奏和可能的人声朗读部分（至少跳过 25% 或 30 秒）
        min_skip = max(duration * 0.25, 30.0)
        safe_start = max(silence_end, min_skip)

        # 确保目标时长不超过可用时长
        available_duration = duration - safe_start - 5.0  # 留 5 秒结尾余量
        target_duration = min(target_duration, available_duration)

        if prefer_position == "intro":
            # 从安全起点开始（但仍然跳过前奏）
            return (safe_start, safe_start + target_duration)

        elif prefer_position == "middle":
            # 从中间开始
            start = safe_start + (available_duration - target_duration) / 2
            return (round(start, 2), round(start + target_duration, 2))

        else:  # chorus/drop - 找高能量段落（优先中后段）
            segments = self.analyze_energy(music_path)

            if not segments:
                # 默认取中后段位置（40%-60% 位置，通常是 Drop）
                start = safe_start + available_duration * 0.4
                return (round(start, 2), round(start + target_duration, 2))

            # 找到能量最高的连续段落，优先选择中后段
            best_start = safe_start
            best_score = 0

            for i, seg in enumerate(segments):
                # 确保起点在安全范围内
                if seg["start"] < safe_start:
                    continue

                # 计算从这个位置开始的平均能量
                end_time = seg["start"] + target_duration
                if end_time > duration - 3:  # 留 3 秒余量
                    continue

                # 计算这个范围内的平均能量
                total_energy = 0
                count = 0
                for s in segments:
                    if s["start"] >= seg["start"] and s["end"] <= end_time:
                        total_energy += s["energy"]
                        count += 1

                avg_energy = total_energy / count if count > 0 else 0

                # 计算位置权重：中后段（40%-70%）位置加分
                position_ratio = (seg["start"] - safe_start) / available_duration
                position_bonus = 0
                if 0.3 <= position_ratio <= 0.7:
                    position_bonus = 0.2  # 中后段加 20% 权重

                score = avg_energy + position_bonus

                if score > best_score:
                    best_score = score
                    best_start = seg["start"]

            # 验证选中的片段有足够响度
            loudness = self.get_audio_loudness(music_path, best_start, min(5, target_duration))
            if loudness < -45:  # 太安静，可能是静音或朗读
                print(f"[MusicAnalyzer] 检测到低响度片段 ({loudness}dB)，调整到中后段")
                # 直接跳到歌曲 40% 位置
                best_start = safe_start + available_duration * 0.4

            return (round(best_start, 2), round(best_start + target_duration, 2))

    def extract_segment(
        self,
        music_path: str,
        start: float,
        end: float,
        output_name: Optional[str] = None,
        fade_in: float = 0.1,
        fade_out: float = 0.3,
    ) -> str:
        """
        提取音乐片段 - 使用更短的淡入淡出，保持 DJ 风格的硬切感

        Args:
            music_path: 源音乐文件
            start: 开始时间（秒）
            end: 结束时间（秒）
            output_name: 输出文件名
            fade_in: 淡入时长（DJ 风格用短淡入）
            fade_out: 淡出时长（DJ 风格用短淡出）

        Returns:
            输出文件路径
        """
        path = Path(music_path)
        if not output_name:
            output_name = f"{path.stem}_{start:.1f}_{end:.1f}"

        output_path = self.cache_dir / f"{output_name}.mp3"

        duration = end - start

        # 使用 ffmpeg 裁剪并添加淡入淡出
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", str(music_path),
            "-t", str(duration),
            "-af", f"afade=t=in:st=0:d={fade_in},afade=t=out:st={duration - fade_out}:d={fade_out}",
            "-acodec", "libmp3lame",
            "-q:a", "2",
            str(output_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                print(f"[MusicAnalyzer] ffmpeg 错误: {result.stderr}")
                raise MusicGenerationError(f"片段提取失败: {result.stderr}")

            print(f"[MusicAnalyzer] 提取片段: {output_path}")
            return str(output_path)

        except subprocess.TimeoutExpired:
            raise MusicGenerationError("片段提取超时")

    def get_bpm(self, music_path: str) -> int:
        """获取音乐 BPM"""
        try:
            import librosa

            y, sr = librosa.load(str(music_path), sr=22050, duration=30)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = int(float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo))
            return bpm

        except ImportError:
            return 128  # EDM 默认 BPM
        except Exception:
            return 128


def find_best_segment(music_path: str, duration: float) -> Tuple[float, float]:
    """便捷函数：找到最佳片段"""
    analyzer = MusicAnalyzer()
    return analyzer.find_best_segment(music_path, duration)


def extract_segment(music_path: str, start: float, end: float) -> str:
    """便捷函数：提取片段"""
    analyzer = MusicAnalyzer()
    return analyzer.extract_segment(music_path, start, end)
