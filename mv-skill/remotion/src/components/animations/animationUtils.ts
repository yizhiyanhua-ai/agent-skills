import { interpolate, Easing } from "remotion";
import { AnimationType } from "../../types";

/**
 * 应用动画效果并返回 CSS 样式
 */
export function applyAnimation(
  animation: AnimationType,
  frame: number,
  fps: number,
  durationInFrames: number
): React.CSSProperties {
  const progress = frame / durationInFrames;

  switch (animation) {
    case "zoom-in":
      return {
        transform: `scale(${interpolate(progress, [0, 1], [1, 1.3])})`,
      };

    case "zoom-out":
      return {
        transform: `scale(${interpolate(progress, [0, 1], [1.3, 1])})`,
      };

    case "pan-left":
      return {
        transform: `translateX(${interpolate(progress, [0, 1], [5, -5])}%)`,
      };

    case "pan-right":
      return {
        transform: `translateX(${interpolate(progress, [0, 1], [-5, 5])}%)`,
      };

    case "pan-up":
      return {
        transform: `translateY(${interpolate(progress, [0, 1], [5, -5])}%)`,
      };

    case "pan-down":
      return {
        transform: `translateY(${interpolate(progress, [0, 1], [-5, 5])}%)`,
      };

    case "shake":
      return applyShake(frame, fps);

    case "ken-burns":
      return applyKenBurns(progress);

    case "rotate":
      return {
        transform: `rotate(${interpolate(progress, [0, 1], [0, 5])}deg) scale(1.1)`,
      };

    case "flash":
    case "speed-lines":
    case "none":
    default:
      return {};
  }
}

/**
 * 震动效果
 */
function applyShake(frame: number, fps: number): React.CSSProperties {
  const intensity = 10;
  const frequency = 15;

  // 使用正弦波创建震动
  const phase = (frame / fps) * frequency * Math.PI * 2;
  const offsetX = Math.sin(phase) * intensity;
  const offsetY = Math.cos(phase * 1.3) * intensity * 0.7;

  // 随时间衰减
  const decay = Math.exp(-frame / (fps * 2));

  return {
    transform: `translate(${offsetX * decay}px, ${offsetY * decay}px)`,
  };
}

/**
 * Ken Burns 效果（缓慢推移）
 */
function applyKenBurns(progress: number): React.CSSProperties {
  const scale = interpolate(progress, [0, 1], [1, 1.15], {
    easing: Easing.inOut(Easing.ease),
  });

  const translateX = interpolate(progress, [0, 1], [0, 3], {
    easing: Easing.inOut(Easing.ease),
  });

  return {
    transform: `scale(${scale}) translateX(${translateX}%)`,
  };
}

/**
 * 速度线效果参数
 */
export interface SpeedLinesConfig {
  count: number;
  speed: number;
  color: string;
  angle: number;
}

export const defaultSpeedLinesConfig: SpeedLinesConfig = {
  count: 20,
  speed: 2000,
  color: "#ffffff",
  angle: 0,
};
