import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  OffthreadVideo,
} from "remotion";

interface VideoMixSceneProps {
  videoSrc: string;
  colorScheme: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
  };
  intensity: number;
  overlayEffect: string;
  songTitle?: string;
}

export const VideoMixScene: React.FC<VideoMixSceneProps> = ({
  videoSrc,
  colorScheme,
  intensity = 1,
  overlayEffect = "flash",
  songTitle,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const time = frame / fps;

  // 视频缩放动画 - 轻微的呼吸效果
  const videoScale = interpolate(
    Math.sin(time * 2),
    [-1, 1],
    [1, 1.08],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: colorScheme.background }}>
      {/* 视频背景 */}
      <AbsoluteFill
        style={{
          transform: `scale(${videoScale})`,
          transformOrigin: "center center",
        }}
      >
        <OffthreadVideo
          src={videoSrc}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
          muted
        />
      </AbsoluteFill>

      {/* 3D 粒子效果叠加 */}
      <Particles3DOverlay
        frame={frame}
        fps={fps}
        colors={colorScheme}
        intensity={intensity}
        width={width}
        height={height}
      />

      {/* 3D 光线效果 */}
      <LightBeams3DOverlay
        frame={frame}
        fps={fps}
        colors={colorScheme}
        intensity={intensity}
      />

      {/* 3D 几何图形效果 */}
      <Geometric3DOverlay
        frame={frame}
        fps={fps}
        colors={colorScheme}
        intensity={intensity}
      />

      {/* 节拍闪光效果 */}
      <BeatFlashOverlay
        frame={frame}
        fps={fps}
        colors={colorScheme}
        intensity={intensity}
      />

      {/* 动态效果叠加 */}
      <DynamicOverlay
        effect={overlayEffect}
        frame={frame}
        fps={fps}
        colors={colorScheme}
        intensity={intensity}
      />

      {/* 颜色调色叠加 */}
      <ColorGradingOverlay colors={colorScheme} intensity={intensity * 0.25} />

      {/* 边缘光晕 */}
      <VignetteOverlay colors={colorScheme} intensity={intensity * 0.4} />

      {/* 扫描线效果 */}
      <ScanlineOverlay intensity={intensity * 0.15} />

      {/* 歌曲标题 */}
      {songTitle && (
        <SongTitleOverlay
          title={songTitle}
          frame={frame}
          fps={fps}
          colors={colorScheme}
        />
      )}
    </AbsoluteFill>
  );
};

// 3D 粒子效果
const Particles3DOverlay: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
  width: number;
  height: number;
}> = ({ frame, fps, colors, intensity, width, height }) => {
  const time = frame / fps;
  const particleCount = 30;

  const particles = Array.from({ length: particleCount }, (_, i) => {
    // 使用确定性的伪随机
    const seed = i * 137.5;
    const baseX = ((seed * 7) % 100) / 100;
    const baseY = ((seed * 13) % 100) / 100;
    const speed = 0.5 + ((seed * 3) % 100) / 200;
    const size = 2 + ((seed * 11) % 100) / 25;
    const phase = (seed * 17) % (Math.PI * 2);

    // 3D 运动效果
    const z = Math.sin(time * speed + phase) * 0.5 + 0.5;
    const scale = 0.3 + z * 0.7;
    const x = baseX * width + Math.sin(time * speed * 2 + phase) * 50;
    const y = (baseY * height + time * 100 * speed) % height;

    // 颜色循环
    const colorIndex = Math.floor((time + i * 0.1) * 2) % 3;
    const particleColors = [colors.primary, colors.secondary, colors.accent];
    const color = particleColors[colorIndex];

    return (
      <div
        key={i}
        style={{
          position: "absolute",
          left: x,
          top: y,
          width: size * scale,
          height: size * scale,
          borderRadius: "50%",
          background: color,
          boxShadow: `0 0 ${size * 2}px ${color}, 0 0 ${size * 4}px ${color}`,
          opacity: 0.6 * intensity * scale,
          transform: `scale(${scale})`,
        }}
      />
    );
  });

  return (
    <AbsoluteFill style={{ pointerEvents: "none", overflow: "hidden" }}>
      {particles}
    </AbsoluteFill>
  );
};

// 3D 光线效果
const LightBeams3DOverlay: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;
  const beamCount = 6;

  const beams = Array.from({ length: beamCount }, (_, i) => {
    const angle = (i / beamCount) * 360 + time * 30;
    const length = 150 + Math.sin(time * 3 + i) * 50;
    const width = 3 + Math.sin(time * 2 + i * 0.5) * 2;
    const opacity = 0.3 + Math.sin(time * 4 + i) * 0.2;

    const colorIndex = i % 3;
    const beamColors = [colors.primary, colors.secondary, colors.accent];

    return (
      <div
        key={i}
        style={{
          position: "absolute",
          left: "50%",
          top: "30%",
          width: `${length}%`,
          height: width,
          background: `linear-gradient(90deg, ${beamColors[colorIndex]}00, ${beamColors[colorIndex]}, ${beamColors[colorIndex]}00)`,
          transform: `translateX(-50%) rotate(${angle}deg)`,
          transformOrigin: "left center",
          opacity: opacity * intensity,
          filter: `blur(${1}px)`,
        }}
      />
    );
  });

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        mixBlendMode: "screen",
      }}
    >
      {beams}
    </AbsoluteFill>
  );
};

// 3D 几何图形效果
const Geometric3DOverlay: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  // 旋转的三角形
  const triangleRotation = time * 60;
  const triangleScale = 0.8 + Math.sin(time * 2) * 0.2;

  // 旋转的六边形
  const hexRotation = -time * 40;
  const hexScale = 0.7 + Math.sin(time * 1.5 + 1) * 0.3;

  // 脉冲圆环
  const ringScale = 1 + Math.sin(time * 3) * 0.3;
  const ringOpacity = 0.3 + Math.sin(time * 3) * 0.2;

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* 外圈旋转三角形 */}
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          border: `2px solid ${colors.primary}`,
          opacity: 0.4 * intensity,
          transform: `rotate(${triangleRotation}deg) scale(${triangleScale})`,
          clipPath: "polygon(50% 0%, 0% 100%, 100% 100%)",
          boxShadow: `0 0 20px ${colors.primary}, inset 0 0 20px ${colors.primary}`,
        }}
      />

      {/* 中圈六边形 */}
      <div
        style={{
          position: "absolute",
          width: 300,
          height: 300,
          border: `2px solid ${colors.secondary}`,
          opacity: 0.35 * intensity,
          transform: `rotate(${hexRotation}deg) scale(${hexScale})`,
          clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
          boxShadow: `0 0 15px ${colors.secondary}, inset 0 0 15px ${colors.secondary}`,
        }}
      />

      {/* 内圈脉冲圆环 */}
      <div
        style={{
          position: "absolute",
          width: 200,
          height: 200,
          borderRadius: "50%",
          border: `3px solid ${colors.accent}`,
          opacity: ringOpacity * intensity,
          transform: `scale(${ringScale})`,
          boxShadow: `0 0 25px ${colors.accent}, inset 0 0 25px ${colors.accent}`,
        }}
      />

      {/* 中心点 */}
      <div
        style={{
          position: "absolute",
          width: 20,
          height: 20,
          borderRadius: "50%",
          background: colors.accent,
          boxShadow: `0 0 30px ${colors.accent}, 0 0 60px ${colors.accent}`,
          opacity: 0.8 * intensity,
        }}
      />
    </AbsoluteFill>
  );
};

// 节拍闪光效果
const BeatFlashOverlay: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  // 模拟节拍 - 每 0.5 秒一次
  const beatPhase = (time * 2) % 1;
  const flashOpacity = interpolate(
    beatPhase,
    [0, 0.05, 0.15],
    [0.5, 0.3, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 只在节拍点闪光
  if (beatPhase > 0.15) return null;

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 50% 30%, ${colors.accent}${Math.floor(flashOpacity * 255 * intensity).toString(16).padStart(2, '0')}, transparent 60%)`,
        mixBlendMode: "screen",
      }}
    />
  );
};

// 动态效果选择器
const DynamicOverlay: React.FC<{
  effect: string;
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ effect, frame, fps, colors, intensity }) => {
  const time = frame / fps;

  switch (effect) {
    case "glitch":
      return <GlitchEffect time={time} frame={frame} colors={colors} intensity={intensity} />;
    case "strobe":
      return <StrobeEffect time={time} intensity={intensity} />;
    case "color-shift":
      return <ColorShiftEffect time={time} colors={colors} intensity={intensity} />;
    default:
      return null;
  }
};

// 故障效果
const GlitchEffect: React.FC<{
  time: number;
  frame: number;
  colors: any;
  intensity: number;
}> = ({ time, frame, colors, intensity }) => {
  const glitchTrigger = Math.sin(time * 15 + frame * 0.1) > 0.9;
  if (!glitchTrigger) return null;

  const offsetX = Math.sin(frame * 0.5) * 8 * intensity;

  return (
    <>
      <AbsoluteFill
        style={{
          background: colors.primary,
          mixBlendMode: "multiply",
          opacity: 0.2 * intensity,
          transform: `translateX(${offsetX}px)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: colors.secondary,
          mixBlendMode: "multiply",
          opacity: 0.2 * intensity,
          transform: `translateX(${-offsetX}px)`,
        }}
      />
    </>
  );
};

// 频闪效果
const StrobeEffect: React.FC<{
  time: number;
  intensity: number;
}> = ({ time, intensity }) => {
  const strobeOn = Math.sin(time * 20) > 0.85;
  if (!strobeOn) return null;

  return (
    <AbsoluteFill
      style={{
        background: `rgba(255,255,255,${0.3 * intensity})`,
        mixBlendMode: "overlay",
      }}
    />
  );
};

// 颜色偏移效果
const ColorShiftEffect: React.FC<{
  time: number;
  colors: any;
  intensity: number;
}> = ({ time, colors, intensity }) => {
  const hueShift = (time * 45) % 360;

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(${hueShift}deg, ${colors.primary}15, ${colors.secondary}15, ${colors.accent}15)`,
        mixBlendMode: "overlay",
        opacity: intensity * 0.6,
      }}
    />
  );
};

// 颜色调色叠加
const ColorGradingOverlay: React.FC<{
  colors: any;
  intensity: number;
}> = ({ colors, intensity }) => {
  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${colors.primary}${Math.floor(intensity * 40).toString(16).padStart(2, '0')}, transparent 50%, ${colors.secondary}${Math.floor(intensity * 40).toString(16).padStart(2, '0')})`,
        mixBlendMode: "overlay",
      }}
    />
  );
};

// 暗角效果
const VignetteOverlay: React.FC<{
  colors: any;
  intensity: number;
}> = ({ colors, intensity }) => {
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at center, transparent 35%, ${colors.background}${Math.floor(intensity * 180).toString(16).padStart(2, '0')} 100%)`,
        pointerEvents: "none",
      }}
    />
  );
};

// 扫描线效果
const ScanlineOverlay: React.FC<{
  intensity: number;
}> = ({ intensity }) => {
  return (
    <AbsoluteFill
      style={{
        background: `repeating-linear-gradient(
          0deg,
          transparent,
          transparent 2px,
          rgba(0,0,0,${0.1 * intensity}) 2px,
          rgba(0,0,0,${0.1 * intensity}) 4px
        )`,
        pointerEvents: "none",
      }}
    />
  );
};

// 歌曲标题叠加
const SongTitleOverlay: React.FC<{
  title: string;
  frame: number;
  fps: number;
  colors: any;
}> = ({ title, frame, fps, colors }) => {
  const entranceProgress = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
    durationInFrames: Math.floor(fps * 0.8),
  });

  const exitProgress = spring({
    frame: frame - Math.floor(fps * 2.5),
    fps,
    config: { damping: 200 },
    durationInFrames: Math.floor(fps * 0.5),
  });

  const opacity = interpolate(
    entranceProgress - exitProgress,
    [0, 1],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const translateY = interpolate(
    entranceProgress,
    [0, 1],
    [50, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const scale = interpolate(
    entranceProgress,
    [0, 1],
    [0.8, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 180,
      }}
    >
      <div
        style={{
          opacity,
          transform: `translateY(${translateY}px) scale(${scale})`,
          fontSize: 52,
          fontWeight: "bold",
          color: "#fff",
          textShadow: `
            0 0 20px ${colors.primary},
            0 0 40px ${colors.primary},
            0 0 60px ${colors.secondary},
            2px 2px 4px rgba(0,0,0,0.8)
          `,
          fontFamily: "Orbitron, Noto Sans SC, sans-serif",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
        }}
      >
        {title}
      </div>
    </AbsoluteFill>
  );
};

export default VideoMixScene;
