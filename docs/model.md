# Model

This document describes the computation from camera pixel to displayed colour, and the geometry that results. The choice of how to place the animal's colour space inside ours is covered separately in [Exchange rate](exchange-rate.md).

## 1. From pixels to spectra

A camera records three numbers per pixel, not a spectrum. To compute what an animal's cones would absorb, Dichromascope reconstructs a plausible reflectance spectrum for each pixel using the basis of Mallett & Yuksel (2019). Their method writes any linear-sRGB colour as a weighted sum of three smooth, non-negative reflectance curves, chosen so that the result is physically valid (between 0 and 1 at every wavelength) and reproduces the original colour exactly under D65 light.

The reconstruction is linear in linear-sRGB, so the whole pixel-to-cone step reduces to a fixed 2×3 matrix per species. That is what makes the live camera fast.

**Limitations.** Many spectra share the same RGB (metamers), and the reconstruction picks a smooth one. Real surfaces with sharp spectral features, such as fluorescent dyes or some flowers, can look different to the animal than the reconstruction implies. Photos also contain no ultraviolet, so species with UV-sensitive cones (mice, many birds) cannot be simulated from ordinary images. The illuminant is assumed to be D65.

## 2. Cone sensitivities

Each cone class is modelled with the visual-pigment template of Govardovskii et al. (2000) for A1 (vitamin A1) pigments: an alpha band whose shape scales with the peak wavelength λmax, plus a smaller beta band in the near-UV. The template is multiplied by a simple logistic lens cutoff, converted from quantal to energy units, and integrated against the reconstructed spectrum under D65.

Catches are normalised (von Kries) so that a white surface gives a catch of 1 in both classes. With this normalisation, white is the animal's neutral point by construction.

The peak wavelengths for each species come from electroretinography, microspectrophotometry or behaviour; see the [species pages](species/). The template ignores pre-receptoral filtering beyond the lens edge, self-screening and any macular pigment. These mostly shift the short-wavelength cone and would move the neutral point by a few nanometres.

**Validation.** The model's neutral points (the wavelength at which the two cone catches are equal relative to white) are 480 nm for the horse and 486 nm for the dog. Behavioural neutral points are about 480 nm for both (Geisbauer et al. 2004; Neitz, Geist & Jacobs 1989).

## 3. The animal's colour space

A dichromat's response to a surface is two catches, (q_S, q_L). Two coordinates describe it:

- **Chromatic:** c = ln(q_S / q_L). Zero is the neutral point. Negative values are long-wavelength dominated (what we call red, orange, yellow, green); positive values are short-wavelength dominated (blue, violet).
- **Luminance:** u = ln Y, with Y = q_L. The long-wavelength cone dominates luminance in these species. This is a simplification: the true achromatic channel may pool both cone classes and rods.

Logarithms appear because receptor responses are compared as ratios (Weber's law); see below.

## 4. Discrimination: the receptor-noise metric

How far apart two colours are, in units of "just noticeable", is given by the receptor-noise-limited (RNL) model of Vorobyev & Osorio (1998). Its premise is that colour discrimination is limited by noise in the photoreceptors. For a dichromat the chromatic distance between two stimuli is

  ΔS = |Δ ln(q_S/q_L)| / e_c, with e_c² = e_S² + e_L².

Here e_i is the noise of receptor class i, expressed as a Weber fraction. Noise in a class falls as more receptors of that class are pooled, so e_i = ω / √(η_i), where η_i is the class's share of cones and ω is the Weber fraction of a single class. A dichromat with few short-wavelength cones therefore has a noisier chromatic channel. This is the main reason dichromats' colour discrimination is coarser than their cone spectra alone would suggest.

The luminance channel is treated the same way, with its own behavioural Weber fraction ω_Y.

**Photon noise at low light.** Weber's law (constant ω) holds only while photoreceptor noise is dominated by intrinsic, intensity-proportional sources. In dim light, photon shot noise dominates and relative noise grows as 1/√(photon catch). Dichromascope combines the two regimes as

  e(Y) = ω · √(1 + Y₀/Y),

where Y₀ is the luminance at which the two noise sources are equal. Olsson, Lind & Kelber (2015) found this structure behaviourally in chickens. Thresholds followed Weber's law from bright light down to about 10 cd/m² and rose below that as photon noise took over. How Y₀ is calibrated for each species is described in [Parameters](parameters.md#light-level-calibration).

## 5. The metric and its geometry

With u = ln Y, the two channels give the line element

  ds² = (dc² / e_c² + du² / e_Y²) / (1 + Y₀ e^(−u)).

Three regimes follow:

- **Bright light** (Y ≫ Y₀): the conformal factor is constant, so the metric is flat. In (c, u) coordinates the colour space is a flat strip, with a fixed number of chromatic JNDs at every brightness.
- **Dim light** (Y ≪ Y₀): with r = 2√(Y/Y₀) the metric becomes ds² = dr² + r²(e_Y/2e_c)² dc². That is polar coordinates. The colour space is a cone with its apex at black, and chroma becomes an angle. As light falls, the number of distinguishable colours shrinks towards zero.
- **The transition:** the Gaussian curvature is K = e²·(ln e)″, which is positive and concentrated where the regimes meet. Integrated, it equals the cone's opening angle (Gauss–Bonnet). So the full colour space is a flat strip joined smoothly to a cone, shaped like a bell.

This geometry is intrinsic. It is fixed by physiology and owes nothing to how the space is later drawn in human colours. The Lab page draws this bell and its embedding, so you can watch it change with light level.

## 6. Drawing the sheet in human colour space

The human side uses OKLab (Ottosson 2020), a modern approximately perceptually uniform colour space. Distances in OKLab are taken as proportional to human JNDs, with one JND conventionally taken as 0.02. That number matters only in the "1:1" mode; see [Exchange rate](exchange-rate.md#pinned-11).

The viewer places the animal's sheet as a surface of revolution about OKLab's grey axis:

- the animal's chromatic coordinate becomes hue angle;
- the animal's luminance becomes OKLab lightness;
- the radius (chroma) at each lightness follows the number of chromatic JNDs the animal has at that luminance, so it shrinks towards black in dim light, as the cone geometry requires.

A sheet like this can be embedded isometrically in OKLab only if the hue span is wide enough. Otherwise the cone part would need ruffles (negative curvature). The Lab page shows this constraint live.

**Human space is not flat either.** Large colour differences are less than the sum of small ones ("diminishing returns"), and Bujack et al. (2022) argue that perceptual colour space is not even Riemannian at large scales. OKLab is a good local approximation, so the isometry claims here are local claims.

## 7. What the model leaves out

- **Rods as a colour dimension.** Rods now contribute to brightness (see [Rods](rods.md)), but not to colour. A rod–cone colour channel is possible in principle at dusk, but no evidence for one was found in these species.
- **Spatial vision.** Cats need large stimuli to discriminate colour at all: they fail below about 20° (Loop & Bruce 1978). Dogs see about three times less fine detail than humans (Lind et al. 2017). The simulation does not blur the image.
- **Post-receptoral nonlinearity.** Saturation is usually discriminated less well than hue (Danilova & Mollon 2016; Green et al. 2022), which the RNL model does not capture.
- **The animal's adaptation state beyond what is described in [Exchange rate](exchange-rate.md#adaptation).**
