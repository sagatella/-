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
import data from "./data/packing.json";

const { fontFamily } = loadFont("normal", {
  weights: ["500", "800"],
  subsets: ["cyrillic", "latin"],
});

// Same typographic system and accent colour as the talking-head reels.
const ACCENT = "#FFD35A";
const SIDE = 72;
const CAPTION_BOTTOM = 320; // keeps captions above the bottom 15% UI zone
const HOOK_TOP = 590;
const PRICE_TOP = 250; // below the top 10% UI zone
const INSERT_TOP = 700;
const INSERT_H = 510;

type CapWord = { w: string; s: number; e: number; accent: boolean };
type CapGroup = { start: number; end: number; words: CapWord[] };
type PriceCard = { start: number; end: number; title: string; sub: string; price: string | null };
type InsertSpec = { start: number; end: number; kind: string; src: string; position?: string };

const fade = (t: number, a: number, b: number, inS = 0.3, outS = 0.4) =>
  interpolate(t, [a, a + inS, b - outS, b], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const Caption: React.FC<{ t: number }> = ({ t }) => {
  const groups = data.captions as CapGroup[];
  const g = groups.find((x) => t >= x.start && t < x.end);
  if (!g) return null;
  const pop = interpolate(t - g.start, [0, 0.1], [0, 1], { extrapolateRight: "clamp" });
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
          const gap = i < g.words.length - 1 ? g.words[i + 1].s : w.e;
          const bold = t >= w.s && t < Math.max(w.e, gap);
          return (
            <span
              key={i}
              style={{ display: "inline-grid", marginRight: i < g.words.length - 1 ? "0.26em" : 0 }}
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
              <span aria-hidden style={{ gridArea: "1 / 1", fontWeight: 800, visibility: "hidden" }}>
                {w.w}
              </span>
            </span>
          );
        })}
      </div>
    </div>
  );
};

const Hook: React.FC<{ t: number }> = ({ t }) => {
  const hook = data.hook;
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
          fontSize: 78,
          lineHeight: 1.1,
          textAlign: "center",
          color: ACCENT, // the hook/title is always yellow (AGENTS.md, step 4)
          whiteSpace: "pre-line",
          textShadow: "0 4px 28px rgba(0,0,0,0.7), 0 0 2px rgba(0,0,0,0.45)",
        }}
      >
        {hook.text}
      </div>
    </div>
  );
};

const Price: React.FC<{ card: PriceCard; t: number }> = ({ card, t }) => {
  const o = fade(t, card.start, card.end, 0.28, 0.3);
  if (o <= 0) return null;
  const slide = interpolate(t, [card.start, card.start + 0.28], [-26, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div
      style={{
        position: "absolute",
        left: SIDE,
        right: SIDE,
        top: PRICE_TOP,
        opacity: o,
        transform: `translateY(${slide}px)`,
        background: "rgba(10,10,10,0.62)",
        borderRadius: 36,
        padding: "26px 36px 28px",
        fontFamily,
        textAlign: "center",
        boxShadow: "0 16px 50px rgba(0,0,0,0.4)",
      }}
    >
      <div style={{ fontSize: 40, fontWeight: 800, color: "#fff", lineHeight: 1.15 }}>{card.title}</div>
      <div style={{ fontSize: 108, fontWeight: 800, color: ACCENT, lineHeight: 1.1, marginTop: 6 }}>
        {card.price ?? "цена ?"}
      </div>
      {card.sub ? (
        <div style={{ fontSize: 30, fontWeight: 500, color: "rgba(255,255,255,0.78)", marginTop: 2 }}>{card.sub}</div>
      ) : null}
    </div>
  );
};

const InsertView: React.FC<{ ins: InsertSpec; t: number }> = ({ ins, t }) => {
  const o = fade(t, ins.start, ins.end, 0.2, 0.2);
  if (o <= 0) return null;
  const s = interpolate(t, [ins.start, ins.end], [1.0, 1.045], { easing: Easing.out(Easing.quad) });
  return (
    <div
      style={{
        position: "absolute",
        left: SIDE,
        right: SIDE,
        top: INSERT_TOP,
        height: INSERT_H,
        borderRadius: 36,
        overflow: "hidden",
        opacity: o,
        boxShadow: "0 18px 60px rgba(0,0,0,0.45)",
        background: "#111",
      }}
    >
      <Img
        src={staticFile(ins.src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: ins.position ?? "50% 50%",
          transform: `scale(${s})`,
        }}
      />
    </div>
  );
};

export const Packing: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <OffthreadVideo
        src={staticFile("rough_r2.mp4")}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
      {(data.inserts as InsertSpec[]).map((ins, i) => (
        <InsertView key={i} ins={ins} t={t} />
      ))}
      {(data.prices as PriceCard[]).map((c, i) => (
        <Price key={i} card={c} t={t} />
      ))}
      <Hook t={t} />
      <Caption t={t} />
    </AbsoluteFill>
  );
};
