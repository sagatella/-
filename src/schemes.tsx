import React from "react";
import { Easing, interpolate } from "remotion";

// Code-built diagrams for the insert zone (936 x 540). Same font as the captions,
// one accent colour, filled shapes only - no outlines.
export type SchemeSpec =
  | { type: "chain"; steps: string[]; at: number[] }
  | { type: "stat"; value: string; label: string; at: number[] }
  | { type: "update"; title: string; from: string; to: string; label: string; at: number[] }
  | {
      type: "contrast";
      title: string;
      left: { label: string; verdict: string };
      right: { label: string; verdict: string };
      at: number[];
    }
  | { type: "timeline"; from: { title: string; sub: string }; to: { title: string; sub: string }; note: string; at: number[] };

const CARD = "rgba(255,255,255,0.09)";

const appear = (t: number, at: number) => {
  const p = interpolate(t, [at, at + 0.28], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return { opacity: p, transform: `translateY(${(1 - p) * 22}px)` } as React.CSSProperties;
};

export const Scheme: React.FC<{
  spec: SchemeSpec;
  t: number;
  fontFamily: string;
  accent: string;
}> = ({ spec, t, fontFamily, accent }) => {
  const root: React.CSSProperties = {
    position: "absolute",
    inset: 0,
    background: "linear-gradient(160deg,#1b1b1d,#0f0f10)",
    fontFamily,
    color: "#fff",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    padding: 36,
    boxSizing: "border-box",
  };

  if (spec.type === "chain") {
    return (
      <div style={root}>
        {spec.steps.map((s, i) => {
          const last = i === spec.steps.length - 1;
          return (
            <React.Fragment key={i}>
              <div
                style={{
                  ...appear(t, spec.at[i]),
                  width: "100%",
                  height: 124,
                  borderRadius: 28,
                  background: last ? accent : CARD,
                  color: last ? "#151515" : "#fff",
                  fontWeight: 800,
                  fontSize: 58,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {s}
              </div>
              {!last && (
                <div
                  style={{
                    ...appear(t, spec.at[i + 1] - 0.05),
                    fontSize: 44,
                    fontWeight: 800,
                    color: accent,
                    height: 50,
                    lineHeight: "50px",
                  }}
                >
                  ↓
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    );
  }

  if (spec.type === "update") {
    return (
      <div style={{ ...root, gap: 6 }}>
        <div style={{ ...appear(t, spec.at[0]), fontSize: 34, fontWeight: 800, color: accent, letterSpacing: 2 }}>{spec.title}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 26, lineHeight: 1.05 }}>
          <div style={{ ...appear(t, spec.at[0] + 0.1), fontSize: 92, fontWeight: 800, color: "rgba(255,255,255,0.45)" }}>{spec.from}</div>
          <div style={{ ...appear(t, spec.at[1] - 0.05), fontSize: 80, fontWeight: 800, color: accent }}>→</div>
          <div style={{ ...appear(t, spec.at[1]), fontSize: 132, fontWeight: 800, color: accent }}>{spec.to}</div>
        </div>
        <div style={{ ...appear(t, spec.at[2]), fontSize: 38, fontWeight: 500, textAlign: "center", color: "#fff", marginTop: 8, lineHeight: 1.22 }}>
          {spec.label}
        </div>
      </div>
    );
  }

  if (spec.type === "stat") {
    return (
      <div style={root}>
        <div style={{ ...appear(t, spec.at[0]), fontSize: spec.value.length > 4 ? 118 : 190, fontWeight: 800, color: accent, lineHeight: 1.05, textAlign: "center" }}>
          {spec.value}
        </div>
        <div style={{ ...appear(t, spec.at[0] + 0.15), fontSize: 46, fontWeight: 500, marginTop: 14, textAlign: "center", color: "#fff" }}>
          {spec.label}
        </div>
      </div>
    );
  }

  if (spec.type === "contrast") {
    const card = (c: { label: string; verdict: string }, at: number, good: boolean) => (
      <div
        style={{
          ...appear(t, at),
          width: 432,
          height: 330,
          borderRadius: 32,
          background: CARD,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 10,
        }}
      >
        <div style={{ fontSize: 42, fontWeight: 500, textAlign: "center" }}>{c.label}</div>
        <div style={{ fontSize: c.verdict.length <= 3 ? 132 : 96, fontWeight: 800, color: good ? accent : "rgba(255,255,255,0.5)", lineHeight: 1.05 }}>
          {c.verdict}
        </div>
      </div>
    );
    return (
      <div style={root}>
        <div style={{ ...appear(t, 0), fontSize: 50, fontWeight: 800, marginBottom: 26 }}>{spec.title}</div>
        <div style={{ display: "flex", gap: 36 }}>
          {card(spec.left, spec.at[0], false)}
          {card(spec.right, spec.at[1], true)}
        </div>
      </div>
    );
  }

  // timeline
  const box = (c: { title: string; sub: string }, at: number, hi: boolean) => (
    <div
      style={{
        ...appear(t, at),
        width: 384,
        height: 250,
        borderRadius: 32,
        background: hi ? accent : CARD,
        color: hi ? "#151515" : "#fff",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 8,
      }}
    >
      <div style={{ fontSize: 50, fontWeight: 800, textAlign: "center" }}>{c.title}</div>
      <div style={{ fontSize: 38, fontWeight: 500 }}>{c.sub}</div>
    </div>
  );
  return (
    <div style={root}>
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        {box(spec.from, spec.at[0], false)}
        <div style={{ ...appear(t, spec.at[1] - 0.05), fontSize: 64, fontWeight: 800, color: accent }}>→</div>
        {box(spec.to, spec.at[1], true)}
      </div>
      <div style={{ ...appear(t, spec.at[2]), marginTop: 34, fontSize: 38, fontWeight: 500, opacity: 0.9 }}>
        {spec.note}
      </div>
    </div>
  );
};
