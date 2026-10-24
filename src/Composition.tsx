import { AbsoluteFill, Composition } from "remotion";

export const MyComposition = () => {
  return (
    <Composition
      id="Test"
      component={TestScene}
      durationInFrames={300}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};

export const TestScene: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#000",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          color: "#fff",
          fontSize: 220,
          fontWeight: 800,
          fontFamily: "Helvetica, Arial, sans-serif",
          letterSpacing: 8,
        }}
      >
        ТЕСТ
      </div>
    </AbsoluteFill>
  );
};
