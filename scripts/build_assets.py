#!/usr/bin/env python3
"""Generate the animated sci-fi SVG panels used by the profile README.

GitHub sanitises README HTML (no JS, no <style> on the page), but SVGs served
as images keep their internal SMIL/CSS animations. Every panel is therefore a
self-contained SVG with no external fonts, images or scripts.

Edit the DATA section below, then run:

    python3 scripts/build_assets.py

Outputs are written to ./assets/. Deterministic: the same input produces
byte-identical files (random elements use a fixed seed), so diffs stay clean.
"""

from __future__ import annotations

import math
import random
from html import escape
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# DATA — edit here
# ──────────────────────────────────────────────────────────────────────────────

NAME = "KSHITIZ KUMAR SINHA"
TAGLINE = "MATHEMATICS  ·  MACHINE LEARNING  ·  COGNITIVE SYSTEMS"
AFFILIATION = "PhD SCHOLAR @ SARALA BIRLA UNIVERSITY  ·  RANCHI, INDIA"
ROLES = [
    "Mathematics Educator — CBSE IX–X",
    "PhD Scholar — Applied ML × Fluid Dynamics",
    "Founder — Tungston Theory",
    "Computer Vision & Full-Stack Engineer",
]

TERMINAL = [
    ("cmd", "whoami"),
    ("out", "Mathematics teacher. ML researcher. System builder."),
    ("cmd", "cat mission.txt"),
    ("out", "I teach mathematics. I research Applied ML for Fluid Dynamics."),
    ("out", "The two aren't as separate as they sound — both are about"),
    ("out", "finding structure in complexity."),
    ("cmd", "./tungston --status"),
    ("ok", "[ BUILDING ] a gamified intelligence system for mathematical thinking."),
    ("out", "Not faster problem-solving. Different perception."),
]

# (code, skill, credential, value out of 12)
STATS = [
    ("STR", "Mathematics", "M.Sc · PhD (2028)", 11),
    ("INT", "Machine Learning", "Applied ML · CV", 12),
    ("WIS", "Pedagogy", "CTET · B.Ed · CBSE", 10),
    ("DEX", "Computer Vision", "PyTorch · YOLO", 9),
    ("CHA", "Mentorship", "240+ students", 10),
]

QUESTS = [
    ("ACTIVE", "Tungston Theory — gamified maths intelligence"),
    ("ONGOING", "PhD — Applied ML for Fluid Dynamics (2025–2028)"),
    ("ONGOING", "Mentor — 20+ rural students, Ranchi"),
]

# (slug, title, description, tags, glyph)
PROJECTS = [
    ("vision-fusion", "VISION-FUSION",
     "Modular real-time CV — YOLOv8, face detection, motion analysis, CNN classification. One pipeline.",
     ["YOLOv8", "OpenCV", "PyTorch"], "reticle"),
    ("air-volume", "AIR-VOLUME-CONTROL",
     "Gesture-based system volume control via hand landmarks. No peripherals.",
     ["MediaPipe", "OpenCV", "Python"], "hand"),
    ("handwriting-emotion", "HANDWRITING-EMOTION-DETECTION",
     "Emotion detection from pen-trajectory data. Handwriting as a psychological signal.",
     ["Time-series", "Deep Learning", "HCI"], "pen"),
]

QUOTE = [
    "I don't want students to solve questions.",
    "I want them to see patterns where others see problems.",
]

# ──────────────────────────────────────────────────────────────────────────────
# THEME
# ──────────────────────────────────────────────────────────────────────────────

BG0, BG1 = "#03050b", "#0a1022"
CYAN, MAGENTA, VIOLET = "#00f0ff", "#ff2bd6", "#8a5cff"
GREEN, AMBER = "#39ff88", "#ffb800"
TEXT, DIM, LINE = "#d7e3ff", "#6b7c9e", "#1b2a4a"
MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

OUT = Path(__file__).resolve().parent.parent / "assets"
rng = random.Random(42)


def e(s: str) -> str:
    return escape(s, quote=True)


def svg(w: int, h: int, body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{e(title)}">\n'
        f"<title>{e(title)}</title>\n{body}\n</svg>\n"
    )


def common_defs(w: int, h: int) -> str:
    return f"""
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/>
  </linearGradient>
  <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/>
    <stop offset="1" stop-color="{MAGENTA}"/>
  </linearGradient>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
    <path d="M32 0H0V32" fill="none" stroke="{CYAN}" stroke-opacity=".06"/>
  </pattern>
  <filter id="neon" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="3.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="1.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="16"/></clipPath>"""


def frame_open(w: int, h: int) -> str:
    return (
        f'<g clip-path="url(#frame)">\n'
        f'  <rect width="{w}" height="{h}" fill="url(#bg)"/>\n'
        f'  <rect width="{w}" height="{h}" fill="url(#grid)"/>\n'
    )


def frame_close(w: int, h: int, scan_dur: float = 6) -> str:
    """Moving scanline, HUD corner brackets and border."""
    c, s = CYAN, 22
    corners = (
        f"M8 {8+s}V8H{8+s} M{w-8-s} 8H{w-8}V{8+s} "
        f"M{w-8} {h-8-s}V{h-8}H{w-8-s} M{8+s} {h-8}H8V{h-8-s}"
    )
    return f"""  <rect x="0" y="-6" width="{w}" height="3" fill="{c}" opacity=".10">
    <animate attributeName="y" values="-6;{h+6}" dur="{scan_dur}s" repeatCount="indefinite"/>
  </rect>
</g>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="16" fill="none" stroke="{c}" stroke-opacity=".28"/>
<path d="{corners}" fill="none" stroke="{c}" stroke-width="2" filter="url(#soft)">
  <animate attributeName="stroke-opacity" values="1;.35;1" dur="3s" repeatCount="indefinite"/>
</path>"""


def twinkles(w: int, h: int, n: int, y_max: float | None = None) -> str:
    out = []
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, y_max or h)
        r = rng.choice([0.6, 0.8, 1.0, 1.3])
        d, b = rng.uniform(2, 6), rng.uniform(0, 6)
        col = rng.choice([CYAN, TEXT, VIOLET, TEXT])
        out.append(
            f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity=".2">'
            f'<animate attributeName="opacity" values=".1;.9;.1" dur="{d:.1f}s" '
            f'begin="-{b:.1f}s" repeatCount="indefinite"/></circle>'
        )
    return "\n".join(out)


# ──────────────────────────────────────────────────────────────────────────────
# Math-driven geometry
# ──────────────────────────────────────────────────────────────────────────────

def lorenz_path(x0: float, y0: float, w: float, h: float, steps: int = 2600) -> tuple[str, float]:
    """Lorenz attractor (σ=10, ρ=28, β=8/3) via RK4, projected onto the x–z plane.

    Fitting for a fluid-dynamics researcher: Lorenz derived it from a truncated
    model of Rayleigh–Bénard convection.
    """
    s, r, b, dt = 10.0, 28.0, 8.0 / 3.0, 0.01

    def f(p):
        x, y, z = p
        return (s * (y - x), x * (r - z) - y, x * y - b * z)

    p = (0.1, 0.0, 0.0)
    pts = []
    for i in range(steps + 300):
        k1 = f(p)
        k2 = f(tuple(p[j] + dt / 2 * k1[j] for j in range(3)))
        k3 = f(tuple(p[j] + dt / 2 * k2[j] for j in range(3)))
        k4 = f(tuple(p[j] + dt * k3[j] for j in range(3)))
        p = tuple(p[j] + dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]) for j in range(3))
        if i >= 300:  # discard transient
            pts.append((p[0], p[2]))
    xs, zs = [q[0] for q in pts], [q[1] for q in pts]
    mnx, mxx, mnz, mxz = min(xs), max(xs), min(zs), max(zs)
    sc = min(w / (mxx - mnx), h / (mxz - mnz))
    ox = x0 + (w - (mxx - mnx) * sc) / 2
    oy = y0 + (h - (mxz - mnz) * sc) / 2
    proj = [(ox + (x - mnx) * sc, oy + (mxz - z) * sc) for x, z in pts]
    length = sum(math.dist(proj[i], proj[i + 1]) for i in range(len(proj) - 1))
    d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in proj)
    return d, length


def sine_path(x0: float, x1: float, y: float, amp: float, wl: float, phase: float = 0) -> str:
    pts = []
    x = x0
    while x <= x1:
        pts.append(f"{x:.1f} {y + amp * math.sin(2 * math.pi * x / wl + phase):.1f}")
        x += 8
    return "M" + " L".join(pts)


# ──────────────────────────────────────────────────────────────────────────────
# Panels
# ──────────────────────────────────────────────────────────────────────────────

def header() -> str:
    W, H = 1200, 380
    horizon = 300
    lorenz_d, lorenz_len = lorenz_path(978, 70, 190, 196)

    floor = []
    vx = W / 2
    for i in range(-14, 15):
        floor.append(f'<line x1="{vx}" y1="{horizon}" x2="{vx + i * 90}" y2="{H}"/>')
    for i in range(7):
        floor.append(
            f'<line x1="0" x2="{W}" y1="{horizon}" y2="{horizon}">'
            f'<animate attributeName="y1" values="{horizon};{H + 2}" dur="3.5s" '
            f'begin="-{i * 0.5:.1f}s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="0;1" keySplines=".55 0 1 .45"/>'
            f'<animate attributeName="y2" values="{horizon};{H + 2}" dur="3.5s" '
            f'begin="-{i * 0.5:.1f}s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="0;1" keySplines=".55 0 1 .45"/></line>'
        )

    streams = []
    for i, (yy, amp, wl, col, dur) in enumerate(
        [(262, 7, 260, CYAN, 7), (274, 5, 190, VIOLET, 9), (252, 4, 340, MAGENTA, 11)]
    ):
        streams.append(
            f'<path d="{sine_path(0, W, yy, amp, wl, i)}" fill="none" stroke="{col}" '
            f'stroke-width="1.2" stroke-opacity=".45" stroke-dasharray="90 26 6 26">'
            f'<animate attributeName="stroke-dashoffset" values="0;-400" dur="{dur}s" '
            f'repeatCount="indefinite"/></path>'
        )

    # cycling role line — each role owns an equal slice of the cycle
    n, slot = len(ROLES), 3.2
    total = n * slot
    roles = []
    for i, role in enumerate(ROLES):
        a, b = i / n, (i + 1) / n
        eps = 0.02
        kt = sorted({0, max(a - 1e-4, 0), a, min(a + eps, 1), max(b - eps, 0), b, 1})
        vals = []
        for t in kt:
            vals.append("1" if (a + eps <= t <= b - eps) else "0")
        roles.append(
            f'<text x="600" y="246" opacity="0">{e(role)}'
            f'<animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" '
            f'keyTimes="{";".join(f"{t:.4f}" for t in kt)}" values="{";".join(vals)}"/></text>'
        )

    reticle = f"""
  <g transform="translate(128 175)" fill="none" stroke="{CYAN}" opacity=".55">
    <circle r="86" stroke-opacity=".25"/>
    <circle r="70" stroke-dasharray="4 10" stroke-width="2">
      <animateTransform attributeName="transform" type="rotate" values="0;360" dur="24s" repeatCount="indefinite"/>
    </circle>
    <circle r="56" stroke="{MAGENTA}" stroke-dasharray="120 232" stroke-width="2.5">
      <animateTransform attributeName="transform" type="rotate" values="360;0" dur="6s" repeatCount="indefinite"/>
    </circle>
    <circle r="40" stroke-opacity=".5"/>
    <path d="M-96 0H-76M76 0H96M0-96V-76M0 76V96" stroke-width="2"/>
    <g fill="{CYAN}" stroke="none" font-family="{MONO}" font-size="13" text-anchor="middle">
      <text y="-4">∇·u = 0</text>
      <text y="14" fill="{DIM}" font-size="9" letter-spacing="2">INCOMPRESSIBLE</text>
    </g>
    <line x1="0" y1="0" x2="86" y2="0" stroke="{CYAN}" stroke-opacity=".7">
      <animateTransform attributeName="transform" type="rotate" values="0;360" dur="4s" repeatCount="indefinite"/>
    </line>
  </g>"""

    lorenz = f"""
  <g opacity=".75" filter="url(#soft)">
    <defs><path id="lorenz" d="{lorenz_d}"/></defs>
    <use href="#lorenz" fill="none" stroke="url(#beam)" stroke-width="1" stroke-opacity=".18"/>
    <use href="#lorenz" fill="none" stroke="url(#beam)" stroke-width="1.4"
          stroke-dasharray="{lorenz_len:.0f} {lorenz_len:.0f}" stroke-dashoffset="{lorenz_len:.0f}">
      <animate attributeName="stroke-dashoffset" values="{lorenz_len:.0f};0;0;{-lorenz_len:.0f}"
               keyTimes="0;.55;.75;1" dur="16s" repeatCount="indefinite"/>
    </use>
  </g>
  <text x="1073" y="292" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{DIM}" letter-spacing="2">LORENZ · σ=10 ρ=28 β=8/3</text>"""

    glitch = lambda col, dx: (  # noqa: E731
        f'<text x="600" y="172" fill="{col}" opacity=".55" textLength="720" lengthAdjust="spacingAndGlyphs">{e(NAME)}'
        f'<animateTransform attributeName="transform" type="translate" dur="5s" repeatCount="indefinite" '
        f'keyTimes="0;.88;.9;.92;.94;.96;1" values="0 0;0 0;{dx} 0;{-dx} 1;{dx/2} 0;0 0;0 0"/></text>'
    )

    body = f"""<defs>{common_defs(W, H)}
  <radialGradient id="halo" cx=".5" cy=".42" r=".55">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity=".28"/>
    <stop offset=".6" stop-color="{CYAN}" stop-opacity=".05"/>
    <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="nameGrad" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="800" y2="0" spreadMethod="repeat">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".33" stop-color="#ffffff"/>
    <stop offset=".5" stop-color="{VIOLET}"/><stop offset=".75" stop-color="{MAGENTA}"/>
    <stop offset="1" stop-color="{CYAN}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;800 0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="floorFade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG1}" stop-opacity="1"/><stop offset=".35" stop-color="{BG1}" stop-opacity="0"/>
  </linearGradient>
</defs>
{frame_open(W, H)}  <rect width="{W}" height="{H}" fill="url(#halo)"/>
{twinkles(W, H, 70, y_max=horizon)}
  <g stroke="{CYAN}" stroke-opacity=".22">{"".join(floor)}</g>
  <rect y="{horizon}" width="{W}" height="{H - horizon}" fill="url(#floorFade)"/>
  <line x1="0" x2="{W}" y1="{horizon}" y2="{horizon}" stroke="{CYAN}" stroke-opacity=".6" filter="url(#soft)"/>
  <g>{"".join(streams)}</g>
{reticle}
{lorenz}

  <!-- top HUD -->
  <g font-family="{MONO}" font-size="12" letter-spacing="1.5">
    <circle cx="34" cy="32" r="4" fill="{GREEN}"><animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></circle>
    <text x="46" y="36" fill="{GREEN}">SYS.ONLINE</text>
    <text x="150" y="36" fill="{DIM}">//  NODE: RANCHI.IN  //  23.34°N 85.31°E</text>
    <text x="{W - 32}" y="36" fill="{DIM}" text-anchor="end">UPLINK <tspan fill="{CYAN}">▮▮▮▮</tspan><tspan fill="{LINE}">▮</tspan>  ·  BUILD 2026.11</text>
  </g>

  <!-- name + glitch -->
  <g font-family="{MONO}" font-size="58" font-weight="800" text-anchor="middle">
    {glitch(MAGENTA, 4)}
    {glitch(CYAN, -4)}
    <text x="600" y="172" fill="url(#nameGrad)" filter="url(#neon)" textLength="720" lengthAdjust="spacingAndGlyphs">{e(NAME)}</text>
  </g>
  <text x="600" y="208" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{TEXT}" letter-spacing="3">{e(TAGLINE)}</text>
  <g font-family="{MONO}" font-size="16" fill="{CYAN}" text-anchor="middle">
    {"".join(roles)}
  </g>

  <!-- bottom HUD -->
  <g font-family="{MONO}" font-size="12" letter-spacing="1.5">
    <rect x="24" y="{H - 44}" width="430" height="24" rx="4" fill="{BG0}" fill-opacity=".85" stroke="{CYAN}" stroke-opacity=".3"/>
    <text x="38" y="{H - 28}" fill="{TEXT}">{e(AFFILIATION)}</text>
    <rect x="{W - 344}" y="{H - 44}" width="320" height="24" rx="4" fill="{BG0}" fill-opacity=".85" stroke="{MAGENTA}" stroke-opacity=".3"/>
    <text x="{W - 184}" y="{H - 28}" fill="{MAGENTA}" text-anchor="middle" letter-spacing="0">∂u/∂t + (u·∇)u = −∇p/ρ + ν∇²u</text>
  </g>
{frame_close(W, H)}"""
    return svg(W, H, body, f"{NAME} — {TAGLINE}")


def terminal() -> str:
    W, line_h, top = 900, 30, 78
    H = top + line_h * (len(TERMINAL) + 1) + 26
    prompt = "kshitiz@tungston:~$ "
    char_w = 8.4  # ~0.6em at 14px monospace
    t = 0.6
    lines = []
    for i, (kind, text) in enumerate(TERMINAL):
        y = top + i * line_h
        if kind == "cmd":
            n = len(text)
            dur = max(0.04 * n, 0.4)
            px = 36 + len(prompt) * char_w
            widths = ";".join(f"{k * char_w:.1f}" for k in range(n + 1))
            kts = ";".join(f"{k / n:.4f}" for k in range(n + 1))
            lines.append(f"""  <clipPath id="c{i}"><rect x="{px:.1f}" y="{y - 18}" width="0" height="26">
    <animate attributeName="width" begin="{t + 0.25:.2f}s" dur="{dur:.2f}s" fill="freeze" calcMode="discrete"
             values="{widths}" keyTimes="{kts}"/></rect></clipPath>
  <g opacity="0"><animate attributeName="opacity" values="0;1" begin="{t:.2f}s" dur=".01s" fill="freeze"/>
    <text x="36" y="{y}"><tspan fill="{GREEN}">kshitiz</tspan><tspan fill="{DIM}">@</tspan><tspan fill="{VIOLET}">tungston</tspan><tspan fill="{DIM}">:</tspan><tspan fill="{CYAN}">~</tspan><tspan fill="{DIM}">$ </tspan></text>
    <text x="{px:.1f}" y="{y}" fill="{TEXT}" clip-path="url(#c{i})">{e(text)}</text>
  </g>""")
            t += 0.25 + dur + 0.35
        else:
            col = GREEN if kind == "ok" else "#a9b7d6"
            lines.append(
                f'  <text x="36" y="{y}" fill="{col}" opacity="0"><tspan fill="{MAGENTA}">› </tspan>{e(text)}'
                f'<animate attributeName="opacity" values="0;1" begin="{t:.2f}s" dur=".25s" fill="freeze"/></text>'
            )
            t += 0.22
    y = top + len(TERMINAL) * line_h
    px = 36 + len(prompt) * char_w
    lines.append(f"""  <g opacity="0"><animate attributeName="opacity" values="0;1" begin="{t:.2f}s" dur=".01s" fill="freeze"/>
    <text x="36" y="{y}"><tspan fill="{GREEN}">kshitiz</tspan><tspan fill="{DIM}">@</tspan><tspan fill="{VIOLET}">tungston</tspan><tspan fill="{DIM}">:</tspan><tspan fill="{CYAN}">~</tspan><tspan fill="{DIM}">$ </tspan></text>
    <rect x="{px:.1f}" y="{y - 15}" width="9" height="19" fill="{CYAN}">
      <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/>
    </rect></g>""")

    dots = "".join(
        f'<circle cx="{30 + k * 20}" cy="26" r="6" fill="{c}"/>'
        for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"])
    )
    body = f"""<defs>{common_defs(W, H)}</defs>
{frame_open(W, H)}  <rect width="{W}" height="52" fill="{BG0}" fill-opacity=".9"/>
  <line x1="0" x2="{W}" y1="52" y2="52" stroke="{CYAN}" stroke-opacity=".3"/>
  {dots}
  <text x="{W / 2}" y="31" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{DIM}" letter-spacing="2">~/kshitiz — neural-shell — 120×{len(TERMINAL) + 1}</text>
  <text x="{W - 28}" y="31" text-anchor="end" font-family="{MONO}" font-size="11" fill="{GREEN}">● LIVE</text>
  <g font-family="{MONO}" font-size="14" xml:space="preserve">
{chr(10).join(lines)}
  </g>
{frame_close(W, H, 4)}"""
    return svg(W, H, body, "About — " + " ".join(t for k, t in TERMINAL if k != "cmd"))


def character_sheet() -> str:
    W, H = 900, 520
    rows = []
    bx, bw, top, gap = 40, 520, 116, 58
    for i, (code, skill, cred, val) in enumerate(STATS):
        y = top + i * gap
        fw = bw * val / 12
        delay = 0.3 + i * 0.18
        segs = "".join(
            f'<line x1="{bx + k * bw / 12:.1f}" x2="{bx + k * bw / 12:.1f}" y1="{y + 10}" y2="{y + 20}"/>'
            for k in range(1, 12)
        )
        rows.append(f"""  <g font-family="{MONO}">
    <text x="{bx}" y="{y}" font-size="15" font-weight="700" fill="{CYAN}" letter-spacing="2">{code}</text>
    <text x="{bx + 56}" y="{y}" font-size="15" fill="{TEXT}">{e(skill)}</text>
    <text x="{bx + bw}" y="{y}" font-size="12" fill="{DIM}" text-anchor="end">{e(cred)}  ·  <tspan fill="{MAGENTA}">{val:02d}/12</tspan></text>
    <rect x="{bx}" y="{y + 10}" width="{bw}" height="10" rx="2" fill="{LINE}" fill-opacity=".6"/>
    <rect x="{bx}" y="{y + 10}" width="0" height="10" rx="2" fill="url(#beam)" filter="url(#soft)">
      <animate attributeName="width" values="0;{fw:.1f}" begin="{delay:.2f}s" dur="1.2s" fill="freeze"
               calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>
    </rect>
    <rect x="{bx}" y="{y + 10}" width="40" height="10" fill="#fff" opacity=".0" clip-path="url(#bar{i})">
      <animate attributeName="x" values="{bx - 40};{bx + fw:.1f}" begin="{delay + 1.3:.2f}s" dur="2.4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;.35;0" begin="{delay + 1.3:.2f}s" dur="2.4s" repeatCount="indefinite"/>
    </rect>
    <clipPath id="bar{i}"><rect x="{bx}" y="{y + 10}" width="{fw:.1f}" height="10" rx="2"/></clipPath>
    <g stroke="{BG0}" stroke-width="2">{segs}</g>
  </g>""")

    # radar chart
    cx, cy, R = 735, 240, 108
    n = len(STATS)
    ang = [-math.pi / 2 + 2 * math.pi * k / n for k in range(n)]
    rings = "".join(
        f'<polygon points="{" ".join(f"{cx + R * f * math.cos(a):.1f},{cy + R * f * math.sin(a):.1f}" for a in ang)}"/>'
        for f in (0.25, 0.5, 0.75, 1)
    )
    spokes = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx + R * math.cos(a):.1f}" y2="{cy + R * math.sin(a):.1f}"/>' for a in ang)
    pts = " ".join(f"{cx + R * s[3] / 12 * math.cos(a):.1f},{cy + R * s[3] / 12 * math.sin(a):.1f}" for s, a in zip(STATS, ang))
    zero = " ".join(f"{cx},{cy}" for _ in ang)
    labels = "".join(
        f'<text x="{cx + (R + 20) * math.cos(a):.1f}" y="{cy + (R + 20) * math.sin(a) + 4:.1f}">{s[0]}</text>'
        for s, a in zip(STATS, ang)
    )
    vertices = "".join(
        f'<circle cx="{cx + R * s[3] / 12 * math.cos(a):.1f}" cy="{cy + R * s[3] / 12 * math.sin(a):.1f}" r="3" fill="{MAGENTA}" opacity="0">'
        f'<animate attributeName="opacity" values="0;1" begin="1.6s" dur=".3s" fill="freeze"/></circle>'
        for s, a in zip(STATS, ang)
    )
    radar = f"""  <defs>
    <radialGradient id="sweep" cx="0" cy="0" r="1" gradientUnits="objectBoundingBox">
      <stop offset="0" stop-color="{CYAN}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <g fill="none" stroke="{CYAN}" stroke-opacity=".22">{rings}{spokes}</g>
  <path d="M{cx} {cy} L{cx} {cy - R} A{R} {R} 0 0 1 {cx + R * math.sin(math.radians(40)):.1f} {cy - R * math.cos(math.radians(40)):.1f} Z" fill="{CYAN}" fill-opacity=".10">
    <animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" dur="5s" repeatCount="indefinite"/>
  </path>
  <polygon points="{zero}" fill="{VIOLET}" fill-opacity=".25" stroke="{MAGENTA}" stroke-width="2" filter="url(#soft)">
    <animate attributeName="points" values="{zero};{pts}" begin=".4s" dur="1.4s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>
  </polygon>
  {vertices}
  <g font-family="{MONO}" font-size="12" fill="{CYAN}" text-anchor="middle" font-weight="700">{labels}</g>"""

    qy = 430
    quests = []
    for i, (status, text) in enumerate(QUESTS):
        y = qy + i * 26
        col = GREEN if status == "ACTIVE" else AMBER
        quests.append(f"""  <g font-family="{MONO}" font-size="13">
    <circle cx="{bx + 5}" cy="{y - 4}" r="4" fill="{col}"><animate attributeName="opacity" values="1;.25;1" dur="{1.2 + i * 0.4:.1f}s" repeatCount="indefinite"/></circle>
    <text x="{bx + 18}" y="{y}" fill="{col}" font-weight="700" letter-spacing="1">{status:<8}</text>
    <text x="{bx + 110}" y="{y}" fill="{TEXT}">▸ {e(text)}</text>
  </g>""")

    body = f"""<defs>{common_defs(W, H)}</defs>
{frame_open(W, H)}{twinkles(W, H, 25)}
  <g font-family="{MONO}">
    <text x="40" y="44" font-size="13" fill="{DIM}" letter-spacing="3">◢ OPERATOR PROFILE  //  ID: KKS-0x2F</text>
    <text x="40" y="72" font-size="20" font-weight="800" fill="{TEXT}" letter-spacing="2">{e(NAME)}</text>
    <text x="{W - 40}" y="72" font-size="13" fill="{CYAN}" text-anchor="end" letter-spacing="1">CLASS: MATHEMATICIAN × ML RESEARCHER × SYSTEM BUILDER</text>
  </g>
  <line x1="40" x2="{W - 40}" y1="88" y2="88" stroke="url(#beam)" stroke-opacity=".7"/>
{chr(10).join(rows)}
{radar}
  <line x1="40" x2="{W - 40}" y1="{qy - 30}" y2="{qy - 30}" stroke="{CYAN}" stroke-opacity=".2" stroke-dasharray="4 6"/>
  <text x="{W - 40}" y="{qy - 38}" font-family="{MONO}" font-size="11" fill="{DIM}" text-anchor="end" letter-spacing="3">QUEST LOG</text>
{chr(10).join(quests)}
{frame_close(W, H)}"""
    return svg(W, H, body, "Character sheet — " + ", ".join(f"{s[1]} {s[3]}/12" for s in STATS))


def glyph(kind: str, cx: float, cy: float) -> str:
    if kind == "reticle":
        return f"""<g transform="translate({cx} {cy})" fill="none" stroke="{CYAN}" stroke-width="1.6">
      <rect x="-26" y="-26" width="52" height="52" stroke-dasharray="14 24" stroke-dashoffset="7"/>
      <circle r="16" stroke="{MAGENTA}" stroke-dasharray="25 75"><animateTransform attributeName="transform" type="rotate" values="0;360" dur="3s" repeatCount="indefinite"/></circle>
      <circle r="3" fill="{CYAN}"/>
      <rect x="-30" y="-30" width="60" height="60" stroke-opacity=".4"><animate attributeName="stroke-opacity" values=".1;.8;.1" dur="2s" repeatCount="indefinite"/></rect>
    </g>"""
    if kind == "hand":
        bars = "".join(
            f'<rect x="{-24 + k * 10}" y="0" width="6" height="10" fill="url(#beam)">'
            f'<animate attributeName="height" values="6;{14 + k * 7};6" dur="{1 + k * 0.15:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="-3;{-(7 + k * 3.5):.1f};-3" dur="{1 + k * 0.15:.2f}s" repeatCount="indefinite"/></rect>'
            for k in range(5)
        )
        return f"""<g transform="translate({cx} {cy})">
      <circle r="32" fill="none" stroke="{CYAN}" stroke-opacity=".3"/>{bars}
    </g>"""
    # pen trajectory: a Lissajous curve drawn on loop
    pts = " L".join(
        f"{cx + 26 * math.sin(3 * t + math.pi / 2):.1f} {cy + 22 * math.sin(2 * t):.1f}"
        for t in [k * 2 * math.pi / 120 for k in range(121)]
    )
    return f"""<path d="M{pts}" fill="none" stroke="{MAGENTA}" stroke-width="1.8" stroke-dasharray="260 260" stroke-dashoffset="260" filter="url(#soft)">
      <animate attributeName="stroke-dashoffset" values="260;0;-260" dur="4s" repeatCount="indefinite"/></path>
    <circle r="3" fill="{CYAN}"><animateMotion dur="4s" repeatCount="indefinite" path="M{pts}"/></circle>"""


def project_card(idx: int, title: str, desc: str, tags: list[str], kind: str) -> str:
    W, H = 900, 128
    tag_x, tag_svg = 128, []
    for t in tags:
        w = len(t) * 7.2 + 20
        tag_svg.append(
            f'<rect x="{tag_x}" y="86" width="{w:.0f}" height="22" rx="11" fill="{CYAN}" fill-opacity=".08" stroke="{CYAN}" stroke-opacity=".4"/>'
            f'<text x="{tag_x + w / 2:.0f}" y="101" text-anchor="middle" fill="{CYAN}">{e(t)}</text>'
        )
        tag_x += w + 8
    body = f"""<defs>{common_defs(W, H)}</defs>
{frame_open(W, H)}  <rect width="104" height="{H}" fill="{BG0}" fill-opacity=".8"/>
  <line x1="104" x2="104" y1="0" y2="{H}" stroke="{CYAN}" stroke-opacity=".3"/>
  {glyph(kind, 52, H / 2)}
  <g font-family="{MONO}">
    <text x="128" y="38" font-size="11" fill="{DIM}" letter-spacing="3">MODULE_0{idx + 1}</text>
    <text x="236" y="38" font-size="18" font-weight="800" fill="{TEXT}" letter-spacing="2">{e(title)}</text>
    <text x="128" y="66" font-size="13" fill="#a9b7d6">{e(desc)}</text>
    <g font-size="11">{"".join(tag_svg)}</g>
    <text x="{W - 32}" y="101" font-size="13" font-weight="700" fill="{MAGENTA}" text-anchor="end" letter-spacing="2">ACCESS REPO ›
      <animate attributeName="opacity" values="1;.35;1" dur="1.8s" repeatCount="indefinite"/></text>
  </g>
{frame_close(W, H, 3 + idx)}"""
    return svg(W, H, body, f"{title} — {desc}")


def divider(label: str) -> str:
    W, H = 900, 40
    body = f"""<defs>
  <linearGradient id="pulse" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}"/>
    <stop offset="1" stop-color="{MAGENTA}" stop-opacity="0"/>
  </linearGradient>
  <filter id="neon"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<line x1="0" x2="{W}" y1="20" y2="20" stroke="{CYAN}" stroke-opacity=".25"/>
<rect x="-160" y="18.5" width="160" height="3" fill="url(#pulse)" filter="url(#neon)">
  <animate attributeName="x" values="-160;{W}" dur="3.2s" repeatCount="indefinite"/>
</rect>
<rect x="{W / 2 - 130}" y="6" width="260" height="28" rx="4" fill="{BG0}" stroke="{CYAN}" stroke-opacity=".5"/>
<text x="{W / 2}" y="25" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="{CYAN}" letter-spacing="4">{e(label)}</text>
<circle cx="{W / 2 - 116}" cy="20" r="3" fill="{MAGENTA}"><animate attributeName="opacity" values="1;.2;1" dur="1.2s" repeatCount="indefinite"/></circle>
<circle cx="{W / 2 + 116}" cy="20" r="3" fill="{MAGENTA}"><animate attributeName="opacity" values=".2;1;.2" dur="1.2s" repeatCount="indefinite"/></circle>"""
    return svg(W, H, body, label)


def footer() -> str:
    W, H = 1200, 220
    waves = []
    for i, (yy, amp, wl, col, dur, op) in enumerate(
        [(150, 14, 300, CYAN, 6, .5), (160, 10, 220, VIOLET, 8, .4), (170, 8, 400, MAGENTA, 10, .35)]
    ):
        d1 = sine_path(-400, W + 400, yy, amp, wl, 0)
        waves.append(
            f'<path d="{d1}" fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="1.5">'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;{-wl} 0" dur="{dur}s" repeatCount="indefinite"/></path>'
        )
    lines = "".join(
        f'<text x="600" y="{70 + i * 34}" opacity="0">{e(q)}'
        f'<animate attributeName="opacity" values="0;1" begin="{0.4 + i * 0.9:.1f}s" dur="1s" fill="freeze"/></text>'
        for i, q in enumerate(QUOTE)
    )
    body = f"""<defs>{common_defs(W, H)}</defs>
{frame_open(W, H)}{twinkles(W, H, 45, y_max=130)}
  <g>{"".join(waves)}</g>
  <g font-family="{MONO}" font-size="22" font-style="italic" fill="{TEXT}" text-anchor="middle" filter="url(#soft)">{lines}</g>
  <text x="600" y="{H - 22}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{DIM}" letter-spacing="4">— END OF TRANSMISSION —
    <animate attributeName="opacity" values="1;.3;1" dur="2.4s" repeatCount="indefinite"/></text>
{frame_close(W, H, 5)}"""
    return svg(W, H, body, " ".join(QUOTE))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    files = {
        "header.svg": header(),
        "terminal.svg": terminal(),
        "character-sheet.svg": character_sheet(),
        "footer.svg": footer(),
        "divider-about.svg": divider("01 // BOOT LOG"),
        "divider-profile.svg": divider("02 // OPERATOR STATS"),
        "divider-projects.svg": divider("03 // MODULES"),
        "divider-stack.svg": divider("04 // ARSENAL"),
        "divider-activity.svg": divider("05 // TELEMETRY"),
    }
    for i, (slug, title, desc, tags, kind) in enumerate(PROJECTS):
        files[f"project-{slug}.svg"] = project_card(i, title, desc, tags, kind)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"  wrote assets/{name}  ({len(content.encode()) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
