import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  Audio,
  staticFile,
} from "remotion";
import { TitleScene } from "../components/scenes/TitleScene";
import { ActionScene } from "../components/scenes/ActionScene";
import { TransitionOverlay } from "../components/effects/TransitionOverlay";
import { Scene, Storyboard } from "../types";

interface MVCompositionProps extends Storyboard {}

export const MVComposition: React.FC<MVCompositionProps> = ({
  meta,
  music,
  scenes,
}) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();

  // 加载风格配置
  const styleConfig = getStyleConfig(meta.style);

  return (
    <AbsoluteFill style={{ backgroundColor: styleConfig.background }}>
      {/* 音乐轨道 */}
      {music.file && (
        <Audio src={staticFile(music.file)} volume={1} />
      )}

      {/* 场景序列 */}
      {scenes.map((scene, index) => {
        const startFrame = Math.round(scene.start * fps);
        const durationFrames = Math.round((scene.end - scene.start) * fps);

        return (
          <Sequence
            key={scene.id}
            from={startFrame}
            durationInFrames={durationFrames}
            name={scene.id}
          >
            <SceneRenderer
              scene={scene}
              styleConfig={styleConfig}
              beats={music.beats || []}
              bpm={music.bpm || 128}
            />

            {/* 转场效果 */}
            {scene.transition && scene.transition !== "none" && (
              <TransitionOverlay
                type={scene.transition}
                durationFrames={Math.round(0.3 * fps)}
                styleConfig={styleConfig}
              />
            )}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

interface SceneRendererProps {
  scene: Scene;
  styleConfig: StyleConfig;
  beats: number[];
  bpm: number;
}

const SceneRenderer: React.FC<SceneRendererProps> = ({
  scene,
  styleConfig,
  beats,
  bpm,
}) => {
  switch (scene.type) {
    case "title":
      return (
        <TitleScene
          text={scene.content?.text || ""}
          subtitle={scene.content?.subtitle}
          visual={scene.visual}
          animation={scene.animation}
          styleConfig={styleConfig}
        />
      );

    case "action":
    case "lyrics":
    default:
      return (
        <ActionScene
          visual={scene.visual}
          animation={scene.animation}
          lyrics={scene.content?.lyrics}
          beatSync={scene.beat_sync}
          beats={beats}
          bpm={bpm}
          styleConfig={styleConfig}
        />
      );
  }
};

// 风格配置
interface StyleConfig {
  background: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  textColor: string;
  fontFamily: string;
}

function getStyleConfig(style: string): StyleConfig {
  const configs: Record<string, StyleConfig> = {
    "anime-hype": {
      background: "#0D0D0D",
      primaryColor: "#FF4500",
      secondaryColor: "#FFD700",
      accentColor: "#1E90FF",
      textColor: "#FFFFFF",
      fontFamily: "Noto Sans SC, sans-serif",
    },
    cyberpunk: {
      background: "#0a0a0f",
      primaryColor: "#ff00ff",
      secondaryColor: "#00ffff",
      accentColor: "#ff0080",
      textColor: "#ffffff",
      fontFamily: "Orbitron, sans-serif",
    },
    lyric: {
      background: "#1a1a2e",
      primaryColor: "#e94560",
      secondaryColor: "#533483",
      accentColor: "#16213e",
      textColor: "#ffffff",
      fontFamily: "Noto Serif SC, serif",
    },
  };

  return configs[style] || configs["anime-hype"];
}
