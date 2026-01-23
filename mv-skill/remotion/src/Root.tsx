import { Composition } from "remotion";
import { MVComposition } from "./compositions/MVComposition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MVComposition"
        component={MVComposition}
        durationInFrames={30 * 55} // 55 seconds at 30fps
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          meta: {
            title: "MV Preview",
            style: "anime-hype",
            duration: 55,
            resolution: "1080x1920",
            fps: 30,
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
