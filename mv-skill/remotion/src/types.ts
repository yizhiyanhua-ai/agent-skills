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
  style: "anime-hype" | "cyberpunk" | "lyric";
  duration: number;
  resolution: string;
  fps: number;
}

export interface Music {
  source: "suno" | "local" | "none";
  prompt?: string;
  file: string | null;
  bpm: number | null;
  beats: number[];
}

export interface Scene {
  id: string;
  start: number;
  end: number;
  type: "title" | "action" | "transition" | "lyrics";
  content?: SceneContent;
  visual: Visual;
  animation: AnimationType;
  transition?: TransitionType;
  beat_sync?: boolean;
}

export interface SceneContent {
  text?: string;
  subtitle?: string;
  lyrics?: string;
}

export interface Visual {
  source: "auto" | "ai" | "stock" | "user";
  prompt?: string;
  stock_keywords?: string[];
  quality_priority?: "high" | "medium" | "low";
  allow_ai_fallback?: boolean;
  file: string | null;
  media_type?: "image" | "video";
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
