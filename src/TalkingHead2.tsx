import React from "react";
import {
  AbsoluteFill,
  Img,
  Easing,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Montserrat";
import data from "./data/th2.json";
import { Scheme, SchemeSpec } from "./schemes";

const { fontFamily } = loadFont("normal", {
  weights: ["500", "800"],
  subsets: ["cyrillic", "latin"],
});

// One font, one accent colour for the whole reel.
const ACCENT = "#FFD35A";
const SIDE = 72; // minimum margin from the edges
const CAPTION_BOTTOM = 320; // 1920 - 320 = 1600 -> above the 15% bottom UI zone (1632)
const INSERT_TOP = 880; // below the face
const INSERT_H = 510; // ~27% of the frame, ends above the captions
const HOOK_TOP = 930;
const PUNCH = 1.085; // alternating punch-in on jump cuts

type CapWord = { w: string; s: number; e: number; accent: boolean };
type CapGroup = { start: number; end: number; words: CapWord[] };

export type InsertSpec = {
  start: number;
  end: number;
  kind: "image" | "video" | "scheme";
  src?: string;
  position?: string; // object-position for images/video
  trimFrom?: number; // seconds into the source video
  scheme?: SchemeSpec;
  full?: boolean;
};

export type HookSpec = { text: string; start: number; end: number };

const fade = (t: number, a: number, b: number, inS = 0.3, outS = 0.4) =>
  interpolate(t, [a, a + inS, b - outS, b], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const Caption: React.FC<{ t: number; hookEnd: number }> = ({ t, hookEnd }) => {
  const groups = data.captions as CapGroup[];
  // While the hook (which repeats the first sentence) is up, it acts as the caption.
  // The tail of that sentence gets normal captions again just before the hook leaves.
  const from = hookEnd - 0.2;
  const shown = groups
    .filter((x) => x.end > from || x.start >= hookEnd)
    .map((x) =>
      x.start < from
        ? { ...x, start: from, words: x.words.filter((w) => w.e > from - 0.1) }
        : x,
    );
  const g = shown.find((x) => t >= x.start && t < x.end);
  if (!g || g.words.length === 0) return null;
  const local = t - g.start;
  const pop = interpolate(local, [0, 0.1], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        left: SIDE,
        right: SIDE,
        bottom: CAPTION_BOTTOM,
        display: "flex",
        justifyContent: "center",
        opacity: pop,
        transform: `translateY(${(1 - pop) * 10}px)`,
      }}
    >
      <div
        style={{
          background: "rgba(8,8,8,0.42)",
          borderRadius: 32,
          padding: "16px 30px 20px",
          textAlign: "center",
          fontFamily,
          fontSize: 78,
          lineHeight: 1.16,
          color: "#fff",
          textShadow: "0 3px 20px rgba(0,0,0,0.55)",
        }}
      >
        {g.words.map((w, i) => {
          const current = t >= w.s && t < w.e;
          const gap = i < g.words.length - 1 ? g.words[i + 1].s : w.e;
          const active = t >= w.s && t < Math.max(w.e, gap);
          const bold = current || active;
          return (
            <span
              key={i}
              style={{
                display: "inline-grid",
                marginRight: i < g.words.length - 1 ? "0.26em" : 0,
              }}
            >
              <span
                style={{
                  gridArea: "1 / 1",
                  fontWeight: bold ? 800 : 500,
                  color: w.accent ? ACCENT : "#fff",
                }}
              >
                {w.w}
              </span>
              {/* invisible bold copy reserves the width so words do not jump */}
              <span
                aria-hidden
                style={{ gridArea: "1 / 1", fontWeight: 800, visibility: "hidden" }}
              >
                {w.w}
              </span>
            </span>
          );
        })}
      </div>
    </div>
  );
};

const Hook: React.FC<{ hook: HookSpec; t: number }> = ({ hook, t }) => {
  const o = fade(t, hook.start, hook.end);
  if (o <= 0) return null;
  const drift = interpolate(t, [hook.start, hook.end], [14, -6]);
  return (
    <div
      style={{
        position: "absolute",
        left: SIDE,
        right: SIDE,
        top: HOOK_TOP,
        display: "flex",
        justifyContent: "center",
        opacity: o,
        transform: `translateY(${drift}px)`,
      }}
    >
      <div
        style={{
          fontFamily,
          fontWeight: 800,
          fontSize: 96,
          lineHeight: 1.1,
          textAlign: "center",
          color: ACCENT, // the hook/title is always yellow (see AGENTS.md, step 4)
          whiteSpace: "pre-line",
          textShadow: "0 4px 28px rgba(0,0,0,0.65), 0 0 2px rgba(0,0,0,0.4)",
        }}
      >
        {hook.text}
      </div>
    </div>
  );
};

const InsertView: React.FC<{ ins: InsertSpec; t: number }> = ({ ins, t }) => {
  const o = interpolate(t, [ins.start, ins.start + 0.2, ins.end - 0.2, ins.end], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  if (o <= 0) return null;
  const s = interpolate(t, [ins.start, ins.end], [1.0, 1.045], {
    easing: Easing.out(Easing.quad),
  });
  const box: React.CSSProperties = ins.full
    ? { left: 0, right: 0, top: 0, bottom: 0, borderRadius: 0 }
    : { left: SIDE, right: SIDE, top: INSERT_TOP, height: INSERT_H, borderRadius: 36 };
  const media: React.CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    objectPosition: ins.position ?? "50% 50%",
    transform: `scale(${s})`,
  };
  return (
    <div
      style={{
        position: "absolute",
        overflow: "hidden",
        opacity: o,
        boxShadow: "0 18px 60px rgba(0,0,0,0.45)",
        background: "#111",
        ...box,
      }}
    >
      {ins.kind === "image" && <Img src={staticFile(ins.src!)} style={media} />}
      {ins.kind === "video" && (
        <OffthreadVideo
          src={staticFile(ins.src!)}
          muted
          startFrom={Math.round((ins.trimFrom ?? 0) * 30)}
          style={media}
        />
      )}
      {ins.kind === "scheme" && <Scheme spec={ins.scheme!} t={t - ins.start} fontFamily={fontFamily} accent={ACCENT} />}
    </div>
  );
};

export const TalkingHead2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const segs = data.segments as { start: number; end: number }[];
  let segIdx = segs.findIndex((s) => t >= s.start && t < s.end);
  if (segIdx < 0) segIdx = segs.length - 1;
  const extra = (data.punches as number[]).filter((x) => t >= x).length;
  const zoom = (segIdx + extra) % 2 === 1 ? PUNCH : 1;
  const hook = data.hook as HookSpec | null;
  const inserts = data.inserts as InsertSpec[];

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AbsoluteFill style={{ transform: `scale(${zoom})`, transformOrigin: "50% 8%" }}>
        <OffthreadVideo src={staticFile("rough_th2.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
      {inserts.map((ins, i) => (
        <InsertView key={i} ins={ins} t={t} />
      ))}
      {hook && <Hook hook={hook} t={t} />}
      <Caption t={t} hookEnd={0} />
    </AbsoluteFill>
  );
};
