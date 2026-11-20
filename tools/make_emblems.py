#!/usr/bin/env python3
"""
Draw the project's own center artwork: emblems that belong to no one.

    python tools/make_emblems.py            # writes the SVGs into artwork/
    python tools/make_emblems.py --out DIR  # somewhere else

Each is an old symbol of the whole church (or, the rose, of the Lutheran
churches), drawn here from nothing but geometry, so none is traced from a
church's logo and none carries anyone's copyright or trademark:

    Luther_Rose.svg       the black cross in a red heart on a white rose, in a
                          sky-blue field within a gold ring, as Luther described
                          his seal in 1530
    Chi_Rho_Roundel.svg   the Chi-Rho, the first two letters of "Christ" in Greek
    Celtic_Cross_Roundel.svg      the ringed cross of Ireland and Scotland
    Canterbury_Cross_Roundel.svg  the cross of the Saxon brooch found at
                          Canterbury, used as a sign of the Anglican churches

They are released into the public domain (CC0 1.0).  Nothing but the standard
library is needed, and the same input always writes the same bytes.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500">\n{}</svg>\n'

INK = "#1a1a1a"


def n(v: float) -> str:
    """A coordinate to one decimal place, without a trailing .0."""
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def turned(path: str, degrees: float) -> str:
    return f'<path transform="rotate({n(degrees)})" d="{path}"/>'


def rim(field: str) -> str:
    """The gold ring every picture sits in, and the field that fills it.  Its
    two black lines are drawn by picture(), over the picture, so that they
    stay the band's edges whatever the picture reaches into."""
    return ('<circle cx="250" cy="250" r="250" fill="#e3b21a"/>\n'
            f'<circle cx="250" cy="250" r="225" fill="{field}"/>\n')


# The band's two edges: the outer line lies inside the circle's edge, so the
# picture ends in black where the month ring meets it, with no gold showing
# beyond; the inner line is the field's edge.
RIM_LINES = (f'<circle cx="250" cy="250" r="248.5" fill="none" stroke="{INK}" stroke-width="3"/>\n'
             f'<circle cx="250" cy="250" r="225" fill="none" stroke="{INK}" stroke-width="3"/>\n')


def rays(count: int, color: str, radius: float = 223.5, turn: float = 0.0) -> str:
    """Every other one of `count` wedges about 0,0: with the field behind, a sunburst of two shades."""
    step = 2 * math.pi / count
    out = []
    for i in range(0, count, 2):
        a, b = turn + i * step, turn + (i + 1) * step
        out.append(f"M0 0L{n(radius * math.sin(a))} {n(-radius * math.cos(a))}"
                   f"A{n(radius)} {n(radius)} 0 0 1 {n(radius * math.sin(b))} {n(-radius * math.cos(b))}Z")
    return f'<path fill="{color}" d="{"".join(out)}"/>'


def picture(field: str, inner: str) -> str:
    return SVG.format(rim(field) + f'<g transform="translate(250 250)" stroke-linejoin="round">\n{inner}\n</g>\n' + RIM_LINES)


def luther_rose() -> str:
    # A double heraldic rose: five broad outer petals that meet along their
    # sides, each lip rising to a point at its middle, five smaller petals
    # between them round the heart, and the sepals' points showing between.
    petal = ("M-35-48L-86-118C-104-146-100-188-70-196C-46-202-16-196 0-216"
             "C16-196 46-202 70-196C100-188 104-146 86-118L35-48Z")
    sepal = "M0-118C-30-150-24-190 0-224C24-190 30-150 0-118Z"
    # The heart and its cross are measured from the Commons drawing: a shallow
    # cleft; the cross's head a little below it, its bar about a third of the
    # way down and half the heart wide, its foot near the heart's point.
    heart = ("M0 86C-110 10-94-84-46-84C-22-84-6-76 0-65"
             "C6-76 22-84 46-84C94-84 110 10 0 86Z")
    five = lambda d, off=0, more="": "".join(
        f'<path transform="rotate({n(off + 72 * i)}){more}" d="{d}"/>' for i in range(5))
    return picture("#2f74b8",
        f'<g fill="#2e8b3e" stroke="{INK}" stroke-width="2.5">{five(sepal, 36)}</g>\n'
        f'<g stroke="#14602a" stroke-width="2" fill="none">{five("M0-150V-214", 36)}</g>\n'
        f'<g fill="#eef1f5" stroke="{INK}" stroke-width="3">{five(petal)}</g>\n'
        f'<g fill="none" stroke="#7d8794" stroke-width="2" stroke-linecap="round">{five("M0-150V-204M-30-150Q-44-168-66-176M30-150Q44-168 66-176")}</g>\n'
        f'<g fill="#fff" stroke="{INK}" stroke-width="4.6">{five(petal, 36, " scale(.64)")}</g>\n'
        f'<g fill="none" stroke="#7d8794" stroke-width="2" stroke-linecap="round">{five("M0-100V-128", 36)}</g>\n'
        f'<path d="{heart}" fill="#d81e2c" stroke="{INK}" stroke-width="3"/>\n'
        # The cross stands in the middle of the heart, red above its head: a Latin
        # cross, head and arms about as long as the stem is wide, the foot nearly three times that.
        '<path d="M-13-58h26v25h29v27h-29v74h-26v-74h-29v-27h29z"/>')


def chi_rho() -> str:
    marks = ('<path d="M0-170V176"/><path d="M0-170H20A52 52 0 0 1 20-66H0"/>'
             '<path d="M-112-88L112 136M112-88L-112 136"/>')
    return picture("#a3182b",
        rays(24, "#7d1020")
        + '<circle r="196" fill="none" stroke="#f2c230" stroke-width="4"/>'
        + f'<g fill="none" stroke-linecap="round"><g stroke="{INK}" stroke-width="32">{marks}</g>'
        + f'<g stroke="#f2c230" stroke-width="24">{marks}</g></g>')


def celtic_cross() -> str:
    # A standing cross on a green hill, the sun behind it.
    arms = "M-27-163H27L20-52L124-59V-5L20-12L27 170H-27L-20-12L-124-5V-59L-20-52Z"
    hill_back = "M-207 90C-120 40-40 66 40 86C100 100 160 78 207 90A225.5 225.5 0 0 1-207 90Z"
    hill_front = "M-180 136C-92 104 0 146 80 124C120 114 150 121 180 136A225.5 225.5 0 0 1-180 136Z"
    stone = "#f3ead2"
    return picture("#1d4f91",
        rays(24, "#2f6fb3")
        + f'<circle cy="-32" r="124" fill="#f0b429" stroke="{INK}" stroke-width="2.5"/>'
        + f'<path d="{hill_back}" fill="#3f9a4e" stroke="{INK}" stroke-width="2.5"/>'
        + f'<circle cy="-32" r="86" fill="none" stroke="{INK}" stroke-width="26"/>'
        + f'<circle cy="-32" r="86" fill="none" stroke="{stone}" stroke-width="20"/>'
        + f'<path d="{arms}" fill="{stone}" stroke="{INK}" stroke-width="3"/>'
        + f'<circle cy="-32" r="10" fill="#d81e2c" stroke="{INK}" stroke-width="2.5"/>'
        + f'<path d="{hill_front}" fill="#1f6b36" stroke="{INK}" stroke-width="2.5"/>')


def canterbury_cross() -> str:
    reach, half = 190.0, math.radians(31)
    x, y = reach * math.sin(half), -reach * math.cos(half)
    arm = (f"M-22-20Q-27-104 {n(-x)} {n(y)}A{n(reach)} {n(reach)} 0 0 1 {n(x)} {n(y)}"
           "Q27-104 22-20Z")
    panel = "M0-66L-36-150Q0-163 36-150Z"
    four = lambda d: "".join(turned(d, 90 * i) for i in range(4))
    return picture("#1b3f8a",
        rays(16, "#122c66", turn=math.pi / 16)
        + f'<g fill="#f2c230" stroke="{INK}" stroke-width="3">{four(arm)}<path d="M-24-24h48v48h-48z"/></g>'
        + f'<g fill="#b3202d" stroke="{INK}" stroke-width="2.5">{four(panel)}<path d="M-12-12h24v24h-24z"/></g>')


def burning_bush() -> str:
    # The bush that burned and was not consumed (Exodus 3), the Reformed
    # churches' old emblem: a scene, drawn from nothing.
    flame = "M0 0C-50-36-22-84-8-140C24-98 50-42 0 0Z"
    def fire(scale: float, color: str) -> str:
        # Each flame's foot is down among the leaves, which are drawn over it:
        # the bush is on fire, not a fire set on top of a bush.
        spots = ((-116, 54, -40, .55), (-78, 36, -24, .8), (-40, 24, -10, 1.0), (0, 16, 2, 1.18),
                 (42, 24, 12, 1.0), (80, 36, 26, .8), (118, 54, 42, .55))
        return f'<g fill="{color}" stroke="{INK}" stroke-width="2">' + "".join(
            f'<path transform="translate({x} {y}) rotate({r}) scale({n(k * scale)})" vector-effect="non-scaling-stroke" d="{flame}"/>'
            for x, y, r, k in spots) + '</g>'
    leaves = ((-92, 40, 40), (-52, 22, 44), (0, 12, 50), (52, 22, 44), (92, 40, 40), (-64, 62, 40), (0, 58, 48), (64, 62, 40))
    ground = "M-189.6 122C-120 98-60 110 0 116C70 123 130 100 189.6 122A225.5 225.5 0 0 1-189.6 122Z"
    return picture("#2a2f7a",
        rays(24, "#3a4099")
        + '<g transform="translate(0 26)"><circle cy="-40" r="150" fill="#f6c445" opacity=".9"/>'
        # The tallest flame stops short of the ring (its tip is at about -203 of 225).
        + fire(1.48, "#d81e2c") + fire(1.12, "#f08a1c") + fire(.74, "#fbe07a") + '</g>'
        + f'<path d="{ground}" fill="#c9952f" stroke="{INK}" stroke-width="2.5"/>'
        + '<g transform="translate(0 26)">'
        + f'<path d="M-12 150L-9 70H9L12 150Z" fill="#6b4423" stroke="{INK}" stroke-width="2.5"/>'
        + f'<g fill="#1f6b36" stroke="{INK}" stroke-width="2.5">'
        + "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in leaves) + '</g>'
        + '<g fill="#1f6b36">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r - 3}"/>' for x, y, r in leaves) + '</g>'
        # and a few small flames among the leaves in front
        + "".join(tongue(x, y, .3, turn) for x, y, turn in ((-70, 74, -10), (-22, 58, -4), (30, 80, 6), (76, 62, 12))) + '</g>')


def chalice_and_host() -> str:
    # The cup and the bread of the Eucharist, the host shining above the chalice.
    o = f'stroke="{INK}" stroke-width="3"'
    gold, deep = "#f2c230", "#c48a12"
    return picture("#5a1d6e",
        rays(24, "#451457")
        + '<g transform="translate(0 -84)">' + rays(32, gold, radius=112)
        + f'<circle r="66" fill="#fffdf6" {o}/>'
        + '<path d="M-8-38h16v16h18v16h-18v44h-16v-44h-18v-16h18z" fill="#b3202d"/></g>'
        + f'<path d="M-64 168C-56 132-24 124-9 120V84H9V120C24 124 56 132 64 168Z" fill="{gold}" {o}/>'
        + f'<ellipse cy="96" rx="24" ry="13" fill="{gold}" {o}/>'
        + f'<path d="M-76 0C-76 56-38 84 0 84C38 84 76 56 76 0Z" fill="{gold}" {o}/>'
        + f'<ellipse rx="76" ry="15" fill="{deep}" {o}/>'
        + f'<path d="M-52 22C-48 50-28 66-6 70" fill="none" stroke="#fbe9a6" stroke-width="6" stroke-linecap="round"/>')


def moravian_star() -> str:
    # The many-pointed star first made in the Moravian school at Niesky and hung
    # in Advent wherever there are Moravians: seen from the front, its points in
    # three ranks, each with a lit face and a shaded one.
    def point(angle: float, length: float, shoulder: float, spread: float, lit: str, dim: str) -> str:
        a = math.radians(angle)
        tip = f"{n(length * math.sin(a))} {n(-length * math.cos(a))}"
        left, right = (f"{n(shoulder * math.sin(a + s))} {n(-shoulder * math.cos(a + s))}"
                       for s in (-math.radians(spread), math.radians(spread)))
        return (f'<path d="M0 0L{left}L{tip}Z" fill="{lit}"/>'
                f'<path d="M0 0L{right}L{tip}Z" fill="{dim}"/>')
    ranks = (
        ([22.5 + 45 * i for i in range(8)], 142, 52, 21, "#e9e6d8", "#aeb9d0"),
        ([45 + 90 * i for i in range(4)], 182, 56, 24, "#f6f3e6", "#bcc6da"),
        ([90 * i for i in range(4)], 210, 60, 26, "#fffdf2", "#c9d3e6"),
    )
    star = "".join(point(a, *rest) for angles, *rest in ranks for a in angles)
    # The point that faces the viewer: a square pyramid seen from its tip.
    near = ('<path d="M0 0L-30-30H30Z" fill="#fffdf2"/><path d="M0 0L30-30V30Z" fill="#dfe5f0"/>'
            '<path d="M0 0L30 30H-30Z" fill="#c9d3e6"/><path d="M0 0L-30 30V-30Z" fill="#eef1f6"/>')
    return picture("#0f2557",
        rays(24, "#17337a")
        + '<circle r="128" fill="#f4d35e"/><circle r="100" fill="#fbe9a6"/>'
        + f'<g stroke="{INK}" stroke-width="2">{star}{near}</g>')


# ---- The seasons' own pictures (data/season_art.csv says which season shows which) ----

FLAME = "M0 0C-50-36-22-84-8-140C24-98 50-42 0 0Z"


def tongue(x: float, y: float, size: float, turn: float = 0.0) -> str:
    """A flame standing at x,y: red-orange round a yellow heart."""
    return (f'<g transform="translate({n(x)} {n(y)}) rotate({n(turn)}) scale({n(size)})" stroke="{INK}" stroke-width="{n(2 / size)}">'
            f'<path d="{FLAME}" fill="#f08a1c"/><path transform="translate(1 -4) scale(.55)" d="{FLAME}" fill="#fbe07a" stroke="none"/></g>')


def star(points: int, long: float, short: float, waist: float, fill: str, turn: float = 0.0) -> str:
    """A star of long and short rays by turns (`points` of each), pinched to `waist` between them."""
    path = []
    for i in range(points * 2):
        a = math.radians(turn + i * 180 / points)
        r = long if i % 2 == 0 else short
        b = a + math.radians(90 / points)
        path.append(f"{n(r * math.sin(a))} {n(-r * math.cos(a))}L{n(waist * math.sin(b))} {n(-waist * math.cos(b))}")
    return f'<path d="M{"L".join(path)}Z" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'


def ground(y: float, sag: float, fill: str) -> str:
    """The foot of the field from height y down, its top a gentle hill."""
    x = math.sqrt(225.5 ** 2 - y ** 2)
    return (f'<path d="M{n(-x)} {n(y)}Q0 {n(y - sag)} {n(x)} {n(y)}A225.5 225.5 0 0 1 {n(-x)} {n(y)}Z" '
            f'fill="{fill}" stroke="{INK}" stroke-width="2.5"/>')


def season_advent(lit: int = 4) -> str:
    # The Advent wreath, seen from a little above: four candles standing round
    # a wreath of leaves, three violet and one rose, `lit` of them burning:
    # one more each week, from the left, so the rose candle is lit on the
    # third Sunday.
    o = f'stroke="{INK}" stroke-width="2.5"'
    # A leaf, its stalk at 0,0 and its point up, with its midrib.
    leaf = "M0 8C-15-8-14-42 0-64C14-42 15-8 0 8ZM0 0V-48"
    greens = ("#2e8b3e", "#1f6b36", "#3f9a4e")
    count, rx, ry, cy = 48, 148.0, 56.0, 92.0

    def on_ring(degrees: float) -> tuple:
        t = math.radians(degrees)
        return rx * math.cos(t), cy + ry * math.sin(t)

    # Everything standing on the wreath, each with how near it is (its y), so
    # that the nearer is drawn over the farther.
    things = []
    for i in range(count):
        t = 2 * math.pi * (i + .5) / count
        x, y = rx * math.cos(t), cy + ry * math.sin(t)
        # Along the wreath, each leaf leaning out or in by turns.
        dx, dy = -rx * math.sin(t), ry * math.cos(t)
        turn = math.degrees(math.atan2(dx, -dy)) + (-46, 8, 46, -8)[i % 4]
        things.append((y, True, f'<path transform="translate({n(x)} {n(y)}) rotate({n(turn)})" '
                                f'fill="{greens[i % 3]}" d="{leaf}"/>'))
    # The candles, by where each stands on the wreath (degrees round it: 0 at
    # the right, 90 nearest), in the order they are lit: round the back from
    # the left to the right, and evenly apart across the picture.  Each stands
    # a little into the wreath, behind the leaves beside it.
    candles = ((160, "#6a4bb3"), (251, "#6a4bb3"), (289, "#e58fb0"), (20, "#6a4bb3"))
    tall = 150
    for i, (degrees, color) in enumerate(candles):
        x, y = on_ring(degrees)
        x, foot = round(x), round(y) - 4
        things.append((foot - 12, False,
            f'<path d="M{x - 17} {foot}V{foot - tall}H{x + 17}V{foot}Z" fill="{color}" {o}/>'
            f'<path d="M{x - 9} {foot - tall + 8}V{foot - 12}" stroke="#fff" stroke-opacity=".35" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M{x} {foot - tall}v-12" stroke="{INK}" stroke-width="3"/>'
            + (tongue(x, foot - tall - 8, .36) if i < lit else "")))
    # Berries in pairs, at the front and at the back, lying on the leaves.
    berries = (48, 80, 152, 228, 270, 312)
    for degrees in berries:
        x, y = on_ring(degrees)
        things.append((y + 30, False, "".join(
            f'<circle cx="{n(x + bx)}" cy="{n(y + by)}" r="7" fill="#d81e2c" stroke="{INK}" stroke-width="2"/>'
            for bx, by in ((-7, 2), (7, -4)))))
    standing, in_leaves = "", False
    for _, is_leaf, mark in sorted(things):
        if is_leaf != in_leaves:
            standing += f'<g stroke="{INK}" stroke-width="2">' if is_leaf else '</g>'
            in_leaves = is_leaf
        standing += mark
    standing += '</g>' if in_leaves else ''
    stem = (f'<ellipse cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="none" stroke="#17532a" stroke-width="20"/>')
    return picture("#2b2f77",
        rays(24, "#3a3f95")
        + '<circle cy="-60" r="132" fill="#474da8"/>'
        + stem + standing)


def season_christmas() -> str:
    # The manger under the star.
    o = f'stroke="{INK}" stroke-width="2.5"'
    beam = '<path d="M0-126L-40 96H40Z" fill="#3f5fb0"/>'
    straw = "".join(f'<path d="M{x} 70L{x + lean} {36 - abs(x) // 9}" stroke="#f2c230" stroke-width="5" stroke-linecap="round"/>'
                    for x, lean in ((-86, -14), (-70, -6), (-54, -10), (54, 10), (70, 6), (86, 14), (-96, -20), (96, 20)))
    # The sky: stars scattered as they fall, no two sides alike, most of them
    # small and a few bright ones with points.
    dots = ((-171, -52, 3.4), (-139, -131, 2), (-88, -171, 3), (-63, -84, 1.8), (-190, 14, 2.2),
            (-121, -22, 2.6), (-152, 61, 1.8), (-37, -196, 1.8), (-104, -108, 1.6), (71, -189, 2.4),
            (109, -146, 1.8), (153, -103, 3), (83, -62, 2.2), (181, -41, 1.8), (134, 9, 2.8),
            (188, 52, 2), (47, -92, 1.6), (119, -84, 1.6), (-78, 34, 1.6), (143, -147, 1.6))
    sparkle = lambda x, y, k: (f'<path transform="translate({x} {y})" d="M0-{k}L{n(k * .22)}-{n(k * .22)}L{k} 0L{n(k * .22)} {n(k * .22)}'
                               f'L0 {k}L-{n(k * .22)} {n(k * .22)}L-{k} 0L-{n(k * .22)}-{n(k * .22)}Z" fill="#fffdf2"/>')
    sky = ("".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fffdf2"/>' for x, y, r in dots)
           + sparkle(-129, -79, 11) + sparkle(127, -42, 8) + sparkle(96, -176, 9) + sparkle(-176, -14, 6))
    return picture("#10235c",
        rays(24, "#18317a")
        + sky
        + beam
        + f'<g transform="translate(0 -126)">{star(4, 78, 34, 15, "#f2c230")}{star(4, 30, 13, 7, "#fffdf2")}</g>'
        + ground(112, 26, "#1f4d2c")
        # the manger: crossed legs, the trough, straw, and the child in swaddling bands
        + f'<path d="M-92 150L-60 66M92 150L60 66M-92 66L-60 150M92 66L60 150" fill="none" stroke="{INK}" stroke-width="15" stroke-linecap="round"/>'
        + '<path d="M-92 150L-60 66M92 150L60 66M-92 66L-60 150M92 66L60 150" fill="none" stroke="#8a5a2b" stroke-width="10" stroke-linecap="round"/>'
        + straw
        + f'<circle cx="-46" cy="38" r="34" fill="#f2c230" {o}/>'
        + f'<path d="M-52 62C-20 30 60 24 84 52C70 76-20 82-52 62Z" fill="#fffdf6" {o}/>'
        + f'<path d="M-22 44L-4 74M12 36L30 72M46 36L62 66" fill="none" stroke="#b9c2d6" stroke-width="4" stroke-linecap="round"/>'
        + f'<circle cx="-46" cy="40" r="19" fill="#f1c9a5" {o}/>'
        + f'<path d="M-108 62H108L92 104H-92Z" fill="#a8703a" {o}/>'
        + f'<path d="M-100 76H100M-96 90H96" fill="none" stroke="{INK}" stroke-width="2" opacity=".5"/>')


def season_epiphany() -> str:
    # The star and the three crowns of the wise men.
    o = f'stroke="{INK}" stroke-width="2.5"'
    def crown(x: float, y: float, k: float, jewel: str) -> str:
        return (f'<g transform="translate({x} {y}) scale({k})">'
                f'<path d="M-50 34L-58-30L-28 0L0-44L28 0L58-30L50 34Z" fill="#f2c230" {o}/>'
                f'<path d="M-52 34H52V52H-52Z" fill="#e3a81a" {o}/>'
                + "".join(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{jewel}" stroke="{INK}" stroke-width="2"/>'
                          for cx, cy in ((-58, -34), (0, -48), (58, -34), (0, 43)))
                + f'<circle cx="-30" cy="43" r="5" fill="#fffdf2" stroke="{INK}" stroke-width="2"/>'
                + f'<circle cx="30" cy="43" r="5" fill="#fffdf2" stroke="{INK}" stroke-width="2"/></g>')
    return picture("#0f5a50",
        rays(24, "#0b463e")
        + '<path d="M0-104L-156 158H156Z" fill="#1c7a6c"/>'
        + f'<g transform="translate(0 -104)">{star(4, 92, 40, 17, "#f2c230")}{star(4, 36, 15, 8, "#fffdf2")}</g>'
        + crown(-124, 82, .74, "#d81e2c") + crown(124, 82, .74, "#2f74b8") + crown(0, 110, .9, "#7a3fb0"))


def season_lent() -> str:
    # The cross and the crown of thorns: the head as long as the arms (100),
    # the foot a little over twice that, and the arms showing beyond the crown.
    # The crown is two briars wound round one another, each passing over and
    # under the other by turns, with thorns of uneven length standing off them
    # at uneven angles, as a thorn branch has them.
    o = f'stroke="{INK}" stroke-width="3"'
    waves, mid, swing = 7, 77.0, 8.5

    def briar(which: int, degrees: float) -> tuple:
        """Where briar `which` (0 or 1) is at `degrees` round the crown."""
        t = math.radians(degrees)
        r = mid + (swing if which == 0 else -swing) * math.sin(waves * t) + 2.5 * math.sin(2 * t + 1 + which)
        return r * math.sin(t), -r * math.cos(t)

    def run(which: int, start: float, end: float) -> str:
        """Briar `which` from `start` to `end` degrees, as a path."""
        steps = max(2, round((end - start) / 4))
        return "M" + "L".join(f"{n(x)} {n(y)}" for x, y in
                              (briar(which, start + (end - start) * i / steps) for i in range(steps + 1)))

    def strand(d: str, color: str) -> str:
        return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="13" stroke-linejoin="round"/>'
                f'<path d="{d}" fill="none" stroke="{color}" stroke-width="8" stroke-linejoin="round"/>')
    brown = ("#7a5230", "#5e3d20")
    # The two briars cross every 180/waves degrees; at every other crossing
    # the first is on top, so a short length of it is drawn again there.
    cross_at = 180 / waves
    woven = strand(run(0, 0, 360) + "Z", brown[0]) + strand(run(1, 0, 360) + "Z", brown[1])
    woven += "".join(strand(run(0, (2 * j + .5) * cross_at, (2 * j + 1.5) * cross_at), brown[0]) for j in range(waves))
    # The thorns: where round the crown, which briar, how far the thorn leans
    # from straight out (past 90 it points in), and how long.
    thorns = ""
    for degrees, which, lean, length in (
            (6, 0, 24, 30), (21, 1, -38, 22), (39, 0, -12, 34), (52, 1, 150, 18), (68, 0, 36, 26),
            (88, 1, -20, 32), (101, 0, 8, 20), (117, 1, 44, 30), (133, 0, -150, 17), (146, 1, -30, 26),
            (163, 0, 16, 34), (181, 1, -8, 22), (196, 0, 40, 28), (212, 1, 162, 18), (226, 0, -34, 30),
            (243, 1, 12, 24), (259, 0, -18, 34), (272, 1, 46, 22), (290, 0, 146, 17), (303, 1, -42, 28),
            (319, 0, 4, 32), (334, 1, 30, 22), (349, 0, -26, 28)):
        x, y = briar(which, degrees)
        a = math.radians(degrees + lean)
        ux, uy = math.sin(a), -math.cos(a)                 # the way the thorn points
        tip = (x + ux * length, y + uy * length)
        thorns += (f'<path d="M{n(x - uy * 4.5)} {n(y + ux * 4.5)}L{n(tip[0])} {n(tip[1])}'
                   f'L{n(x + uy * 4.5)} {n(y - ux * 4.5)}Z"/>')
    return picture("#4a1d73",
        rays(24, "#3a155c")
        + '<circle cy="-40" r="140" fill="#62329a"/>'
        + f'<path d="M-24-164H24V-64H124V-16H24V198H-24V-16H-124V-64H-24Z" fill="#8a5a2b" {o}/>'
        + f'<path d="M-10-156V188M-114-46H114" fill="none" stroke="#6b4423" stroke-width="4" stroke-linecap="round"/>'
        + f'<g transform="translate(0 -40)"><g fill="#4e3219" stroke="{INK}" stroke-width="2" stroke-linejoin="round">{thorns}</g>{woven}</g>')


def season_holy_week() -> str:
    # The three crosses on the hill, the sky gone dark.
    cross = "M-9-138H9V-104H43V-86H9V40H-9V-86H-43V-104H-9Z"
    return picture("#3a0d16",
        rays(24, "#52131f")
        + f'<circle cy="-52" r="96" fill="#e7a23a" stroke="{INK}" stroke-width="2.5"/>'
        + '<circle cy="-52" r="74" fill="#f6d36b"/>'
        + f'<g fill="#1a1210" stroke="{INK}" stroke-width="2">'
        + f'<path transform="translate(-112 62) scale(.74)" d="{cross}"/><path transform="translate(112 62) scale(.74)" d="{cross}"/>'
        + f'<path transform="translate(0 44) scale(1.16)" d="{cross}"/></g>'
        + ground(92, 76, "#1a1210"))


def season_easter() -> str:
    # The empty tomb at sunrise: the stone, big enough to seal the door, rolled away.
    o = f'stroke="{INK}" stroke-width="2.5"'
    return picture("#f39a2b",
        rays(24, "#f7c04a")
        + f'<circle cy="40" r="118" fill="#fff3b0" {o}/>'
        + '<circle cy="40" r="92" fill="#fffdf2"/>'
        + ground(96, 30, "#3f9a4e")
        + f'<path d="M-166 132C-166 26-100-40-14-40C72-40 138 26 138 132Z" fill="#b9b3a6" {o}/>'
        + f'<path d="M-136 120C-130 50-88-4-24-12M24-26C66-10 100 36 110 100" fill="none" stroke="#8f897c" stroke-width="5" stroke-linecap="round"/>'
        # the door: 84 wide and 100 high; the stone beside it is 136 across
        + f'<path d="M-62 132V74A42 42 0 0 1 22 74V132Z" fill="#1a1210" {o}/>'
        + f'<circle cx="104" cy="72" r="68" fill="#d2ccbf" {o}/>'
        + f'<path d="M62 46A52 52 0 0 1 122 20" fill="none" stroke="#fffdf2" stroke-width="6" stroke-linecap="round"/>'
        + f'<path d="M70 98A50 50 0 0 0 150 104" fill="none" stroke="#a39d90" stroke-width="5" stroke-linecap="round"/>'
        + ground(128, 12, "#1f6b36"))


def mirrored(start: tuple, curves: tuple) -> str:
    """A closed shape the same on both sides: `curves` (each two control points
    and an end) run from `start` at the top middle down the left side to the
    bottom middle, and the right side is their reflection."""
    def pt(q) -> str:
        return f"{n(q[0])} {n(q[1])}"
    flip = lambda q: (-q[0], q[1])
    path = "M" + pt(start) + "".join("C" + " ".join(pt(q) for q in c) for c in curves)
    ends = [start] + [c[2] for c in curves]
    for i in range(len(curves) - 1, -1, -1):
        c1, c2, _ = curves[i]
        path += "C" + " ".join(pt(flip(q)) for q in (c2, c1, ends[i]))
    return path + "Z"


def season_pentecost() -> str:
    # The dove descending as the old windows have it: one white shape, seen
    # from above as it comes down, the tail fanned at the top and the head and
    # bill below.  Each wing is round and low where it folds, runs up its
    # leading edge to one point that leans in, and comes back to the shoulder
    # in feathers, each shorter than the last.  A glory round it, and the
    # tongues of fire.
    o = f'stroke="{INK}" stroke-width="3"'
    dove = mirrored((0, -180), (
        ((-12, -180), (-20, -170), (-22, -158)),      # the tail's middle feather
        ((-30, -180), (-54, -182), (-62, -150)),      # the next,
        ((-70, -170), (-92, -166), (-98, -140)),      # and the outermost, to the corner
        ((-84, -116), (-48, -110), (-40, -84)),       # in to the waist
        ((-36, -56), (-52, -24), (-52, 20)),          # the back, to the shoulder
        ((-55, 8), (-62, 3), (-74, 6)),               # the wing's trailing edge: a feather,
        ((-75, -8), (-82, -15), (-96, -14)),          # and another,
        ((-93, -29), (-99, -39), (-114, -44)),        # and another, each longer,
        ((-110, -60), (-115, -74), (-128, -84)),      # and another,
        ((-126, -102), (-130, -119), (-140, -134)),   # and the last, up to the tip
        ((-160, -100), (-182, -30), (-182, 40)),      # down the leading edge
        ((-182, 98), (-160, 142), (-120, 142)),       # the round of the fold, hanging low
        ((-88, 142), (-54, 124), (-38, 90)),          # beneath, up to the breast
        ((-40, 100), (-30, 104), (-22, 110)),         # the breast, in to the neck
        ((-40, 118), (-40, 160), (-18, 166)),         # the head
        ((-10, 170), (-4, 184), (0, 200)),            # the bill
    ))
    extras = (f'<path d="M-52 20C-56 44-52 64-44 78M52 20C56 44 52 64 44 78" fill="none" '
              f'stroke="{INK}" stroke-width="3.6" stroke-linecap="round"/>')    # the sides of the body, over the wings
    flames = "".join(tongue(x, y, .4, turn) for x, y, turn in
                     ((-150, 150, -8), (-100, 178, -5), (-50, 194, -2), (0, 200, 0), (50, 194, 2), (100, 178, 5), (150, 150, 8)))
    return picture("#b3202d",
        rays(24, "#8a1424")
        + f'<circle cy="-30" r="150" fill="#f2c230" {o}/>'
        + '<g transform="translate(0 -30)">' + rays(24, "#f7d766", 148.5) + '</g>'
        + '<g transform="translate(0 -30) scale(.78)">'
        + f'<path d="{dove}" fill="#fffdf6" stroke="{INK}" stroke-width="3.6"/>'
        + extras + '</g>'
        + flames)


def on_sunburst(source: str, field: str, shade: str, recolor: dict, reach: float = 180.0,
                outline: bool = True, count: int = 24, circles_last: bool = False):
    """A drawing kept in artwork/sources set in gold on a sunburst: its own
    colors swapped as `recolor` says, fitted so its longer side spans the field.
    `circles_last` draws the source's circles over its other shapes on both
    sides (the Armenian cross lists one side's buds before its points and the
    other's after, which shows once each shape is outlined)."""
    def draw() -> str:
        text = (HERE.parent / "artwork" / "sources" / source).read_text(encoding="utf-8")
        w, h = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', text).groups())
        inner = text[text.index(">", text.index("<svg")) + 1:text.rindex("</svg>")].strip()
        inner = re.sub(r'\s*fill-opacity="[^"]*"', "", inner)
        for old, new in recolor.items():
            inner = inner.replace(old, new)
        inner = re.sub(r">\s+<", "><", inner)
        if circles_last:
            circles = re.findall(r"<circle[^>]*/>", inner)
            end = inner.rindex("</g>")
            inner = re.sub(r"<circle[^>]*/>", "", inner[:end]) + "".join(circles) + inner[end:]
        k = 2 * reach / max(w, h)
        edge = (f' stroke="{INK}" stroke-width="{n(5 / k)}" paint-order="stroke"' if outline else "")
        return picture(field, rays(count, shade)
            + f'<g transform="scale({k:.4f}) translate({n(-w / 2)} {n(-h / 2)})" fill="#f2c230"{edge}>{inner}</g>')
    return draw


EMBLEMS = {
    "Luther_Rose.svg": luther_rose,
    "Chi_Rho_Roundel.svg": chi_rho,
    "Celtic_Cross_Roundel.svg": celtic_cross,
    "Canterbury_Cross_Roundel.svg": canterbury_cross,
    "Chalice_and_Host_Roundel.svg": chalice_and_host,
    "Burning_Bush_Roundel.svg": burning_bush,
    "Moravian_Star_Roundel.svg": moravian_star,
    "Season_Advent_1.svg": lambda: season_advent(1),
    "Season_Advent_2.svg": lambda: season_advent(2),
    "Season_Advent_3.svg": lambda: season_advent(3),
    "Season_Advent_4.svg": lambda: season_advent(4),
    "Season_Christmas.svg": season_christmas,
    "Season_Epiphany.svg": season_epiphany,
    "Season_Lent.svg": season_lent,
    "Season_Holy_Week.svg": season_holy_week,
    "Season_Easter.svg": season_easter,
    "Season_Pentecost.svg": season_pentecost,
    "Orthodox_Cross_Roundel.svg": on_sunburst("OrthodoxCross.svg", "#3b2a7a", "#2c1f5e", {' fill="#000080"': ""}),
    "Armenian_Cross_Roundel.svg": on_sunburst("Armenian_Cross.svg", "#b5451b", "#933612", {}, circles_last=True),
    "Syriac_Cross_Roundel.svg": on_sunburst("Western_Syriac_Cross.svg", "#6d1a36", "#541229", {' fill="#000000"': ""}),
    "Coptic_Cross_Roundel.svg": on_sunburst("Coptic_Cross.svg", "#0e5a8a", "#0a466c", {"#6b3a1e": "#f2c230", "#ffffff": "#a3182b", "#fff\"": "#a3182b\""}, reach=172, outline=False),
    "Ethiopian_Cross_Roundel.svg": on_sunburst("Ethiopian_Cross.svg", "#1f6b36", "#17532a", {"#7a5a10": "#f2c230", "#ffffff": "#a3182b"}, reach=176, outline=False),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Draw the project's own center artwork.")
    parser.add_argument("--out", type=Path, default=HERE.parent / "artwork",
                        help="the folder to write into (default: artwork/)")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for name, draw in EMBLEMS.items():
        text = draw()
        (args.out / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"✓ {args.out / name}  ({len(text.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
