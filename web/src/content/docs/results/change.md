---
title: Change detection results
description: Between 22 October and 3 November 2026, 99.89% of Hưng Yên shows no significant SAR change; the main exception is a new dark-water cluster of about 1.6 km² whose cause is not verified.
sidebar:
  order: 1
---

This page reports what the statistical change detection found between the two same-geometry NISAR acquisitions, **22 Oct 2026 and 3 Nov 2026** (track 148, descending, 20 m). The method (log-ratio test with a Gamma speckle model, |z| > 5 in both HH and HV, minimum patch 0.05 km²) is described in [Change detection method](/methods/change-detection/). Explore it on the [interactive map, change view](/?view=change).

:::caution[Not verified on the ground]
No change patch has been confirmed with optical imagery or field data: clouds covered the area almost continuously during the period. Every interpretation below is a **hypothesis based on SAR physics.**
:::

## Change detection summary: 99.89% unchanged

| Class | Rule | Area (km²) | Share of AOI | Patches |
|---|---|---|---|---|
| 1 No significant change | — | 2,569.03 | 99.895% | — |
| 2 New water / surface flattening | HH and HV both decrease (z < −5) and HH on 3 Nov < −15 dB | **1.579** | 0.061% | 5 |
| 3 HH and HV decrease (other) | both decrease, HH on 3 Nov ≥ −15 dB | 0.381 | 0.015% | 5 |
| 4 HH and HV increase | both increase (z > 5) | 0.583 | 0.023% | 7 |
| 5 HV-only decrease | only HV significant, negative | 0 | 0% | 0 |
| 6 HV-only increase | only HV significant, positive | 0.158 | 0.006% | 2 |

Total analysed area: 2,571.73 km² (6.43 million 20 m cells). Patches smaller than 0.05 km² (125 cells) were reassigned to class 1, so small changes such as individual fields are deliberately not reported. In total **19 patches** passed the test.

![Change classes between 22 Oct and 3 Nov 2026](/figures/common/change_detection.png)

## The new-water cluster near 106.484°E, 20.463°N

The only substantial change in the province is a cluster of dark patches next to a river bend in the south-east of the province, centred near **106.484°E, 20.463°N**.

- **Size:** all 5 class-2 patches (1.58 km² in total) lie within about 3 km of this point; the two largest are 0.71 km² and 0.62 km². Including the adjacent class-3 patches (0.32 km² within the same area), the cluster covers about 1.6–1.9 km² depending on what is counted. It has a roughly rectangular, field-like shape.
- **Backscatter drop** (mean of linear power over all class-2 cells, in dB):

| Date | HH (dB) | HV (dB) |
|---|---|---|
| 22 Oct (descending) | −10.3 | −17.5 |
| 27 Oct (ascending) | −12.0 | −19.9 |
| 3 Nov (descending) | −16.4 | −23.1 |

- **The decrease is gradual:** the intermediate 27 Oct acquisition already lies between the two. Because 27 Oct comes from the opposite (ascending) look direction, this intermediate value is indicative only.
- For comparison, the unchanged part of the province averages about −3 dB in HH and −12.5 dB in HV on every date.

![HH and HV difference 3 Nov − 22 Oct in dB over the whole province; the dark red spot south-east of the centre is the new-water cluster](/figures/common/change_22oct_3nov.png)

The right-hand panel below shows HH backscatter around the cluster on 22 Oct, 27 Oct and 3 Nov (left to right): the field block next to the river bend darkens progressively. The two left panels of this early exploratory figure (a threshold classification and HH − HV, with Vietnamese titles) are superseded by the [land-cover results](/results/landcover/).

![Exploratory SAR analysis; right panel: HH around the new-water cluster on 22 Oct, 27 Oct and 3 Nov](/figures/common/sar_analysis.png)

### Physical interpretation of the new-water cluster (hypothesis)

A simultaneous drop of about 6 dB in **both** HH and HV to values typical of open water (HH below −15 dB) is what L-band SAR shows when a rough surface (crops, stubble, wet soil) becomes a **smooth water surface**: the radar pulse is reflected away from the sensor like a mirror (specular reflection), so little energy comes back in either polarisation.

Plausible causes, consistent with the project theme of water management:
- flooding of a field or a group of fields (e.g. after harvest, or to prepare an aquaculture pond);
- filling of fish/shrimp ponds or an embanked area next to the river;
- a temporary inundation behind a dyke.

**The cause is unknown and unverified.** It has not been checked with optical imagery (clouds), high-resolution imagery or local information.

## Other change patches

| Class | Area (km²) | Longitude | Latitude | HH 22 Oct (dB) | HH 3 Nov (dB) |
|---|---|---|---|---|---|
| 2 New water | 0.713 | 106.4820 | 20.4667 | −11.4 | −16.7 |
| 2 New water | 0.624 | 106.4848 | 20.4610 | −9.7 | −16.3 |
| 4 Increase | 0.127 | 106.0756 | 20.7290 | −10.2 | −5.2 |
| 3 Decrease (other) | 0.118 | 106.4830 | 20.4561 | −8.6 | −13.7 |
| 4 Increase | 0.102 | 106.3051 | 20.5620 | −11.4 | −6.5 |
| 2 New water | 0.092 | 106.4883 | 20.4576 | −9.9 | −15.8 |
| 6 HV-only increase | 0.090 | 106.4685 | 20.3502 | −3.8 | −2.4 |
| 4 Increase | 0.086 | 106.0649 | 20.8508 | −11.5 | −6.0 |
| 3 Decrease (other) | 0.082 | 106.4944 | 20.4641 | −8.4 | −13.2 |
| 4 Increase | 0.082 | 106.1040 | 20.7303 | −12.5 | −6.3 |
| 2 New water | 0.080 | 106.4907 | 20.4697 | −11.6 | −16.1 |
| 4 Increase | 0.072 | 106.1948 | 20.5219 | −8.8 | +6.8 |
| 2 New water | 0.070 | 106.4739 | 20.4834 | −9.2 | −15.6 |
| 6 HV-only increase | 0.067 | 106.4924 | 20.3138 | −10.9 | −8.6 |
| 3 Decrease (other) | 0.063 | 106.4871 | 20.4680 | −9.0 | −14.1 |
| 3 Decrease (other) | 0.062 | 106.4067 | 20.4621 | −3.4 | −10.0 |
| 4 Increase | 0.060 | 106.0545 | 20.8531 | −8.7 | +1.5 |
| 3 Decrease (other) | 0.056 | 106.4877 | 20.4593 | −9.0 | −14.0 |
| 4 Increase | 0.054 | 106.3048 | 20.5660 | −11.3 | −6.3 |

Coordinates are patch centroids (WGS84); dB values are the mean HH over the patch.

- **Increases (class 4, 0.58 km², 7 patches)** cluster in the north-west (around 106.05–106.10°E, 20.73–20.85°N) with two more near 106.30°E, 20.56°N and one at 106.19°E, 20.52°N. Averaged over all class-4 cells, HH goes from −10.2 to −9.1 to **+0.8 dB** and HV from −18.2 to −17.1 to −11.6 dB: the increase happens mostly between 27 Oct and 3 Nov. Possible causes include new structures or materials, a change in soil moisture or roughness, or double-bounce between water and vegetation/structures. **Not verified.**
- **HV-only increases (class 6, 0.16 km², 2 patches)** lie in the south-east (around 106.47–106.49°E, 20.31–20.35°N). An HV increase alone usually points to more volume scattering (vegetation structure). **Not verified.**
- **No HV-only decrease** (class 5) passed the test.

## What the change results mean for rice harvest

No widespread HV decrease, the expected signature of crops being cut, was detected. This is discussed in [Rice harvest](/results/rice-harvest/).

## Limitations of the change results

- **Only one same-geometry pair** (22 Oct → 3 Nov, 12 days). The 27 Oct acquisition has a different geometry and is used only as a qualitative intermediate.
- **Strict threshold** (|z| > 5 in both polarisations, ≥ 0.05 km²) favours few false alarms over sensitivity; small or gradual changes are missed.
- **No ground truth:** all interpretations are hypotheses.
- The patch list is also available to the AI assistant and on the [map](/?view=change).
