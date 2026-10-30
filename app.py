"""ProstheticLab — interactive educational prosthetic-hand design simulator.

Run locally with:
    streamlit run app.py

The scores and cost ranges in this prototype are illustrative teaching estimates,
not clinical performance claims or quotes for real prostheses.
"""

from __future__ import annotations

import base64
import json
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
# Brand, loading screen, and layout chooser
# -----------------------------------------------------------------------------
CREATOR = "Chris Younan"
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5de0d0"/><stop offset="1" stop-color="#78a7ff"/></linearGradient>
<radialGradient id="b" cx=".5" cy=".35" r=".75"><stop offset="0" stop-color="#1d3858"/><stop offset="1" stop-color="#091120"/></radialGradient></defs>
<circle cx="100" cy="100" r="94" fill="url(#b)" stroke="url(#g)" stroke-width="5"/>
<circle cx="100" cy="100" r="82" fill="none" stroke="#5de0d0" stroke-opacity=".3" stroke-width="1.5" stroke-dasharray="2 8" stroke-linecap="round"/>
<g stroke="#091120" stroke-width="2.5">
<rect x="66" y="52" width="14" height="62" rx="7" fill="url(#g)"/><rect x="83" y="42" width="14" height="72" rx="7" fill="url(#g)"/>
<rect x="100" y="48" width="14" height="66" rx="7" fill="url(#g)"/><rect x="117" y="62" width="14" height="52" rx="7" fill="url(#g)"/>
<rect x="44" y="108" width="14" height="40" rx="7" fill="url(#g)" transform="rotate(-32 51 128)"/>
<rect x="64" y="100" width="72" height="56" rx="18" fill="url(#g)"/></g>
<g fill="#091120"><circle cx="73" cy="82" r="3.8"/><circle cx="90" cy="74" r="3.8"/><circle cx="107" cy="78" r="3.8"/><circle cx="124" cy="88" r="3.8"/></g>
<g fill="#5de0d0"><circle cx="73" cy="82" r="1.5"/><circle cx="90" cy="74" r="1.5"/><circle cx="107" cy="78" r="1.5"/><circle cx="124" cy="88" r="1.5"/></g>
<circle cx="100" cy="130" r="10" fill="#091120" stroke="#fff" stroke-opacity=".85" stroke-width="2"/><circle cx="100" cy="130" r="3.4" fill="#5de0d0"/>
<rect x="82" y="157" width="36" height="14" rx="4" fill="#5de0d0"/></svg>"""
LOGO_URI = "data:image/svg+xml;base64," + base64.b64encode(LOGO_SVG.encode()).decode()

SPLASH_HTML = """<style>
@property --pl-n{syntax:'<integer>';initial-value:0;inherits:false}
#pl-splash{position:fixed;inset:0;z-index:2147483000;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:1rem;
background:radial-gradient(ellipse at 50% 38%,#17304f 0%,#0a1220 55%,#060a12 100%);animation:pl-bg 5.4s ease forwards;font-family:'Manrope',sans-serif}
@keyframes pl-bg{0%,82%{opacity:1;visibility:visible}100%{opacity:0;visibility:hidden}}
#pl-splash img{width:150px;height:150px;animation:pl-logo 5.4s cubic-bezier(.4,0,.2,1) forwards;filter:drop-shadow(0 0 28px rgba(93,224,208,.45))}
@keyframes pl-logo{0%{opacity:0;transform:scale(.6)}12%,66%{opacity:1;transform:scale(1)}92%,100%{opacity:0;transform:scale(4.2)}}
.pl-f{opacity:0;animation:pl-fade 5.4s ease forwards}
@keyframes pl-fade{0%{opacity:0;transform:translateY(10px)}14%,64%{opacity:1;transform:none}74%,100%{opacity:0;transform:translateY(-6px)}}
.pl-s{font-family:'DM Mono',monospace;letter-spacing:.3em;font-size:.78rem;color:#5de0d0;margin-top:1.5rem}
.pl-t{font-size:clamp(2.2rem,8vw,3.7rem);font-weight:800;letter-spacing:-.05em;color:#f4f8ff;margin:.3rem 0;line-height:1.05}.pl-t span{color:#5de0d0}
.pl-by{color:#9fb2cc;font-size:1.02rem}.pl-by b{color:#fff;font-weight:800}
.pl-bar{width:min(320px,70vw);height:5px;border-radius:5px;background:#16263b;margin-top:1.7rem;overflow:hidden}
.pl-bar i{display:block;height:100%;width:0;border-radius:5px;background:linear-gradient(90deg,#5de0d0,#78a7ff);animation:pl-fill 5.4s linear forwards}
@keyframes pl-fill{0%,8%{width:0}66%,100%{width:100%}}
.pl-pct{font-family:'DM Mono',monospace;font-size:.75rem;color:#8da4c1;margin-top:.7rem;counter-reset:pln var(--pl-n);animation:pl-cnt 5.4s linear forwards}
.pl-pct::after{content:counter(pln) '%'}
@keyframes pl-cnt{0%,8%{--pl-n:0}66%,100%{--pl-n:100}}
</style>
<div id="pl-splash"><img src="__LOGO__" alt="ProstheticLab logo">
<div class="pl-f pl-s">WELCOME TO</div><div class="pl-f pl-t">Prosthetic<span>Lab</span></div>
<div class="pl-f pl-by">Designed &amp; built by <b>__NAME__</b></div>
<div class="pl-f pl-bar"><i></i></div><div class="pl-f pl-pct"></div></div>"""

st.session_state.setdefault("mode", None)
if not st.session_state.get("splashed"):
    st.session_state["splashed"] = True
    st.markdown(SPLASH_HTML.replace("__LOGO__", LOGO_URI).replace("__NAME__", CREATOR), unsafe_allow_html=True)

IS_MOBILE = st.session_state["mode"] == "mobile"
st.markdown("<style>@media (max-width:720px){.trow{grid-template-columns:1fr!important}}</style>", unsafe_allow_html=True)

if st.session_state["mode"] is None:
    st.markdown(
        "<style>[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl'],[data-testid='collapsedControl']{display:none!important}"
        ".block-container{max-width:880px!important;padding-top:3rem!important}</style>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div style='text-align:center'><img src='{LOGO_URI}' style='width:104px;filter:drop-shadow(0 0 22px rgba(93,224,208,.4))'>
        <div class='eyebrow' style='margin-top:1rem'>WELCOME</div><div class='hero-title'>Prosthetic<span>Lab</span></div>
        <div class='hero-sub' style='margin:0 auto 1.6rem'>Designed &amp; built by <b style='color:#fff'>{CREATOR}</b>.<br>How would you like to explore?</div></div>""",
        unsafe_allow_html=True,
    )
    pick_d, pick_m = st.columns(2, gap="large")
    for col, key, icon, name, blurb, mode in [
        (pick_d, "pick_desktop", "🖥️", "Desktop", "Side control panel, large 3D viewer, two-column lab.", "desktop"),
        (pick_m, "pick_mobile", "📱", "Mobile", "Touch-first layout: sticky 3D viewer, big controls, pinch to zoom.", "mobile"),
    ]:
        with col:
            st.markdown(
                f"<div class='learn-card' style='text-align:center;min-height:120px;margin-bottom:.6rem'><div style='font-size:2rem'>{icon}</div>"
                f"<div class='learn-title'>{name}</div><div class='learn-copy'>{blurb}</div></div>",
                unsafe_allow_html=True,
            )
            if st.button(f"Open {name} layout", key=key, use_container_width=True):
                st.session_state["mode"] = mode
                st.rerun()
    st.markdown(f"<div class='tiny-note' style='text-align:center;margin-top:1.5rem'>PROSTHETICLAB · BY {CREATOR.upper()}</div>", unsafe_allow_html=True)
    st.stop()

if IS_MOBILE:
    st.markdown("""<style>
      [data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none!important}
      .block-container{padding:.8rem .7rem 4rem!important}
      .hero-sub{display:none}
      .stButton>button{min-height:3rem;font-size:1rem}
      [data-baseweb="select"]>div{min-height:3rem}
      .stTabs [data-baseweb="tab-list"]{overflow-x:auto;gap:.1rem}
      .stTabs [data-baseweb="tab"]{padding:.7rem .75rem;white-space:nowrap;font-size:.8rem}
      .metric-card{min-height:auto;padding:.7rem .85rem}.metric-value{font-size:1.6rem}
      .st-key-viewer{position:sticky;top:.25rem;z-index:60;background:#0a1220;padding:.2rem 0 .35rem;margin-bottom:.4rem}
      h3{font-size:1.2rem!important}
    </style>""", unsafe_allow_html=True)

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


HAND3D_HTML = r"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%;background:transparent;overflow:hidden;font-family:'Manrope',Arial,sans-serif}
#v{position:absolute;inset:0;border:1px solid #25364d;border-radius:20px;overflow:hidden;background:radial-gradient(circle at 50% 38%,#1c3453 0%,#0d1829 60%,#080e18 100%)}
canvas{display:block;touch-action:none;cursor:grab}canvas:active{cursor:grabbing}
.hint{position:absolute;bottom:50px;left:14px;font:500 10px 'DM Mono',monospace;letter-spacing:.14em;color:#7f97b4;pointer-events:none}
.bar{position:absolute;bottom:12px;left:12px;display:flex;gap:6px}
.bar button{background:#12233a;color:#cfe0f5;border:1px solid #2c4262;border-radius:9px;padding:6px 11px;font:700 11px 'Manrope',Arial;cursor:pointer}
.bar button:hover{border-color:#5de0d0}.bar button.on{background:#5de0d0;color:#06151d;border-color:#5de0d0}
.tag{position:absolute;left:0;top:0;pointer-events:none;font:500 10px 'DM Mono',monospace;letter-spacing:.08em;color:#e8f1ff;white-space:nowrap;
background:rgba(10,20,34,.82);border:1px solid var(--c);border-radius:8px;padding:4px 8px 4px 8px}
.tag b{color:var(--c);font-weight:500;margin-right:6px}
.hud{position:absolute;top:12px;right:12px;width:178px;background:rgba(10,20,34,.84);border:1px solid #2c4262;border-radius:12px;padding:10px 12px;font:500 10px 'DM Mono',monospace;color:#9fb4cf;letter-spacing:.06em}
.hud .row{display:flex;justify-content:space-between;margin:6px 0 3px}.hud .v{color:#eaf3ff}
.hud .b2{height:5px;background:#1d3048;border-radius:4px;overflow:hidden}.hud .b2 i{display:block;height:100%;background:linear-gradient(90deg,#5de0d0,#78a7ff)}
#st{margin-top:9px;font-weight:700}
.toast{position:absolute;top:14px;left:50%;transform:translateX(-50%);padding:7px 16px;border-radius:20px;font:800 12px 'Manrope',Arial;display:none;white-space:nowrap;z-index:5}
.info{position:absolute;bottom:12px;right:12px;width:205px;background:rgba(10,20,34,.92);border:1px solid #5de0d0;border-radius:12px;padding:10px 12px;color:#c3d3e8;font:500 11px/1.5 'Manrope',Arial;display:none}
.info b{display:block;color:#fff;font-size:12px;margin-bottom:3px}
.mob .hint,.mob .tag{display:none}
.mob .hud{top:8px;right:8px;left:8px;width:auto;display:grid;grid-template-columns:1fr 1fr;gap:1px 14px;padding:7px 10px}
.mob .hud .row{margin:3px 0}.mob .hud .b2{align-self:center}.mob #st{grid-column:1/3;margin-top:3px}
.mob .bar{bottom:8px;left:8px;right:8px;flex-wrap:wrap;justify-content:center}
.mob .bar button{padding:10px 13px;font-size:12px}
.mob .info{left:8px;right:8px;width:auto;bottom:62px}
</style></head><body><div id="v">
<div class="hint">DRAG ROTATE · SCROLL ZOOM · RIGHT-DRAG PAN</div>
<div class="bar"><button id="bt">&#9654; Run test</button><button id="bx">X-ray</button><button id="bs" class="on">Auto-spin</button><button id="bz">+</button><button id="bo">&minus;</button><button id="br">Reset</button></div>
<div class="tag" id="t1"></div><div class="tag" id="t2"></div>
<div class="hud"><div class="row"><span>GRIP FORCE</span><span class="v" id="hs"></span></div><div class="b2"><i id="hsb"></i></div>
<div class="row"><span>STABILITY</span><span class="v" id="hb"></span></div><div class="b2"><i id="hbb"></i></div>
<div class="row"><span>WEIGHT</span><span class="v" id="hw"></span></div><div class="row"><span>COST</span><span class="v" id="hc"></span></div><div id="st"></div></div>
<div class="toast" id="ts"></div><div class="info" id="inf"></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
const CFG=__CFG__, V3=THREE.Vector3, rad=d=>d*Math.PI/180;
const ST=(function(){try{return window.parent.__pl=window.parent.__pl||{}}catch(e){return {}}})();
const root=document.getElementById('v');if(CFG.mobile)root.classList.add('mob');
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.outputEncoding=THREE.sRGBEncoding;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
root.insertBefore(renderer.domElement,root.firstChild);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(32,1,.1,100);
// Studio environment for believable metal reflections
const pm=new THREE.PMREMGenerator(renderer),es=new THREE.Scene();
es.add(new THREE.Mesh(new THREE.SphereGeometry(30,32,16),new THREE.MeshBasicMaterial({color:0x22344d,side:THREE.BackSide})));
[[0,14,8,16,3,0xffffff,5],[-14,3,-6,3,12,0x5de0d0,3],[14,4,5,3,10,0x78a7ff,3],[0,-6,10,14,2,0xffe2b0,1.5]].forEach(b=>{
 const m=new THREE.Mesh(new THREE.BoxGeometry(b[3],b[4],.5),new THREE.MeshBasicMaterial({color:new THREE.Color(b[5]).multiplyScalar(b[6])}));m.position.set(b[0],b[1],b[2]);m.lookAt(0,0,0);es.add(m)});
scene.environment=pm.fromScene(es,.03).texture;
scene.add(new THREE.HemisphereLight(0xbfd9ff,0x1a2233,.35));
const key=new THREE.DirectionalLight(0xffffff,1.1);key.position.set(4,7,9);scene.add(key);
const rim=new THREE.DirectionalLight(CFG.within?0x5de0d0:0xff5b5b,.9);rim.position.set(-7,3,-6);scene.add(rim);

const DC={'Tendon-driven':0xf8c66b,'Direct-motor':0x78a7ff,'Underactuated':0x5de0d0}[CFG.drive];
const JC=CFG.joint==='Compliant joint'?0xf8c66b:0x5de0d0;
const mat=(c,m,r,o)=>new THREE.MeshStandardMaterial(Object.assign({color:c,metalness:m,roughness:r},o||{}));
const M={shell:mat(0x3b475a,.75,.34),metal:mat(0xb9c4d3,.92,.24),dark:mat(0x1b222d,.6,.45),pad:mat(0x10151c,0,.85),plate:mat(0x56657b,.85,.3),
 cyan:mat(0x5de0d0,.2,.4,{emissive:0x5de0d0,emissiveIntensity:.3+CFG.power*.12}),jc:mat(JC,.3,.45,{emissive:JC,emissiveIntensity:.5}),
 rubber:mat(0xc99a3c,0,.7),drive:mat(DC,.8,.3,{emissive:DC,emissiveIntensity:0}),amber:mat(0xf8c66b,.3,.4,{emissive:0xf8c66b,emissiveIntensity:.35}),pcb:mat(0x0d3b2e,.4,.5)};
const shellMats=[M.shell,M.pad,M.plate];
const mesh=(g,m,x,y,z)=>{const o=new THREE.Mesh(g,m);o.position.set(x||0,y||0,z||0);return o};
const hand=new THREE.Group();scene.add(hand);
const tg=(o,k)=>{o.userData.part=k;return o},gearJ=[];
function gearMesh(r,n){const g=new THREE.Group();g.add(mesh(new THREE.CylinderGeometry(r,r,.06,24),M.metal));
 for(let k=0;k<n;k++){const a=k*2*Math.PI/n,t=mesh(new THREE.BoxGeometry(r*.4,.06,r*.32),M.metal,Math.cos(a)*r,0,Math.sin(a)*r);t.rotation.y=-a;g.add(t)}
 g.add(mesh(new THREE.CylinderGeometry(r*.3,r*.3,.08,12),M.dark));return g}

function rrect(w,h,r){const s=new THREE.Shape(),x=-w/2,y=-h/2;s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);return s}
// --- Palm, wrist, socket
const pg=new THREE.ExtrudeGeometry(rrect(1.7,1.9,.4),{depth:.6,bevelEnabled:true,bevelThickness:.15,bevelSize:.15,bevelSegments:6,curveSegments:14});pg.translate(0,0,-.3);
hand.add(mesh(pg,M.shell));
hand.add(mesh(new THREE.BoxGeometry(1.35,1.5,.05),M.plate,0,0,-.47));
hand.add(mesh(new THREE.BoxGeometry(1.0,.045,.03),M.cyan,0,.45,-.5));
hand.add(mesh(new THREE.BoxGeometry(1.0,.045,.03),M.cyan,0,.3,-.5));
hand.add(mesh(new THREE.BoxGeometry(1.25,.95,.08),M.pad,0,-.1,.46));
const cy=(r1,r2,h,m,y)=>mesh(new THREE.CylinderGeometry(r1,r2,h,32),m,0,y,0);
hand.add(cy(.62,.55,.7,M.metal,-1.45));
[-1.2,-1.5,-1.75].forEach(y=>{const t=mesh(new THREE.TorusGeometry(.6,.04,10,40),M.dark,0,y,0);t.rotation.x=Math.PI/2;hand.add(t)});
hand.add(cy(.8,.74,1.2,M.shell,-2.4));
const ring=mesh(new THREE.TorusGeometry(.78,.035,10,48),M.cyan,0,-1.85,0);ring.rotation.x=Math.PI/2;hand.add(ring);
hand.add(cy(.7,.7,.25,M.dark,-3.05));

// --- Internals: motors, PCB, battery
const nm=CFG.motors,motors=[];
for(let i=0;i<nm;i++){const x=nm===1?0:-.62+1.24*i/(nm-1);
 const g=new THREE.Group();g.position.set(x,.2,-.02);
 g.add(mesh(new THREE.CylinderGeometry(.13,.13,.62,20),M.drive));
 g.add(mesh(new THREE.CylinderGeometry(.07,.07,.2,12),M.metal,0,-.4,0));
 for(let k=0;k<3;k++){const a=k*2.094,f=mesh(new THREE.BoxGeometry(.05,.5,.03),M.cyan,Math.sin(a)*.135,0,Math.cos(a)*.135);f.rotation.y=a;g.add(f)}
 const ge=gearMesh(.17,10);ge.position.y=-.42;g.add(ge);g.userData.part='motor';
 g.add(mesh(new THREE.CylinderGeometry(.15,.15,.08,20),M.dark,0,.2,0));
 hand.add(g);motors.push(g)}
let wt=null;
if(CFG.drive==='Underactuated'){const m=new THREE.Group();m.position.set(0,.8,-.2);m.add(mesh(new THREE.BoxGeometry(1.3,.05,.05),M.metal));
 const pv=mesh(new THREE.CylinderGeometry(.07,.07,.12,14),M.amber);pv.rotation.x=Math.PI/2;m.add(pv);
 const mk=x=>{const s=new THREE.Group();s.position.set(x,-.14,0);s.add(mesh(new THREE.BoxGeometry(.6,.04,.04),M.cyan),mesh(new THREE.BoxGeometry(.03,.14,.03),M.metal,0,.07,0));m.add(s);return s};
 wt={m,a:mk(-.43),b:mk(.43)};hand.add(m)}
hand.add(tg(mesh(new THREE.BoxGeometry(1.35,.45,.05),M.pcb,0,-.6,-.2),'pcb'));
for(let i=0;i<4;i++)hand.add(mesh(new THREE.BoxGeometry(.07,.04,.03),M.cyan,-.45+.3*i,-.52,-.17));
hand.add(tg(mesh(new THREE.BoxGeometry(.95,.4,.3),M.dark,0,-.6,.08),'pcb'));
hand.add(mesh(new THREE.BoxGeometry(.8,.05,.32),M.amber,0,-.6,.08));

// --- Joint + segment builders
function joint(r){const g=new THREE.Group();g.userData.part='joint';
 if(CFG.joint==='Compliant joint'){g.add(mesh(new THREE.SphereGeometry(r*.8,18,14),M.rubber));
  [-.14,0,.14].forEach(k=>{const t=mesh(new THREE.TorusGeometry(r*.85,r*.11,10,28),M.rubber,0,r*k*2,0);t.rotation.x=Math.PI/2;g.add(t)})}
 else{g.add(mesh(new THREE.SphereGeometry(r*.97,18,14),M.dark));
  const pin=mesh(new THREE.CylinderGeometry(r*.36,r*.36,r*2.15,18),M.jc);pin.rotation.z=Math.PI/2;g.add(pin);
  if(CFG.joint==='Multi-link')[-1,1].forEach(s=>{g.add(mesh(new THREE.BoxGeometry(r*.2,r*1.9,r*.55),M.metal,s*r*1.0,r*.3,0));
   g.add(mesh(new THREE.CylinderGeometry(r*.12,r*.12,r*.3,10),M.jc,s*r*1.05,r*.95,0)).rotation.z=Math.PI/2})}
 if(CFG.drive==='Direct-motor'){const gw=new THREE.Group();gw.rotation.z=Math.PI/2;gw.position.x=r*1.12;const ge=gearMesh(r*.72,8);gw.add(ge);g.add(gw);gearJ.push(ge)}
 return g}
function seg(L,r,last){const g=new THREE.Group();
 g.add(mesh(new THREE.CylinderGeometry(r*.88,r,L,24),last?M.shell:M.metal,0,L/2,0));
 g.add(mesh(new THREE.BoxGeometry(r*1.25,L*.76,r*.5),M.pad,0,L/2,r*.78));
 g.add(mesh(new THREE.BoxGeometry(r*.9,L*.6,r*.2),M.plate,0,L/2,-r*.88));
 if(last){g.add(mesh(new THREE.SphereGeometry(r*.88,20,14),M.shell,0,L,0));
  const p=mesh(new THREE.SphereGeometry(r*.66,16,12),M.pad,0,L*.8,r*.78);p.scale.set(1,1.25,.6);g.add(p);
  g.add(mesh(new THREE.BoxGeometry(r*.4,.03,.03),M.cyan,0,L*.45,-r*1.0))}
 return g}
const FD=[{x:-.66,y:1.08,L:[.85,.55,.42],r:.19},{x:-.22,y:1.1,L:[.95,.62,.45],r:.2},{x:.22,y:1.08,L:[.88,.58,.43],r:.19},{x:.64,y:.98,L:[.68,.42,.36],r:.16}];
const fingers=FD.map(d=>{const mcp=new THREE.Group();mcp.position.set(d.x,d.y,0);mcp.userData.part='finger';hand.add(mcp);
 mcp.add(joint(d.r),seg(d.L[0],d.r));
 const pip=new THREE.Group();pip.position.y=d.L[0];mcp.add(pip);pip.add(joint(d.r*.92),seg(d.L[1],d.r*.92));
 const dip=new THREE.Group();dip.position.y=d.L[1];pip.add(dip);dip.add(joint(d.r*.85),seg(d.L[2],d.r*.85,true));
 return {d,mcp,pip,dip}});
const th=(function(){const cmc=new THREE.Group();cmc.position.set(-.95,-.55,.15);cmc.userData.part='thumb';cmc.rotation.order='YXZ';hand.add(cmc);
 cmc.add(joint(.24),seg(.75,.24));
 const mp=new THREE.Group();mp.position.y=.75;cmc.add(mp);mp.add(joint(.21),seg(.55,.21));
 const ip=new THREE.Group();ip.position.y=.55;mp.add(ip);ip.add(joint(.19),seg(.45,.19,true));
 return {cmc,mp,ip}})();
const fPad=f=>f.dip.localToWorld(new V3(0,f.d.L[2]*.78,f.d.r*.85*.8));
const tPad=()=>th.ip.localToWorld(new V3(0,.45*.78,.19*.8));
function apply(a){fingers.forEach((f,i)=>{f.mcp.rotation.x=rad(a[3*i]);f.pip.rotation.x=rad(a[3*i+1]);f.dip.rotation.x=rad(a[3*i+2])});
 th.cmc.rotation.set(rad(a[13]),rad(a[14]),rad(a[12]),'YXZ');th.mp.rotation.x=rad(a[15]);th.ip.rotation.x=rad(a[16])}

// --- Grip poses: [index,middle,ring,pinky]x[mcp,pip,dip], thumb [abduct,flex,oppose,mp,ip]
const P={open:[4,2,2,4,2,2,4,2,2,4,2,2,35,0,0,5,5],
 power:[60,75,55,62,78,55,64,80,52,66,80,50,20,25,55,25,25],
 hook:[8,100,65,8,102,65,8,104,62,8,104,60,35,0,0,5,5],
 pinch:[38,48,28,55,75,45,60,80,45,65,85,45,0,0,0,0,0],
 tripod:[38,48,28,42,52,30,60,80,45,65,85,45,0,0,0,0,0]};
const contact={};
function solve(name,idx){const p=P[name];apply(p);hand.updateMatrixWorld(true);
 const tg=new V3();idx.forEach(i=>tg.add(fPad(fingers[i])));tg.multiplyScalar(1/idx.length);
 const t=[30,20,50,20,20],lo=[0,-10,0,0,0],hi=[70,60,90,70,70],st=[30,30,30,30,30];
 const cost=()=>{apply(p.slice(0,12).concat(t));hand.updateMatrixWorld(true);return tPad().distanceTo(tg)};
 let best=cost();
 for(let it=0;it<300;it++){let imp=false;
  for(let k=0;k<5;k++)for(const s of[1,-1]){const o=t[k];t[k]=Math.max(lo[k],Math.min(hi[k],o+s*st[k]));const c=cost();if(c<best-1e-4){best=c;imp=true}else t[k]=o}
  if(!imp){for(let k=0;k<5;k++)st[k]*=.6;if(st[0]<.05)break}}
 for(let k=0;k<5;k++)p[12+k]=t[k];contact[name]=tg}
solve('pinch',[0]);solve('tripod',[0,1]);
// --- Held objects
const BR=.6,BCY=.5,BCZ=.5+BR+.04;
function hitF(f,cy,cz,R){const d=(p,rr)=>Math.hypot(p.y-cy,p.z-cz)-R-rr;
 return d(fPad(f),.03)<=0||d(f.pip.localToWorld(new V3()),f.d.r*.92)<=0||d(f.dip.localToWorld(new V3()),f.d.r*.85)<=0}
function wrap(name,ra,cy,cz,R){const p=P[name];fingers.forEach((f,i)=>{let s=0;
 for(;s<1.6;s+=.02){f.mcp.rotation.x=rad(ra[0]*s);f.pip.rotation.x=rad(ra[1]*s);f.dip.rotation.x=rad(ra[2]*s);hand.updateMatrixWorld(true);if(hitF(f,cy,cz,R))break}
 p[3*i]=ra[0]*s;p[3*i+1]=ra[1]*s;p[3*i+2]=ra[2]*s})}
function thumbTo(p,tg){apply(p);hand.updateMatrixWorld(true);const t=[30,20,50,20,20],lo=[0,-10,0,0,0],hi=[70,60,90,70,70],st=[30,30,30,30,30];
 const cost=()=>{apply(p.slice(0,12).concat(t));hand.updateMatrixWorld(true);return tPad().distanceTo(tg)};let best=cost();
 for(let it=0;it<300;it++){let imp=false;for(let k=0;k<5;k++)for(const s of[1,-1]){const o=t[k];t[k]=Math.max(lo[k],Math.min(hi[k],o+s*st[k]));const c=cost();if(c<best-1e-4){best=c;imp=true}else t[k]=o}
  if(!imp){for(let k=0;k<5;k++)st[k]*=.6;if(st[0]<.05)break}}
 for(let k=0;k<5;k++)p[12+k]=t[k]}
wrap('power',[55,70,50],BCY,BCZ,BR);thumbTo(P.power,new V3(-.45,BCY-BR*.95,BCZ));
apply(P.hook);hand.updateMatrixWorld(true);const hookC=new V3();fingers.forEach(f=>hookC.add(fPad(f)));hookC.multiplyScalar(.25);
const glass=mat(0x7fb8ff,0,.08,{transparent:true,opacity:.42}),water=mat(0x2f7fe0,0,.2,{transparent:true,opacity:.75}),cap=mat(0xf8c66b,.3,.4);
const bottle=new THREE.Group(),bb=new THREE.Group();bb.rotation.z=-Math.PI/2;bottle.add(bb);
bb.add(mesh(new THREE.CylinderGeometry(BR,BR,1.7,36),glass),mesh(new THREE.CylinderGeometry(BR*.9,BR*.9,1.2,36),water,0,-.15,0),mesh(new THREE.CylinderGeometry(.27,BR,.36,36),glass,0,1.03,0),mesh(new THREE.CylinderGeometry(.27,.27,.5,24),glass,0,1.46,0),mesh(new THREE.CylinderGeometry(.3,.3,.2,24),cap,0,1.8,0));
bottle.position.set(-.1,BCY,BCZ);
const bar=new THREE.Group(),rod=mesh(new THREE.CylinderGeometry(.1,.1,2.6,16),M.metal);rod.rotation.z=Math.PI/2;bar.add(rod);
[-1.3,1.3].forEach(x=>bar.add(mesh(new THREE.SphereGeometry(.17,16,12),M.amber,x,0,0)));bar.position.set(0,hookC.y,hookC.z);
const ball=mesh(new THREE.SphereGeometry(.17,24,18),M.amber);ball.position.copy(contact.pinch);
const pen=mesh(new THREE.CylinderGeometry(.07,.07,2.6,16),M.amber);pen.rotation.set(rad(15),0,rad(78));pen.position.copy(contact.tripod);
const objs={power:bottle,hook:bar,pinch:ball,tripod:pen};
Object.values(objs).forEach(o=>{o.visible=false;o.userData.part='object';hand.add(o)});
const GR=CFG.grip,held=objs[GR]||null;if(held)held.visible=true;
const home=held?held.position.clone():null,homeR=held?held.rotation.clone():null;
const target=P[GR]||P.open;
let cur=(ST.pose||P.open).slice();apply(cur);
hand.children.forEach(c=>{if(!c.userData.part)c.userData.part=c.position.y<-1.1?'wrist':(c.isGroup?'':'palm')});
const arrows=[0,1,2,3,4].map(()=>{const a=new THREE.ArrowHelper(new V3(0,0,1),new V3(),.5,0xf8c66b,.16,.1);a.visible=false;scene.add(a);return a});
function forces(amt){const pads=fingers.map(fPad);pads.push(tPad());const hp=hand.position;let use=[],aim=[];
 if(GR==='power'||GR==='hook'){const cy=(GR==='power'?BCY:hookC.y)+hp.y,cz=GR==='power'?BCZ:hookC.z;use=[0,1,2,3,4];aim=pads.map(p=>new V3(p.x,cy,cz))}
 else if(GR==='pinch'){use=[0,4];aim=[pads[4],pads[0]]}
 else if(GR==='tripod'){const c=pads[0].clone().add(pads[1]).add(pads[4]).multiplyScalar(1/3);use=[0,1,4];aim=[c,c,c]}
 const sf=.25+.9*CFG.strength/100;
 arrows.forEach((a,i)=>{const k=use.indexOf(i);if(k<0||amt<.05){a.visible=false;return}
  const d=aim[k].clone().sub(pads[i]);if(d.length()<1e-3){a.visible=false;return}d.normalize();const L=amt*sf;
  a.visible=true;a.position.copy(pads[i]).addScaledVector(d,-L);a.setDirection(d);a.setLength(L,Math.min(.18,L*.5),.09)})}

// --- HUD + design-review status
const NEED={power:65,hook:62,pinch:62,tripod:55},NEEDP={power:0,hook:0,pinch:60,tripod:55};
const okS=!held||CFG.strength>=NEED[GR],okP=!held||CFG.precision>=NEEDP[GR];
if(held&&!(okS&&okP))held.position.y=home.y-.1;
const $=id=>document.getElementById(id);
$('hs').textContent=CFG.strength;$('hsb').style.width=CFG.strength+'%';$('hb').textContent=CFG.stability;$('hbb').style.width=CFG.stability+'%';
$('hw').textContent=CFG.weight+' g';$('hc').textContent='$'+CFG.cost.toLocaleString()+' / $'+CFG.budget.toLocaleString();$('hc').style.color=CFG.within?'#79f0db':'#ff8f8f';
$('st').textContent=!held?'\u25CB NO OBJECT':(okS&&okP?'\u25CF SECURE HOLD':(okS?'\u25B2 TOO IMPRECISE':'\u25B2 SLIP RISK'));
$('st').style.color=!held?'#8fa6c2':(okS&&okP?'#5de0d0':'#f8c66b');
if(!CFG.within)$('st').textContent+='  \u00B7 OVER BUDGET';

// --- Run test: reach, close, lift, hold, release
const toast=$('ts'),DUR=[1,1.2,1,1,1.2,1.2],TOT=DUR.reduce((a,b)=>a+b,0);let test=null,falling=false,vy=0;
function showToast(t,good){toast.textContent=t;toast.style.display='block';toast.style.background=good?'#12322f':'#3a1a1f';toast.style.color=good?'#79f0db':'#ffb3b3';toast.style.border='1px solid '+(good?'#2a675f':'#7b3340')}
function resetObj(){hand.add(held);held.position.copy(home);held.rotation.copy(homeR);if(!(okS&&okP))held.position.y=home.y-.1;falling=false;vy=0;hand.position.y=0}
function stepTest(dt){const t=test;t.t+=dt;
 if(t.t>=TOT){test=null;resetObj();setTimeout(()=>{if(!test)toast.style.display='none'},3000);return target}
 let ph=0,acc=0;while(ph<5&&t.t>=acc+DUR[ph]){acc+=DUR[ph];ph++}
 const u=Math.min(1,(t.t-acc)/DUR[ph]);
 if(t.ph!==ph){t.ph=ph;
  if(ph===2&&!(okS&&okP)){scene.attach(held);falling=true;vy=0;showToast(okS?'MISSED \u2014 precision '+CFG.precision+' < '+NEEDP[GR]+' needed':'DROPPED \u2014 grip force '+CFG.strength+' < '+NEED[GR]+' needed',false)}
  if(ph===3&&okS&&okP)showToast('HELD \u2014 grip force '+CFG.strength+' (needs '+NEED[GR]+')',true);
  if(ph===4&&held.parent===hand){scene.attach(held);falling=true;vy=0}}
 const e=u*u*(3-2*u);hand.position.y=ph===2?.7*e:ph===3?.7:ph===4?.7*(1-e):0;
 return(ph===0||ph>=4)?P.open:target}
$('bt').onclick=()=>{if(!held){showToast('Choose a grip with an object (not Open) to run the test',false);setTimeout(()=>toast.style.display='none',2500);return}
 if(test)return;toast.style.display='none';resetObj();test={t:0,ph:-1};C.spin=false;sync()};

// --- Tendon routing (X-ray)
const lines=fingers.map((f,i)=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(15),3));
 const l=new THREE.Line(g,new THREE.LineBasicMaterial({color:DC}));l.frustumCulled=false;l.visible=false;scene.add(l);
 return {l,f,m:motors[Math.min(nm-1,Math.floor(i*nm/4))]}});
const beads=lines.map(()=>{const s=mesh(new THREE.SphereGeometry(.055,10,8),M.amber);s.visible=false;scene.add(s);return s}),WHITE=new THREE.Color(1,1,1);
function updLines(){lines.forEach((o,bi)=>{const f=o.f,r=f.d.r,a=o.l.geometry.attributes.position.array;
 const pts=[new V3(o.m.position.x,-.2,.1).add(hand.position),f.mcp.localToWorld(new V3(0,0,r*1.12)),f.pip.localToWorld(new V3(0,0,r*1.05)),f.dip.localToWorld(new V3(0,0,r*.95)),f.dip.localToWorld(new V3(0,f.d.L[2]*.8,r*.95))];
 pts.forEach((p,i)=>{a[3*i]=p.x;a[3*i+1]=p.y;a[3*i+2]=p.z});o.l.geometry.attributes.position.needsUpdate=true;const cu=Math.min(1,(f.mcp.rotation.x+f.pip.rotation.x+f.dip.rotation.x)/3.6);o.l.material.color.setHex(DC).lerp(WHITE,cu*.6);beads[bi].position.lerpVectors(pts[0],pts[1],.9-.7*cu)})}

// --- Floor
const grid=new THREE.GridHelper(14,28,CFG.within?0x5de0d0:0xff5b5b,CFG.within?0x24405c:0x5c2430);grid.position.y=-3.3;grid.material.transparent=true;grid.material.opacity=.35;scene.add(grid);

// --- Camera orbit (custom: drag rotate, wheel zoom, right-drag pan)
const def={th:.6,ph:1.4,d:CFG.mobile?15.5:12.5,tx:0,ty:CFG.mobile?.6:-.1,tz:.3};
const C=(ST.mob===CFG.mobile&&ST.cam)||Object.assign({spin:true,xray:false},def);ST.cam=C;ST.mob=CFG.mobile;
function cam(){const s=Math.sin(C.ph);camera.position.set(C.tx+C.d*s*Math.sin(C.th),C.ty+C.d*Math.cos(C.ph),C.tz+C.d*s*Math.cos(C.th));camera.lookAt(C.tx,C.ty,C.tz)}
const el=renderer.domElement;let last=null,drag=false;
el.addEventListener('contextmenu',e=>e.preventDefault());
let down=null;const ray=new THREE.Raycaster(),mv2=new THREE.Vector2(),inf=$('inf');
const JT={'Single hinge':'One rotation axis: simple, strong and easy to maintain, but the curl looks less natural.','Multi-link':'Coupled links shape a more natural curl path, at the cost of more parts to tune.','Compliant joint':'A flexible section absorbs impacts and misalignment, but positioning is less exact under load.'};
const MT={'Tendon-driven':'Motor + spool: pulls a cable that curls a finger, like a tendon. Light fingers, but cables stretch and wear.','Direct-motor':'Geared motor driving a joint directly. Precise and independent, but heavier and costlier.','Underactuated':'Shared motor driving a linkage that curls several fingers together; they adapt around the object.'};
const INF={palm:['Palm shell','Houses motors, battery and electronics. More hardware means more weight for the user.'],wrist:['Wrist & socket','Connects the hand to the limb. Weight and fit here decide daily comfort.'],pcb:['Control board & battery','Reads the command signal and sets motor power and speed.'],finger:['Finger segment','Silicone pads add friction for gripping. Segment length sets reach.'],thumb:['Thumb','Opposing the fingers is what makes pinch, tripod and power grips possible.'],
 joint:['Joint: '+CFG.joint,JT[CFG.joint]],motor:['Actuator: '+CFG.drive,MT[CFG.drive]],object:['Test object',{power:'A bottle: a power grip wraps the fingers around it and force must beat its weight.',hook:'A handle bar: curled fingers carry a load without the thumb.',pinch:'A small part: pinching needs fine control more than force.',tripod:'A pen: thumb plus two fingers for stable, precise control.'}[GR]||'']};
function pick(e){const r=el.getBoundingClientRect();mv2.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);ray.setFromCamera(mv2,camera);
 const h=ray.intersectObjects(scene.children,true).filter(x=>x.object.type==='Mesh')[0];let k=null;
 if(h){let o=h.object;while(o&&!k){k=o.userData.part||null;o=o.parent}}
 if(k&&INF[k]){inf.style.display='block';inf.innerHTML='<b>'+INF[k][0]+'</b>'+INF[k][1]}else inf.style.display='none'}
const pts=new Map();let pd=0;
el.addEventListener('pointerdown',e=>{el.setPointerCapture(e.pointerId);pts.set(e.pointerId,[e.clientX,e.clientY]);last=[e.clientX,e.clientY];down=pts.size>1?null:[e.clientX,e.clientY];drag=true;C.spin=false;sync();if(pts.size===2){const q=[...pts.values()];pd=Math.hypot(q[0][0]-q[1][0],q[0][1]-q[1][1])}});
const endp=e=>{pts.delete(e.pointerId);drag=pts.size>0;if(pts.size)last=[...pts.values()][0];if(down&&Math.hypot(e.clientX-down[0],e.clientY-down[1])<5)pick(e);down=null};
el.addEventListener('pointerup',endp);el.addEventListener('pointercancel',endp);
el.addEventListener('pointermove',e=>{if(pts.has(e.pointerId))pts.set(e.pointerId,[e.clientX,e.clientY]);if(pts.size===2){const q=[...pts.values()],dd=Math.hypot(q[0][0]-q[1][0],q[0][1]-q[1][1]);if(pd)C.d=Math.max(4,Math.min(20,C.d*pd/dd));pd=dd;return}if(!drag)return;const dx=e.clientX-last[0],dy=e.clientY-last[1];last=[e.clientX,e.clientY];
 if(e.buttons&2||e.shiftKey){const k=C.d*.0016,rt=new V3().setFromMatrixColumn(camera.matrix,0),up=new V3().setFromMatrixColumn(camera.matrix,1);
  C.tx+=(-rt.x*dx+up.x*dy)*k;C.ty+=(-rt.y*dx+up.y*dy)*k;C.tz+=(-rt.z*dx+up.z*dy)*k}
 else{C.th-=dx*.009;C.ph=Math.max(.15,Math.min(Math.PI-.15,C.ph-dy*.009))}});
el.addEventListener('wheel',e=>{e.preventDefault();C.d=Math.max(4,Math.min(20,C.d*Math.exp(e.deltaY*.0012)))},{passive:false});
function sync(){$('bs').classList.toggle('on',C.spin);$('bx').classList.toggle('on',C.xray);setX()}
function setX(){const o=C.xray?.16:1;shellMats.forEach(m=>{m.transparent=C.xray;m.opacity=o;m.depthWrite=!C.xray;m.needsUpdate=true});lines.forEach(q=>q.l.visible=C.xray);beads.forEach(s=>s.visible=C.xray&&CFG.drive==='Tendon-driven')}
$('bx').onclick=()=>{C.xray=!C.xray;sync()};$('bs').onclick=()=>{C.spin=!C.spin;sync()};
$('bz').onclick=()=>C.d=Math.max(4,C.d*.85);$('bo').onclick=()=>C.d=Math.min(20,C.d*1.18);
$('br').onclick=()=>{Object.assign(C,def);C.spin=true;sync()};sync();

// --- Callout tags
const T1=$('t1'),T2=$('t2');
T1.style.setProperty('--c','#'+DC.toString(16).padStart(6,'0'));T1.innerHTML='<b>ACTUATION</b>'+CFG.drive.toUpperCase();
T2.style.setProperty('--c','#'+JC.toString(16).padStart(6,'0'));T2.innerHTML='<b>JOINT</b>'+CFG.joint.toUpperCase();
function place(t,p,dx,dy,w,h){const v=p.clone().project(camera);t.style.transform='translate('+Math.round((v.x*.5+.5)*w+dx)+'px,'+Math.round((-v.y*.5+.5)*h+dy)+'px)'}

function resize(){const w=root.clientWidth,h=root.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix()}
new ResizeObserver(resize).observe(root);resize();
const clock=new THREE.Clock();
(function loop(){requestAnimationFrame(loop);const dt=Math.min(.05,clock.getDelta());
 const tgt=test?stepTest(dt):target,kk=1-Math.exp(-dt*(1.5+CFG.resp*1.1));let mvd=0,gd=0;
 for(let i=0;i<17;i++){const dl=tgt[i]-cur[i];mvd+=Math.abs(dl);cur[i]+=dl*kk;gd+=Math.abs(target[i]-cur[i])}
 apply(cur);ST.pose=cur.slice();hand.updateMatrixWorld(true);
 const amt=held?Math.max(0,1-gd/120):0,act=Math.min(1,mvd/30)+(amt>.6?.2:0);
 const om=act*(1.5+CFG.power*1.1);motors.forEach((g,i)=>{g.rotation.y+=om*dt*(i%2?-1:1)});
 M.drive.emissiveIntensity=.1+act*(.25+CFG.power*.07);
 gearJ.forEach(ge=>{ge.rotation.y=-2.5*ge.parent.parent.parent.rotation.x});
 if(wt){const c=i=>cur[3*i]+cur[3*i+1]+cur[3*i+2];wt.m.rotation.z=((c(0)+c(1))-(c(2)+c(3)))*.0018;wt.a.rotation.z=(c(0)-c(1))*.0035;wt.b.rotation.z=(c(2)-c(3))*.0035}
 if(falling){vy-=20*dt;held.position.y+=vy*dt;if(held.position.y<-2.9){held.position.y=-2.9;vy*=-.25;if(Math.abs(vy)<.5)falling=false}}
 if(held)forces(amt);
 if(C.spin&&!drag)C.th+=.004;cam();camera.updateMatrixWorld();
 if(C.xray)updLines();
 const w=root.clientWidth,h=root.clientHeight;
 place(T1,new V3(motors[motors.length-1].position.x+.15,.2,0),30,-8,w,h);
 place(T2,fingers[0].pip.localToWorld(new V3(0,0,0)),-150,-30,w,h);
 renderer.render(scene,camera)})();
})();
</script></body></html>"""


def build_hand_3d(grip_pattern: str, drive_name: str, joint_name: str, power: int, extra: dict | None = None) -> str:
    """Interactive Three.js prosthetic hand: drag to orbit, scroll to zoom, X-ray to see internals."""
    motors = {"Tendon-driven": 4, "Direct-motor": 5, "Underactuated": 2}.get(drive_name, 4)
    weight = 190 + motors * 42 + power * 7 + {"Multi-link": 35, "Compliant joint": 12}.get(joint_name, 0)
    cfg = {"grip": grip_pattern, "drive": drive_name, "joint": joint_name, "power": power, "motors": motors, "weight": weight,
           "strength": 70, "precision": 70, "stability": 70, "resp": 6, "cost": 0, "budget": 0, "within": True, "mobile": False}
    cfg.update(extra or {})
    return HAND3D_HTML.replace("__CFG__", json.dumps(cfg))


# -----------------------------------------------------------------------------
# Header and navigation
# -----------------------------------------------------------------------------
if IS_MOBILE:
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:.75rem'><img src='{LOGO_URI}' style='width:48px'><div><div class='eyebrow'>BY {CREATOR.upper()}</div>"
        "<div style='font-size:1.6rem;font-weight:800;color:#f4f8ff;letter-spacing:-.04em;line-height:1.1'>Prosthetic<span style='color:#5de0d0'>Lab</span></div></div></div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:1rem'><img src='{LOGO_URI}' style='width:62px'><div class='eyebrow'>ENGINEERING EXPLORER · MODULE 02 · BY {CREATOR.upper()}</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hero-title">Prosthetic<span>Lab</span></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Design a conceptual prosthetic hand. Swap its mechanisms, change the grip, and see how engineers balance useful motion, strength, comfort, and cost.</div>',
    unsafe_allow_html=True,
)
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

tab_build, tab_mechanics, tab_tradeoffs = st.tabs(
    ["BUILD", "HOW IT WORKS", "TRADE-OFFS"] if IS_MOBILE else ["01  /  BUILD LAB", "02  /  HOW IT WORKS", "03  /  DESIGN TRADE-OFFS"]
)
if IS_MOBILE:
    with tab_build:
        try:
            viewer_slot = st.container(key="viewer")
        except TypeError:
            viewer_slot = st.container()
        ctrl_host = st.expander("🎛  Build controls", expanded=True)
else:
    ctrl_host = st.sidebar
with ctrl_host:
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

    if not IS_MOBILE:
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        if st.button("↩  Change layout", key="chg_side", use_container_width=True):
            st.session_state["mode"] = None
            st.rerun()

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

def render_viewer(height, compact=False):
    if not compact:
        st.markdown('<div class="section-kicker">LIVE CONCEPT VIEW</div>', unsafe_allow_html=True)
        st.markdown(f"### {grip}")
    extra_pill = f" &nbsp; <span class='soft-pill'>{grip}</span>" if compact else ""
    st.markdown(f"<span class='status-pill'>● LIVE</span> &nbsp; <span class='soft-pill'>{drive}</span> &nbsp; <span class='soft-pill'>{joint}</span>{extra_pill}", unsafe_allow_html=True)
    components.html(
        build_hand_3d(g["pattern"], drive, joint, motor_power, {
            "strength": strength, "precision": precision, "stability": stability, "resp": response_speed,
            "cost": cost_estimate, "budget": budget, "within": within_budget, "mobile": IS_MOBILE,
        }),
        height=height, scrolling=False,
    )


def render_notes():
    st.markdown(f"<div class='callout'><b style='color:#eef4ff'>Task focus:</b> {g['use']} &nbsp;<span class='tiny-note'>Try: Run test, X-ray, and tap any part of the hand.</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='tiny-note'>{d['summary']}</div>", unsafe_allow_html=True)


def render_metrics():
    st.markdown('<div class="section-kicker">SIMULATED PERFORMANCE</div>', unsafe_allow_html=True)
    st.markdown("### What this design prioritizes")
    col_a, col_b = st.columns(2, gap="small" if IS_MOBILE else "medium")
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
        if IS_MOBILE:
            st.markdown(
                f"<div style='margin:.6rem 0'><div style='display:flex;justify-content:space-between;align-items:baseline'><span style='font-weight:700;color:#dce7f6;font-size:.95rem'>{label}</span>"
                f"<span style='font-family:DM Mono,monospace;color:#5de0d0;font-size:1.05rem'>{score:02d}</span></div>"
                f"<div style='height:8px;background:#22344b;border-radius:6px;margin-top:.3rem'><div style='width:{score}%;height:100%;border-radius:6px;background:linear-gradient(90deg,#5de0d0,#78a7ff)'></div></div></div>",
                unsafe_allow_html=True,
            )
            continue
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


def render_compare():
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
                f'''<div style="background:#101b2b;border:1px solid {border};border-radius:14px;padding:1rem;min-height:115px;margin-bottom:.5rem">
                <div style="font-family:DM Mono,monospace;color:{'#5de0d0' if selected else '#8ea4bf'};font-size:.68rem;letter-spacing:.1em">{'CURRENT SELECTION' if selected else 'DRIVE OPTION'}</div>
                <div style="font-size:1.02rem;color:#f1f6ff;font-weight:800;margin:.35rem 0">{name}</div>
                <div style="font-size:.82rem;color:#9eafc4">{tag}</div><div style="font-size:.73rem;color:#5de0d0;margin-top:.5rem">{price}</div></div>''',
                unsafe_allow_html=True,
            )


with tab_build:
    if IS_MOBILE:
        with viewer_slot:
            render_viewer(400, compact=True)
        render_notes()
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        render_metrics()
    else:
        left, right = st.columns([1.04, 1], gap="large")
        with left:
            render_viewer(620)
            render_notes()
        with right:
            render_metrics()
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    render_compare()

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
            f'''<div class="trow" style="display:grid;grid-template-columns:1.05fr 1.55fr 1.55fr;gap:.8rem;background:{'#132136' if i % 2 == 0 else '#0e1928'};border:1px solid #24354b;border-radius:11px;padding:.85rem 1rem;margin:.45rem 0;align-items:start">
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
    st.markdown("<div class='tiny-note'>PROSTHETICLAB · A CONCEPTUAL LEARNING TOOL FOR ASSISTIVE-TECHNOLOGY ENGINEERING · BY CHRIS YOUNAN</div>", unsafe_allow_html=True)
with foot_r:
    st.markdown("<div style='text-align:right;color:#6f879f;font-family:DM Mono,monospace;font-size:.7rem'>BUILD / TEST / REFINE</div>", unsafe_allow_html=True)

if IS_MOBILE:
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    if st.button("↩  Change layout", key="chg_foot", use_container_width=True):
        st.session_state["mode"] = None
        st.rerun()
