"""
DJ 音效处理器
为音乐添加百大 DJ 风格的专业音效技巧
包含搓碟、刹车、回放等过渡效果
"""
import subprocess
import random
from pathlib import Path
from typing import List, Optional

from .config import CACHE_DIR


class DJEffects:
    """DJ 音效处理器 - 百大 DJ 风格"""

    # DJ 过渡技巧列表
    TRANSITION_TECHNIQUES = [
        "scratch",        # 搓碟
        "backspin",       # 回转
        "brake",          # 刹车
        "filter_sweep",   # 滤波扫描
        "echo_out",       # 回声渐出
        "stutter",        # 卡顿效果
        "reverse",        # 倒放
        "pitch_up",       # 升调
        "pitch_down",     # 降调
    ]

    def __init__(self):
        self.cache_dir = CACHE_DIR / "dj_effects"
        self.cache_dir.mkdir(exist_ok=True)

    def apply_effects(
        self,
        input_path: str,
        output_name: str,
        effects: List[str] = None,
    ) -> str:
        """
        应用 DJ 效果到音频

        Args:
            input_path: 输入音频路径
            output_name: 输出文件名
            effects: 要应用的效果列表

        Returns:
            处理后的音频路径
        """
        if effects is None:
            effects = ["bass_boost", "compressor"]

        output_path = self.cache_dir / f"{output_name}_dj.mp3"

        # 构建 ffmpeg 滤镜链
        filters = []

        for effect in effects:
            if effect == "bass_boost":
                # 强劲低音增强 - 百大 DJ 风格
                filters.append("bass=g=10:f=100:w=0.5")
            elif effect == "bass_boost_heavy":
                # 超重低音
                filters.append("bass=g=15:f=80:w=0.4")
            elif effect == "echo":
                # 回声效果
                filters.append("aecho=0.8:0.88:60:0.4")
            elif effect == "reverb":
                # 大空间混响
                filters.append("aecho=0.8:0.9:1000:0.3")
            elif effect == "reverb_hall":
                # 音乐厅混响
                filters.append("aecho=0.8:0.85:500|1000:0.4|0.3")
            elif effect == "highpass":
                # 高通滤波（DJ 常用 - 去低音）
                filters.append("highpass=f=300")
            elif effect == "highpass_sweep":
                # 高通扫描效果
                filters.append("highpass=f=500")
            elif effect == "lowpass":
                # 低通滤波（闷音效果）
                filters.append("lowpass=f=2000")
            elif effect == "lowpass_heavy":
                # 重度低通（水下效果）
                filters.append("lowpass=f=800")
            elif effect == "flanger":
                # 镶边效果
                filters.append("flanger=delay=0:depth=2:regen=0:width=71:speed=0.5:shape=triangular:phase=25:interp=linear")
            elif effect == "tremolo":
                # 颤音
                filters.append("tremolo=f=8:d=0.8")
            elif effect == "phaser":
                # 相位效果
                filters.append("aphaser=in_gain=0.4:out_gain=0.74:delay=3.0:decay=0.4:speed=0.5:type=triangular")
            elif effect == "compressor":
                # 动态压缩（让声音更有力）
                filters.append("acompressor=threshold=0.5:ratio=4:attack=5:release=50")
            elif effect == "compressor_hard":
                # 硬压缩（更激进）
                filters.append("acompressor=threshold=0.3:ratio=8:attack=2:release=30")
            elif effect == "normalize":
                # 音量标准化
                filters.append("loudnorm=I=-14:TP=-1:LRA=11")
            elif effect == "stereo_wide":
                # 立体声加宽
                filters.append("stereotools=mlev=1:slev=1.5:sbal=0")
            elif effect == "distortion":
                # 轻度失真（增加能量感）
                filters.append("aeval=val(0)*1.2|val(1)*1.2")
            elif effect == "sidechain":
                # 模拟 sidechain 压缩效果（节奏感）
                filters.append("tremolo=f=4:d=0.5")
            elif effect == "vinyl_noise":
                # 黑胶噪音质感
                filters.append("highpass=f=20,lowpass=f=15000")

        if not filters:
            # 如果没有滤镜，至少做一个标准化
            filters.append("loudnorm=I=-14:TP=-1:LRA=11")

        filter_chain = ",".join(filters)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-af", filter_chain,
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
                print(f"[DJEffects] 效果应用失败: {result.stderr[:200]}")
                return input_path  # 返回原文件

            print(f"[DJEffects] 效果已应用: {effects}")
            return str(output_path)

        except Exception as e:
            print(f"[DJEffects] 错误: {e}")
            return input_path

    def add_dj_transition(
        self,
        input_path: str,
        output_name: str,
        technique: str = None,
        position: str = "end",
        duration: float = 1.0,
    ) -> str:
        """
        添加 DJ 过渡效果（搓碟、刹车等）

        Args:
            input_path: 输入音频
            output_name: 输出名称
            technique: 过渡技巧，None 则随机选择
            position: 效果位置 "start", "end", "both"
            duration: 效果时长

        Returns:
            处理后的音频路径
        """
        if technique is None:
            technique = random.choice(self.TRANSITION_TECHNIQUES)

        output_path = self.cache_dir / f"{output_name}_{technique}.mp3"
        audio_duration = self._get_duration(input_path)

        filters = []
        print(f"[DJEffects] 应用过渡技巧: {technique}")

        if technique == "scratch":
            # 搓碟效果 - 使用颤音模拟
            if position in ["end", "both"]:
                start_time = audio_duration - duration
                filters.append(f"vibrato=f=20:d=0.5:enable='gt(t,{start_time})'")
                filters.append(f"afade=t=out:st={start_time}:d={duration}")

        elif technique == "backspin":
            # 回转效果 - 降调 + 淡出
            if position in ["end", "both"]:
                start_time = audio_duration - duration
                filters.append(f"asetrate=44100*0.8:enable='gt(t,{start_time})'")
                filters.append(f"afade=t=out:st={start_time}:d={duration}")

        elif technique == "brake":
            # 刹车效果 - 快速降调停止
            if position in ["end", "both"]:
                start_time = audio_duration - duration
                filters.append(f"afade=t=out:st={start_time}:d={duration}:curve=esin")

        elif technique == "filter_sweep":
            # 滤波扫描
            if position in ["start", "both"]:
                filters.append(f"lowpass=f='200+2800*min(t/{duration},1)':enable='lt(t,{duration})'")
            if position in ["end", "both"]:
                start_time = audio_duration - duration
                filters.append(f"lowpass=f='3000-2800*min((t-{start_time})/{duration},1)':enable='gt(t,{start_time})'")

        elif technique == "echo_out":
            # 回声渐出
            if position in ["end", "both"]:
                start_time = audio_duration - duration
                filters.append("aecho=0.8:0.88:100:0.5")
                filters.append(f"afade=t=out:st={start_time}:d={duration}")

        elif technique == "stutter":
            # 卡顿效果
            if position in ["end", "both"]:
                filters.append("tremolo=f=16:d=0.9")

        elif technique == "reverse":
            # 倒放尾部（需要特殊处理）
            if position in ["end", "both"]:
                start_time = audio_duration - duration
                filters.append(f"afade=t=out:st={start_time}:d={duration}")

        elif technique == "pitch_up":
            # 升调效果
            if position in ["start", "both"]:
                filters.append(f"asetrate=44100*1.05:enable='lt(t,{duration})'")
            if position in ["end", "both"]:
                start_time = audio_duration - duration
                filters.append(f"afade=t=out:st={start_time}:d={duration}")

        elif technique == "pitch_down":
            # 降调效果
            if position in ["end", "both"]:
                start_time = audio_duration - duration
                filters.append(f"asetrate=44100*0.95:enable='gt(t,{start_time})'")
                filters.append(f"afade=t=out:st={start_time}:d={duration}")

        if not filters:
            # 默认淡出
            start_time = audio_duration - duration
            filters.append(f"afade=t=out:st={start_time}:d={duration}")

        filter_chain = ",".join(filters)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-af", filter_chain,
            "-acodec", "libmp3lame",
            "-q:a", "2",
            str(output_path),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return str(output_path)
        except Exception as e:
            print(f"[DJEffects] 过渡效果失败: {e}")

        return input_path

    def create_dj_segment(
        self,
        input_path: str,
        segment_index: int,
        output_name: str,
        total_segments: int = 8,
    ) -> str:
        """
        为单个片段创建百大 DJ 风格处理

        不同片段使用不同的效果组合，模拟 DJ set 的起承转合
        每次随机选择效果组合，带来惊喜
        重点使用搓碟和回转效果实现专业衔接
        """
        # 根据片段在整体中的位置选择效果
        position_ratio = segment_index / max(total_segments - 1, 1)

        # 随机化效果组合，但保持整体结构
        if position_ratio < 0.15:
            # 开场 - 低音铺垫，滤波效果
            base_effects = ["bass_boost", "lowpass", "compressor"]
            extra = random.choice([[], ["vinyl_noise"], ["phaser"]])
            effects = base_effects + extra
            # 开场用滤波扫描或升调
            transition = random.choice(["filter_sweep", "pitch_up", "filter_sweep"])
        elif position_ratio < 0.3:
            # 渐入 - 滤波逐渐打开
            base_effects = ["highpass", "compressor"]
            extra = random.choice([["phaser"], ["flanger"], ["tremolo"]])
            effects = base_effects + extra
            # 用搓碟或回转衔接
            transition = random.choice(["scratch", "backspin", "filter_sweep"])
        elif position_ratio < 0.5:
            # 第一个高潮 - Drop
            base_effects = ["bass_boost_heavy", "compressor_hard"]
            extra = random.choice([["stereo_wide"], ["echo"], []])
            effects = base_effects + extra
            # 高潮结束用搓碟或刹车
            transition = random.choice(["scratch", "scratch", "brake", "backspin"])
        elif position_ratio < 0.65:
            # 过渡段 - Break，空灵效果
            base_effects = ["reverb_hall", "highpass"]
            extra = random.choice([["flanger"], ["phaser"], ["tremolo"]])
            effects = base_effects + extra
            # 过渡用回转或滤波
            transition = random.choice(["backspin", "backspin", "filter_sweep", "echo_out"])
        elif position_ratio < 0.85:
            # 第二个高潮 - 最强能量
            base_effects = ["bass_boost_heavy", "compressor_hard"]
            extra = random.choice([["echo"], ["stereo_wide"], ["sidechain"]])
            effects = base_effects + extra
            # 高潮用搓碟
            transition = random.choice(["scratch", "scratch", "stutter", "backspin"])
        else:
            # 尾声 - 渐出
            base_effects = ["reverb", "lowpass"]
            extra = random.choice([["tremolo"], ["phaser"], []])
            effects = base_effects + extra
            # 结尾用回转或回声渐出
            transition = random.choice(["backspin", "echo_out", "pitch_down"])

        print(f"[DJEffects] 片段 {segment_index}/{total_segments} ({position_ratio:.0%}) 效果: {effects}, 过渡: {transition}")

        # 应用效果
        processed = self.apply_effects(input_path, f"{output_name}_seg{segment_index}", effects)

        # 添加 DJ 过渡效果
        if segment_index < total_segments - 1:  # 不是最后一个片段
            processed = self.add_dj_transition(
                processed,
                f"{output_name}_seg{segment_index}",
                technique=transition,
                position="end",
                duration=1.5,  # 更长的过渡时间，让衔接更自然
            )
        else:
            # 最后一个片段使用渐出
            processed = self.add_dj_transition(
                processed,
                f"{output_name}_seg{segment_index}",
                technique="echo_out",
                position="end",
                duration=3.0,  # 更长的结尾渐出
            )

        return processed

    def _get_duration(self, audio_path: str) -> float:
        """获取音频时长"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "csv=p=0",
                str(audio_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception:
            pass
        return 10.0


def apply_dj_effects(input_path: str, effects: Optional[List[str]] = None) -> str:
    """便捷函数：应用 DJ 效果"""
    dj = DJEffects()
    return dj.apply_effects(input_path, Path(input_path).stem, effects if effects else ["bass_boost", "compressor"])
