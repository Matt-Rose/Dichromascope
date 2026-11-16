# Rods

Everything in the [model](model.md) up to here concerns cones. Cones are the right story in daylight, when rods are saturated or swamped, but they are only half of it in dim light. This document covers what rods add, what Dichromascope models (step A, rods in the brightness channel) and what it deliberately does not model (step B, rods as a third colour dimension).

## Three regimes

Human vision is conventionally divided into photopic (cones), mesopic (rods and cones), and scotopic (rods only) ranges. The mesopic range runs from roughly 0.01 to 10 cd/m² (Schwartz 2009). The boundaries differ between species and are part of what the parameters below try to capture.

| Regime | Receptors | Colour dimensions possible | What Dichromascope shows |
|---|---|---|---|
| Daylight | Two cone classes (rods saturated) | 1 chromatic + brightness | Full colour sheet |
| Dusk | Two cone classes + rods | Up to 2 chromatic + brightness | Fading colour; brightness increasingly from rods |
| Night | Rods only | Brightness only | Grey, with grain |

## Step A: rods in the brightness channel

### Rod catch

Rod catches are computed like cone catches: a Govardovskii A1 template at the rod peak wavelength, integrated against the reconstructed spectrum under D65 and normalised to white. Rod peaks:
- **Dog:** about 508 nm (Jacobs et al. 1993).
- **Cat:** 501 nm, from dark-adapted ganglion-cell recordings (Guenther & Zrenner 1993).
- **Horse:** not measured. Mammalian rhodopsin varies little, so about 500 nm is used.

### Rod noise and saturation

Each receptor system gets its own noise as a function of absolute luminance Y (the luminance of the surface, in cd/m²):

- Cones: e_C(Y) = ω_Y · √(1 + Y₀/Y), as in the [model](model.md#4-discrimination-the-receptor-noise-metric).
- Rods: e_R(Y) = k_R · ω_Y · √(1 + Y₀ᴿ/Y) · (1 + (Y/Y_sat)²).

The three rod parameters are:

- **Y₀ᴿ = Y₀ / G_R**, the rod photon-noise knee. G_R is how much more sensitive rods are than cones. Human rods are roughly 1000× more sensitive than cones at absolute threshold. Kang et al. (2009) found cats about 0.74 log units (5×) more sensitive than humans in matched dim-light experiments, so the cat gets G_R = 5000. Dog and horse use the human value.
- **k_R**, how much coarser the rod system's Weber fraction is than the cones'. Human rod increment thresholds are noisier and depart from Weber's law in ways the cones do not (Sharpe et al. 1989, 1992). k_R = 3 is an assumption.
- **Y_sat ≈ 100 cd/m²**, rod saturation. Rods' increment thresholds rise faster than Weber's law once even a small fraction of rhodopsin is bleached (Aguilar & Stiles 1954). The value is an order-of-magnitude human figure.

### Pooling

Rod and cone brightness signals are combined by inverse-variance weighting, the statistically optimal pooling of two independent noisy estimates:

  1/e_Y² = 1/e_C² + 1/e_R².

This sets the brightness JND density at each luminance, and so the brightness axis of the sheet. The brightness coordinate of each pixel is the same weighted combination of log rod and log cone catches, with weights evaluated at the adaptation level (18% of white). The info line reports the rod share when it exceeds 2%.

With the default parameters, rods carry about 40% of brightness at 10 cd/m², about 86% at 1 cd/m², and essentially all of it below 0.1 cd/m². That matches the human mesopic range reasonably well, which is reassuring given that most of the rod parameters are borrowed from humans.

### What you see

- **Purkinje shift.** As rods take over brightness, long-wavelength surfaces darken relative to short-wavelength ones, because rods peak near 500 nm. In the toy scene, the red ball sinks towards the shadows at dusk while the blue ball holds its brightness.
- **Colour fades while brightness persists.** Colour depends on cones only (step A). Below the cone knee (about 10 cd/m²) the chromatic radius shrinks, and below the colour limit (about 0.02 cd/m²) the image is grey. Brightness detail continues on rods well below that.
- **Grain.** Lightness is re-matched to the display range at every light level, standing for light adaptation (Laughlin's principle again), so a dim scene is not simply shown dark. Re-matching alone would hide the fact that the animal distinguishes fewer grey levels in dim light. So each pixel's lightness gets noise with a standard deviation of 0.35 animal JNDs. In daylight (about 22 JNDs) this is below human threshold. At dusk it shows as grain. In starlight (1–2 JNDs) it dominates, which is roughly how dim vision feels.
- **The colour exchange rate is fixed in daylight.** The colour axis is not re-matched at each light level, because that would stretch the shrinking colour range back to full saturation. Colour is matched at 3000 cd/m², and dimmer light then shows up as genuine desaturation.

## Step B: rods as a third colour dimension (not implemented)

With three receptor classes active, a dusk dichromat is in principle a trichromat. It could compare rods against cones as well as cones against each other.

There is precedent in humans. Red–green dichromats become partially trichromatic for large fields in dim light, which is attributed to rods feeding the red–green channel they otherwise underuse (Smith & Pokorny 1977). Normal trichromats show rod intrusion as hue shifts and broken colour matches, not as a new hue, because their three post-receptoral channels are already in use.

Whether cats, dogs or horses have a spare post-receptoral channel that rods could use is unknown. Two observations bear on it. Horses lose colour discrimination at the same light level as humans (Roth et al. 2008), so rods do not extend their colour vision below the cone limit, though that experiment could not detect an *extra* dimension at higher light levels. And cats need very large stimuli to discriminate colour at all (Loop & Bruce 1978), which resembles the human large-field effect. That resemblance is suggestive, nothing more.

If implemented, step B would make the animal's colour space change dimension with light: one-dimensional at night, three-dimensional at dusk, two-dimensional in daylight. The dusk volume would need a three-dimensional embedding in human colour space. It is left as a possible clearly labelled speculative mode ([issue #1](https://github.com/Matt-Rose/Dichromascope/issues/1)).

## Limitations

- **Most rod parameters are graded D,** borrowed from humans. The cat's extra sensitivity is the only species-specific number with direct support.
- **The camera hides real light levels.** It auto-exposes, so the Light dial, not the camera, sets the light level, and the photo's own exposure is ignored.
- **Spatial pooling is not simulated.** Rods trade spatial resolution for sensitivity, so night vision is blurrier as well as noisier, and the grain is purely temporal and per-pixel.
- **The Lab page is still cone-only.**
