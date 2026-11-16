# Parameters

Each species needs seven numbers. This document explains how they were found, how much to trust them, and what each one controls. The values themselves, with sources, are in [`species.json`](../species.json). Per-species evidence is on the [species pages](species/).

| Parameter | Symbol | Controls |
|---|---|---|
| Short-cone peak wavelength | λ_S | Cone spectra, neutral point, chromatic range |
| Long-cone peak wavelength | λ_L | As above |
| Lens cutoff | — | Only sensitivity below ~400 nm (negligible for photos) |
| Short-cone share of cones | η_S | Chromatic noise e_c = ω·√(1/η_S + 1/η_L); with few S cones, colour is coarse |
| Chromatic Weber fraction | ω | Chromatic JND count; shape of the colour space |
| Luminance Weber fraction | ω_Y | Luminance JND count; shape of the colour space |
| Colour-vision light limit | Y_fail | Calibrates the photon-noise knee Y₀ and the Light dial |

## Where the evidence comes from

There are three kinds of source.

1. **Method papers.** The Lund vision group (Kelber, Vorobyev, Osorio, Olsson, Roth and colleagues) fit behavioural thresholds with the same receptor-noise model Dichromascope uses. Kelber, Vorobyev & Osorio (2003) review the approach, and Olsson, Lind & Kelber (2015) is the template for separating the Weber and photon-noise regimes. Two cautions come from this literature. Behavioural thresholds can sit above the receptor-noise prediction: cichlid fish matched the model only with Weber fractions above the usual 5% (Escobar-Camacho et al. 2019). And thresholds vary across colour space and between hue and saturation (Green et al. 2022).
2. **Species behaviour.** Training studies in which animals choose between stimuli that differ in brightness or colour. These give Weber fractions, neutral points and absolute light limits. They are few, use few animals, and depend on the task.
3. **Retinal anatomy and physiology.** Cone peak wavelengths come from electroretinography, ganglion-cell recordings and pigment genetics. Cone proportions come from opsin-specific labelling of retinal wholemounts. These are the most reliable numbers.

## Grading

| Grade | Meaning |
|---|---|
| A | Measured in this species, several animals, modern method, consistent across studies |
| B | Measured in this species, but few animals, older method, indirect, or a range |
| C | Derived from measured quantities via the model |
| D | Assumed or borrowed from another species; no direct evidence found |

## The ratio principle

Behavioural thresholds depend on stimulus size, duration, criterion, training and motivation. Comparing a dog's Weber fraction from one task with a human's from another mixes all of that in. The robust quantity is the **ratio** between species measured in the same apparatus. For example, Roth, Balkenius & Kelber (2008) tested humans in their horse apparatus and found the same colour-vision light limit. For brightness, the same lab's method gives Weber fractions of 0.22–0.27 for dogs (Griebel and colleagues 2004), 0.42–0.45 for horses (Geisbauer et al. 2004) and 0.35 for manatees (Griebel & Schmid 1997), against about 0.14 for humans in comparable tasks.

Range matching, the default [exchange rate](exchange-rate.md), uses only the animal's own JND counts, so it needs no human reference at all. The 1:1 modes do need one. There the human JND is set by J in OKLab, and that value is a convention, not a measurement.

## Choices made

- **Luminance Weber fractions are behavioural.** They are large: 0.25 for the dog, 0.44 for the horse. The cat's is borrowed from the dog because no cat brightness Weber fraction was found. Replacing the previous placeholder of 0.05 with these values is the largest change, and it makes the colour spaces far less elongated (next section).
- **Chromatic Weber fractions are a literature default.** No behavioural colour-discrimination threshold suitable for fitting the receptor-noise model was found for any of the three species. They use ω = 0.05 per cone class, the conventional value, graded D. The fish result above suggests behavioural values may be higher. Note the inconsistency: a behavioural value for luminance alongside a receptor-level value for colour. If the same post-receptoral losses apply to both channels, colour is overstated relative to brightness.
- **Short-cone shares** use central-retina values where available, because the viewer simulates looking at the scene directly.

## Light-level calibration

The Light dial is labelled with the luminance of a white surface in cd/m². It gets real units from one behavioural number: the dimmest light at which the animal can still tell colours apart (Y_fail).

In the noise model, the number of chromatic JNDs available at white luminance Y is

  T_c(Y) = T_c / √(1 + Y₀/Y),

where T_c is the count in bright light. Colour discrimination fails when T_c(Y) falls to 1, which happens at Y_fail = Y₀/(T_c² − 1). Inverting,

  **Y₀ = (T_c² − 1) · Y_fail.**

For all three species this gives Y₀ ≈ 9–12 cd/m², from a colour limit of 0.02 cd/m² and T_c ≈ 22–24. That is independently close to the 10 cd/m² at which Olsson, Lind & Kelber (2015) saw chickens' colour thresholds leave Weber's law. That agreement is a useful cross-check, though different species and stimuli are involved.

Caveats:
- The behavioural colour limit was measured with particular stimulus pairs, not the full gamut, so T_c for those stimuli is smaller than the full-gamut T_c. This overestimates Y₀, perhaps by several-fold.
- Below a few cd/m², rods start to contribute and the two-cone model stops being the whole story ([issue #1](https://github.com/Matt-Rose/Dichromascope/issues/1)).
- For orientation, a white surface is roughly 10⁴ cd/m² in sun, 10³ under overcast sky, 10² indoors, 1–10 at dusk, and 0.01–0.1 under a full moon. These are order-of-magnitude figures.

## Consequences for the colour space

Using the derived counts in bright light, over the white-to-0.2% luminance range used by the viewer:

| Species | Neutral point (model / behaviour) | Chromatic JNDs T_c | Luminance JNDs T_Y | Shape T_c : T_Y |
|---|---|---|---|---|
| Cat | 500 nm / — | 22 | 25 | 0.9 |
| Dog | 486 nm / ~480 nm | 22 | 25 | 0.9 |
| Horse | 480 nm / ~480 nm | 24 | 14 | 1.7 |
| *Old placeholder (cat)* | | *18* | *124* | *0.14* |

With the placeholder, the colour space was about seven times longer in brightness than in colour, so colour looked weak. With behavioural brightness thresholds, the dog's and cat's spaces are nearly square. The horse's space is wider in colour than in brightness, because horses discriminate brightness unusually poorly.

## What would change the picture

In order of impact:

1. **A behavioural chromatic threshold for any of the three species,** fitted with the receptor-noise model. This sets T_c directly, and through it the shape of the space and the light calibration.
2. **A cat brightness Weber fraction.** The cat's luminance axis is currently borrowed from the dog.
3. **Colour-vision light limits for cat and dog,** which would replace the borrowed horse value in the light calibration.
4. **Task-matched human thresholds** for the brightness and colour tasks above, which would make the 1:1 modes physiological instead of conventional.
5. **Rod contribution in mesopic light** ([issue #1](https://github.com/Matt-Rose/Dichromascope/issues/1)).
