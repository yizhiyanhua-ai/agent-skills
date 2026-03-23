"""
串烧生成器
生成歌曲串烧的分镜脚本
"""
import random
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from .config import TEMPLATES_DIR, CACHE_DIR, DEFAULT_CONFIG
from .music_downloader import MusicDownloader
from .music_analyzer import MusicAnalyzer
from .music_merger import MusicMerger
from .dj_effects import DJEffects
from .video_asset_fetcher import VideoAssetFetcher
from .exceptions import MVSkillError


class MedleyGenerator:
    """串烧生成器"""

    def __init__(self, theme: str = "nostalgic"):
        self.theme = theme
        self.template = self._load_template(theme)
        self.songs: List[Dict] = []
        self.downloader = MusicDownloader()
        self.analyzer = MusicAnalyzer()
        self.merger = MusicMerger()
        self.dj_effects = DJEffects()
        self.is_dj_theme = self.template.get("use_dj_scenes", False)
        self.use_video_mix = self.template.get("use_video_mix", False)

        # 如果使用视频混剪，初始化视频获取器
        if self.use_video_mix:
            try:
                self.video_fetcher = VideoAssetFetcher()
            except Exception as e:
                print(f"[MedleyGenerator] 视频获取器初始化失败: {e}")
                self.video_fetcher = None
        else:
            self.video_fetcher = None

    def _load_template(self, theme: str) -> Dict:
        """加载串烧主题模板"""
        template_path = TEMPLATES_DIR / "medley" / f"{theme}.yaml"
        if not template_path.exists():
            # 尝试默认模板
            template_path = TEMPLATES_DIR / "medley" / "nostalgic.yaml"
            if not template_path.exists():
                raise MVSkillError(f"串烧主题模板不存在: {theme}")

        with open(template_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def add_song(
        self,
        keyword: str,
        duration: Optional[float] = None,
        start: Optional[float] = None,
        end: Optional[float] = None,
    ):
        """
        添加歌曲到串烧

        Args:
            keyword: 歌曲搜索关键词
            duration: 片段时长（秒），如果不指定则自动选择
            start: 手动指定开始时间
            end: 手动指定结束时间
        """
        self.songs.append({
            "keyword": keyword,
            "duration": duration,
            "start": start,
            "end": end,
            "file": None,
            "segment_file": None,
        })

    def auto_select_songs(self, count: int = 4):
        """
        根据主题自动选择歌曲

        Args:
            count: 歌曲数量
        """
        keywords = self.template.get("song_keywords", [])
        if not keywords:
            raise MVSkillError("主题模板没有推荐歌曲")

        # 随机选择
        selected = random.sample(keywords, min(count, len(keywords)))
        for keyword in selected:
            self.add_song(keyword)

        print(f"[MedleyGenerator] 自动选择 {len(selected)} 首歌曲: {selected}")

    def generate(
        self,
        total_duration: int = 45,
        title: Optional[str] = None,
    ) -> Dict:
        """
        生成串烧分镜脚本

        Args:
            total_duration: 总时长（秒）
            title: 串烧标题

        Returns:
            分镜脚本字典
        """
        if not self.songs:
            raise MVSkillError("没有添加歌曲，请先调用 add_song() 或 auto_select_songs()")

        if not title:
            title = f"{self.template.get('display_name', self.theme)}串烧"

        print(f"[MedleyGenerator] 开始生成串烧: {title}")
        print(f"  主题: {self.theme}")
        print(f"  歌曲数: {len(self.songs)}")
        print(f"  总时长: {total_duration}秒")

        # 1. 下载所有歌曲
        self._download_songs()

        # 2. 计算每首歌的片段时长
        segment_durations = self._calculate_segment_durations(total_duration)

        # 3. 分析并提取最佳片段
        segments = self._extract_segments(segment_durations)

        # 4. 合并音乐
        merged_music = self._merge_segments(segments, title)

        # 5. 生成分镜脚本
        storyboard = self._generate_storyboard(
            title=title,
            total_duration=total_duration,
            merged_music=merged_music,
            segments=segments,
        )

        return storyboard

    def _download_songs(self):
        """下载所有歌曲"""
        print("\n[MedleyGenerator] 下载歌曲...")

        for i, song in enumerate(self.songs):
            if song.get("file") and Path(song["file"]).exists():
                print(f"  [{i+1}/{len(self.songs)}] {song['keyword']}: 已存在")
                continue

            print(f"  [{i+1}/{len(self.songs)}] 搜索: {song['keyword']}")
            music_path = self.downloader.search_and_download(song["keyword"])

            if music_path:
                song["file"] = str(music_path)
                print(f"    下载完成: {music_path}")
            else:
                print(f"    ⚠️ 下载失败: {song['keyword']}")

    def _calculate_segment_durations(self, total_duration: int) -> List[float]:
        """计算每首歌的片段时长"""
        rhythm = self.template.get("rhythm", {})
        default_duration = rhythm.get("segment_duration", {}).get("default", 10)
        min_duration = rhythm.get("segment_duration", {}).get("min", 6)
        max_duration = rhythm.get("segment_duration", {}).get("max", 15)

        # 有效歌曲数量
        valid_songs = [s for s in self.songs if s.get("file")]
        if not valid_songs:
            raise MVSkillError("没有成功下载的歌曲")

        count = len(valid_songs)

        # 计算每首歌的时长
        durations = []
        for song in self.songs:
            if not song.get("file"):
                durations.append(0)
                continue

            if song.get("duration"):
                # 使用指定时长
                durations.append(song["duration"])
            else:
                # 平均分配
                avg = total_duration / count
                # 限制在范围内
                durations.append(max(min_duration, min(max_duration, avg)))

        # 调整总时长
        total = sum(durations)
        if total != total_duration and total > 0:
            scale = total_duration / total
            durations = [d * scale for d in durations]

        return durations

    def _extract_segments(self, durations: List[float]) -> List[Dict]:
        """提取每首歌的最佳片段"""
        print("\n[MedleyGenerator] 分析并提取片段...")

        segments = []
        for i, (song, duration) in enumerate(zip(self.songs, durations)):
            if not song.get("file") or duration <= 0:
                continue

            print(f"  [{i+1}/{len(self.songs)}] {song['keyword']}: {duration:.1f}秒")

            # 确定片段范围
            if song.get("start") is not None and song.get("end") is not None:
                start, end = song["start"], song["end"]
            else:
                start, end = self.analyzer.find_best_segment(
                    song["file"],
                    duration,
                    prefer_position="chorus",
                )

            # 提取片段
            segment_file = self.analyzer.extract_segment(
                song["file"],
                start,
                end,
                output_name=f"seg_{i}_{song['keyword'][:10]}",
            )

            song["segment_file"] = segment_file
            song["segment_start"] = start
            song["segment_end"] = end

            segments.append({
                "index": i,
                "keyword": song["keyword"],
                "file": segment_file,
                "duration": end - start,
                "original_start": start,
                "original_end": end,
            })

            print(f"    片段: {start:.1f}s - {end:.1f}s")

        return segments

    def _merge_segments(self, segments: List[Dict], title: str) -> str:
        """合并所有片段"""
        print("\n[MedleyGenerator] 合并音乐片段...")

        # 如果是 DJ 主题，先对每个片段应用 DJ 效果
        if self.is_dj_theme:
            print("[MedleyGenerator] 应用 DJ 音效...")
            dj_presets = self.template.get("dj_effects", {}).get("presets", [])
            processed_segments = []
            for i, seg in enumerate(segments):
                preset_idx = i % len(dj_presets) if dj_presets else 0
                effects = dj_presets[preset_idx] if dj_presets else ["bass_boost", "compressor"]
                processed_file = self.dj_effects.apply_effects(
                    seg["file"],
                    f"dj_seg_{i}",
                    effects=effects,
                )
                processed_segments.append(processed_file)
                seg["dj_effects"] = effects
            segment_files = processed_segments
        else:
            segment_files = [s["file"] for s in segments]

        crossfade = self.template.get("transitions", {}).get("duration", 0.5)

        merged_path = self.merger.merge(
            segment_files,
            output_name=title.replace(" ", "_"),
            crossfade=crossfade,
        )

        return merged_path

    def _generate_storyboard(
        self,
        title: str,
        total_duration: int,
        merged_music: str,
        segments: List[Dict],
    ) -> Dict:
        """生成分镜脚本"""
        print("\n[MedleyGenerator] 生成分镜脚本...")

        visual_style = self.template.get("visual_style", {})
        rhythm = self.template.get("rhythm", {})
        scenes_per_segment = rhythm.get("scenes_per_segment", 3)

        # 基础元数据
        storyboard = {
            "meta": {
                "title": title,
                "style": f"medley-{self.theme}",
                "duration": total_duration,
                "resolution": DEFAULT_CONFIG["resolution"],
                "fps": DEFAULT_CONFIG["fps"],
                "type": "medley",
                "song_count": len(segments),
            },
            "music": {
                "source": "medley",
                "file": merged_music,
                "bpm": 120,  # 串烧的平均 BPM
                "beats": [],
                "segments": [
                    {
                        "keyword": s["keyword"],
                        "duration": s["duration"],
                    }
                    for s in segments
                ],
            },
            "scenes": [],
        }

        # 生成场景
        current_time = 0
        scene_index = 0
        crossfade = self.template.get("transitions", {}).get("duration", 0.5)

        for seg_idx, segment in enumerate(segments):
            seg_duration = segment["duration"]
            if seg_idx > 0:
                seg_duration -= crossfade  # 减去交叉淡化重叠

            # 每个片段生成多个场景
            scene_duration = seg_duration / scenes_per_segment

            for i in range(scenes_per_segment):
                scene_id = f"seg{seg_idx}_scene{i}_{scene_index}"
                start_time = current_time
                end_time = current_time + scene_duration

                scene = self._create_scene(
                    scene_id=scene_id,
                    start=round(start_time, 2),
                    end=round(end_time, 2),
                    segment_index=seg_idx,
                    scene_index_in_segment=i,
                    song_keyword=segment["keyword"],
                )
                storyboard["scenes"].append(scene)

                current_time = end_time
                scene_index += 1

        print(f"  生成 {len(storyboard['scenes'])} 个场景")
        return storyboard

    def _create_scene(
        self,
        scene_id: str,
        start: float,
        end: float,
        segment_index: int,
        scene_index_in_segment: int,
        song_keyword: str,
    ) -> Dict:
        """创建单个场景"""
        # DJ 主题使用特殊的场景类型
        if self.is_dj_theme:
            return self._create_dj_scene(
                scene_id=scene_id,
                start=start,
                end=end,
                segment_index=segment_index,
                scene_index_in_segment=scene_index_in_segment,
                song_keyword=song_keyword,
            )

        visual_style = self.template.get("visual_style", {})
        animations = self.template.get("animations", {}).get("preferred", ["ken-burns"])
        transitions = self.template.get("transitions", {}).get("preferred", ["fade"])
        scene_prompts = self.template.get("scene_prompts", {}).get("default", [])

        # 选择动画和转场
        animation = animations[scene_index_in_segment % len(animations)]
        transition = transitions[scene_index_in_segment % len(transitions)]

        # 生成视觉提示词
        base_prompt = random.choice(scene_prompts) if scene_prompts else f"{song_keyword}, cinematic"
        ai_suffix = visual_style.get("ai_prompt_suffix", "")
        visual_prompt = f"{base_prompt}, {song_keyword}, {ai_suffix}"

        # 生成搜索关键词
        stock_keywords = visual_style.get("stock_keywords", [])[:3]
        stock_keywords.append(song_keyword.split()[0] if song_keyword else "music")

        return {
            "id": scene_id,
            "start": start,
            "end": end,
            "type": "action",
            "visual": {
                "source": "auto",
                "prompt": visual_prompt,
                "stock_keywords": stock_keywords,
                "quality_priority": "high",
                "allow_ai_fallback": True,
                "prefer_video": True,  # 优先使用视频素材
                "file": None,
            },
            "animation": animation,
            "transition": transition,
            "beat_sync": True,
            "metadata": {
                "segment_index": segment_index,
                "song_keyword": song_keyword,
            },
        }

    def _create_dj_scene(
        self,
        scene_id: str,
        start: float,
        end: float,
        segment_index: int,
        scene_index_in_segment: int,
        song_keyword: str,
    ) -> Dict:
        """创建 DJ 风格场景 - 支持视频混剪或程序化生成"""
        visual_style = self.template.get("visual_style", {})
        color_schemes = visual_style.get("color_schemes", [])
        transitions = self.template.get("transitions", {}).get("preferred", ["flash", "glitch"])
        intensity = self.template.get("animations", {}).get("intensity", "high")

        # 随机选择配色方案
        color_scheme = random.choice(color_schemes) if color_schemes else {
            "primary": "#FF00FF",
            "secondary": "#00FFFF",
            "accent": "#FFFF00",
            "background": "#0a0a0f",
        }

        # 随机选择转场
        transition = random.choice(transitions)

        # 强度随机化
        intensity_map = {"low": 0.5, "medium": 0.8, "high": 1.0}
        base_intensity = intensity_map.get(intensity, 1.0)
        intensity_value = base_intensity * (0.8 + random.random() * 0.4)  # 80%-120%

        # 如果使用视频混剪模式
        if self.use_video_mix:
            video_categories = visual_style.get("video_categories", [
                "nightclub", "dj", "festival", "laser", "neon",
                "abstract", "crowd", "lights", "smoke", "tunnel"
            ])
            video_category = random.choice(video_categories)

            # DJ 风格动画效果
            dj_effects = visual_style.get("dj_overlay_effects", [
                "flash", "glitch", "color-shift", "zoom-pulse", "strobe"
            ])
            overlay_effect = random.choice(dj_effects)

            return {
                "id": scene_id,
                "start": start,
                "end": end,
                "type": "video_mix",  # 视频混剪场景类型
                "visual": {
                    "source": "video",
                    "video_category": video_category,
                    "color_scheme": color_scheme,
                    "intensity": intensity_value,
                    "overlay_effect": overlay_effect,
                    "file": None,  # 稍后由 video_fetcher 填充
                },
                "animation": "dj-pulse",
                "transition": transition,
                "beat_sync": True,
                "metadata": {
                    "segment_index": segment_index,
                    "song_keyword": song_keyword,
                    "video_category": video_category,
                    "scene_index": scene_index_in_segment,
                },
            }
        else:
            # 程序化生成模式
            visual_types = visual_style.get("visual_types", ["nightclub", "spectrum", "particles"])
            visual_type = random.choice(visual_types)

            return {
                "id": scene_id,
                "start": start,
                "end": end,
                "type": "dj",  # DJ 场景类型
                "visual": {
                    "source": "programmatic",  # 程序化生成
                    "visual_type": visual_type,
                    "color_scheme": color_scheme,
                    "intensity": intensity_value,
                    "file": None,  # DJ 场景不需要素材文件
                },
                "animation": "dj-pulse",
                "transition": transition,
                "beat_sync": True,
                "metadata": {
                    "segment_index": segment_index,
                    "song_keyword": song_keyword,
                    "dj_visual_type": visual_type,
                },
            }


def generate_medley(
    theme: str,
    songs: List[str],
    total_duration: int = 45,
    title: Optional[str] = None,
) -> Dict:
    """
    便捷函数：生成串烧

    Args:
        theme: 主题名称
        songs: 歌曲关键词列表
        total_duration: 总时长
        title: 标题

    Returns:
        分镜脚本
    """
    generator = MedleyGenerator(theme=theme)
    for song in songs:
        generator.add_song(song)
    return generator.generate(total_duration=total_duration, title=title)
