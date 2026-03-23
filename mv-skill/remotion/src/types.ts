/**
 * MV Skill 类型定义
 */

export interface Storyboard {
  meta: Meta;
  music: Music;
  scenes: Scene[];
}

export interface Meta {
  title: string;
  style: string;  // "anime-hype" | "cyberpunk" | "lyric" | "medley-*"
  duration: number;
  resolution: string;
  fps: number;
  type?: "single" | "medley";
  song_count?: number;
}

export interface Music {
  source: "suno" | "local" | "none" | "medley";
  prompt?: string;
  file: string | null;
  bpm: number | null;
  beats: number[];
  segments?: MusicSegment[];
}

export interface MusicSegment {
  keyword: string;
  duration: number;
}

export interface Scene {
  id: string;
  start: number;
  end: number;
  type: "title" | "action" | "transition" | "lyrics" | "dj" | "video_mix";
  content?: SceneContent;
  visual: Visual;
  animation: AnimationType;
  transition?: TransitionType;
  beat_sync?: boolean;
  metadata?: SceneMetadata;
}

export interface SceneMetadata {
  segment_index?: number;
  song_keyword?: string;
  video_category?: string;
  scene_index?: number;
  dj_visual_type?: string;
}

export interface SceneContent {
  text?: string;
  subtitle?: string;
  lyrics?: string;
}

export interface Visual {
  source: "auto" | "ai" | "stock" | "user" | "programmatic" | "video";
  prompt?: string;
  stock_keywords?: string[];
  quality_priority?: "high" | "medium" | "low";
  allow_ai_fallback?: boolean;
  file: string | null;
  media_type?: "image" | "video";
  // DJ scene properties
  visual_type?: string;
  color_scheme?: ColorScheme;
  intensity?: number;
  // Video mix scene properties
  video_category?: string;
  overlay_effect?: string;
}

export interface ColorScheme {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
}

export type AnimationType =
  | "none"
  | "zoom-in"
  | "zoom-out"
  | "pan-left"
  | "pan-right"
  | "pan-up"
  | "pan-down"
  | "shake"
  | "flash"
  | "ken-burns"
  | "speed-lines"
  | "rotate";

export type TransitionType =
  | "none"
  | "fade"
  | "cross-fade"
  | "flash"
  | "wipe-left"
  | "wipe-right"
  | "wipe-diagonal"
  | "impact-frame"
  | "glitch"
  | "pixelate";

export interface StyleConfig {
  background: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  textColor: string;
  fontFamily: string;
}
