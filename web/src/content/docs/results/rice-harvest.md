---
title: Rice harvest (negative result)
description: No rice-harvest signal was found in the 12-day NISAR window, most likely because the main season was already harvested before 22 October 2026; Dynamic World was too cloudy to help.
sidebar:
  order: 3
---

One early idea for the project was to map **rice harvest** in Hưng Yên from the NISAR time series. This page explains why that idea was dropped. It is a negative result and is reported for completeness.

## What a harvest would look like in L-band SAR

When a standing rice crop is cut, the volume of stems and leaves disappears. At L-band this usually shows as a **drop in HV** (cross-polarisation, driven by volume scattering), often with a change in HH depending on soil moisture and stubble. A field that is flooded after harvest becomes a smooth water surface and darkens in **both** HH and HV.

## What was found in the 12-day window

- **No harvest signal at scale.** Between 22 Oct and 3 Nov 2026, the statistical change detection found **99.89% of the province unchanged** at the chosen significance (|z| > 5 in HH and HV, patches ≥ 0.05 km²). There was no widespread HV decrease of the kind expected from harvest; no "HV-only decrease" patch passed the test at all ([Change results](/results/change/)).
- **Many fields already look bare.** The SAR-only land-cover map classifies about 44–46% of the province as Bare land ([Land-cover results](/results/landcover/)), consistent with fields already harvested or ploughed.
- **Interpretation (not verified):** most rice fields were probably **harvested before 22 Oct**, so the 12-day window falls after the main-season harvest. This fits the usual crop calendar of the Red River Delta, but it has not been checked against local harvest dates or field data.

## Why the rice topic is weak for this dataset

- **Window too short and too late:** only 12 days of VALIDATED data (22 Oct – 3 Nov 2026) are allowed in this project, and only one same-geometry pair (22 Oct and 3 Nov, track 148). A harvest timeline needs acquisitions spanning the whole harvest period.
- **Change-detection threshold is strict:** gradual or field-by-field changes below 0.05 km² are deliberately not reported.
- **No optical confirmation:** clouds covered most of the province during the period (only about 32% of the AOI had at least one clear Sentinel-2 observation).

## Dynamic World could not be used as a reference

Google's Dynamic World near-real-time land-cover product was considered as a reference for crops and bare land. Within the 22 Oct – 3 Nov 2026 window it **covered only 6.2% of the AOI** (because it is derived from cloud-free Sentinel-2 pixels), so it was **not used** for labels or validation.

## Where the project focus went instead

The project therefore focuses on (1) **water-management changes** (fields, ponds, dykes), where the main finding is the [new-water cluster](/results/change/), and (2) a **four-class SAR-only land-cover map** ([Land-cover results](/results/landcover/)).
