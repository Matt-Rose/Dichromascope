# Dichromascope documentation

Dichromascope shows a scene the way a dichromatic mammal (a cat, dog or horse) might see it, re-expressed in human colour. These documents explain how it does that, where every number comes from, and which numbers are guesses.

Start with **Model** if you want the pipeline, **Exchange rate** if you want to know why the colours look the way they do, and **Parameters** if you want to check the physiology.

| Document | What it covers |
|---|---|
| [Model](model.md) | Cone templates, spectral upsampling, the receptor-noise metric, photon noise, and the geometry of the animal's colour space |
| [Exchange rate](exchange-rate.md) | How animal discriminations are mapped onto human ones: range matching, Laughlin's efficient coding, the 1:1 alternative, adaptation and its noise cap |
| [Rods](rods.md) | Dim light: rods in the brightness channel, the Purkinje shift, grain, and why rods might (or might not) add a colour dimension |
| [Parameters](parameters.md) | How the physiological parameters were found, the grading scheme, the ratio principle, and the light-level calibration |
| [Cat](species/cat.md) · [Dog](species/dog.md) · [Horse](species/horse.md) | Per-species evidence, values chosen, and open questions |
| [References](references.md) | Full bibliography |

The numbers themselves live in [`species.json`](../species.json), with a source and a confidence grade for each one. `tools/sync_species.py` copies them into the two pages.

## The idea in one paragraph

A dichromat has two cone classes, so its colour experience can vary along only two dimensions: a single chromatic axis (roughly "how much more the short-wavelength cone is excited than the long-wavelength cone") and brightness. Humans have three. Any rendering of the animal's view for a human therefore draws a two-dimensional sheet inside our three-dimensional colour space. Physiology fixes the sheet's intrinsic geometry: how many just-noticeable differences (JNDs) the animal has along each axis, and how that changes with light level. Physiology does not fix how the sheet is placed in human colour space. Dichromascope fixes that remaining freedom with one principle from neuroscience (Laughlin's efficient coding) and an optimisation against the display gamut. One genuinely arbitrary choice is left as a dial: which human hues the animal's colours are painted in.

## What is solid and what is not

- **Solid:** cone peak wavelengths for all three species; short-cone proportions for the dog; the horse's colour-vision light limit; the neutral points the model predicts for dog and horse, which agree with behavioural measurements.
- **Reasonable:** brightness Weber fractions for dog and horse (few animals, one lab's method); short-cone proportions for cat and horse (ranges).
- **Assumed:** the chromatic receptor-noise Weber fraction for all three species (a literature default), and everything about the cat's brightness discrimination and colour-vision light limit.

The [parameters document](parameters.md#what-would-change-the-picture) lists what each assumption controls and what a better measurement would change.
