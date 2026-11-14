---
title: Project overview
description: What the Dancing with the SARs project does, where, with which data, and what it found.
sidebar:
  order: 1
---

**Dancing with the SARs** is our entry to the NASA Space Apps Challenge 2026 challenge of the same name. We use NISAR L-band radar images to answer two questions about Hưng Yên province in Vietnam's Red River Delta: *where did water management change the land surface in late October 2026*, and *can we map land cover from radar alone when optical satellites are blind because of clouds?*

:::tip[Explore the results]
Open the [interactive map](/map/?view=overview) to see the three radar dates, the detected changes and the land-cover map with its confidence layers. You can also [ask the AI assistant](/chat/) any question about the project.
:::

## The challenge: Dancing with the SARs

The Space Apps 2026 challenge *Dancing with the SARs* (Earth Science theme, intermediate/advanced) asks teams to build an interactive, open-source application that uses radar data from the NASA–ISRO **NISAR** mission to monitor and visualise changes of the Earth's surface, such as agricultural activity, flooding or wetland loss. Teams pick a study area, download free NISAR data (optionally adding optical imagery or GIS layers for context), present the results in an interactive digital format, and propose physical explanations for what they see, or do not see, in the SAR data. SAR (Synthetic Aperture Radar) sends its own microwave pulses and measures the echo, so it works day and night and sees through clouds; it is very sensitive to surface roughness and moisture, which makes water stand out. Our project uses the NISAR **GCOV** product (Level-2 geocoded, terrain-corrected backscatter) at maturity level **VALIDATED** (processing version CRID P05036), which became available from 21 October 2026.

## Study area: the new Hưng Yên province

- **Where:** Hưng Yên province, northern Vietnam, in the flat, intensively farmed Red River Delta.
- **What "new" means:** in the 2025 administrative merger, the old Hưng Yên province and the old Thái Bình province were combined into a single province named Hưng Yên. Our area of interest (AOI) is the boundary of this merged province.
- **Size:** the AOI boundary has a geometric area of **2,571.7 km²** (6.43 million cells of 20 m × 20 m on the UTM 48N grid). The boundary file also carries an official administrative area attribute of 2,514.81 km²; the two numbers come from different sources and were not reconciled. See [Area of interest](/data/aoi/).
- **Landscape:** rice paddies, vegetable and fruit fields, fish and shrimp ponds, dense villages surrounded by trees, towns, rivers, canals and dykes. Water levels in fields and ponds are actively managed by people.

## Why radar: clouds hide the delta

- **Clouds in the study window:** between 22 October and 3 November 2026, no single Sentinel-2 optical image was clear enough. Even a 12-day cloud-masked median composite has at least one clear observation over only **about 32% of the AOI**. See [Sentinel-2](/data/sentinel2/).
- **Dynamic World** (Google's near-real-time land-cover product, derived from Sentinel-2) covers only **6.2% of the AOI** in the same window, so it could not be used.
- **Radar works through clouds:** all three NISAR acquisitions cover 100% of the AOI.

## The two research questions

1. **Water-management change detection.** Between two radar images from the same orbit track (22 October and 3 November 2026), which places changed significantly, and do the changes look like fields, ponds or embanked areas being flooded or drained? Method: a statistical log-ratio test that accounts for radar speckle. See [Change detection method](/methods/change-detection/).
2. **Four-class land cover from SAR alone.** Can we classify every 20 m cell into **Water, Vegetation, Bare land, Built-up** using only NISAR HH and HV backscatter from three dates, so the map also covers the cloudy ~68% of the province? See [Classification method](/methods/classification/).

## Data used (only 22 October to 3 November 2026)

| Data | Role | Details |
|---|---|---|
| NISAR GCOV VALIDATED, frequency A | Main input | 22 Oct (track 148 descending, 20 m), 27 Oct (track 054 ascending, 10 m), 3 Nov (track 148 descending, 20 m). HH and HV. See [NISAR data](/data/nisar/). |
| Sentinel-2 surface reflectance composite | Only for drawing labels | 10 m median 22 Oct–3 Nov, cloud-masked with Cloud Score+. **Not a model input.** |
| Label polygons | Training labels | 1,347 rectangles drawn by the team: Water 190, Vegetation 485, Bare land 444, Built-up 228. See [Labels](/data/labels/). |
| AOI boundary | Clipping | Merged Hưng Yên province, 8-part MultiPolygon. |

The 29 October acquisition (track 076) was excluded because it covers only 4% of the AOI. No PROVISIONAL products and no data from outside the 22 October–3 November window are used.

## Headline results and their caveats

### Change detection result (22 October → 3 November 2026)

- **99.89% of the AOI shows no statistically significant change** in this 12-day period (z-test threshold |z| > 5 on both HH and HV, patches ≥ 0.05 km²).
- **The only notable signal is a cluster of new open water of about 1.6 km²** around 106.48°E, 20.46°N, next to a stretch of river in the south-eastern part of the province. HH backscatter fell from about −10 to −16 dB and HV from about −17 to −23 dB, already decreasing on 27 October. The shape is a rectangular block, typical of embanked fields or ponds.
- **Cause unverified:** we hypothesise that fields, ponds or an embanked area were deliberately flooded, but clouds prevented any optical confirmation. See [Change results](/results/change/) and the [change view of the map](/map/?view=change).
- **No rice-harvest signal** was found within the 12 days; most rice appears to have been harvested before 22 October.

### Land-cover result (SAR only, 4 classes)

- **Balanced accuracy (BA) about 93%** for Random Forest (SVM 93.6%) under 5 km spatial-block cross-validation. The baseline of always predicting the majority class gives 25%.
- **Important caveat:** this 93% is measured on **pure 20 m cells** that lie entirely inside a labelled rectangle. It is **not** the accuracy of the full map, which also contains mixed cells and areas far from any label. Map-level accuracy is unknown.
- **No independent test set:** a blind set of 250 random cells was prepared (`labeling/blind_test_cells.gpkg`) but was not labelled, and the team decided not to label it.
- **Areas are unvalidated:** the consensus map assigns about 24% of the AOI to Built-up and about 44% to Bare land. These shares are not bias-corrected. Built-up is the least reliable class: 23.5% of cells predicted as Built-up fall outside the model's area of applicability.
- **What matters most:** using three dates and both polarisations. The choice of model barely matters (11 of 14 models within 1 point).
- See [Classification method](/methods/classification/), [Validation](/methods/validation/), and the [land-cover](/map/?view=landcover) and [confidence](/map/?view=confidence) views of the map.

## Where to go next

- [NISAR data](/data/nisar/), [AOI](/data/aoi/), [Sentinel-2](/data/sentinel2/), [Labels](/data/labels/)
- [Preprocessing](/methods/preprocessing/), [Change detection](/methods/change-detection/), [Classification](/methods/classification/), [Validation](/methods/validation/)
- [How to reproduce](/reproduce/), [Glossary](/glossary/)
