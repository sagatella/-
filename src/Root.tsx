import "./index.css";
import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { TalkingHead } from "./TalkingHead";
import data from "./data/talkinghead.json";
import { Packing } from "./Packing";
import { TalkingHead2 } from "./TalkingHead2";
import th2 from "./data/th2.json";
import packing from "./data/packing.json";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="TalkingHead"
        component={TalkingHead}
        durationInFrames={Math.round(data.duration * data.fps)}
        fps={data.fps}
        width={1080}
        height={1920}
      />
      <Composition
        id="TalkingHead2"
        component={TalkingHead2}
        durationInFrames={Math.round(th2.duration * th2.fps)}
        fps={th2.fps}
        width={1080}
        height={1920}
      />
      <Composition
        id="Packing"
        component={Packing}
        durationInFrames={Math.round(packing.duration * packing.fps)}
        fps={packing.fps}
        width={1080}
        height={1920}
      />
      <MyComposition />
    </>
  );
};
