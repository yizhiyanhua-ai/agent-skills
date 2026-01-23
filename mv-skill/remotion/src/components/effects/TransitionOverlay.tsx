import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import { TransitionType, StyleConfig } from "../../types";

interface TransitionOverlayProps {
  type: TransitionType;
  durationFrames: number;
  styleConfig: StyleConfig;
}

export const TransitionOverlay: React.FC<TransitionOverlayProps> = ({
  type,
  durationFrames,
  styleConfig,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // 转场发生在场景结束前
  const transitionStart = durationInFrames - durationFrames;
  const localFrame = frame - transitionStart;

  if (frame < transitionStart) {
    return null;
  }

  const progress = localFrame / durationFrames;

  switch (type) {
    case "fade":
      return <FadeTransition progress={progress} />;

    case "cross-fade":
      return <CrossFadeTransition progress={progress} />;

    case "flash":
      return <FlashTransition progress={progress} color="#ffffff" />;

    case "impact-frame":
      return (
        <ImpactFrameTransition
          progress={progress}
          colors={[styleConfig.primaryColor, styleConfig.secondaryColor, "#ffffff"]}
        />
      );

    case "wipe-diagonal":
      return <WipeDiagonalTransition progress={progress} />;

    case "glitch":
      return <GlitchTransition progress={progress} />;

    default:
      return null;
  }
};

const FadeTransition: React.FC<{ progress: number }> = ({ progress }) => {
  const opacity = interpolate(progress, [0, 1], [0, 1]);
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#000000",
        opacity,
      }}
    />
  );
};

const CrossFadeTransition: React.FC<{ progress: number }> = ({ progress }) => {
  const opacity = interpolate(progress, [0, 0.5, 1], [0, 0.5, 0]);
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#000000",
        opacity,
      }}
    />
  );
};

interface FlashTransitionProps {
  progress: number;
  color: string;
}

const FlashTransition: React.FC<FlashTransitionProps> = ({ progress, color }) => {
  // 快速闪白然后消失
  const opacity = interpolate(
    progress,
    [0, 0.1, 0.3, 1],
    [0, 1, 1, 0],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: color,
        opacity,
      }}
    />
  );
};

interface ImpactFrameTransitionProps {
  progress: number;
  colors: string[];
}

const ImpactFrameTransition: React.FC<ImpactFrameTransitionProps> = ({
  progress,
  colors,
}) => {
  // 多帧冲击效果
  const frameIndex = Math.floor(progress * colors.length * 2);
  const showFrame = frameIndex < colors.length;

  if (!showFrame) {
    return null;
  }

  const colorIndex = frameIndex % colors.length;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors[colorIndex],
      }}
    />
  );
};

const WipeDiagonalTransition: React.FC<{ progress: number }> = ({ progress }) => {
  const clipPath = `polygon(
    ${interpolate(progress, [0, 1], [100, 0])}% 0%,
    100% 0%,
    100% 100%,
    ${interpolate(progress, [0, 1], [100, 0])}% 100%
  )`;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#000000",
        clipPath,
      }}
    />
  );
};

const GlitchTransition: React.FC<{ progress: number }> = ({ progress }) => {
  const glitchIntensity = interpolate(
    progress,
    [0, 0.5, 1],
    [0, 1, 0]
  );

  // 简单的故障效果：随机位移条纹
  const stripes = Array.from({ length: 10 }, (_, i) => {
    const y = i * 10;
    const offset = Math.sin(progress * Math.PI * 10 + i) * glitchIntensity * 20;

    return (
      <div
        key={i}
        style={{
          position: "absolute",
          left: offset,
          top: `${y}%`,
          width: "100%",
          height: "10%",
          backgroundColor: i % 2 === 0 ? "rgba(255,0,0,0.3)" : "rgba(0,255,255,0.3)",
          mixBlendMode: "difference",
        }}
      />
    );
  });

  if (glitchIntensity < 0.1) {
    return null;
  }

  return <AbsoluteFill>{stripes}</AbsoluteFill>;
};
