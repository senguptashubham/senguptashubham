#!/usr/bin/env python3
"""Regenerates assets/study-scene-{dark,light}.svg once a day.

- Weather outside the window follows the real weather in Reykjavik
  (Open-Meteo, no API key). If the API is unreachable, falls back to a
  date-seeded preset so the calendar and screen still update.
- Dark mode is always night (moon at its real phase, clear skies only).
- Light mode is always day (a pale sun, clear skies only).
- The Mac screen rotates through five plot presets, seeded by the date.
- The tear-off calendar shows today's date (UTC == Reykjavik time).

Standard library only. Never raises: any failure degrades gracefully.
"""
import datetime
import json
import math
import random
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEATHER_URL = ("https://api.open-meteo.com/v1/forecast"
               "?latitude=64.1466&longitude=-21.9426&current=weather_code")

PALETTES = {
    "dark": dict(
        wood1="#77502e", wood2="#5a3c20", wood3="#916740",
        rain="#9db4d0", rainO="0.5", flake="#d8e0ec",
        cloud="#2a3450", moon="#e8ddc2",
        city1="#252e47", city2="#151c2d", haze="#8a5a8f",
        neonM="#d268b0", neonC="#5fd0c0", litO="0.9",
        cream="#ddd1b4", cream2="#c9bd9e", creamEdge="#a99a78",
        mac1="#cfc3a6", mac2="#b8ab8d", mac3="#9c8f72",
        screen="#171310", amber="#e0a458",
        ink="#6b5d45", metal="#514c3c", metal2="#3a362a",
        leaf1="#587347", leaf2="#445c37",
        terra="#a75c3c", terra2="#87482e", paint3="#5b6d84",
        poolO="0.09",
        bookA="#74573f", bookB="#556680", bookC="#87482e",
        bookD="#647251", bookE="#98844e",
        sky_top="#0f1420", sky_mid="#1a2133", sky_low="#241f36",
        cone="#e0a458", coneO1="0.13", coneO2="0.02",
        moonglow="#e8ddc2", moonglowO="0.25",
        sign_glowO="0.55", star="#e8ddc2",
    ),
    "light": dict(
        wood1="#775030", wood2="#5b3c21", wood3="#8f6335",
        rain="#5b7089", rainO="0.45", flake="#f4f7fa",
        cloud="#e3e8ee", moon="#f4efe2",
        city1="#a3aeba", city2="#7f8b9c", haze="#b3a0be",
        neonM="#c07aae", neonC="#61b3a7", litO="0.4",
        cream="#f3ead4", cream2="#d5c8a4", creamEdge="#a3946e",
        mac1="#d3c6a9", mac2="#b9ac8c", mac3="#9c8f70",
        screen="#241f19", amber="#c98d3d",
        ink="#5a4c36", metal="#5c5744", metal2="#454033",
        leaf1="#567244", leaf2="#425936",
        terra="#a55839", terra2="#84462c", paint3="#52637a",
        poolO="0.06",
        bookA="#70543f", bookB="#52637a", bookC="#84462c",
        bookD="#61704d", bookE="#93804b",
        sky_top="#b7c3cf", sky_mid="#c7d0d9", sky_low="#cfccd4",
        cone="#c98d3d", coneO1="0.10", coneO2="0.015",
        moonglow="#f4efe2", moonglowO="0.08",
        sign_glowO="0.25", star="#f4efe2",
        sun="#ead9a0", sunglow="#e8c87a",
    ),
}

WMO_MAP = [
    ((0, 1), "clear"),
    ((2, 3), "overcast"), ((45, 48), "overcast"),
    ((51, 67), "rain"), ((80, 82), "rain"), ((95, 99), "rain"),
    ((71, 77), "snow"), ((85, 86), "snow"),
]


def fetch_weather_preset(rng):
    try:
        with urllib.request.urlopen(WEATHER_URL, timeout=15) as r:
            code = int(json.load(r)["current"]["weather_code"])
        for (lo, hi), preset in WMO_MAP:
            if lo <= code <= hi:
                return preset, "api"
        return "overcast", "api"
    except Exception as e:
        print(f"weather api unavailable ({e}); using seeded fallback")
        return rng.choices(["clear", "overcast", "rain", "snow"],
                           weights=[3, 3, 3, 1])[0], "fallback"


def moon_phase(d):
    """0 = new, 0.5 = full, back to 1 = new. Good to ~a day."""
    ref = datetime.datetime(2000, 1, 6, 18, 14)
    days = (datetime.datetime(d.year, d.month, d.day) - ref).total_seconds() / 86400.0
    return (days % 29.530588) / 29.530588


def moon_svg(p, phase):
    """Moon at (272,72) r10; shadow disc offset trick for the phase."""
    ill = (1 - math.cos(2 * math.pi * phase)) / 2
    r = 10
    if ill < 0.04:
        return ""  # new moon: not visible
    direction = -1 if phase < 0.5 else 1
    dx = direction * 2 * r * ill
    parts = [
        f'<circle cx="272" cy="72" r="20" fill="url(#moonglow)"/>',
        f'<g clip-path="url(#moonclip)">',
        f'  <circle cx="272" cy="72" r="{r}" fill="{p["moon"]}" opacity="0.9"/>',
        f'  <circle cx="268" cy="69" r="2.4" fill="{p["sky_low"]}" opacity="0.4"/>',
        f'  <circle cx="276" cy="76" r="1.6" fill="{p["sky_low"]}" opacity="0.4"/>',
    ]
    if ill < 0.97:
        parts.append(
            f'  <circle cx="{272 + dx:.1f}" cy="72" r="{r + 0.6:.1f}" fill="{p["sky_top"]}"/>')
    parts.append('</g>')
    return "\n      ".join(parts)


def sun_svg(p):
    return (f'<circle cx="272" cy="72" r="22" fill="url(#sunglow)"/>\n      '
            f'<circle cx="272" cy="72" r="11" fill="{p["sun"]}"/>')


def stars_svg(p, rng):
    out = []
    for _ in range(8):
        x = rng.randint(102, 298)
        y = rng.randint(46, 100)
        if abs(x - 272) < 26 and abs(y - 72) < 26:
            continue  # keep clear of the moon
        r = rng.choice([0.8, 1.0, 1.3])
        o = rng.choice([0.4, 0.55, 0.7])
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{p["star"]}" opacity="{o}"/>')
    return "\n      ".join(out)


CLOUD_SETS = {
    "few": [(150, 78, 30, 10, 1.0), (170, 71, 19, 8, 1.0)],
    "some": [(148, 76, 34, 11, 1.0), (170, 68, 22, 9, 1.0),
             (238, 106, 30, 9, 0.8), (216, 99, 18, 7, 0.8)],
    "heavy": [(140, 70, 44, 13, 1.0), (168, 60, 30, 11, 1.0),
              (238, 88, 40, 12, 0.95), (210, 80, 26, 10, 0.95),
              (160, 108, 36, 11, 0.85), (272, 116, 34, 11, 0.85),
              (120, 96, 26, 9, 0.8)],
}


def clouds_svg(p, style, drift=True):
    out = []
    for i, (cx, cy, rx, ry, o) in enumerate(CLOUD_SETS[style]):
        cls = f' class="cloud{"A" if i % 2 == 0 else "B"}"' if drift else ""
        out.append(f'<ellipse{cls} cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
                   f'fill="{p["cloud"]}" opacity="{o}"/>')
    return "\n      ".join(out)


RAIN_SVG = """<g class="rain">
        <g class="rainA" stroke-width="1.3" stroke-linecap="round">
          <line x1="112" y1="52" x2="109" y2="66"/><line x1="148" y1="34" x2="145" y2="48"/>
          <line x1="184" y1="58" x2="181" y2="72"/><line x1="220" y1="40" x2="217" y2="54"/>
          <line x1="256" y1="52" x2="253" y2="66"/><line x1="290" y1="44" x2="287" y2="58"/>
        </g>
        <g class="rainB" stroke-width="1.1" stroke-linecap="round" opacity="0.7">
          <line x1="128" y1="46" x2="125" y2="58"/><line x1="164" y1="30" x2="161" y2="42"/>
          <line x1="200" y1="52" x2="197" y2="64"/><line x1="238" y1="34" x2="235" y2="46"/>
          <line x1="272" y1="48" x2="269" y2="60"/>
        </g>
        <g class="rainC" stroke-width="1.5" stroke-linecap="round">
          <line x1="120" y1="38" x2="117" y2="54"/><line x1="172" y1="46" x2="169" y2="62"/>
          <line x1="212" y1="30" x2="209" y2="46"/><line x1="248" y1="42" x2="245" y2="58"/>
          <line x1="282" y1="34" x2="279" y2="50"/>
        </g>
      </g>"""


def snow_svg(p, rng):
    groups = {"snowA": [], "snowB": [], "snowC": []}
    names = list(groups)
    for _ in range(15):
        g = rng.choice(names)
        x = rng.randint(102, 298)
        y = rng.randint(30, 90)
        r = rng.choice([1.2, 1.5, 1.8])
        groups[g].append(f'<circle cx="{x}" cy="{y}" r="{r}"/>')
    out = ['<g fill="%s" opacity="0.8">' % p["flake"]]
    for g, flakes in groups.items():
        out.append(f'  <g class="{g}">' + "".join(flakes) + '</g>')
    out.append('</g>')
    return "\n      ".join(out)


def sky_contents(preset, mode, p, rng, phase):
    """Everything weather-ish inside the panes, behind the city."""
    if preset == "clear":
        celestial = moon_svg(p, phase) if mode == "dark" else sun_svg(p)
        extra = stars_svg(p, rng) if mode == "dark" else ""
        return f'{celestial}\n      {extra}\n      {clouds_svg(p, "few")}', ""
    if preset == "overcast":
        return clouds_svg(p, "heavy"), ""
    if preset == "rain":
        return clouds_svg(p, "some"), RAIN_SVG
    if preset == "snow":
        return clouds_svg(p, "some"), snow_svg(p, rng)
    raise ValueError(preset)


# ---------------------------------------------------------------- screen plots

def plot_loss(rng, a):
    x, y = 24, rng.randint(20, 26)
    d = [f"M{x} {y}"]
    for _ in range(9):
        x += rng.randint(5, 8)
        y = min(62, y + rng.randint(-3, 7))
        d.append(f"L{x} {y}")
    return (_axes(a) +
            f'<path d="{" ".join(d)}" stroke="{a}" fill="none" stroke-width="1.4" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def plot_train_val(rng, a):
    def curve(y0, floor):
        x, y = 24, y0
        d = [f"M{x} {y}"]
        for _ in range(8):
            x += rng.randint(6, 8)
            y = min(floor, y + rng.randint(-2, 6))
            d.append(f"L{x} {y}")
        return " ".join(d)
    return (_axes(a) +
            f'<path d="{curve(22, 62)}" stroke="{a}" fill="none" stroke-width="1.4" stroke-linecap="round"/>' +
            f'<path d="{curve(26, 48)}" stroke="{a}" fill="none" stroke-width="1.2" '
            f'stroke-dasharray="3 2" opacity="0.7" stroke-linecap="round"/>')


def plot_scatter(rng, a):
    pts = "".join(
        f'<circle cx="{x}" cy="{max(18, min(64, int(58 - 0.55 * (x - 24) + rng.randint(-7, 7))))}" '
        f'r="1.4" fill="{a}"/>'
        for x in sorted(rng.sample(range(26, 88), 12)))
    return (_axes(a) + pts +
            f'<path d="M26 58 L86 24" stroke="{a}" stroke-width="1" opacity="0.6" '
            f'stroke-dasharray="4 3"/>')


def plot_sine(rng, a):
    ph = rng.uniform(0, math.pi)
    pts = [(x, 40 - 16 * math.sin((x - 24) / 9.5 + ph)) for x in range(24, 89, 4)]
    smooth = "M" + " L".join(f"{x} {y:.1f}" for x, y in pts)
    rough = "M" + " L".join(
        f"{x} {y + rng.uniform(-4, 4):.1f}" for x, y in pts[::2])
    return (_axes(a) +
            f'<path d="{smooth}" stroke="{a}" fill="none" stroke-width="1.4" stroke-linecap="round"/>' +
            f'<path d="{rough}" stroke="{a}" fill="none" stroke-width="1" opacity="0.55" '
            f'stroke-dasharray="2 3" stroke-linecap="round"/>')


def plot_hist(rng, a):
    bars, x = [], 26
    for h in [rng.randint(6, 14), rng.randint(14, 22), rng.randint(24, 34),
              rng.randint(30, 40), rng.randint(24, 34), rng.randint(12, 22),
              rng.randint(5, 12)]:
        bars.append(f'<rect x="{x}" y="{60 - h}" width="6" height="{h}" fill="{a}" opacity="0.85"/>')
        x += 9
    return _axes(a) + "".join(bars)


def _axes(a):
    return f'<path d="M22 18 v44 h66" stroke="{a}" fill="none" opacity="0.4" stroke-width="1"/>'


PLOTS = [plot_loss, plot_train_val, plot_scatter, plot_sine, plot_hist]


def screen_svg(rng, p):
    plot = rng.choice(PLOTS)
    return plot(rng, p["amber"])


# ---------------------------------------------------------------- calendar

def calendar_svg(d, p):
    month = d.strftime("%b").lower()
    weekday = d.strftime("%a").lower()
    return f'''<g transform="translate(376,54) rotate(-2)">
    <rect x="0" y="8" width="76" height="82" rx="3" fill="{p["cream"]}" stroke="{p["creamEdge"]}" stroke-width="1"/>
    <path d="M0 28 h76 v-17 q0 -3 -3 -3 h-70 q-3 0 -3 3 z" fill="{p["terra"]}"/>
    <circle cx="20" cy="8" r="2.6" fill="none" stroke="{p["metal"]}" stroke-width="1.6"/>
    <circle cx="56" cy="8" r="2.6" fill="none" stroke="{p["metal"]}" stroke-width="1.6"/>
    <text x="38" y="22" text-anchor="middle" font-family="ui-monospace,'Courier New',monospace" font-size="11" fill="{p["cream"]}">{month}</text>
    <text x="38" y="63" text-anchor="middle" font-family="ui-monospace,'Courier New',monospace" font-size="30" font-weight="bold" fill="{p["ink"]}">{d.day}</text>
    <text x="38" y="80" text-anchor="middle" font-family="ui-monospace,'Courier New',monospace" font-size="10" fill="{p["creamEdge"]}">{weekday}</text>
  </g>'''


# ---------------------------------------------------------------- the scene

def build_svg(mode, preset, d, phase, seed):
    p = PALETTES[mode]
    rng = random.Random(seed + (1 if mode == "dark" else 2))
    weather, precip = sky_contents(preset, mode, p, rng, phase)
    plot = screen_svg(random.Random(seed + 7), p)  # same plot both modes
    cal = calendar_svg(d, p)
    sunglow_def = (f'''<radialGradient id="sunglow">
      <stop offset="30%" stop-color="{p.get("sunglow", "#fff")}" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="{p.get("sunglow", "#fff")}" stop-opacity="0"/>
    </radialGradient>''' if mode == "light" else "")
    label = ("an engineer's study at night" if mode == "dark" else "an engineer's study")
    return f'''<svg width="920" height="400" viewBox="0 0 920 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}: a desk with a retro computer, a lamp, a watch, a shelf of books, and a window showing today's weather over a distant city">
  <defs>
    <style>
      .rain line {{ stroke:{p["rain"]}; opacity:{p["rainO"]}; }}
      .rainA {{ animation: fall 1.35s linear infinite; }}
      .rainB {{ animation: fall 1.6s linear infinite; animation-delay:-0.6s; }}
      .rainC {{ animation: fall 1.15s linear infinite; animation-delay:-0.3s; }}
      @keyframes fall {{ from {{ transform: translateY(-40px); }} to {{ transform: translateY(200px); }} }}
      .snowA {{ animation: snowfall 5.5s linear infinite; }}
      .snowB {{ animation: snowfall 7s linear infinite; animation-delay:-2.5s; }}
      .snowC {{ animation: snowfall 4.5s linear infinite; animation-delay:-1s; }}
      @keyframes snowfall {{ from {{ transform: translate(0,-30px); }} to {{ transform: translate(14px,200px); }} }}
      .cloudA {{ animation: drift 70s ease-in-out infinite alternate; }}
      .cloudB {{ animation: drift 95s ease-in-out infinite alternate-reverse; }}
      @keyframes drift {{ from {{ transform: translateX(0); }} to {{ transform: translateX(16px); }} }}
      .lit {{ opacity: {p["litO"]}; }}
      .flick {{ animation: flick 9s ease-in-out infinite; }}
      @keyframes flick {{
        0%,44%,56%,69%,75%,100% {{ opacity: {p["litO"]}; }}
        50% {{ opacity: 0.2; }}
        72% {{ opacity: 0.45; }}
      }}
      .cursor {{ animation: blink 1.1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity:0; }} }}
      .steam {{ fill:none; stroke:{p["cream2"]}; stroke-width:1.6; stroke-linecap:round; opacity:0; }}
      .steamA {{ animation: rise 3.8s ease-in-out infinite; }}
      .steamB {{ animation: rise 3.8s ease-in-out infinite; animation-delay:1.7s; }}
      @keyframes rise {{
        0% {{ opacity:0; transform: translateY(0); }}
        25% {{ opacity:0.45; }}
        100% {{ opacity:0; transform: translateY(-16px); }}
      }}
      .secondhand {{ animation: sweep 60s linear infinite; transform-origin: 372px 262px; }}
      @keyframes sweep {{ to {{ transform: rotate(360deg); }} }}
      .lampglow {{ animation: breathe 7s ease-in-out infinite; }}
      @keyframes breathe {{ 0%,100% {{ opacity:0.55; }} 50% {{ opacity:0.85; }} }}
      @media (prefers-reduced-motion: reduce) {{
        .rainA,.rainB,.rainC,.snowA,.snowB,.snowC,.cloudA,.cloudB,.cursor,.steamA,.steamB,.secondhand,.lampglow,.flick {{ animation:none; }}
        .steam {{ opacity:0.3; }}
      }}
    </style>
    <radialGradient id="moonglow">
      <stop offset="30%" stop-color="{p["moonglow"]}" stop-opacity="{p["moonglowO"]}"/>
      <stop offset="100%" stop-color="{p["moonglow"]}" stop-opacity="0"/>
    </radialGradient>
    {sunglow_def}
    <linearGradient id="skygrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{p["sky_top"]}"/>
      <stop offset="55%" stop-color="{p["sky_mid"]}"/>
      <stop offset="100%" stop-color="{p["sky_low"]}"/>
    </linearGradient>
    <linearGradient id="cone" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{p["cone"]}" stop-opacity="{p["coneO1"]}"/>
      <stop offset="100%" stop-color="{p["cone"]}" stop-opacity="{p["coneO2"]}"/>
    </linearGradient>
    <linearGradient id="floorfade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="1"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <mask id="fadeMask">
      <rect x="0" y="0" width="920" height="296" fill="#ffffff"/>
      <rect x="0" y="296" width="920" height="80" fill="url(#floorfade)"/>
    </mask>
    <filter id="blurFar" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.4"/></filter>
    <filter id="blurGlow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.6"/></filter>
    <clipPath id="panes">
      <rect x="97" y="41" width="95" height="74"/>
      <rect x="199" y="41" width="104" height="74"/>
      <rect x="97" y="122" width="95" height="97"/>
      <rect x="199" y="122" width="104" height="97"/>
    </clipPath>
    <clipPath id="moonclip"><circle cx="272" cy="72" r="10"/></clipPath>
  </defs>

  <!-- window -->
  <g>
    <rect x="97" y="41" width="206" height="178" fill="url(#skygrad)"/>
    <g clip-path="url(#panes)">
      {weather}
      <g fill="{p["city1"]}" filter="url(#blurFar)">
        <rect x="100" y="140" width="16" height="36"/><rect x="118" y="132" width="14" height="44"/>
        <rect x="134" y="146" width="20" height="30"/><rect x="156" y="126" width="16" height="50"/>
        <rect x="174" y="138" width="12" height="38"/><rect x="188" y="122" width="18" height="54"/>
        <rect x="208" y="136" width="14" height="40"/><rect x="224" y="144" width="18" height="32"/>
        <rect x="244" y="130" width="14" height="46"/><rect x="260" y="138" width="20" height="38"/>
        <rect x="282" y="146" width="14" height="30"/><rect x="298" y="140" width="10" height="36"/>
      </g>
      <rect x="97" y="156" width="206" height="24" fill="{p["haze"]}" opacity="0.16" filter="url(#blurGlow)"/>
      <g fill="{p["city2"]}">
        <rect x="104" y="148" width="26" height="71"/><rect x="146" y="158" width="22" height="61"/>
        <rect x="184" y="142" width="30" height="77"/><rect x="230" y="154" width="24" height="65"/>
        <rect x="262" y="148" width="26" height="71"/><rect x="296" y="158" width="7" height="61"/>
      </g>
      <g>
        <rect class="lit" x="110" y="156" width="3" height="3" fill="{p["amber"]}"/>
        <rect class="lit" x="120" y="164" width="3" height="3" fill="{p["neonC"]}"/>
        <rect class="lit" x="110" y="176" width="3" height="3" fill="{p["amber"]}"/>
        <rect class="lit" x="152" y="166" width="3" height="3" fill="{p["amber"]}"/>
        <rect class="lit flick" x="160" y="174" width="3" height="3" fill="{p["neonM"]}"/>
        <rect class="lit" x="190" y="150" width="3" height="3" fill="{p["amber"]}"/>
        <rect class="lit" x="198" y="158" width="3" height="3" fill="{p["amber"]}"/>
        <rect class="lit" x="206" y="150" width="3" height="3" fill="{p["neonC"]}"/>
        <rect class="lit" x="190" y="168" width="3" height="3" fill="{p["amber"]}"/>
        <rect class="lit" x="236" y="162" width="3" height="3" fill="{p["amber"]}"/>
        <rect class="lit flick" x="244" y="170" width="3" height="3" fill="{p["amber"]}"/>
        <rect class="lit" x="268" y="156" width="3" height="3" fill="{p["neonC"]}"/>
        <rect class="lit" x="276" y="164" width="3" height="3" fill="{p["amber"]}"/>
        <rect class="lit" x="268" y="178" width="3" height="3" fill="{p["amber"]}"/>
      </g>
      <rect x="209" y="150" width="4" height="24" fill="{p["neonM"]}" opacity="{p["sign_glowO"]}" filter="url(#blurGlow)"/>
      <rect class="lit" x="209" y="150" width="4" height="24" fill="{p["neonM"]}"/>
      {precip}
    </g>
    <g fill="{p["wood1"]}">
      <rect x="84" y="28" width="232" height="13" rx="3"/>
      <rect x="84" y="28" width="13" height="204" rx="3"/>
      <rect x="303" y="28" width="13" height="204" rx="3"/>
      <rect x="84" y="219" width="232" height="13" rx="3"/>
      <rect x="192" y="41" width="7" height="178"/>
      <rect x="97" y="115" width="206" height="7"/>
    </g>
    <rect x="84" y="28" width="232" height="13" rx="3" fill="{p["wood3"]}" opacity="0.35"/>
    <rect x="76" y="232" width="248" height="12" rx="3" fill="{p["wood1"]}"/>
    <rect x="76" y="232" width="248" height="3" rx="1.5" fill="{p["wood3"]}" opacity="0.5"/>
    <g transform="translate(150,10)">
      <path d="M116 222 l3 -12 q3 -4 6 0 l3 12 z" fill="{p["leaf1"]}"/>
      <path d="M112 222 q-4 -8 1 -13 q3 5 3 13 z" fill="{p["leaf2"]}"/>
      <path d="M130 222 q4 -8 -1 -13 q-3 5 -3 13 z" fill="{p["leaf2"]}"/>
      <path d="M108 222 h28 l-3 10 h-22 z" fill="{p["terra"]}"/>
    </g>
  </g>

  <!-- tear-off calendar -->
  {cal}

  <!-- shelf -->
  <g>
    <path d="M848 108 q4 18 -2 34" fill="none" stroke="{p["leaf1"]}" stroke-width="1.6"/>
    <path d="M856 108 q6 14 2 26" fill="none" stroke="{p["leaf2"]}" stroke-width="1.4"/>
    <circle cx="845" cy="128" r="2.6" fill="{p["leaf1"]}"/>
    <circle cx="847" cy="140" r="2.3" fill="{p["leaf2"]}"/>
    <circle cx="857" cy="126" r="2.3" fill="{p["leaf2"]}"/>
    <circle cx="859" cy="134" r="2" fill="{p["leaf1"]}"/>
    <g>
      <rect x="648" y="62" width="15" height="48" rx="2" fill="{p["bookA"]}"/>
      <rect x="666" y="56" width="17" height="54" rx="2" fill="{p["bookB"]}"/>
      <rect x="686" y="64" width="14" height="46" rx="2" fill="{p["bookC"]}"/>
      <rect x="703" y="58" width="16" height="52" rx="2" fill="{p["bookD"]}"/>
      <g transform="rotate(12 738 110)">
        <rect x="731" y="60" width="14" height="50" rx="2" fill="{p["bookE"]}"/>
      </g>
    </g>
    <g transform="translate(778,68)">
      <path d="M14 0 q10 0 11 10 q1 8 -4 13 q-2 3 -1 7 l3 6 h-18 l3 -6 q1 -4 -1 -7 q-5 -5 -4 -13 q1 -10 11 -10 z" fill="{p["cream"]}" stroke="{p["creamEdge"]}" stroke-width="0.8"/>
      <rect x="0" y="36" width="28" height="6" rx="1.5" fill="{p["cream2"]}"/>
    </g>
    <path d="M832 96 h24 l-3 12 h-18 z" fill="{p["terra2"]}"/>
    <path d="M838 96 q-6 -10 0 -16 q4 6 3 16 z" fill="{p["leaf1"]}"/>
    <path d="M848 96 q6 -10 0 -16 q-4 6 -3 16 z" fill="{p["leaf2"]}"/>
    <rect x="636" y="110" width="252" height="10" rx="3" fill="{p["wood1"]}"/>
    <rect x="636" y="110" width="252" height="3" rx="1.5" fill="{p["wood3"]}" opacity="0.5"/>
    <path d="M652 120 l-6 12 M872 120 l6 12" stroke="{p["wood2"]}" stroke-width="3" stroke-linecap="round"/>
  </g>

  <!-- desk lamp -->
  <g>
    <path class="lampglow" d="M683 196 L711 216 L705 279 L585 279 Z" fill="url(#cone)"/>
    <ellipse class="lampglow" cx="645" cy="283" rx="88" ry="7" fill="{p["amber"]}" opacity="{p["poolO"]}"/>
    <rect x="726" y="272" width="54" height="9" rx="4" fill="{p["metal2"]}"/>
    <path d="M753 274 v-52" fill="none" stroke="{p["metal"]}" stroke-width="4.5" stroke-linecap="round"/>
    <path d="M753 222 L712 190" fill="none" stroke="{p["metal"]}" stroke-width="4.5" stroke-linecap="round"/>
    <circle cx="753" cy="222" r="3.2" fill="{p["metal2"]}"/>
    <path d="M683 196 L698.6 180 L721 196 L711 216 Z" fill="{p["metal"]}"/>
    <line x1="683" y1="196" x2="711" y2="216" stroke="{p["amber"]}" stroke-width="3.5" stroke-linecap="round" class="lampglow"/>
  </g>

  <!-- notebooks + pencil -->
  <g>
    <rect x="252" y="266" width="80" height="9" rx="2" fill="{p["paint3"]}"/>
    <rect x="258" y="258" width="72" height="9" rx="2" fill="{p["terra2"]}"/>
    <rect x="258" y="258" width="6" height="9" fill="{p["cream2"]}"/>
    <g transform="rotate(-4 290 252)">
      <rect x="262" y="250" width="52" height="4" rx="2" fill="{p["amber"]}"/>
      <path d="M314 250 l7 2 l-7 2 z" fill="{p["cream"]}"/>
      <rect x="258" y="250" width="6" height="4" rx="2" fill="{p["terra"]}"/>
    </g>
  </g>

  <!-- mechanical watch -->
  <g>
    <rect x="338" y="258" width="26" height="9" rx="4" fill="{p["wood2"]}"/>
    <rect x="380" y="258" width="26" height="9" rx="4" fill="{p["wood2"]}"/>
    <circle cx="372" cy="262" r="17" fill="{p["metal"]}"/>
    <circle cx="372" cy="262" r="14" fill="{p["cream"]}"/>
    <g stroke="{p["ink"]}" stroke-width="1">
      <line x1="372" y1="250.5" x2="372" y2="253"/>
      <line x1="372" y1="271" x2="372" y2="273.5"/>
      <line x1="360.5" y1="262" x2="363" y2="262"/>
      <line x1="381" y1="262" x2="383.5" y2="262"/>
    </g>
    <line x1="372" y1="262" x2="372" y2="254" stroke="{p["ink"]}" stroke-width="1.6" stroke-linecap="round"/>
    <line x1="372" y1="262" x2="378" y2="265" stroke="{p["ink"]}" stroke-width="1.6" stroke-linecap="round"/>
    <line class="secondhand" x1="372" y1="266" x2="372" y2="251" stroke="{p["terra"]}" stroke-width="0.9" stroke-linecap="round"/>
    <circle cx="372" cy="262" r="1.4" fill="{p["metal2"]}"/>
    <rect x="388" y="259.5" width="3.5" height="5" rx="1" fill="{p["metal2"]}"/>
  </g>

  <!-- retro macintosh, today's plot on screen -->
  <g transform="translate(432,158)">
    <path d="M6 0 h96 q6 0 6 6 v92 h-108 v-92 q0 -6 6 -6 z" fill="{p["mac1"]}"/>
    <path d="M0 98 h108 v10 q0 4 -4 4 h-100 q-4 0 -4 -4 z" fill="{p["mac2"]}"/>
    <rect x="12" y="10" width="84" height="62" rx="4" fill="{p["mac3"]}"/>
    <rect x="16" y="14" width="76" height="54" rx="2" fill="{p["screen"]}"/>
    {plot}
    <rect class="cursor" x="80" y="56" width="5" height="7" fill="{p["amber"]}"/>
    <rect x="62" y="80" width="30" height="4" rx="1.5" fill="{p["mac3"]}"/>
    <rect x="14" y="82" width="10" height="6" rx="1" fill="{p["mac2"]}"/>
    <path d="M18 112 h72 v6 h8 v4 h-88 v-4 h8 z" fill="{p["mac3"]}"/>
  </g>

  <!-- coffee mug -->
  <g>
    <path class="steam steamA" d="M588 232 q-3 -7 1 -12 q4 -5 1 -11"/>
    <path class="steam steamB" d="M600 234 q3 -7 -1 -12 q-4 -5 -1 -11"/>
    <path d="M580 246 h30 q1 16 -6 26 q-2 4 -9 4 q-7 0 -9 -4 q-7 -10 -6 -26 z" fill="{p["terra"]}"/>
    <path d="M610 250 q10 0 9 9 q-1 8 -10 8 l1 -4 q5 0 6 -4 q0 -5 -6 -5 z" fill="{p["terra"]}"/>
    <path d="M582 250 q13 4 26 0" fill="none" stroke="{p["terra2"]}" stroke-width="2"/>
  </g>

  <!-- desk -->
  <rect x="70" y="280" width="780" height="15" rx="4" fill="{p["wood1"]}"/>
  <rect x="70" y="280" width="780" height="4" rx="2" fill="{p["wood3"]}" opacity="0.6"/>
  <g stroke="{p["wood2"]}" stroke-width="1" opacity="0.5">
    <path d="M150 288 q120 3 240 0"/>
    <path d="M480 290 q100 -3 200 0"/>
  </g>
  <rect x="80" y="295" width="760" height="8" rx="3" fill="{p["wood2"]}"/>
  <g mask="url(#fadeMask)">
    <rect x="118" y="303" width="14" height="72" fill="{p["wood2"]}"/>
    <rect x="788" y="303" width="14" height="72" fill="{p["wood2"]}"/>
  </g>
</svg>
'''


def main():
    args = sys.argv[1:]
    forced = None
    date_arg = None
    for i, a in enumerate(args):
        if a == "--preset" and i + 1 < len(args):
            forced = args[i + 1]
        if a == "--date" and i + 1 < len(args):
            date_arg = args[i + 1]
    today = (datetime.date.fromisoformat(date_arg) if date_arg
             else datetime.datetime.utcnow().date())
    seed = int(today.strftime("%Y%m%d"))
    rng = random.Random(seed)
    if forced:
        preset, source = forced, "forced"
    else:
        preset, source = fetch_weather_preset(rng)
    phase = moon_phase(today)
    print(f"{today} · weather={preset} ({source}) · moon phase={phase:.2f}")
    for mode in ("dark", "light"):
        out = ROOT / "assets" / f"study-scene-{mode}.svg"
        out.write_text(build_svg(mode, preset, today, phase, seed), encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
