# Exchange rate

The [model](model.md) gives the animal's colour space as a two-dimensional sheet with a known metric: so many chromatic JNDs by so many luminance JNDs, with a shape that changes with light level. To show it to a human, every animal discrimination has to become a human one. The central question is the exchange rate: **how big, in human JNDs, should one animal JND look?**

Dichromascope offers three answers. Range matching is the default, and the "Rate" button cycles through the other two.

## Why the exchange rate cannot be read off physiology

JNDs are thresholds measured within a species. Nothing in a cat's receptor noise says what its just-noticeable step feels like compared with ours. Asserting that one cat JND equals one human JND is a claim about the size of subjective experience, not about physiology. There is also a practical problem: animal and human thresholds are measured with different tasks, stimuli and criteria, so even the numbers being equated are not commensurate. That is why the [parameters](parameters.md#the-ratio-principle) are taken as animal-to-human ratios from comparable tasks wherever possible.

A structuralist reading of qualia makes the same point more sharply. If a colour experience is defined only by its relations to other colour experiences (its position in a quality space; Clark 1993), then the animal's space is fixed only up to similarity. Its overall scale has no meaning, and choosing one is a convention.

## Range matching (default)

The convention Dichromascope adopts comes from Laughlin (1981). Studying a fly's large monopolar cells, Laughlin showed that their contrast-response curve closely matched the cumulative distribution of contrasts in natural scenes. That is exactly the curve that maximises information transmitted through a neuron with a bounded output range: it uses every output level equally often (histogram equalisation).

The principle applied here is that **each system uses its whole output range.** So the animal's full chromatic range is mapped onto the largest hue arc the display can show, and the animal's full luminance range onto the display's full lightness range. The two channels are matched separately because they are separate neural channels with separate bounded outputs. As a result the overall shape of the animal's space is preserved only up to a different stretch in each direction, but each channel's internal spacing is preserved.

The info line in the viewer reports the resulting rates, such as "1 cat colour JND → 1.0 of yours".

### Weber's law already is Laughlin

The receptor-noise metric is built on Weber's law: thresholds proportional to intensity, so JNDs are equally spaced in log intensity. Laughlin's prescription is a response equal to the cumulative distribution of inputs. For a scale-invariant input distribution, p(Y) ∝ 1/Y (a good first approximation for natural luminances), the cumulative distribution is ln Y. **So Weber's law is the efficient code for a scale-invariant world, and equally spaced JNDs are already histogram-equalised for the animal's long-run environment.** More generally, an efficient population code has Fisher information whose square root is proportional to the prior density of stimuli (Ganguli & Simoncelli 2014), so JND density tracks how often stimuli occur.

This is why range matching does not conflict with respecting the animal's JNDs. With adaptation set to 0, the map is a uniform rescaling of the animal's JND metric in each channel. That is the efficient code for the animal's average world, displayed on the human's output range.

## Adaptation

The **Adaptation** dial blends in the statistics of the current scene, over a time constant of about 1 s.

- **Lightness.** The lightness curve becomes a mixture of the long-run (Weber) code and the cumulative distribution of the scene's luminances over the last second or so. Tones that are common in the frame get more display range, and rare ones are compressed.
- **Colour.** The animal's neutral point shifts towards the scene's mean chromaticity, a von Kries or grey-world shift. The Hue dial's tick shows where neutral currently sits.

### The noise cap

Equalisation must not create discriminations the animal cannot make. Local gain is therefore capped: one animal JND may grow to at most one human JND. If the long-run rate already exceeds that, it may grow no further. This is contrast-limited histogram equalisation (Pizer et al. 1987), but with the clip limit set by receptor noise rather than by taste.

In practice this means a channel can adapt its gain only if its long-run rate is below 1. Under the old placeholder parameters, lightness had a long-run rate of about 0.25 and could adapt by up to 4×, while colour (rate about 1.3) could not adapt its gain at all. With the [measured parameters](parameters.md), the animals have few luminance JNDs: about 21 for cat and dog at 1000 cd/m², and about 12 for the horse. Range matching therefore magnifies both channels (cat: colour 1.2, lightness 1.7), the cap allows no further gain in either, and adaptation acts only through the neutral-point shift. That is a direct consequence of how coarse these animals' brightness discrimination is.

Your phone already auto-exposes and white-balances before Dichromascope sees the frame. That is a similar adaptation, done in human cone space. So the effect is smaller on live camera than on a photo or the toy scene.

## Pinned 1:1

The alternative is to assert that one animal JND looks like one human JND. The Rate button offers this at two human JND sizes, J = 0.02 and J = 0.01 in OKLab units, because the answer depends heavily on J:

- **J = 0.02** is a conventional "noticeable" difference. **J = 0.01** is closer to threshold (about ΔE00 = 1).
- **Lightness becomes a fixed-gain window.** If the animal has more luminance JNDs than fit on the display, the window covers only part of the animal's range. Shadows or highlights then crush, and the adaptation dial slides the window like auto-exposure. If they fit, the full range is shown with spare room.
- **Colour sets its own chroma.** Arc length round the hue circle equals the animal's chromatic JND count × J. That is usually paler than range matching, and much paler at J = 0.01.

1:1 makes a stronger claim than range matching, and its appearance depends on a number (J) that is itself a convention. It is offered to show how much the picture depends on that choice.

## The placement in human colour space

Several things are fixed by an optimisation rather than by a dial:

- the hue span the animal's colours occupy;
- the white lightness and black lightness;
- the peak chroma.

The optimiser maximises the geometric mean of chromatic range and lightness range, both measured in human JNDs, subject to at most 10% of the sheet falling outside the sRGB gamut.

Some consequences:

- **Wider hue spans are cheap.** The arc length round each ring is fixed by the JND count, so a wider span means a smaller radius, which fits the gamut more easily. Spans are capped at 330° so that the two ends of the animal's axis are never painted in adjacent hues. That would be a topological lie: the animal's most different colours would look nearly the same to us.
- **Black may be lifted.** Deep shadows are traded for chroma when that increases the objective. A different weighting of colour against lightness would choose differently, and the weighting is a convention.
- **Hue rotation is the remaining freedom.** Nothing in physiology says whether the animal's long-wavelength end should look red to us or green. The default paints it red, so that spectral order matches ours, and the Hue dial rotates it.
