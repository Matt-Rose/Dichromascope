#!/usr/bin/env python3
"""
Render dichromatic-animal colour vision on a trichromatic (sRGB) display.

Pipeline
  1. Cone sensitivities from the Govardovskii (2000) A1 nomogram (alpha + beta
     band) x a crude lens-transmission edge, converted quantal -> energy.
  2. sRGB photo -> reflectance spectrum (Mallett & Yuksel 2019 basis, linear in
     linear-sRGB) under D65 -> 2 animal cone catches, von-Kries normalised so a
     white surface gives catch = 1 in both classes.
  3. "Expansion" to the three human axes: LMS_human = q_short*u_S + q_long*u_L,
     with u_S = human LMS of 475 nm (scaled to S=1) and u_L = white - u_S
     (~575 nm yellow). A dichromat has no third channel, so the image occupies a
     2-D plane (luminance + blue-yellow) of human colour space; the animal-
     invisible axis is pinned to that plane. For a UV cone the same assignment
     is a false-colour mapping (UV -> human blue).
  4. HPE (D65-normalised) LMS -> linear sRGB, clip, gamma.

Usage
  python dichromat_sim.py photo.jpg -s dog cat horse -o out.png
  python dichromat_sim.py --strips -s dog cat horse mouse -o strips.png
  python dichromat_sim.py --demo [scene|swatches] -o demo.png
  python dichromat_sim.py --palette -s dog -m plane boomerang cylinder -o sheets.png
  python dichromat_sim.py photo.jpg -s dog -m plane boomerang cylinder   # rainbow sheets
"""
import argparse
import numpy as np
import colour
from colour.recovery import MSDS_BASIS_FUNCTIONS_sRGB_MALLETT2019 as _BASIS

# lmax (nm) of short / long cone; lens = approx. 50 % ocular-media cutoff (nm).
# Typical literature values (Jacobs 1993 review; Neitz+ 1989 dog; Jacobs+ 1991
# mouse; Carroll+ 2001 horse). Lens values are rough and only matter for UV.
SPECIES = {
    "dog":   dict(s=429, l=555, lens=390),
    "cat":   dict(s=450, l=556, lens=380),
    "horse": dict(s=428, l=539, lens=380),
    "mouse": dict(s=360, l=508, lens=320, uv=True),
}

# animal [short, long] -> human [L, M, S]  (filled in below, once the human
# fundamentals are available): columns u_S, u_L with u_S + u_L = (1,1,1).
A_ASSIGN = None

# sRGB (linear) <-> HPE LMS, D65-normalised (white -> LMS = 1,1,1)
RGB2XYZ = np.array([[0.4124564, 0.3575761, 0.1804375],
                    [0.2126729, 0.7151522, 0.0721750],
                    [0.0193339, 0.1191920, 0.9503041]])
XYZ2LMS = np.array([[0.4002, 0.7076, -0.0808],
                    [-0.2263, 1.1653, 0.0457],
                    [0.0, 0.0, 0.9182]])
LMS2RGB = np.linalg.inv(XYZ2LMS @ RGB2XYZ)

_D65 = colour.SDS_ILLUMINANTS["D65"]
_SS = colour.MSDS_CMFS["Stockman & Sharpe 2 Degree Cone Fundamentals"]


# ----------------------------------------------------------------- spectra --
def nomogram(wl, lmax):
    """Govardovskii et al. 2000, A1 pigment, alpha + beta band, peak ~1."""
    x = lmax / wl
    a = 0.8795 + 0.0459 * np.exp(-((lmax - 300.0) ** 2) / 11940.0)
    alpha = 1.0 / (np.exp(69.7 * (a - x)) + np.exp(28.0 * (0.922 - x))
                   + np.exp(-14.9 * (1.104 - x)) + 0.674)
    lb, bb = 189.0 + 0.315 * lmax, -40.5 + 0.195 * lmax
    return alpha + 0.26 * np.exp(-(((wl - lb) / bb) ** 2))


def cone_sens(wl, sp):
    """(2, N) energy-based sensitivities [short, long], peak-normalised."""
    lens = 1.0 / (1.0 + np.exp(-(wl - sp["lens"]) / 8.0))
    out = []
    for lmax in (sp["s"], sp["l"]):
        s = nomogram(wl, lmax) * lens * wl          # quantal -> energy
        out.append(s / s.max())
    return np.array(out)


def d65(wl):
    return np.interp(wl, _D65.wavelengths, _D65.values)


def human_lms(wl):
    """(N, 3) Stockman-Sharpe 2deg cone fundamentals, zero outside range."""
    return np.stack([np.interp(wl, _SS.wavelengths, _SS.values[:, k],
                               left=0, right=0) for k in range(3)], axis=1)


def anchor_assignment(anchor_nm=475.0):
    """3x2 embedding [u_S | u_L] of the two animal channels into human LMS.

    u_S: human LMS of the 475 nm anchor (white-normalised, scaled to S = 1);
    u_L = (1,1,1) - u_S so achromatic stimuli stay achromatic. 475/575 nm are the
    wavelengths unilateral dichromats match to normal vision (Brettel+ 1997); the
    resulting u_L has L:M ~ 1.17 vs 1.15 for 575 nm light, i.e. both anchors are
    ~coplanar with white. The free (animal-invisible) axis is thus pinned to the
    one that makes 'short-only' ~ blue and 'long-only' ~ yellow."""
    wg = np.arange(340.0, 781.0, 1.0)
    white = (human_lms(wg) * d65(wg)[:, None]).sum(0) / d65(wg).sum()
    v = human_lms(np.array([anchor_nm]))[0] / white
    u_s = v / v[2]
    return np.stack([u_s, 1.0 - u_s], axis=1)


A_ASSIGN = anchor_assignment()


# ------------------------------------------------------------- photo path --
def cone_matrix(species):
    """(2, 3): linear sRGB -> von-Kries-normalised [short, long] cone catch."""
    wl = np.arange(380.0, 781.0, 5.0)
    B = np.stack([np.interp(wl, _BASIS.wavelengths, _BASIS.values[:, k])
                  for k in range(3)], axis=1)       # reflectance basis (N, 3)
    S = cone_sens(wl, SPECIES[species])             # (2, N)
    Q = S @ (d65(wl)[:, None] * B)                  # (2, 3)
    return Q / Q.sum(axis=1, keepdims=True)         # white (1,1,1) -> (1,1)


def srgb_decode(u):
    u = np.asarray(u, float)
    return np.where(u <= 0.04045, u / 12.92, ((u + 0.055) / 1.055) ** 2.4)


def srgb_encode(v):
    v = np.clip(v, 0, 1)
    return np.where(v <= 0.0031308, 12.92 * v, 1.055 * v ** (1 / 2.4) - 0.055)


def render(img, species, mode="plane", return_stats=False):
    """img: float RGB in [0,1] (sRGB-encoded) -> same, as seen by `species`.
    mode: plane | boomerang | cylinder (see rainbow_map)."""
    if SPECIES[species].get("uv"):
        raise ValueError(f"{species}: UV cone is not recoverable from an RGB "
                         "photo; use --strips or feed real UV data.")
    lin = srgb_decode(img)
    q = lin @ cone_matrix(species).T                # (H, W, 2)
    if mode == "plane":
        lms = q @ A_ASSIGN.T                        # (H, W, 3)  <- the expansion
        rgb = lms @ LMS2RGB.T
        clipped = float(np.mean(np.any((rgb < -1e-3) | (rgb > 1 + 1e-3), axis=-1)))
        out = srgb_encode(rgb)
    else:
        out, clipped = rainbow_map(q[..., 0], q[..., 1], species, mode)
    return (out, clipped) if return_stats else out


# ------------------------------------------------- rainbow (curved) sheets --
# OKLab (Ottosson 2020)
_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])
_M1i, _M2i = np.linalg.inv(_M1), np.linalg.inv(_M2)

# Receptor-noise-limited (Vorobyev-Osorio) chromatic metric for a dichromat.
# ASSUMPTIONS (not measured for these species): Weber fraction 0.05 on the long
# cone, short cones 10 % of cones; 1 human JND ~ 0.02 in OKLab.
RNL = dict(omega=0.05, eta_s=0.10, human_jnd=0.02)


def e_chrom():
    r = RNL
    e_l = r["omega"]
    e_s = r["omega"] * np.sqrt((1 - r["eta_s"]) / r["eta_s"])
    return float(np.hypot(e_s, e_l))


def oklab_to_lin(L, a, b):
    lab = np.stack([L, a, b], axis=-1)
    return (((lab @ _M2i.T) ** 3) @ _M1i.T)


def oklch_to_srgb(L, C, h_deg):
    """OKLCh -> sRGB, reducing chroma at fixed L,h until in gamut."""
    h = np.deg2rad(h_deg)

    def inside(c):
        lin = oklab_to_lin(L, c * np.cos(h), c * np.sin(h))
        return np.all((lin > -1e-4) & (lin < 1 + 1e-4), axis=-1)

    ok = inside(C)
    lo, hi = np.zeros_like(C), np.array(C, float)
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        good = inside(mid)
        lo, hi = np.where(good, mid, lo), np.where(good, hi, mid)
    Cf = np.where(ok, C, lo)
    lin = oklab_to_lin(L, Cf * np.cos(h), Cf * np.sin(h))
    return srgb_encode(lin), float(np.mean(~ok))


def chroma_coord(qS, qL, eps=0.02):
    """Signed chromatic opponent coordinate, ln(S/L); 0 = animal neutral."""
    return np.log((qS + eps) / (qL + eps))


def c_range(species):
    """(c_lo, c_hi) over the non-black corners of the sRGB cube."""
    Q = cone_matrix(species)
    cs = []
    for k in range(1, 8):
        rgb = np.array([(k >> 2) & 1, (k >> 1) & 1, k & 1], float)
        q = Q @ rgb
        cs.append(chroma_coord(q[0], q[1]))
    return min(cs), max(cs)


# hue stops (OKLab degrees): red 29, yellow 110, green 142, cyan 195, blue 264, violet 305
MODES = ("plane", "boomerang", "cylinder")


def rainbow_map(qS, qL, species, mode, C0=0.14, L_lo=0.42, L_hi=0.88, Y=None):
    """Map animal catches (qS, qL) to a curved 2-D sheet in OKLCh.

    cylinder  : hue = linear in c (spectral order red..violet), constant chroma.
                Full rainbow, but the animal's neutral point becomes a colour.
    boomerang : neutral stays grey; the short arm runs cyan-blue -> violet, the
                long arm yellow -> red, chroma growing with |c|. No green.
    Lightness (animal luminance qL) is compressed into [L_lo, L_hi] so every
    hue fits in the sRGB gamut at chroma C0."""
    c = chroma_coord(qS, qL)
    lo, hi = c_range(species)
    s = np.clip(np.where(c < 0, c / (-lo), c / hi), -1, 1)
    L = L_lo + (L_hi - L_lo) * np.cbrt(np.clip(qL if Y is None else Y, 0, 1))
    if mode == "cylinder":
        h = 29.0 + (305.0 - 29.0) * (s + 1) / 2
        C = np.full_like(s, C0)
    elif mode == "boomerang":
        h = np.where(s >= 0, 235.0 + 70.0 * s, 95.0 - 66.0 * (-s))
        C = C0 * np.minimum(1.0, np.abs(s) / 0.5)
    else:
        raise ValueError(mode)
    return oklch_to_srgb(L, C, h)


def jnd_budget(species, mode, C0=0.14):
    """Chromatic JNDs available to the animal vs. arc length in the human sheet."""
    lo, hi = c_range(species)
    animal = (hi - lo) / e_chrom()
    J = RNL["human_jnd"]
    if mode == "cylinder":
        human = C0 * np.deg2rad(305.0 - 29.0) / J
    elif mode == "boomerang":
        # arms: chord-ish length of each hue-bent arm, chroma C0 reached at s=0.5
        r1 = C0 * (np.hypot(1, 0) + 0.0)   # straight part to full chroma
        def arm(h0, h1):
            hh = np.deg2rad(np.linspace(h0, h1, 50)); r = np.r_[np.linspace(0, C0, 25), np.full(25, C0)]
            xy = np.stack([r * np.cos(hh), r * np.sin(hh)], 1)
            return np.sum(np.hypot(*np.diff(xy, axis=0).T))
        human = (arm(235, 305) + arm(95, 29)) / J
    else:
        human = float("nan")
    return animal, human


# ------------------------------------------------------------- strip path --
def monochromatic(species, wl):
    """Display RGB (unscaled, linear) for equal-energy monochromatic light."""
    wg = np.arange(340.0, 781.0, 1.0)
    S = cone_sens(wg, SPECIES[species])
    white = (S * d65(wg)).sum(axis=1) / d65(wg).sum()   # catch of mean D65 energy
    q = cone_sens(wl, SPECIES[species]) / white[:, None]
    return (A_ASSIGN @ q).T @ LMS2RGB.T


def human_monochromatic(wl):
    wg = np.arange(340.0, 781.0, 1.0)
    white = (human_lms(wg) * d65(wg)[:, None]).sum(0) / d65(wg).sum()
    return (human_lms(wl) / white) @ LMS2RGB.T


def neutral_point(species):
    """Wavelength between the two lmax where the white-normalised catches match."""
    sp = SPECIES[species]
    wl = np.arange(sp["s"], sp["l"], 0.5)
    q = monochromatic_catches(species, wl)
    i = np.argmin(np.abs(q[0] - q[1]))
    return float(wl[i])


def monochromatic_catches(species, wl):
    wg = np.arange(340.0, 781.0, 1.0)
    S = cone_sens(wg, SPECIES[species])
    white = (S * d65(wg)).sum(axis=1) / d65(wg).sum()
    return cone_sens(wl, SPECIES[species]) / white[:, None]


def strip_image(rgb_lin, height=40):
    rgb = srgb_encode(rgb_lin / max(rgb_lin.max(), 1e-9))
    return np.repeat(rgb[None, :, :], height, axis=0)


# --------------------------------------------------------------- analysis --
def project_on_human(species):
    """Least-squares expansion of each animal cone onto human L, M, S.
    Returns (coeffs (2,3), residual-variance fraction (2,))."""
    wl = np.arange(390.0, 781.0, 1.0)
    F = human_lms(wl)                                # (N, 3)
    S = cone_sens(wl, SPECIES[species])              # (2, N)
    c, *_ = np.linalg.lstsq(F, S.T, rcond=None)      # (3, 2)
    res = S.T - F @ c
    return c.T, (res ** 2).sum(0) / (S.T ** 2).sum(0)


# ------------------------------------------------------------------- demo --
def demo_scene(h=420, w=640, seed=3):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    lin = np.zeros((h, w, 3))
    horizon = int(h * 0.38)
    t = np.clip(yy / horizon, 0, 1)[..., None]
    sky = srgb_decode(np.array([0.30, 0.55, 0.95]))
    haze = srgb_decode(np.array([0.80, 0.88, 0.97]))
    lin[:] = sky * (1 - t) + haze * t

    def smooth(scale):
        n = rng.random((h // scale + 2, w // scale + 2))
        from PIL import Image
        im = Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        return np.asarray(im, float) / 255

    grass = srgb_decode(np.array([0.28, 0.52, 0.16]))
    tex = 0.55 + 0.9 * smooth(3) * 0.5 + 0.6 * smooth(12) * 0.5
    lawn = grass * tex[..., None]
    lin = np.where((yy >= horizon)[..., None], lawn, lin)

    balls = [("red", (0.88, 0.08, 0.06)), ("orange", (0.97, 0.45, 0.04)),
             ("yellow", (0.96, 0.84, 0.08)), ("blue", (0.08, 0.20, 0.85)),
             ("pink", (0.95, 0.45, 0.65))]
    r = 46
    for k, (_, col) in enumerate(balls):
        cx = 90 + k * 118
        cy = 300 + (k % 2) * 28
        sh = ((xx - cx - 14) / (r * 1.1)) ** 2 + ((yy - cy - r + 6) / (r * 0.3)) ** 2 < 1
        lin[sh] *= 0.45
        d2 = (xx - cx) ** 2 + (yy - cy) ** 2
        m = d2 < r * r
        nz = np.sqrt(np.clip(1 - d2 / r ** 2, 0, 1))
        nx, ny = (xx - cx) / r, (yy - cy) / r
        shade = 0.35 + 0.75 * np.clip(-0.5 * nx - 0.6 * ny + 0.62 * nz, 0, 1)
        lin[m] = (srgb_decode(np.array(col)) * shade[..., None])[m]
    return np.clip(srgb_encode(lin), 0, 1)


def sheet_palette(species, mode, nx=300, ny=110):
    """The animal's 2-D colour space drawn in human colours.
    x: chromatic coordinate c = ln(S/L) (short-dominant to the right);
    y: luminance (cube-root spaced, white at top)."""
    lo, hi = c_range(species)
    c = np.linspace(lo, hi, nx)[None, :]
    Y = (np.linspace(0.03, 1.0, ny) ** 3)[::-1][:, None]
    eps = 0.02
    qL = np.broadcast_to(Y, (ny, nx))
    qS = np.clip((qL + eps) * np.exp(c) - eps, 0, None)
    if mode == "plane":
        lms = qS[..., None] * A_ASSIGN[:, 0] + qL[..., None] * A_ASSIGN[:, 1]
        return srgb_encode(lms @ LMS2RGB.T)
    return rainbow_map(qS, qL, species, mode)[0]


def demo_swatches():
    """Hue wheel (saturated / dark / pastel) + grey ramp, 12 columns."""
    import colorsys
    rows = []
    for sat, val in ((1.0, 1.0), (1.0, 0.55), (0.45, 1.0)):
        rows.append([colorsys.hsv_to_rgb(k / 12, sat, val) for k in range(12)])
    rows.append([(g, g, g) for g in np.linspace(0.04, 1.0, 12) ** (1 / 1.0)])
    tile = 50
    img = np.array(rows)                              # (4, 12, 3)
    return np.repeat(np.repeat(img, tile, axis=0), tile, axis=1)


def _save_palettes(species, modes, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    lo, hi = c_range(species)
    fig, axs = plt.subplots(len(modes), 1, figsize=(7.2, 1.9 * len(modes) + 0.5), dpi=160,
                            sharex=True)
    for ax, m in zip(np.atleast_1d(axs), modes):
        ax.imshow(sheet_palette(species, m), extent=[lo, hi, 0, 1], aspect="auto")
        ax.axvline(0, color="w", lw=0.6, ls=":")
        ax.set_yticks([])
        a, h = jnd_budget(species, m)
        extra = "" if m == "plane" else f"  | sheet {h:.0f} JND vs animal {a:.0f}"
        ax.set_ylabel(f"{m}{extra}", rotation=0, ha="right", va="center", fontsize=7)
    np.atleast_1d(axs)[-1].set_xlabel(
        f"{species}: chromatic coordinate ln(S/L); dotted = neutral point; 1 JND ≈ {e_chrom():.2f}; "
        "y = luminance", fontsize=7)
    fig.tight_layout()
    fig.savefig(path)


# -------------------------------------------------------------------- CLI --
def _save_strips(names, path, modes=("plane",)):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    wl = np.arange(340.0, 721.0, 1.0)
    rows = [("human (trichromat)", strip_image(human_monochromatic(wl)), None)]
    for n in names:
        for m in modes:
            uv = SPECIES[n].get("uv")
            lab = n + (" (UV->blue)" if uv and m == "plane" else "") + ("" if m == "plane" else f" · {m}")
            if m == "plane":
                im = strip_image(monochromatic(n, wl))
            else:
                q = monochromatic_catches(n, wl)
                rgb, _ = rainbow_map(q[0], q[1], n, m, Y=q[1] / q[1].max())
                im = np.repeat(rgb[None], 40, axis=0)
            rows.append((lab, im, None if uv else (neutral_point(n) if m == "plane" else None)))
    fig, axs = plt.subplots(len(rows), 1, figsize=(7.2, 0.9 * len(rows) + 0.6),
                            dpi=160, sharex=True)
    for ax, (n, im, npt) in zip(np.atleast_1d(axs), rows):
        ax.imshow(im, extent=[wl[0], wl[-1], 0, 1], aspect="auto")
        ax.set_yticks([])
        ttl = n if npt is None else f"{n}  (neutral ≈ {npt:.0f} nm)"
        ax.set_ylabel(ttl, rotation=0, ha="right", va="center", fontsize=8)
        if npt is not None:
            ax.plot([npt], [0.04], marker="^", color="w", mec="k", ms=5)
    np.atleast_1d(axs)[-1].set_xlabel("wavelength (nm), equal-energy monochromatic light")
    fig.tight_layout()
    fig.savefig(path)
    return fig


def _save_images(path_in, names, out, modes=("plane",)):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    if path_in is None:
        img = demo_scene()
    elif path_in == "swatches":
        img = demo_swatches()
    else:
        img = np.asarray(Image.open(path_in).convert("RGB"), float) / 255
    panels = [("human", img)]
    for n in names:
        for m in modes:
            o, clip = render(img, n, mode=m, return_stats=True)
            sp = SPECIES[n]
            panels.append((f"{n} · {m}  ({sp['s']}/{sp['l']} nm, {100*clip:.1f}% clipped)", o))
    cols = 2 if len(panels) > 2 else len(panels)
    rows = int(np.ceil(len(panels) / cols))
    fig, axs = plt.subplots(rows, cols, figsize=(3.6 * cols, 3.0 * rows), dpi=160)
    for ax in np.atleast_1d(axs).ravel():
        ax.axis("off")
    for ax, (t, im) in zip(np.atleast_1d(axs).ravel(), panels):
        ax.imshow(im)
        ax.set_title(t, fontsize=8)
    fig.tight_layout()
    fig.savefig(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", nargs="?")
    ap.add_argument("-s", "--species", nargs="+", default=["dog"], choices=SPECIES)
    ap.add_argument("-o", "--out", default="out.png")
    ap.add_argument("-m", "--modes", nargs="+", default=["plane"], choices=MODES,
                    help="plane = natural blue-yellow; boomerang / cylinder = rainbow sheets")
    ap.add_argument("--strips", action="store_true", help="spectrum strips")
    ap.add_argument("--demo", nargs="?", const="scene", choices=["scene", "swatches"],
                    help="synthetic test image: toy-on-lawn scene or hue-wheel swatches")
    ap.add_argument("--palette", action="store_true",
                    help="draw the animal's 2-D colour space for each mode")
    a = ap.parse_args()
    if a.palette:
        _save_palettes(a.species[0], a.modes, a.out)
    elif a.strips:
        _save_strips(a.species, a.out, a.modes)
    else:
        if not a.demo and a.image is None:
            ap.error("give an image or --demo")
        src = a.image if not a.demo else (None if a.demo == "scene" else "swatches")
        _save_images(src, a.species, a.out, a.modes)


if __name__ == "__main__":
    main()
