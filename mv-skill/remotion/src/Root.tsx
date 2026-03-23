import { Composition, getInputProps } from "remotion";
import { MVComposition } from "./compositions/MVComposition";
import { Storyboard } from "./types";

export const RemotionRoot: React.FC = () => {
  // 从命令行获取 props
  const inputProps = getInputProps() as Partial<Storyboard>;
  const duration = inputProps?.meta?.duration || 55;
  const fps = inputProps?.meta?.fps || 30;
  const resolution = inputProps?.meta?.resolution || "1080x1920";
  const [width, height] = resolution.split("x").map(Number);

  return (
    <>
      <Composition
        id="MVComposition"
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        component={MVComposition as any}
        durationInFrames={fps * duration}
        fps={fps}
        width={width || 1080}
        height={height || 1920}
        defaultProps={{
          meta: {
            title: "MV Preview",
            style: "anime-hype",
            duration: duration,
            resolution: resolution,
            fps: fps,
          },
          music: {
            source: "none",
            file: null,
            bpm: 128,
            beats: [],
          },
          scenes: [],
        }}
      />
    </>
  );
};
