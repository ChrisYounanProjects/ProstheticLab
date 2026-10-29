"""ProstheticLab — interactive educational prosthetic-hand design simulator.

Run locally with:
    streamlit run app.py

The scores and cost ranges in this prototype are illustrative teaching estimates,
not clinical performance claims or quotes for real prostheses.
"""

from __future__ import annotations

import math
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="ProstheticLab | Design a Hand",
    page_icon="🦾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Design system
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
      :root { --ink:#eef3fb; --muted:#97a7bc; --line:#25344a; --panel:#111c2d; --panel2:#0d1726; --cyan:#5de0d0; --blue:#78a7ff; --amber:#f8c66b; }
      html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
      .stApp { background: radial-gradient(ellipse at 12% 0%, #162843 0%, #0a1220 48%, #080e18 100%); color:var(--ink); }
      .block-container { padding-top: 1.7rem; padding-bottom: 3.5rem; max-width: 1450px; }
      [data-testid="stSidebar"] { background: #0b1422; border-right:1px solid #1d2b3e; }
      [data-testid="stSidebar"] * { color: #d9e5f5; }
      h1,h2,h3 { color:#f3f7ff !important; letter-spacing:-.035em; }
      h1 { font-weight:800 !important; }
      p, li { color:#c3cede; }
      label, .stMarkdown label { color:#d5deeb !important; }
      .eyebrow { font-family:'DM Mono',monospace; text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; color:var(--cyan); }
      .hero-title { font-size:clamp(2.25rem,4.3vw,4.15rem); font-weight:800; line-height:1.03; color:#f7f9fe; letter-spacing:-.065em; margin:.45rem 0 .9rem 0; }
      .hero-title span { color:var(--cyan); }
      .hero-sub { max-width:750px; color:#9fadc2; font-size:1.03rem; line-height:1.7; }
      .section-kicker { color:#8da4c1; font-family:'DM Mono',monospace; font-size:.7rem; letter-spacing:.16em; text-transform:uppercase; margin-bottom:.45rem; }
      .panel { background:linear-gradient(150deg,rgba(20,33,52,.96),rgba(12,22,37,.96)); border:1px solid #25364d; border-radius:20px; padding:1.15rem 1.25rem; box-shadow:0 14px 38px rgba(0,0,0,.14); }
      .metric-card { min-height:135px; background:linear-gradient(145deg,#142238,#101a2b); border:1px solid #2a3b52; border-radius:16px; padding:1rem 1.05rem; }
      .metric-label { font-family:'DM Mono',monospace; color:#91a4bc; font-size:.68rem; text-transform:uppercase; letter-spacing:.1em; }
      .metric-value { font-size:2rem; line-height:1.25; color:#f4f7ff; font-weight:800; letter-spacing:-.055em; margin:.3rem 0 .15rem; }
      .metric-note { font-size:.77rem; color:#9aabc0; }
      .status-pill { display:inline-block; border:1px solid #2a675f; background:#12322f; color:#79f0db; border-radius:100px; padding:.27rem .65rem; font-size:.72rem; font-weight:700; }
      .soft-pill { display:inline-block; border:1px solid #334660; background:#14243a; color:#c2d5ed; border-radius:100px; padding:.25rem .6rem; font-size:.72rem; }
      .callout { border-left:3px solid var(--cyan); padding:.15rem 0 .15rem .85rem; margin:.8rem 0; color:#bdcada; line-height:1.6; }
      .learn-card { height:100%; background:#101b2b; border:1px solid #27384e; border-radius:17px; padding:1.1rem 1.15rem; }
      .learn-number { color:var(--cyan); font-family:'DM Mono',monospace; font-size:.73rem; letter-spacing:.12em; }
      .learn-title { color:#f0f5ff; font-size:1.08rem; font-weight:800; margin:.45rem 0 .5rem; }
      .learn-copy { font-size:.9rem; color:#aab8ca; line-height:1.65; }
      .tiny-note { font-size:.75rem; color:#8496ad; line-height:1.6; }
      .divider { height:1px; background:#25344a; margin:1.3rem 0; }
      [data-testid="stMetric"] { background:#111c2d; border:1px solid #27384e; border-radius:15px; padding:1rem; }
      [data-testid="stMetricLabel"] { color:#94a7bf !important; }
      [data-testid="stMetricValue"] { color:#f2f7ff !important; }
      .stSelectbox [data-baseweb="select"] > div, .stSlider, .stRadio { color:#e5edf8; }
      div[data-testid="stProgressBar"] > div { background:#22344b; }
      div[data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#5de0d0,#78a7ff); }
      .stTabs [data-baseweb="tab-list"] { gap:.5rem; border-bottom:1px solid #25344a; }
      .stTabs [data-baseweb="tab"] { color:#98a9bf; border-radius:10px 10px 0 0; padding:.7rem 1rem; }
      .stTabs [aria-selected="true"] { color:#5de0d0 !important; }
      .stButton > button { background:#5de0d0; color:#06151d; border:0; border-radius:10px; font-weight:800; }
      .stButton > button:hover { background:#8ceee1; color:#06151d; border:0; }
      footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Educational model: deliberately transparent and illustrative
# -----------------------------------------------------------------------------
DRIVES = {
    "Tendon-driven": {
        "cost": 1800,
        "precision": 76,
        "strength": 80,
        "response": 70,
        "comfort": 79,
        "durability": 73,
        "summary": "Motors pull cables routed through the hand, much like tendons pull parts of a biological hand.",
        "pros": "Compact fingers, remote motors can reduce finger weight, and the cable path can be serviceable.",
        "tradeoff": "Cables can stretch or wear, so tension and maintenance matter.",
    },
    "Direct-motor": {
        "cost": 5200,
        "precision": 92,
        "strength": 90,
        "response": 87,
        "comfort": 64,
        "durability": 76,
        "summary": "Small motors or gearboxes move joints more directly, allowing independent finger control.",
        "pros": "Fine control and independently commanded fingers can support precise tasks.",
        "tradeoff": "More actuators can mean greater weight, wiring complexity, power use, and cost.",
    },
    "Underactuated": {
        "cost": 3400,
        "precision": 74,
        "strength": 84,
        "response": 78,
        "comfort": 84,
        "durability": 82,
        "summary": "Fewer motors drive multiple joints, so the fingers can conform around objects instead of requiring one motor per joint.",
        "pros": "A useful balance of adaptive grasping, lower actuator count, and mechanical simplicity.",
        "tradeoff": "Individual finger positions are less independently controllable.",
    },
}

JOINTS = {
    "Single hinge": {
        "cost": 600,
        "precision": -2,
        "strength": 5,
        "response": 2,
        "comfort": -2,
        "durability": 10,
        "summary": "One main rotational axis. Simple geometry makes the joint easier to build and maintain.",
    },
    "Multi-link": {
        "cost": 1500,
        "precision": 8,
        "strength": 1,
        "response": 1,
        "comfort": 2,
        "durability": 1,
        "summary": "Several links coordinate motion, creating a more natural-looking curl path with extra parts to tune.",
    },
    "Compliant joint": {
        "cost": 900,
        "precision": -5,
        "strength": -4,
        "response": 0,
        "comfort": 12,
        "durability": 2,
        "summary": "A flexible section bends slightly under load, helping absorb small impacts and tolerate alignment differences.",
    },
}

GRIPS = {
    "Power grip": {
        "precision": -4,
        "strength": 12,
        "response": -1,
        "comfort": -1,
        "use": "Holding a bottle, handle, or larger object against the palm.",
        "pattern": "power",
    },
    "Precision pinch": {
        "precision": 14,
        "strength": -9,
        "response": 1,
        "comfort": 0,
        "use": "Picking up a small object between the thumb and index finger.",
        "pattern": "pinch",
    },
    "Tripod grip": {
        "precision": 9,
        "strength": -3,
        "response": 0,
        "comfort": 1,
        "use": "Stabilizing a pen or small tool with the thumb and two fingers.",
        "pattern": "tripod",
    },
    "Hook grip": {
        "precision": -7,
        "strength": 10,
        "response": -2,
        "comfort": -3,
        "use": "Supporting a bag handle or loop with curled fingers.",
        "pattern": "hook",
    },
    "Open / point": {
        "precision": 2,
        "strength": -14,
        "response": 8,
        "comfort": 3,
        "use": "Opening the hand, positioning the fingers, or pointing toward a target.",
        "pattern": "open",
    },
}


def clamp_score(value: float) -> int:
    return int(max(5, min(99, round(value))))


def build_hand_svg(grip_pattern: str, drive_name: str, joint_name: str, power: int) -> str:
    """Create a small SVG illustration whose finger pose changes by grip choice."""
    poses = {
        "open": {
            "index": [(133, 202), (127, 164), (126, 123), (130, 91)],
            "middle": [(165, 192), (163, 147), (164, 103), (168, 69)],
            "ring": [(198, 192), (203, 151), (210, 115), (214, 85)],
            "pinky": [(226, 204), (239, 171), (249, 143), (255, 119)],
            "thumb": [(145, 258), (116, 246), (104, 222), (119, 204)],
        },
        "power": {
            "index": [(134, 202), (123, 174), (139, 171), (157, 189)],
            "middle": [(165, 192), (155, 162), (174, 158), (191, 180)],
            "ring": [(198, 194), (192, 166), (211, 168), (226, 190)],
            "pinky": [(226, 204), (231, 185), (247, 191), (251, 208)],
            "thumb": [(145, 258), (115, 247), (132, 226), (160, 221)],
        },
        "pinch": {
            "index": [(134, 202), (127, 165), (139, 137), (164, 126)],
            "middle": [(165, 192), (157, 167), (177, 166), (193, 185)],
            "ring": [(198, 194), (194, 171), (212, 176), (225, 195)],
            "pinky": [(226, 204), (232, 188), (247, 198), (250, 211)],
            "thumb": [(145, 258), (117, 246), (139, 222), (166, 134)],
        },
        "tripod": {
            "index": [(134, 202), (127, 166), (137, 139), (159, 130)],
            "middle": [(165, 192), (159, 157), (173, 133), (195, 130)],
            "ring": [(198, 194), (193, 170), (211, 176), (225, 195)],
            "pinky": [(226, 204), (232, 188), (247, 198), (250, 211)],
            "thumb": [(145, 258), (117, 246), (139, 221), (166, 136)],
        },
        "hook": {
            "index": [(134, 202), (124, 180), (143, 188), (153, 208)],
            "middle": [(165, 192), (155, 169), (176, 180), (190, 203)],
            "ring": [(198, 194), (192, 173), (214, 187), (224, 207)],
            "pinky": [(226, 204), (231, 188), (248, 202), (249, 218)],
            "thumb": [(145, 258), (117, 246), (112, 223), (126, 209)],
        },
    }
    pose = poses.get(grip_pattern, poses["open"])

    def finger(name: str, pts: list[tuple[int, int]], width: int) -> str:
        p0, p1, p2, p3 = pts
        # Outer structural segments and a lighter inner highlight create a machined look.
        d = f"M {p0[0]} {p0[1]} L {p1[0]} {p1[1]} L {p2[0]} {p2[1]} L {p3[0]} {p3[1]}"
        joints = "".join(
            f'<circle cx="{x}" cy="{y}" r="{max(5, width // 2 - 2)}" fill="#162436" stroke="#9cadc1" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y}" r="2.2" fill="#5de0d0"/>'
            for x, y in (p1, p2)
        )
        return (
            f'<path d="{d}" fill="none" stroke="#0a101a" stroke-width="{width + 7}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="url(#metal)" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M {p0[0]} {p0[1]} L {p1[0]} {p1[1]} L {p2[0]} {p2[1]} L {p3[0]} {p3[1]}" fill="none" stroke="#dce6f2" stroke-opacity=".45" stroke-width="2" stroke-linecap="round"/>'
            f'{joints}<circle cx="{p3[0]}" cy="{p3[1]}" r="8" fill="#111927" stroke="#74889f" stroke-width="2"/>'
            f'<circle cx="{p3[0]}" cy="{p3[1]}" r="3" fill="#5de0d0"/>'
        )

    fingers_svg = "".join([
        finger("index", pose["index"], 18),
        finger("middle", pose["middle"], 20),
        finger("ring", pose["ring"], 18),
        finger("pinky", pose["pinky"], 15),
        finger("thumb", pose["thumb"], 19),
    ])

    # Style details vary slightly by selected mechanism and joint type.
    wire_color = "#f8c66b" if drive_name == "Tendon-driven" else ("#78a7ff" if drive_name == "Direct-motor" else "#5de0d0")
    joint_detail = "#f8c66b" if joint_name == "Compliant joint" else "#5de0d0"
    actuator_count = 2 if drive_name == "Underactuated" else (4 if drive_name == "Tendon-driven" else 5)
    actuator_blocks = "".join(
        f'<rect x="{143 + i * 19}" y="258" width="13" height="28" rx="4" fill="#273a50" stroke="{wire_color}" stroke-width="1.5"/>'
        f'<rect x="{146 + i * 19}" y="263" width="7" height="18" rx="2" fill="{wire_color}" fill-opacity=".8"/>'
        for i in range(actuator_count)
    )
    power_len = 30 + power * 2
    return f'''<!doctype html><html><head><style>
      *{{box-sizing:border-box}} body{{margin:0;background:transparent;font-family:Arial,sans-serif;}}
      .wrap{{width:100%;max-width:550px;margin:0 auto;}}
      svg{{width:100%;height:auto;display:block;}}
    </style></head><body><div class="wrap"><svg viewBox="0 0 380 430" role="img" aria-label="Illustration of a mechanical prosthetic hand in the selected grip pose">
      <defs>
        <linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#dbe5f1"/><stop offset=".48" stop-color="#7f91a8"/><stop offset="1" stop-color="#42556d"/></linearGradient>
        <linearGradient id="palm" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#73879e"/><stop offset=".48" stop-color="#34465b"/><stop offset="1" stop-color="#1e2c3e"/></linearGradient>
        <linearGradient id="wrist" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4c6178"/><stop offset="1" stop-color="#1a293a"/></linearGradient>
        <pattern id="grid" width="23" height="23" patternUnits="userSpaceOnUse"><path d="M23 0H0V23" fill="none" stroke="#243650" stroke-width=".6"/></pattern>
      </defs>
      <rect x="3" y="3" width="374" height="424" rx="22" fill="#0b1422" stroke="#24364d"/>
      <rect x="3" y="3" width="374" height="424" rx="22" fill="url(#grid)" opacity=".7"/>
      <circle cx="188" cy="194" r="143" fill="#16263b" opacity=".35"/>
      <g>{fingers_svg}</g>
      <!-- Palm shell -->
      <path d="M124 201 C116 217 117 239 125 258 L140 295 Q147 313 167 319 L240 319 Q266 313 275 291 L287 254 Q293 230 280 210 L259 188 Q248 178 235 187 L220 200 L191 188 L161 187 Q140 183 124 201Z" fill="#0a111c" stroke="#0a111c" stroke-width="10"/>
      <path d="M124 201 C116 217 117 239 125 258 L140 295 Q147 313 167 319 L240 319 Q266 313 275 291 L287 254 Q293 230 280 210 L259 188 Q248 178 235 187 L220 200 L191 188 L161 187 Q140 183 124 201Z" fill="url(#palm)" stroke="#a8b8ca" stroke-width="2"/>
      <path d="M143 218 Q164 204 185 214 L193 292 L164 301 Q148 291 143 272Z" fill="#122033" stroke="#6f849d" stroke-width="1.5"/>
      <path d="M198 212 L246 211 Q263 218 265 237 L255 285 Q251 299 237 301 L206 299Z" fill="#15273b" stroke="#72869d" stroke-width="1.5"/>
      <!-- Electronics and actuators -->
      <rect x="151" y="224" width="88" height="20" rx="4" fill="#0b1421" stroke="{wire_color}" stroke-width="1.5"/>
      <path d="M157 231H178L184 237H204L211 229H231" stroke="{wire_color}" stroke-width="2" fill="none"/>
      <circle cx="178" cy="231" r="3" fill="{wire_color}"/><circle cx="211" cy="229" r="3" fill="{wire_color}"/>
      {actuator_blocks}
      <path d="M150 248 C168 244 187 245 202 252 S235 254 249 247" fill="none" stroke="{wire_color}" stroke-width="2.2" stroke-dasharray="4 4"/>
      <path d="M148 270 L158 270 L163 278 L177 278 L182 268 L197 268" fill="none" stroke="#9fb0c5" stroke-width="2"/>
      <rect x="184" y="274" width="47" height="13" rx="4" fill="#273b50" stroke="#91a3b9" stroke-width="1.2"/>
      <rect x="190" y="278" width="26" height="5" rx="2" fill="{wire_color}"/>
      <circle cx="240" cy="280" r="5" fill="#0b1422" stroke="{joint_detail}" stroke-width="2"/>
      <circle cx="240" cy="280" r="1.7" fill="{joint_detail}"/>
      <!-- Wrist connector -->
      <path d="M163 314 L158 337 Q157 347 169 351 L234 351 Q246 347 244 336 L239 314Z" fill="url(#wrist)" stroke="#91a4b9" stroke-width="2"/>
      <path d="M171 326H231M169 335H233M172 344H230" stroke="#0b1422" stroke-width="3"/>
      <rect x="178" y="354" width="47" height="33" rx="7" fill="#253950" stroke="#8ba0b8" stroke-width="2"/>
      <rect x="188" y="362" width="27" height="16" rx="3" fill="#0c1726" stroke="{wire_color}" stroke-width="1.5"/>
      <path d="M193 370H210" stroke="{wire_color}" stroke-width="2"/>
      <circle cx="188" cy="395" r="3" fill="#5de0d0"/><circle cx="215" cy="395" r="3" fill="#5de0d0"/>
      <!-- Callouts -->
      <path d="M248 235 L292 221 L322 221" stroke="{wire_color}" stroke-width="1.4" fill="none"/>
      <circle cx="248" cy="235" r="3" fill="{wire_color}"/>
      <text x="319" y="211" fill="#a8b8cd" font-size="8" text-anchor="end" letter-spacing="1.3">CONTROL</text>
      <text x="319" y="233" fill="#f0f5ff" font-size="11" text-anchor="end">{drive_name.upper()}</text>
      <path d="M241 282 L283 301 L321 301" stroke="{joint_detail}" stroke-width="1.4" fill="none"/>
      <circle cx="241" cy="282" r="3" fill="{joint_detail}"/>
      <text x="320" y="292" fill="#a8b8cd" font-size="8" text-anchor="end" letter-spacing="1.1">JOINT SYSTEM</text>
      <text x="320" y="313" fill="#f0f5ff" font-size="10" text-anchor="end">{joint_name.upper()}</text>
      <text x="24" y="398" fill="#7c91aa" font-size="9" letter-spacing="1.4">PROSTHETICLAB / CONCEPT MODEL</text>
      <text x="350" y="398" fill="#5de0d0" font-size="10" text-anchor="end">PWR {power:02d}/10</text>
    </svg></div></body></html>'''


# -----------------------------------------------------------------------------
# Header and navigation
# -----------------------------------------------------------------------------
st.markdown('<div class="eyebrow">ENGINEERING EXPLORER · MODULE 02</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Prosthetic<span>Lab</span></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Design a conceptual prosthetic hand. Swap its mechanisms, change the grip, and see how engineers balance useful motion, strength, comfort, and cost.</div>',
    unsafe_allow_html=True,
)
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='eyebrow'>LAB CONSOLE</div>", unsafe_allow_html=True)
    st.markdown("## Build parameters")
    st.caption("Change any control to update the concept model and its estimated trade-offs.")
    drive = st.selectbox("Actuation system", list(DRIVES.keys()), index=2, help="How mechanical force is delivered to the fingers.")
    joint = st.selectbox("Finger joint design", list(JOINTS.keys()), index=1, help="The type of joint used to shape finger movement.")
    grip = st.selectbox("Target grip", list(GRIPS.keys()), index=0, help="The task the hand is being designed to perform.")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("### Tune the system")
    motor_power = st.slider("Motor power", 1, 10, 7, help="Higher settings increase the conceptual strength rating and power demand.")
    response_speed = st.slider("Control responsiveness", 1, 10, 6, help="Higher settings favor faster response in this simplified model.")
    comfort_priority = st.slider("Comfort priority", 1, 10, 7, help="Represents how strongly the design favors a lighter, more comfortable setup.")
    budget = st.slider("Target budget (illustrative)", 500, 12000, 6000, step=250, format="$%d")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='tiny-note'>Educational prototype only. Scores are illustrative relative ratings—not medical-device specifications, a diagnosis, or a real prosthesis quote.</div>", unsafe_allow_html=True)

# Derive all values from current selections.
d = DRIVES[drive]
j = JOINTS[joint]
g = GRIPS[grip]

cost_estimate = 1850 + d["cost"] + j["cost"] + (motor_power - 5) * 95 + max(0, response_speed - 5) * 65
cost_estimate = max(500, cost_estimate)
precision = clamp_score(d["precision"] + j["precision"] + g["precision"] + (response_speed - 5) * 1.7)
strength = clamp_score(d["strength"] + j["strength"] + g["strength"] + (motor_power - 5) * 2.7)
response = clamp_score(d["response"] + j["response"] + g["response"] + (response_speed - 5) * 3.2)
comfort = clamp_score(d["comfort"] + j["comfort"] + g["comfort"] + (comfort_priority - 5) * 2.6 - max(0, motor_power - 7) * 2)
durability = clamp_score(d["durability"] + j["durability"] + (motor_power - 5) * .5)
stability = clamp_score(0.36 * strength + 0.34 * precision + 0.30 * durability + (8 if grip in ("Power grip", "Hook grip") else 0))
within_budget = cost_estimate <= budget

# Main app tabs.
tab_build, tab_mechanics, tab_tradeoffs = st.tabs(["01  /  BUILD LAB", "02  /  HOW IT WORKS", "03  /  DESIGN TRADE-OFFS"])

with tab_build:
    left, right = st.columns([1.04, 1], gap="large")
    with left:
        st.markdown('<div class="section-kicker">LIVE CONCEPT VIEW</div>', unsafe_allow_html=True)
        st.markdown(f"### {grip}")
        st.markdown(f"<span class='status-pill'>● SIMULATION UPDATED</span> &nbsp; <span class='soft-pill'>{drive}</span> &nbsp; <span class='soft-pill'>{joint}</span>", unsafe_allow_html=True)
        components.html(build_hand_svg(g["pattern"], drive, joint, motor_power), height=630, scrolling=False)
        st.markdown(f"<div class='callout'><b style='color:#eef4ff'>Task focus:</b> {g['use']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tiny-note'>{d['summary']}</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-kicker">SIMULATED PERFORMANCE</div>', unsafe_allow_html=True)
        st.markdown("### What this design prioritizes")
        col_a, col_b = st.columns(2, gap="medium")
        with col_a:
            st.markdown(f'''<div class="metric-card"><div class="metric-label">Grip stability</div><div class="metric-value">{stability}<span style="font-size:1rem;color:#8da2bb">/100</span></div><div class="metric-note">Strength, precision, durability blend</div></div>''', unsafe_allow_html=True)
        with col_b:
            st.markdown(f'''<div class="metric-card"><div class="metric-label">Estimated build cost</div><div class="metric-value">${cost_estimate:,}</div><div class="metric-note">Illustrative parts + integration estimate</div></div>''', unsafe_allow_html=True)

        st.markdown("<div style='height:.9rem'></div>", unsafe_allow_html=True)
        metrics = [
            ("Precision", precision, "Small, controlled movements"),
            ("Strength", strength, "Conceptual force potential"),
            ("Response", response, "How quickly a command is reflected"),
            ("Comfort", comfort, "Relative comfort / weight emphasis"),
            ("Durability", durability, "Relative mechanical simplicity"),
        ]
        for label, score, note in metrics:
            m1, m2 = st.columns([0.80, 0.20], vertical_alignment="center")
            with m1:
                st.markdown(f"<div style='font-weight:700;color:#dce7f6;font-size:.88rem'>{label}</div><div style='font-size:.72rem;color:#8297b0;margin-bottom:.2rem'>{note}</div>", unsafe_allow_html=True)
                st.progress(score / 100)
            with m2:
                st.markdown(f"<div style='font-family:DM Mono,monospace;text-align:right;color:#5de0d0;font-size:1.05rem;padding-top:.1rem'>{score:02d}</div>", unsafe_allow_html=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        if within_budget:
            st.markdown(f"<span class='status-pill'>WITHIN TARGET BUDGET</span> &nbsp; <span class='tiny-note'>${budget - cost_estimate:,} remaining</span>", unsafe_allow_html=True)
            st.markdown("<div class='callout'>This design fits the selected budget estimate. That does not guarantee a real build would cost this amount.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='display:inline-block;border:1px solid #7b6335;background:#3a2c17;color:#ffd58a;border-radius:100px;padding:.27rem .65rem;font-size:.72rem;font-weight:700'>OVER TARGET BUDGET</span> &nbsp; <span class='tiny-note'>${cost_estimate - budget:,} above target</span>", unsafe_allow_html=True)
            st.markdown("<div class='callout' style='border-color:#f8c66b'>Consider a simpler joint, a less expensive drive system, or lower power / response settings.</div>", unsafe_allow_html=True)

        st.markdown("#### Mechanism notes")
        st.markdown(f"**Why it might work:** {d['pros']}")
        st.markdown(f"**What to watch:** {d['tradeoff']}")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">QUICK EXPERIMENT</div>', unsafe_allow_html=True)
    st.markdown("### Compare the design choices")
    comparison = st.columns(3, gap="medium")
    compare_items = [
        ("Tendon-driven", "Cable-based movement", "$1.8k drive estimate"),
        ("Direct-motor", "Independent motor control", "$5.2k drive estimate"),
        ("Underactuated", "Fewer motors, adaptive fingers", "$3.4k drive estimate"),
    ]
    for container, (name, tag, price) in zip(comparison, compare_items):
        with container:
            selected = name == drive
            border = "#5de0d0" if selected else "#27384e"
            container.markdown(
                f'''<div style="background:#101b2b;border:1px solid {border};border-radius:14px;padding:1rem;min-height:115px;">
                <div style="font-family:DM Mono,monospace;color:{'#5de0d0' if selected else '#8ea4bf'};font-size:.68rem;letter-spacing:.1em">{'CURRENT SELECTION' if selected else 'DRIVE OPTION'}</div>
                <div style="font-size:1.02rem;color:#f1f6ff;font-weight:800;margin:.35rem 0">{name}</div>
                <div style="font-size:.82rem;color:#9eafc4">{tag}</div><div style="font-size:.73rem;color:#5de0d0;margin-top:.5rem">{price}</div></div>''',
                unsafe_allow_html=True,
            )

with tab_mechanics:
    st.markdown('<div class="section-kicker">MECHANICS 101</div>', unsafe_allow_html=True)
    st.markdown("## Three layers turn an intention into motion")
    st.markdown("A prosthetic hand is a system: the control signal starts the action, an actuator creates movement, and joints guide that movement into a useful grasp.")
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown('''<div class="learn-card"><div class="learn-number">LAYER 01</div><div class="learn-title">Control signal</div><div class="learn-copy">A user interface or sensor provides a command. Depending on the device, that command may come from buttons, motion sensors, or muscle-signal sensors. This demo models the command as a responsiveness slider.</div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown('''<div class="learn-card"><div class="learn-number">LAYER 02</div><div class="learn-title">Actuation</div><div class="learn-copy">Motors produce force. Tendon-driven systems pull cables; direct-motor designs move joints more directly; underactuated systems use fewer motors to coordinate several joints.</div></div>''', unsafe_allow_html=True)
    with c3:
        st.markdown('''<div class="learn-card"><div class="learn-number">LAYER 03</div><div class="learn-title">Joints &amp; contact</div><div class="learn-copy">Hinges, linkages, and flexible joints shape how fingers curl and meet an object. The best geometry depends on the task, the object, the user's needs, and the overall fit.</div></div>''', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("### Your selected mechanism")
    st.markdown(f"**{drive}** — {d['summary']}")
    st.markdown(f"**{joint}** — {j['summary']}")
    st.markdown(f"**{grip}** — {g['use']}")
    st.markdown(f"<div class='callout'><b style='color:#eef4ff'>Engineering question:</b> Can the chosen mechanism deliver the motion needed for the task without adding too much weight, complexity, or cost?</div>", unsafe_allow_html=True)

with tab_tradeoffs:
    st.markdown('<div class="section-kicker">DESIGN REVIEW</div>', unsafe_allow_html=True)
    st.markdown("## Every decision affects another requirement")
    st.markdown("There is no single best design for every user or activity. Engineers compare compromises and test whether a hand works reliably for the intended tasks.")
    rows = [
        ("Tendon-driven", "Routing cables and reducing finger-side motor bulk", "Cable wear, stretch, and tension adjustment"),
        ("Direct-motor", "Independent finger control and precision", "Actuator count, weight, wiring, and energy use"),
        ("Underactuated", "Adaptive grasping with fewer actuators", "Less independent control of each finger"),
        ("Single hinge", "Simple, robust rotational movement", "A less natural curl path"),
        ("Multi-link", "Coordinated, more natural movement path", "More parts and more tuning"),
        ("Compliant joint", "Flexibility and impact tolerance", "Less exact positioning under load"),
    ]
    for i, (name, goal, tradeoff_text) in enumerate(rows):
        st.markdown(
            f'''<div style="display:grid;grid-template-columns:1.05fr 1.55fr 1.55fr;gap:.8rem;background:{'#132136' if i % 2 == 0 else '#0e1928'};border:1px solid #24354b;border-radius:11px;padding:.85rem 1rem;margin:.45rem 0;align-items:start">
              <div style="color:#eaf2ff;font-weight:800">{name}</div>
              <div><div style="font-family:DM Mono,monospace;color:#5de0d0;font-size:.65rem;letter-spacing:.08em;margin-bottom:.25rem">DESIGN BENEFIT</div><div style="color:#aebed1;font-size:.83rem;line-height:1.5">{goal}</div></div>
              <div><div style="font-family:DM Mono,monospace;color:#f8c66b;font-size:.65rem;letter-spacing:.08em;margin-bottom:.25rem">TRADE-OFF</div><div style="color:#aebed1;font-size:.83rem;line-height:1.5">{tradeoff_text}</div></div>
            </div>''',
            unsafe_allow_html=True,
        )
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("### Design review for your current build")
    st.markdown(f"- **Task:** {g['use']}")
    st.markdown(f"- **Best score in this simplified model:** {'precision' if precision >= max(strength, response, comfort, durability) else 'strength' if strength >= max(response, comfort, durability) else 'response' if response >= max(comfort, durability) else 'comfort' if comfort >= durability else 'durability'} ({max(precision, strength, response, comfort, durability)})")
    st.markdown(f"- **Main compromise:** {d['tradeoff']}")
    st.markdown(f"- **Budget check:** estimated ${cost_estimate:,} against a ${budget:,} target — {'within target' if within_budget else 'above target'}.")
    st.markdown("<div class='tiny-note'>Model note: scores are rule-based, illustrative teaching values. Real performance depends on detailed mechanics, control methods, fit, materials, user needs, testing, and many other variables.</div>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
foot_l, foot_r = st.columns([3, 1])
with foot_l:
    st.markdown("<div class='tiny-note'>PROSTHETICLAB · A CONCEPTUAL LEARNING TOOL FOR ASSISTIVE-TECHNOLOGY ENGINEERING</div>", unsafe_allow_html=True)
with foot_r:
    st.markdown("<div style='text-align:right;color:#6f879f;font-family:DM Mono,monospace;font-size:.7rem'>BUILD / TEST / REFINE</div>", unsafe_allow_html=True)
