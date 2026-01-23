import React from "react";
import {
  AbsoluteFill,
  Img,
  Video,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import { Visual, AnimationType, StyleConfig } from "../../types";
import { applyAnimation } from "../animations/animationUtils";

interface ActionSceneProps {
  visual: Visual;
  animation: AnimationType;
  lyrics?: string;
  beatSync?: boolean;
  beats: number[];
  bpm: number;
  styleConfig: StyleConfig;
}

export const ActionScene: React.FC<ActionSceneProps> = ({
  visual,
  animation,
  lyrics,
  beatSync,
  beats,
  bpm,
  styleConfig,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 节拍同步缩放
  const beatScale = beatSync ? calculateBeatScale(frame, fps, bpm) : 1;

  // 应用动画
  const animationStyle = applyAnimation(animation, frame, fps, durationInFrames);

  // 判断是图片还是视频
  const isVideo = visual.media_type === "video" ||
    (visual.file && (visual.file.endsWith(".mp4") || visual.file.endsWith(".mov")));

  return (
    <AbsoluteFill>
      {/* 背景媒体 */}
      {visual.file && (
        <AbsoluteFill
          style={{
            ...animationStyle,
            transform: `${animationStyle.transform || ""} scale(${beatScale})`,
          }}
        >
          {isVideo ? (
            <Video
              src={visual.file}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
              }}
            />
          ) : (
            <Img
              src={visual.file}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
              }}
            />
          )}
        </AbsoluteFill>
      )}

      {/* 歌词叠加 */}
      {lyrics && (
        <LyricsOverlay
          text={lyrics}
          frame={frame}
          fps={fps}
          styleConfig={styleConfig}
        />
      )}
    </AbsoluteFill>
  );
};

interface LyricsOverlayProps {
  text: string;
  frame: number;
  fps: number;
  styleConfig: StyleConfig;
}

const LyricsOverlay: React.FC<LyricsOverlayProps> = ({
  text,
  frame,
  fps,
  styleConfig,
}) => {
  // 歌词淡入
  const opacity = interpolate(frame, [0, fps * 0.3], [0, 1], {
    extrapolateRight: "clamp",
  });

  // 轻微上浮效果
  const translateY = interpolate(frame, [0, fps * 0.5], [20, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 150,
      }}
    >
      <div
        style={{
          opacity,
          transform: `translateY(${translateY}px)`,
          fontSize: 48,
          fontWeight: "bold",
          color: styleConfig.textColor,
          fontFamily: styleConfig.fontFamily,
          textAlign: "center",
          textShadow: `
            0 0 10px ${styleConfig.primaryColor},
            2px 2px 4px rgba(0,0,0,0.9)
          `,
          padding: "0 40px",
          maxWidth: "90%",
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

/**
 * 计算节拍同步缩放
 */
function calculateBeatScale(frame: number, fps: number, bpm: number): number {
  const beatInterval = (60 / bpm) * fps; // 每拍的帧数
  const beatPhase = (frame % beatInterval) / beatInterval;

  // 在节拍点有轻微放大效果
  const scale = interpolate(
    beatPhase,
    [0, 0.1, 0.5, 1],
    [1.05, 1.02, 1, 1],
    { extrapolateRight: "clamp" }
  );

  return scale;
}
