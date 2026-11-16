# Dichromascope

Trying to induce physiologically compatible qualia from dichromats in trichromats.

See the world through the eyes of a dichromat (a cat, dog or horse). This runs live from your camera, and you can also try photos or video clips.

**Live:** https://dichromascope.rose.org.uk/ (allow camera access; on a phone use the rear camera)

## The viewer (`index.html`)

The viewer has four ring dials over a full-screen camera feed. Press and hold the image to see the original.

- **Species** (tap to cycle): cat, dog or horse. Sets the cone λmax values and the noise model.
- **Light**: the luminance of a white surface in cd/m², from moonlight to sun. It is calibrated from each species' colour-vision light limit (see [Parameters](docs/parameters.md#light-level-calibration)).
- **Adaptation** (world ↔ scene): how far the code adapts to the current scene, with a time constant of about 1 s.
- **Hue**: rotates where the animal's colour arc sits on the human hue wheel. The tick marks the animal's neutral point. This is the one choice physiology leaves free.

**Natural** switches to the literal blue–yellow rendering.

### Why so few dials

- **Exchange rate (Laughlin 1981).** Each system uses its whole output range. So the animal's full chromatic range is mapped onto the largest hue arc that fits the display gamut, and its full luminance range onto the display's lightness range. This replaces an arbitrary "1 animal JND = 0.02 OKLab" with a principled exchange rate, shown live in the info line.
- **Weber's law already is Laughlin.** The cumulative distribution of a scale-invariant prior p(Y) ∝ 1/Y is ln Y. So with adaptation at 0, the 1:1 JND map is already the efficient code for the animal's long-run world. The adaptation dial blends in the current scene's distribution.
- **Noise-limited gain.** Scene equalisation can't raise local gain above one human JND per animal JND. That is contrast-limited histogram equalisation with the clip limit set by receptor noise. With the current parameters both channels already run above that rate, so adaptation works only by shifting the neutral point; see [Exchange rate](docs/exchange-rate.md#the-noise-cap).
- **Sheet geometry.** Hue span, white lightness and black lightness are chosen by maximising the geometric mean of chromatic and lightness range, in human JNDs, inside the sRGB gamut (10% clipping tolerance).

## Documentation

The [docs](docs/README.md) explain the model, the exchange rate between animal and human discriminations, where every physiological number comes from and how far to trust it:

- [Model](docs/model.md): cone templates, receptor noise, photon noise and the geometry of the animal's colour space
- [Exchange rate](docs/exchange-rate.md): Laughlin, range matching, the 1:1 alternative and adaptation
- [Parameters](docs/parameters.md): evidence, grading, the ratio principle and the light-level calibration
- Species: [cat](docs/species/cat.md), [dog](docs/species/dog.md), [horse](docs/species/horse.md)
- [References](docs/references.md)

The values are in [`species.json`](species.json); run `python3 tools/sync_species.py` after editing it.

## The Lab (`lab.html`)

The full slider version for exploring the geometry. It has three mappings:

- **Natural.** Cone catches drawn on the blue–yellow plane anchored at 475/575 nm, the wavelengths that human dichromats match to normal vision.
- **Bell.** The receptor-noise metric embedded isometrically in OKLab as a surface of revolution. Hue angle is proportional to c = ln(S/L). In bright light the sheet is a cylinder; where photon noise dominates it becomes a cone with its apex at black, and the transition between them carries positive Gaussian curvature.
- **Grey-anchored.** The same profile, shifted so the neutral point stays grey.

The Lab also shows stretch maps (the singular values of the Jacobian from animal JNDs to human JNDs) and a 3-D view of the sheet.

## Model

- **Cones:** Govardovskii et al. (2000) A1 templates, with a crude lens cutoff.
- **Spectral upsampling:** Mallett & Yuksel (2019) basis under D65. Photos therefore contain no UV.
- **Discrimination:** receptor-noise-limited model (Vorobyev & Osorio 1998), with photon noise `e(Y) = ω·√(1 + Y₀/Y)`.
- **Human side:** OKLab, with 1 JND taken as 0.02.

Parameters come from the literature with confidence grades; the chromatic Weber fractions and most cat values are still assumptions (#3). The adaptation time constant is a rough guess. Rods are ignored (#1).

## Files

- `index.html` is the viewer and `lab.html` is the Lab. There's no build step and no dependencies beyond Google Fonts. Camera access needs https or `localhost`, so run `python3 -m http.server` and open `http://localhost:8000` to use it locally.
- `python/dichromat_sim.py` is the offline batch version (`photo.jpg -s cat dog -m plane boomerang cylinder`). It needs `numpy`, `matplotlib`, `Pillow` and `colour-science`.
