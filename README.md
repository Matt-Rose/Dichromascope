# Dichromascope

Trying to induce physiologically compatible qualia from dichromats in trichromats.

See the world through the eyes of a dichromat (a cat, dog or horse). This runs live from your camera, and you can also try photos or video clips.

**Live:** https://matt-rose.github.io/Dichromascope/ (allow camera access; on a phone use the rear camera)

## What it does

A dichromat has two cone classes, so its colour space is two-dimensional: one chromatic coordinate `c = ln(S/L)` plus luminance. Any rendering for a human trichromat is therefore a 2-D sheet embedded in our 3-D colour space. The page offers three such sheets:

- **Natural.** Cone catches are drawn on the blue–yellow plane anchored at 475/575 nm, the wavelengths that human dichromats match to normal vision. This is the physiologically literal view.
- **Bell.** The animal's receptor-noise metric is embedded isometrically in OKLab as a surface of revolution. Hue angle is proportional to `c`, and the chroma and lightness profiles are solved from the metric. In bright light the sheet is a cylinder. Where photon noise dominates it becomes a cone with its apex at black. The transition carries positive Gaussian curvature.
- **Grey-anchored.** This uses the same profile, but each luminance circle is shifted so the neutral point stays grey. You see half the hue range (inscribed angle theorem), and the luminance direction is no longer exactly isometric.

Stretch maps show the singular values of the Jacobian from animal JNDs to human JNDs, so you can see where a mapping invents or loses discriminability.

## Model

- **Cones:** Govardovskii et al. (2000) A1 templates, with a crude lens cutoff.
- **Spectral upsampling:** Mallett & Yuksel (2019) basis under D65. Photos therefore contain no UV.
- **Discrimination:** receptor-noise-limited model (Vorobyev & Osorio 1998), with photon noise `e(Y) = ω·√(1 + Y₀/Y)`.
- **Human side:** OKLab, with 1 JND taken as 0.02.

The Weber fractions and cone ratios are adjustable assumptions, not measurements for these species. Rods are ignored.

## Files

- `index.html` is the whole app: no build step, no dependencies beyond Google Fonts. Camera access needs https or `localhost`, so run `python3 -m http.server` and open `http://localhost:8000` to use it locally.
- `python/dichromat_sim.py` is the offline batch version (`photo.jpg -s cat dog -m plane boomerang cylinder`). It needs `numpy`, `matplotlib`, `Pillow` and `colour-science`.
