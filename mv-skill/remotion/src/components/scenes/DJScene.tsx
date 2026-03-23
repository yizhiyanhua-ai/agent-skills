import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  spring,
} from "remotion";

// 辅助函数：平滑的脉冲动画（替代 Math.sin）
const smoothPulse = (frame: number, fps: number, frequency: number = 1): number => {
  const time = frame / fps;
  return interpolate(
    Math.sin(time * frequency * Math.PI * 2),
    [-1, 1],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
};

// 辅助函数：弹性缩放动画
const springScale = (frame: number, fps: number, delay: number = 0): number => {
  return spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 100 },
  });
};

interface DJSceneProps {
  visualType: string;
  colorScheme: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
  };
  intensity: number;
  songTitle?: string;
}

export const DJScene: React.FC<DJSceneProps> = ({
  visualType,
  colorScheme,
  intensity = 1,
  songTitle,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 根据类型渲染不同的视觉效果
  const renderVisual = () => {
    switch (visualType) {
      case "nightclub":
        return <NightclubVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "festival":
        return <FestivalVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "lasershow":
        return <LasershowVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "djbooth":
        return <DJBoothVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "crowd":
        return <CrowdVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "waveform":
        return <WaveformVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "spectrum":
        return <SpectrumVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "particles":
        return <ParticleVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "geometric":
        return <GeometricVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "tunnel":
        return <TunnelVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "ledwall":
        return <LEDWallVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "mirrorball":
        return <MirrorBallVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "smokelaser":
        return <SmokeAndLaserVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "strobevj":
        return <StrobeVJVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "cube3d":
        return <Cube3DVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "vortex3d":
        return <Vortex3DVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "neonroom":
        return <NeonRoomVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "cyberwave":
        return <CyberwaveVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      case "hologram":
        return <HologramVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
      default:
        return <Vortex3DVisual frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />;
    }
  };

  return (
    <AbsoluteFill style={{ backgroundColor: colorScheme.background }}>
      {renderVisual()}
      {/* 3D 多彩迷雾烟尘效果 */}
      <ColorfulFog3D frame={frame} fps={fps} colors={colorScheme} intensity={intensity} />
      {songTitle && (
        <SongTitleOverlay title={songTitle} frame={frame} fps={fps} colors={colorScheme} />
      )}
    </AbsoluteFill>
  );
};

// 3D 多彩迷雾烟尘效果（简化版）
const ColorfulFog3D: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden", pointerEvents: "none" }}>
      {/* 底部迷雾层 */}
      {Array.from({ length: 3 }).map((_, i) => {
        const hue = (i * 120 + time * 15) % 360;
        const yOffset = Math.sin(time * 0.4 + i * 0.8) * 3;
        const opacity = interpolate(
          Math.sin(time * 0.6 + i),
          [-1, 1],
          [0.2, 0.4],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        return (
          <div
            key={`fog-bottom-${i}`}
            style={{
              position: "absolute",
              bottom: `${-5 + i * 10 + yOffset}%`,
              left: "-10%",
              width: "120%",
              height: "25%",
              background: `radial-gradient(ellipse at 50% 100%, hsla(${hue}, 80%, 50%, ${opacity}), transparent 70%)`,
              filter: "blur(30px)",
            }}
          />
        );
      })}

      {/* 顶部迷雾层 */}
      {Array.from({ length: 2 }).map((_, i) => {
        const hue = (i * 180 + time * 20 + 90) % 360;
        const yOffset = Math.sin(time * 0.3 + i * 0.5) * 3;
        const opacity = interpolate(
          Math.sin(time * 0.5 + i * 1.2),
          [-1, 1],
          [0.15, 0.3],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        return (
          <div
            key={`fog-top-${i}`}
            style={{
              position: "absolute",
              top: `${-10 + i * 8 + yOffset}%`,
              left: "-5%",
              width: "110%",
              height: "20%",
              background: `radial-gradient(ellipse at 50% 0%, hsla(${hue}, 70%, 55%, ${opacity}), transparent 70%)`,
              filter: "blur(25px)",
            }}
          />
        );
      })}

      {/* 侧边飘动的烟尘 */}
      {Array.from({ length: 4 }).map((_, i) => {
        const side = i % 2 === 0 ? "left" : "right";
        const hue = (i * 90 + time * 25) % 360;
        const yPos = 20 + i * 20 + Math.sin(time * 0.4 + i) * 10;
        const opacity = interpolate(
          Math.sin(time * 0.5 + i * 0.7),
          [-1, 1],
          [0.1, 0.25],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        return (
          <div
            key={`fog-side-${i}`}
            style={{
              position: "absolute",
              top: `${yPos}%`,
              [side]: "-10%",
              width: "35%",
              height: "18%",
              background: `radial-gradient(ellipse, hsla(${hue}, 75%, 55%, ${opacity}), transparent 70%)`,
              filter: "blur(25px)",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// 夜店场景
const NightclubVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {/* 深色背景渐变 */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: `radial-gradient(ellipse at 50% 100%, ${colors.primary}33 0%, ${colors.background} 70%)`,
        }}
      />

      {/* 舞池地板反光 */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          width: "100%",
          height: "40%",
          background: `linear-gradient(to top, ${colors.primary}22, transparent)`,
          transform: `perspective(500px) rotateX(60deg)`,
          transformOrigin: "bottom center",
        }}
      >
        {/* 地板格子 */}
        {Array.from({ length: 8 }).map((_, i) =>
          Array.from({ length: 6 }).map((_, j) => {
            const pulse = Math.sin(time * 4 + i * 0.5 + j * 0.3) > 0.3;
            return (
              <div
                key={`${i}-${j}`}
                style={{
                  position: "absolute",
                  left: `${i * 12.5}%`,
                  top: `${j * 16.6}%`,
                  width: "12%",
                  height: "15%",
                  background: pulse ? colors.primary : colors.secondary,
                  opacity: pulse ? 0.8 : 0.2,
                  boxShadow: pulse ? `0 0 30px ${colors.primary}` : "none",
                  transition: "all 0.1s",
                }}
              />
            );
          })
        )}
      </div>

      {/* 激光束 */}
      {Array.from({ length: 6 }).map((_, i) => {
        const angle = Math.sin(time * 2 + i) * 30;
        const hue = (i * 60 + time * 50) % 360;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: "10%",
              left: `${15 + i * 14}%`,
              width: 4,
              height: "60%",
              background: `linear-gradient(to bottom, hsl(${hue}, 100%, 60%), transparent)`,
              transform: `rotate(${angle}deg)`,
              transformOrigin: "top center",
              boxShadow: `0 0 20px hsl(${hue}, 100%, 50%)`,
              opacity: 0.8 * intensity,
            }}
          />
        );
      })}

      {/* 闪光灯效果 */}
      {Math.sin(time * 8) > 0.7 && (
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            background: `radial-gradient(circle at 50% 20%, ${colors.accent}88, transparent 50%)`,
          }}
        />
      )}

      {/* 烟雾效果 */}
      <div
        style={{
          position: "absolute",
          width: "200%",
          height: "100%",
          background: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.02' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          opacity: 0.15,
          transform: `translateX(${-time * 20 % 100}px)`,
        }}
      />
    </AbsoluteFill>
  );
};

// 露天音乐节场景
const FestivalVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {/* 夜空背景 */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: `linear-gradient(to bottom, #0a0a20 0%, #1a1a40 50%, ${colors.background} 100%)`,
        }}
      />

      {/* 星星 */}
      {Array.from({ length: 50 }).map((_, i) => {
        const x = (i * 37) % 100;
        const y = (i * 23) % 40;
        const twinkle = Math.sin(time * 3 + i) * 0.5 + 0.5;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: 2 + (i % 3),
              height: 2 + (i % 3),
              borderRadius: "50%",
              background: "#fff",
              opacity: twinkle * 0.8,
              boxShadow: `0 0 ${4 + twinkle * 4}px #fff`,
            }}
          />
        );
      })}

      {/* 舞台灯光 */}
      {Array.from({ length: 8 }).map((_, i) => {
        const angle = Math.sin(time * 1.5 + i * 0.8) * 40;
        const hue = (i * 45 + time * 30) % 360;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              bottom: "30%",
              left: `${5 + i * 12}%`,
              width: 100,
              height: 400,
              background: `linear-gradient(to top, hsl(${hue}, 100%, 50%) 0%, transparent 100%)`,
              transform: `rotate(${angle}deg)`,
              transformOrigin: "bottom center",
              opacity: 0.4 * intensity,
              filter: "blur(10px)",
            }}
          />
        );
      })}

      {/* 舞台轮廓 */}
      <div
        style={{
          position: "absolute",
          bottom: "25%",
          left: "10%",
          width: "80%",
          height: "8%",
          background: `linear-gradient(to top, ${colors.primary}44, transparent)`,
          borderTop: `2px solid ${colors.primary}`,
          boxShadow: `0 -10px 40px ${colors.primary}66`,
        }}
      />

      {/* 人群剪影 */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          width: "100%",
          height: "30%",
          background: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 30'%3E%3Cpath d='M0,30 Q5,${20 + Math.sin(time * 4) * 5} 10,30 Q15,${18 + Math.sin(time * 4 + 1) * 5} 20,30 Q25,${22 + Math.sin(time * 4 + 2) * 5} 30,30 Q35,${19 + Math.sin(time * 4 + 3) * 5} 40,30 Q45,${21 + Math.sin(time * 4 + 4) * 5} 50,30 Q55,${18 + Math.sin(time * 4 + 5) * 5} 60,30 Q65,${23 + Math.sin(time * 4 + 6) * 5} 70,30 Q75,${20 + Math.sin(time * 4 + 7) * 5} 80,30 Q85,${19 + Math.sin(time * 4 + 8) * 5} 90,30 Q95,${22 + Math.sin(time * 4 + 9) * 5} 100,30 L100,30 L0,30 Z' fill='%23000'/%3E%3C/svg%3E") repeat-x`,
          backgroundSize: "200px 100%",
          opacity: 0.9,
        }}
      />

      {/* 手机闪光灯 */}
      {Array.from({ length: 20 }).map((_, i) => {
        const x = (i * 47 + time * 10) % 100;
        const y = 70 + (i % 5) * 5;
        const on = Math.sin(time * 5 + i * 2) > 0.6;
        return on ? (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: 4,
              height: 4,
              borderRadius: "50%",
              background: "#fff",
              boxShadow: "0 0 10px #fff",
            }}
          />
        ) : null;
      })}
    </AbsoluteFill>
  );
};

// 激光秀
const LasershowVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: colors.background }}>
      {/* 中心光源 */}
      <div
        style={{
          position: "absolute",
          top: "20%",
          left: "50%",
          width: 20,
          height: 20,
          borderRadius: "50%",
          background: colors.accent,
          boxShadow: `0 0 60px 30px ${colors.accent}`,
          transform: "translateX(-50%)",
        }}
      />

      {/* 激光束扇形 */}
      {Array.from({ length: 12 }).map((_, i) => {
        const baseAngle = (i / 12) * 360;
        const angle = baseAngle + Math.sin(time * 2 + i * 0.5) * 20;
        const length = 800 + Math.sin(time * 3 + i) * 200;
        const hue = (baseAngle + time * 60) % 360;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: "20%",
              left: "50%",
              width: 3,
              height: length,
              background: `linear-gradient(to bottom, hsl(${hue}, 100%, 60%), transparent)`,
              transform: `rotate(${angle}deg)`,
              transformOrigin: "top center",
              boxShadow: `0 0 15px hsl(${hue}, 100%, 50%)`,
              opacity: 0.7 * intensity,
            }}
          />
        );
      })}

      {/* 扫描激光 */}
      {Array.from({ length: 4 }).map((_, i) => {
        const sweep = (time * 100 + i * 90) % 360;
        return (
          <div
            key={`sweep-${i}`}
            style={{
              position: "absolute",
              top: "20%",
              left: "50%",
              width: 2,
              height: 1000,
              background: `linear-gradient(to bottom, ${colors.primary}, transparent)`,
              transform: `rotate(${sweep}deg)`,
              transformOrigin: "top center",
              opacity: 0.5,
            }}
          />
        );
      })}

      {/* 烟雾中的光束散射 */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: `radial-gradient(ellipse at 50% 20%, ${colors.primary}22, transparent 60%)`,
        }}
      />
    </AbsoluteFill>
  );
};

// DJ 台场景
const DJBoothVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: colors.background }}>
      {/* 背景光效 */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: `radial-gradient(ellipse at 50% 30%, ${colors.primary}33, transparent 70%)`,
        }}
      />

      {/* DJ 台轮廓 */}
      <div
        style={{
          position: "absolute",
          bottom: "20%",
          left: "20%",
          width: "60%",
          height: "35%",
          background: `linear-gradient(to top, ${colors.background}, #1a1a2a)`,
          borderRadius: "10px 10px 0 0",
          border: `2px solid ${colors.primary}44`,
          boxShadow: `0 0 30px ${colors.primary}33`,
        }}
      >
        {/* 设备面板 */}
        <div
          style={{
            position: "absolute",
            top: "10%",
            left: "5%",
            width: "90%",
            height: "60%",
            display: "flex",
            justifyContent: "space-around",
            alignItems: "center",
          }}
        >
          {/* 左转盘 */}
          <div
            style={{
              width: 120,
              height: 120,
              borderRadius: "50%",
              background: `conic-gradient(from ${time * 180}deg, #333, #111, #333, #111, #333)`,
              border: `3px solid ${colors.secondary}`,
              boxShadow: `0 0 20px ${colors.secondary}44`,
            }}
          />

          {/* 混音台 */}
          <div
            style={{
              width: 100,
              height: 140,
              background: "#1a1a1a",
              borderRadius: 5,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-around",
              alignItems: "center",
              padding: 10,
            }}
          >
            {Array.from({ length: 4 }).map((_, i) => {
              // 使用确定性伪随机替代 Math.random()
              const pseudoRandom = Math.sin(i * 43.758 + time * 5) * 0.5 + 0.5;
              const level = interpolate(
                Math.sin(time * 6 + i * 2) * 0.5 + 0.5 + pseudoRandom * 0.3,
                [0, 1.3],
                [20, 90],
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
              );
              return (
                <div
                  key={i}
                  style={{
                    width: "80%",
                    height: 15,
                    background: "#333",
                    borderRadius: 3,
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${level}%`,
                      height: "100%",
                      background: `linear-gradient(to right, ${colors.secondary}, ${colors.primary})`,
                      boxShadow: `0 0 10px ${colors.primary}`,
                    }}
                  />
                </div>
              );
            })}
          </div>

          {/* 右转盘 */}
          <div
            style={{
              width: 120,
              height: 120,
              borderRadius: "50%",
              background: `conic-gradient(from ${-time * 180}deg, #333, #111, #333, #111, #333)`,
              border: `3px solid ${colors.secondary}`,
              boxShadow: `0 0 20px ${colors.secondary}44`,
            }}
          />
        </div>
      </div>

      {/* 顶部灯光 */}
      {Array.from({ length: 5 }).map((_, i) => {
        const pulse = Math.sin(time * 4 + i) > 0;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: "5%",
              left: `${15 + i * 17}%`,
              width: 30,
              height: 200,
              background: `linear-gradient(to bottom, ${pulse ? colors.primary : colors.secondary}, transparent)`,
              opacity: pulse ? 0.6 : 0.2,
              filter: "blur(5px)",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// 人群狂欢
const CrowdVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: colors.background }}>
      {/* 舞台灯光 */}
      <div
        style={{
          position: "absolute",
          top: 0,
          width: "100%",
          height: "50%",
          background: `radial-gradient(ellipse at 50% 0%, ${colors.primary}66, transparent 70%)`,
        }}
      />

      {/* 频闪效果 */}
      {Math.sin(time * 10) > 0.8 && (
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            background: `rgba(255,255,255,0.3)`,
          }}
        />
      )}

      {/* 人群 - 多层 */}
      {[0.6, 0.75, 0.9].map((yPos, layer) => (
        <div
          key={layer}
          style={{
            position: "absolute",
            bottom: `${(1 - yPos) * 100}%`,
            width: "100%",
            height: `${yPos * 50}%`,
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-end",
          }}
        >
          {Array.from({ length: 15 + layer * 5 }).map((_, i) => {
            const jump = Math.sin(time * 6 + i * 0.5 + layer) * (10 + layer * 5);
            const sway = Math.sin(time * 3 + i * 0.3) * 5;
            const height = 60 + (i % 3) * 20 - layer * 10;
            return (
              <div
                key={i}
                style={{
                  width: 20 + layer * 5,
                  height: height,
                  background: `linear-gradient(to top, #000, #222)`,
                  borderRadius: "50% 50% 0 0",
                  margin: `0 ${2 + layer}px`,
                  transform: `translateY(${-Math.max(0, jump)}px) translateX(${sway}px)`,
                }}
              >
                {/* 手臂 */}
                {jump > 5 && (
                  <>
                    <div
                      style={{
                        position: "absolute",
                        top: 10,
                        left: -10,
                        width: 4,
                        height: 30,
                        background: "#000",
                        transform: `rotate(${-30 + sway}deg)`,
                        transformOrigin: "bottom right",
                      }}
                    />
                    <div
                      style={{
                        position: "absolute",
                        top: 10,
                        right: -10,
                        width: 4,
                        height: 30,
                        background: "#000",
                        transform: `rotate(${30 - sway}deg)`,
                        transformOrigin: "bottom left",
                      }}
                    />
                  </>
                )}
              </div>
            );
          })}
        </div>
      ))}

      {/* 彩带/纸屑 */}
      {Array.from({ length: 30 }).map((_, i) => {
        const x = (i * 37 + time * 50) % 120 - 10;
        const y = (i * 23 + time * 100) % 120 - 10;
        const hue = (i * 30) % 360;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: 8,
              height: 3,
              background: `hsl(${hue}, 100%, 60%)`,
              transform: `rotate(${time * 200 + i * 45}deg)`,
              opacity: 0.7,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// 波形可视化
const WaveformVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const bars = 40;
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, height: "60%" }}>
        {Array.from({ length: bars }).map((_, i) => {
          // 模拟音频波形
          const phase = (i / bars) * Math.PI * 4 + time * 8;
          const height = 50 + Math.sin(phase) * 40 * intensity + Math.sin(phase * 2.5) * 20;

          return (
            <div
              key={i}
              style={{
                width: 12,
                height: `${height}%`,
                background: `linear-gradient(to top, ${colors.primary}, ${colors.secondary})`,
                borderRadius: 6,
                boxShadow: `0 0 20px ${colors.primary}`,
                transform: `scaleY(${0.8 + Math.sin(phase + time * 4) * 0.2})`,
              }}
            />
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// 频谱可视化
const SpectrumVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const bars = 64;
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 100 }}>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 4, height: "70%" }}>
        {Array.from({ length: bars }).map((_, i) => {
          // 模拟频谱分析 - 使用确定性动画避免闪烁
          const freq = i / bars;
          const bassBoost = freq < 0.2 ? 1.5 : 1;
          // 使用多个正弦波叠加模拟随机感，但保持确定性
          const pseudoRandom = Math.sin(i * 12.9898 + time * 3) * 0.5 + 0.5;
          const height = interpolate(
            (Math.sin(time * 6 + i * 0.3) * 0.5 + 0.5) * 0.5 +
            (Math.sin(time * 12 + i * 0.5) * 0.5 + 0.5) * 0.3 +
            pseudoRandom * 0.2,
            [0, 1],
            [15, 85],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
          ) * intensity * bassBoost;

          const hue = (i / bars) * 60 + 280; // 紫色到粉色渐变

          return (
            <div
              key={i}
              style={{
                width: 8,
                height: `${Math.max(5, height)}%`,
                background: `hsl(${hue}, 100%, 60%)`,
                borderRadius: "4px 4px 0 0",
                boxShadow: `0 0 15px hsl(${hue}, 100%, 50%)`,
                // 移除 CSS transition - Remotion 不支持
              }}
            />
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// 粒子效果
const ParticleVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const particleCount = 50;
  const time = frame / fps;

  return (
    <AbsoluteFill>
      {Array.from({ length: particleCount }).map((_, i) => {
        const seed = i * 137.5;
        const x = ((seed * 7.3) % 100);
        const baseY = ((seed * 13.7) % 100);
        const y = (baseY + time * (20 + (seed % 30))) % 120 - 10;
        const size = 4 + (seed % 12);
        const opacity = 0.3 + (Math.sin(time * 3 + seed) + 1) * 0.35;
        const hue = (seed % 60) + 280;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: size,
              height: size,
              borderRadius: "50%",
              background: `hsl(${hue}, 100%, 70%)`,
              opacity: opacity * intensity,
              boxShadow: `0 0 ${size * 2}px hsl(${hue}, 100%, 60%)`,
              transform: `scale(${1 + Math.sin(time * 5 + seed) * 0.3})`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// 几何图形动画
const GeometricVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;
  const shapes = 8;

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      {Array.from({ length: shapes }).map((_, i) => {
        const angle = (i / shapes) * Math.PI * 2 + time * 0.5;
        const radius = 200 + Math.sin(time * 2 + i) * 50;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        const rotation = time * 60 + i * 45;
        const scale = 0.8 + Math.sin(time * 3 + i * 0.5) * 0.3;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              width: 80,
              height: 80,
              border: `3px solid ${colors.primary}`,
              transform: `translate(${x}px, ${y}px) rotate(${rotation}deg) scale(${scale * intensity})`,
              boxShadow: `0 0 30px ${colors.primary}, inset 0 0 20px ${colors.secondary}`,
            }}
          />
        );
      })}
      {/* 中心圆环 */}
      <div
        style={{
          width: 150,
          height: 150,
          borderRadius: "50%",
          border: `4px solid ${colors.secondary}`,
          boxShadow: `0 0 40px ${colors.secondary}, 0 0 80px ${colors.primary}`,
          transform: `scale(${1 + Math.sin(time * 4) * 0.2 * intensity})`,
        }}
      />
    </AbsoluteFill>
  );
};

// 霓虹灯效果
const NeonVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      {/* 霓虹网格 */}
      <div
        style={{
          position: "absolute",
          width: "200%",
          height: "200%",
          backgroundImage: `
            linear-gradient(${colors.primary}22 1px, transparent 1px),
            linear-gradient(90deg, ${colors.primary}22 1px, transparent 1px)
          `,
          backgroundSize: "50px 50px",
          transform: `perspective(500px) rotateX(60deg) translateY(${-time * 100 % 50}px)`,
          transformOrigin: "center center",
        }}
      />
      {/* 霓虹圆环 */}
      {[1, 2, 3].map((ring) => (
        <div
          key={ring}
          style={{
            position: "absolute",
            width: 200 + ring * 100,
            height: 200 + ring * 100,
            borderRadius: "50%",
            border: `2px solid ${ring % 2 === 0 ? colors.primary : colors.secondary}`,
            opacity: 0.6 - ring * 0.15,
            boxShadow: `0 0 30px ${ring % 2 === 0 ? colors.primary : colors.secondary}`,
            transform: `scale(${1 + Math.sin(time * 2 + ring) * 0.1 * intensity})`,
          }}
        />
      ))}
      {/* 中心光点 */}
      <div
        style={{
          width: 20,
          height: 20,
          borderRadius: "50%",
          background: colors.accent,
          boxShadow: `0 0 60px 30px ${colors.accent}`,
          transform: `scale(${1 + Math.sin(time * 6) * 0.5 * intensity})`,
        }}
      />
    </AbsoluteFill>
  );
};

// 隧道效果
const TunnelVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;
  const rings = 15;

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", overflow: "hidden" }}>
      {Array.from({ length: rings }).map((_, i) => {
        const progress = ((time * 0.5 + i / rings) % 1);
        const scale = 0.1 + progress * 3;
        const opacity = 1 - progress;
        const rotation = time * 30 + i * 24;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              width: 400,
              height: 400,
              border: `3px solid ${i % 2 === 0 ? colors.primary : colors.secondary}`,
              borderRadius: i % 3 === 0 ? "50%" : "0",
              transform: `scale(${scale}) rotate(${rotation}deg)`,
              opacity: opacity * intensity,
              boxShadow: `0 0 20px ${i % 2 === 0 ? colors.primary : colors.secondary}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// 歌曲标题叠加 - 使用 spring 动画实现更自然的入场效果
const SongTitleOverlay: React.FC<{
  title: string;
  frame: number;
  fps: number;
  colors: any;
}> = ({ title, frame, fps, colors }) => {
  // 使用 spring 实现弹性入场
  const entranceProgress = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
    durationInFrames: Math.floor(fps * 0.8),
  });

  // 淡出动画
  const exitProgress = spring({
    frame: frame - Math.floor(fps * 2),
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
        paddingBottom: 200,
      }}
    >
      <div
        style={{
          opacity,
          transform: `translateY(${translateY}px) scale(${scale})`,
          fontSize: 48,
          fontWeight: "bold",
          color: "#fff",
          textShadow: `
            0 0 20px ${colors.primary},
            0 0 40px ${colors.primary},
            0 0 60px ${colors.secondary}
          `,
          fontFamily: "Noto Sans SC, sans-serif",
          letterSpacing: "0.1em",
        }}
      >
        {title}
      </div>
    </AbsoluteFill>
  );
};

// LED 屏幕墙效果
const LEDWallVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;
  const cols = 20;
  const rows = 35;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      {/* LED 像素网格 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gridTemplateRows: `repeat(${rows}, 1fr)`,
          width: "100%",
          height: "100%",
          gap: 2,
          padding: 4,
        }}
      >
        {Array.from({ length: cols * rows }).map((_, i) => {
          const x = i % cols;
          const y = Math.floor(i / cols);

          // 波浪效果
          const wave1 = Math.sin(time * 4 + x * 0.3 + y * 0.2) * 0.5 + 0.5;
          const wave2 = Math.sin(time * 3 - x * 0.2 + y * 0.4) * 0.5 + 0.5;
          const wave3 = Math.sin(time * 5 + (x + y) * 0.15) * 0.5 + 0.5;

          // 随机闪烁
          const flicker = Math.sin(time * 20 + i * 0.7) > 0.9 ? 1.5 : 1;

          const brightness = (wave1 * 0.4 + wave2 * 0.3 + wave3 * 0.3) * intensity * flicker;
          const hue = (time * 30 + x * 5 + y * 3) % 360;

          return (
            <div
              key={i}
              style={{
                background: `hsla(${hue}, 100%, ${50 * brightness}%, ${brightness})`,
                boxShadow: brightness > 0.7 ? `0 0 10px hsla(${hue}, 100%, 60%, 0.8)` : "none",
              }}
            />
          );
        })}
      </div>

      {/* 扫描线效果 */}
      <div
        style={{
          position: "absolute",
          top: `${(time * 50) % 100}%`,
          left: 0,
          width: "100%",
          height: 4,
          background: `linear-gradient(to right, transparent, ${colors.accent}, transparent)`,
          opacity: 0.6,
        }}
      />
    </AbsoluteFill>
  );
};

// 镜球效果
const MirrorBallVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;
  const reflections = 40;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: colors.background }}>
      {/* 镜球本体 */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: "50%",
          width: 150,
          height: 150,
          borderRadius: "50%",
          background: `radial-gradient(circle at 30% 30%, #fff, #888, #333)`,
          transform: `translateX(-50%) rotate(${time * 30}deg)`,
          boxShadow: "0 0 50px rgba(255,255,255,0.3)",
        }}
      >
        {/* 镜面格子 */}
        {Array.from({ length: 24 }).map((_, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              width: "100%",
              height: "100%",
              borderRadius: "50%",
              border: "1px solid rgba(255,255,255,0.3)",
              transform: `rotate(${i * 15}deg)`,
            }}
          />
        ))}
      </div>

      {/* 反射光束 */}
      {Array.from({ length: reflections }).map((_, i) => {
        const angle = (i / reflections) * 360 + time * 60;
        const length = 300 + Math.sin(time * 3 + i) * 100;
        const hue = (i * 20 + time * 40) % 360;
        const opacity = (Math.sin(time * 4 + i * 0.5) + 1) * 0.3 * intensity;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: "20%",
              left: "50%",
              width: 3,
              height: length,
              background: `linear-gradient(to bottom, hsla(${hue}, 100%, 80%, 0.8), transparent)`,
              transform: `rotate(${angle}deg)`,
              transformOrigin: "top center",
              opacity,
            }}
          />
        );
      })}

      {/* 地面光斑 */}
      {Array.from({ length: 20 }).map((_, i) => {
        const x = (i * 47 + time * 30) % 100;
        const y = 60 + (i % 4) * 10;
        const size = 20 + Math.sin(time * 5 + i) * 10;
        const hue = (i * 30 + time * 50) % 360;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: size,
              height: size * 0.3,
              borderRadius: "50%",
              background: `hsla(${hue}, 100%, 70%, 0.6)`,
              filter: "blur(5px)",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// 烟雾机 + 激光效果
const SmokeAndLaserVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: colors.background }}>
      {/* 烟雾层 */}
      {[0, 1, 2].map((layer) => (
        <div
          key={layer}
          style={{
            position: "absolute",
            width: "200%",
            height: "100%",
            background: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.015' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
            opacity: 0.2 - layer * 0.05,
            transform: `translateX(${(-time * (20 + layer * 10)) % 100}px) translateY(${Math.sin(time + layer) * 20}px)`,
          }}
        />
      ))}

      {/* 激光束阵列 */}
      {Array.from({ length: 8 }).map((_, i) => {
        const baseX = 10 + i * 11;
        const angle = Math.sin(time * 2 + i * 0.5) * 25;
        const hue = (i * 45 + time * 60) % 360;
        const on = Math.sin(time * 3 + i * 0.8) > -0.3;

        return on ? (
          <div
            key={i}
            style={{
              position: "absolute",
              top: "5%",
              left: `${baseX}%`,
              width: 4,
              height: "70%",
              background: `linear-gradient(to bottom, hsl(${hue}, 100%, 60%), transparent)`,
              transform: `rotate(${angle}deg)`,
              transformOrigin: "top center",
              boxShadow: `0 0 20px hsl(${hue}, 100%, 50%), 0 0 40px hsl(${hue}, 100%, 40%)`,
              opacity: 0.9 * intensity,
            }}
          />
        ) : null;
      })}

      {/* 交叉激光 */}
      {Array.from({ length: 4 }).map((_, i) => {
        const angle = (time * 40 + i * 90) % 360;
        const hue = (i * 90 + time * 30) % 360;

        return (
          <div
            key={`cross-${i}`}
            style={{
              position: "absolute",
              top: "30%",
              left: "50%",
              width: 2,
              height: 600,
              background: `linear-gradient(to bottom, transparent, hsl(${hue}, 100%, 60%), transparent)`,
              transform: `rotate(${angle}deg)`,
              transformOrigin: "center center",
              opacity: 0.5 * intensity,
            }}
          />
        );
      })}

      {/* 底部烟雾 */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          width: "100%",
          height: "30%",
          background: `linear-gradient(to top, rgba(255,255,255,0.15), transparent)`,
        }}
      />
    </AbsoluteFill>
  );
};

// 频闪 + VJ 效果
const StrobeVJVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  // 频闪节奏
  const strobeOn = Math.sin(time * 16) > 0.7;
  const fastStrobe = Math.sin(time * 30) > 0.9;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: colors.background }}>
      {/* VJ 图形 - 旋转三角形 */}
      {Array.from({ length: 6 }).map((_, i) => {
        const rotation = time * 60 + i * 60;
        const scale = 0.5 + Math.sin(time * 2 + i) * 0.3;
        const hue = (i * 60 + time * 40) % 360;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              width: 0,
              height: 0,
              borderLeft: "100px solid transparent",
              borderRight: "100px solid transparent",
              borderBottom: `180px solid hsla(${hue}, 100%, 50%, 0.3)`,
              transform: `translate(-50%, -50%) rotate(${rotation}deg) scale(${scale})`,
              filter: `drop-shadow(0 0 20px hsl(${hue}, 100%, 50%))`,
            }}
          />
        );
      })}

      {/* 脉冲圆环 */}
      {Array.from({ length: 5 }).map((_, i) => {
        const progress = ((time * 0.8 + i * 0.2) % 1);
        const scale = progress * 4;
        const opacity = (1 - progress) * 0.6;

        return (
          <div
            key={`pulse-${i}`}
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              width: 100,
              height: 100,
              borderRadius: "50%",
              border: `3px solid ${colors.primary}`,
              transform: `translate(-50%, -50%) scale(${scale})`,
              opacity: opacity * intensity,
            }}
          />
        );
      })}

      {/* 频闪效果 */}
      {strobeOn && (
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            background: `rgba(255,255,255,${fastStrobe ? 0.8 : 0.4})`,
          }}
        />
      )}

      {/* 扫描线 */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background: `repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0,0,0,0.1) 2px,
            rgba(0,0,0,0.1) 4px
          )`,
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};

// 3D 立方体效果
const Cube3DVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: colors.background, perspective: 1000 }}>
      {/* 3D 旋转立方体阵列 */}
      {Array.from({ length: 9 }).map((_, i) => {
        const row = Math.floor(i / 3);
        const col = i % 3;
        const rotateX = time * 60 + i * 40;
        const rotateY = time * 80 + i * 30;
        const scale = 0.8 + Math.sin(time * 3 + i) * 0.2;
        const hue = (i * 40 + time * 50) % 360;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${20 + col * 30}%`,
              top: `${20 + row * 25}%`,
              width: 100,
              height: 100,
              transformStyle: "preserve-3d",
              transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(${scale})`,
            }}
          >
            {/* 立方体六个面 */}
            {[0, 1, 2, 3, 4, 5].map((face) => {
              const transforms = [
                "translateZ(50px)",
                "translateZ(-50px) rotateY(180deg)",
                "translateX(50px) rotateY(90deg)",
                "translateX(-50px) rotateY(-90deg)",
                "translateY(-50px) rotateX(90deg)",
                "translateY(50px) rotateX(-90deg)",
              ];
              return (
                <div
                  key={face}
                  style={{
                    position: "absolute",
                    width: 100,
                    height: 100,
                    background: `hsla(${hue + face * 20}, 100%, 50%, 0.3)`,
                    border: `2px solid hsl(${hue + face * 20}, 100%, 60%)`,
                    transform: transforms[face],
                    boxShadow: `inset 0 0 30px hsla(${hue + face * 20}, 100%, 50%, 0.5)`,
                  }}
                />
              );
            })}
          </div>
        );
      })}

      {/* 中心发光球 */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          width: 60,
          height: 60,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${colors.accent}, transparent)`,
          transform: `translate(-50%, -50%) scale(${1 + Math.sin(time * 6) * 0.3})`,
          boxShadow: `0 0 80px 40px ${colors.accent}`,
        }}
      />
    </AbsoluteFill>
  );
};

// 3D 漩涡效果
const Vortex3DVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;
  const rings = 20;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: colors.background, perspective: 800 }}>
      {/* 3D 漩涡环 */}
      {Array.from({ length: rings }).map((_, i) => {
        const progress = (i / rings);
        const z = -500 + progress * 1000;
        const scale = 0.3 + progress * 1.5;
        const rotation = time * 120 + i * 18;
        const opacity = 0.3 + progress * 0.5;
        const hue = (time * 30 + i * 15) % 360;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              width: 300,
              height: 300,
              borderRadius: "50%",
              border: `3px solid hsl(${hue}, 100%, 60%)`,
              transform: `translate(-50%, -50%) translateZ(${z}px) rotate(${rotation}deg) scale(${scale})`,
              opacity: opacity * intensity,
              boxShadow: `0 0 20px hsl(${hue}, 100%, 50%), inset 0 0 20px hsl(${hue}, 100%, 50%)`,
            }}
          />
        );
      })}

      {/* 中心光点 */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          width: 20,
          height: 20,
          borderRadius: "50%",
          background: colors.accent,
          transform: "translate(-50%, -50%)",
          boxShadow: `0 0 100px 50px ${colors.accent}`,
        }}
      />

      {/* 粒子流 */}
      {Array.from({ length: 30 }).map((_, i) => {
        const angle = (i / 30) * Math.PI * 2 + time * 2;
        const radius = 50 + ((time * 100 + i * 20) % 400);
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        const size = 4 + (i % 4);

        return (
          <div
            key={`p-${i}`}
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              width: size,
              height: size,
              borderRadius: "50%",
              background: colors.primary,
              transform: `translate(${x}px, ${y}px)`,
              boxShadow: `0 0 10px ${colors.primary}`,
              opacity: 0.8,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// 霓虹房间效果
const NeonRoomVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#050510", perspective: 600 }}>
      {/* 3D 房间 - 地板 */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: "-50%",
          width: "200%",
          height: "60%",
          background: `
            repeating-linear-gradient(
              90deg,
              transparent,
              transparent 48px,
              ${colors.primary}44 48px,
              ${colors.primary}44 50px
            ),
            repeating-linear-gradient(
              0deg,
              transparent,
              transparent 48px,
              ${colors.secondary}44 48px,
              ${colors.secondary}44 50px
            )
          `,
          transform: `perspective(600px) rotateX(70deg) translateY(${time * 50 % 50}px)`,
          transformOrigin: "bottom center",
        }}
      />

      {/* 侧墙霓虹灯条 */}
      {[0, 1].map((side) => (
        <div
          key={side}
          style={{
            position: "absolute",
            top: "10%",
            [side === 0 ? "left" : "right"]: "5%",
            width: 8,
            height: "60%",
            background: `linear-gradient(to bottom, ${colors.primary}, ${colors.secondary}, ${colors.accent})`,
            boxShadow: `0 0 30px ${colors.primary}, 0 0 60px ${colors.secondary}`,
            opacity: 0.8 + Math.sin(time * 4 + side) * 0.2,
          }}
        />
      ))}

      {/* 天花板灯光 */}
      {Array.from({ length: 5 }).map((_, i) => {
        const pulse = Math.sin(time * 6 + i * 1.2) > 0;
        const hue = (i * 72 + time * 40) % 360;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: "5%",
              left: `${15 + i * 17}%`,
              width: 60,
              height: 200,
              background: `linear-gradient(to bottom, hsl(${hue}, 100%, 60%), transparent)`,
              opacity: pulse ? 0.7 : 0.2,
              filter: "blur(10px)",
              transform: `rotate(${Math.sin(time * 2 + i) * 10}deg)`,
              transformOrigin: "top center",
            }}
          />
        );
      })}

      {/* 中心舞台光柱 */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: "50%",
          width: 100,
          height: "100%",
          background: `linear-gradient(to bottom, ${colors.accent}88, transparent 70%)`,
          transform: `translateX(-50%) scaleX(${1 + Math.sin(time * 4) * 0.3})`,
          filter: "blur(20px)",
        }}
      />
    </AbsoluteFill>
  );
};

// 赛博波浪效果
const CyberwaveVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "linear-gradient(to bottom, #0a0020, #1a0040)" }}>
      {/* 太阳/月亮 */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: "50%",
          width: 200,
          height: 200,
          borderRadius: "50%",
          background: `linear-gradient(to bottom, ${colors.accent}, ${colors.primary})`,
          transform: "translateX(-50%)",
          boxShadow: `0 0 100px ${colors.accent}, 0 0 200px ${colors.primary}`,
        }}
      />

      {/* 水平线条 */}
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            top: `${25 + i * 3}%`,
            left: 0,
            width: "100%",
            height: 2,
            background: colors.primary,
            opacity: 0.5 - i * 0.05,
          }}
        />
      ))}

      {/* 3D 网格地面 */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: "-50%",
          width: "200%",
          height: "50%",
          background: `
            repeating-linear-gradient(
              90deg,
              transparent,
              transparent 38px,
              ${colors.secondary}66 38px,
              ${colors.secondary}66 40px
            ),
            repeating-linear-gradient(
              0deg,
              transparent,
              transparent 38px,
              ${colors.primary}66 38px,
              ${colors.primary}66 40px
            )
          `,
          transform: `perspective(400px) rotateX(75deg) translateY(${time * 80 % 40}px)`,
          transformOrigin: "bottom center",
        }}
      />

      {/* 山脉轮廓 */}
      <svg
        style={{
          position: "absolute",
          bottom: "45%",
          left: 0,
          width: "100%",
          height: "20%",
        }}
        viewBox="0 0 100 20"
        preserveAspectRatio="none"
      >
        <path
          d="M0,20 L10,12 L20,15 L35,5 L50,10 L65,3 L80,12 L90,8 L100,15 L100,20 Z"
          fill="#0a0020"
          stroke={colors.primary}
          strokeWidth="0.3"
        />
      </svg>

      {/* 飞行粒子 */}
      {Array.from({ length: 20 }).map((_, i) => {
        const x = (i * 47 + time * 100) % 120 - 10;
        const y = 20 + (i % 5) * 15;
        const size = 2 + (i % 3);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: size,
              height: size,
              borderRadius: "50%",
              background: colors.accent,
              boxShadow: `0 0 10px ${colors.accent}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// 全息投影效果
const HologramVisual: React.FC<{
  frame: number;
  fps: number;
  colors: any;
  intensity: number;
}> = ({ frame, fps, colors, intensity }) => {
  const time = frame / fps;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: colors.background }}>
      {/* 全息投影底座 */}
      <div
        style={{
          position: "absolute",
          bottom: "15%",
          left: "50%",
          width: 300,
          height: 20,
          background: `linear-gradient(to right, transparent, ${colors.primary}, transparent)`,
          transform: "translateX(-50%)",
          borderRadius: "50%",
          boxShadow: `0 0 40px ${colors.primary}`,
        }}
      />

      {/* 全息光柱 */}
      <div
        style={{
          position: "absolute",
          bottom: "15%",
          left: "50%",
          width: 200,
          height: "60%",
          background: `linear-gradient(to top, ${colors.primary}44, transparent)`,
          transform: "translateX(-50%)",
          clipPath: "polygon(20% 100%, 80% 100%, 60% 0%, 40% 0%)",
        }}
      />

      {/* 全息图形 - 旋转多边形 */}
      {Array.from({ length: 3 }).map((_, i) => {
        const rotation = time * 60 + i * 120;
        const scale = 0.8 + Math.sin(time * 2 + i) * 0.2;
        const y = 35 + i * 5;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: `${y}%`,
              left: "50%",
              width: 150 - i * 30,
              height: 150 - i * 30,
              border: `2px solid ${colors.secondary}`,
              transform: `translateX(-50%) rotate(${rotation}deg) scale(${scale})`,
              opacity: 0.6 + i * 0.1,
              boxShadow: `0 0 20px ${colors.secondary}, inset 0 0 20px ${colors.secondary}`,
            }}
          />
        );
      })}

      {/* 扫描线效果 */}
      <div
        style={{
          position: "absolute",
          top: `${(time * 30) % 100}%`,
          left: "30%",
          width: "40%",
          height: 2,
          background: colors.accent,
          boxShadow: `0 0 20px ${colors.accent}`,
          opacity: 0.8,
        }}
      />

      {/* 数据流 */}
      {Array.from({ length: 10 }).map((_, i) => {
        const x = 35 + (i % 5) * 6;
        const y = (time * 50 + i * 30) % 100;
        // 使用确定性方式生成 0/1，基于 frame 和 index
        const binaryValue = Math.sin(frame * 0.5 + i * 7.123) > 0 ? "1" : "0";
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              fontSize: 12,
              fontFamily: "monospace",
              color: colors.secondary,
              opacity: 0.6,
              textShadow: `0 0 10px ${colors.secondary}`,
            }}
          >
            {binaryValue}
          </div>
        );
      })}

      {/* 闪烁干扰效果 */}
      {Math.sin(time * 20) > 0.95 && (
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            background: `${colors.primary}22`,
          }}
        />
      )}
    </AbsoluteFill>
  );
};

export default DJScene;
