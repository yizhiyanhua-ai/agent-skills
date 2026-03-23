import React from "react";
import {
  AbsoluteFill,
  Img,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  staticFile,
} from "remotion";
import { Visual, AnimationType, StyleConfig } from "../../types";
import { applyAnimation } from "../animations/animationUtils";

interface TitleSceneProps {
  text: string;
  subtitle?: string;
  visual: Visual;
  animation: AnimationType;
  styleConfig: StyleConfig;
}

export const TitleScene: React.FC<TitleSceneProps> = ({
  text,
  subtitle,
  visual,
  animation,
  styleConfig,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 文字动画
  const textOpacity = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });

  const textScale = spring({
    frame,
    fps,
    config: {
      damping: 100,
      stiffness: 200,
      mass: 0.5,
    },
  });

  // 副标题延迟出现
  const subtitleOpacity = interpolate(
    frame,
    [fps * 0.3, fps * 0.8],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 背景动画
  const bgStyle = applyAnimation(animation, frame, fps, durationInFrames);

  // 获取媒体文件路径
  const mediaSrc = visual.file ? staticFile(visual.file) : null;

  return (
    <AbsoluteFill>
      {/* 背景图像 */}
      {mediaSrc && (
        <AbsoluteFill style={bgStyle}>
          <Img
            src={mediaSrc}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
          {/* 暗化遮罩 */}
          <AbsoluteFill
            style={{
              background: `linear-gradient(
                to bottom,
                rgba(0,0,0,0.3) 0%,
                rgba(0,0,0,0.6) 50%,
                rgba(0,0,0,0.3) 100%
              )`,
            }}
          />
        </AbsoluteFill>
      )}

      {/* 标题文字 */}
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div
          style={{
            opacity: textOpacity,
            transform: `scale(${textScale})`,
            textAlign: "center",
          }}
        >
          {/* 主标题 */}
          <h1
            style={{
              fontSize: 80,
              fontWeight: "bold",
              color: styleConfig.textColor,
              fontFamily: styleConfig.fontFamily,
              textShadow: `
                0 0 20px ${styleConfig.primaryColor},
                0 0 40px ${styleConfig.primaryColor},
                2px 2px 4px rgba(0,0,0,0.8)
              `,
              margin: 0,
              letterSpacing: "0.1em",
            }}
          >
            {text}
          </h1>

          {/* 副标题 */}
          {subtitle && (
            <h2
              style={{
                opacity: subtitleOpacity,
                fontSize: 32,
                fontWeight: "normal",
                color: styleConfig.secondaryColor,
                fontFamily: "Bebas Neue, sans-serif",
                textShadow: "2px 2px 4px rgba(0,0,0,0.8)",
                marginTop: 20,
                letterSpacing: "0.3em",
              }}
            >
              {subtitle}
            </h2>
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
