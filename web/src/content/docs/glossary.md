---
title: Glossary
description: Plain-language definitions of the radar, remote-sensing and machine-learning terms used on this site.
sidebar:
  order: 5
---

Short definitions of the technical terms used across the project, with notes on how each one applies here.

## Radar and NISAR terms

**SAR (Synthetic Aperture Radar)**
An imaging radar carried on a satellite or aircraft. It sends microwave pulses and records the echoes; by combining echoes along the flight path it synthesises a much longer antenna and achieves fine resolution. SAR provides its own illumination, so it works day and night and through clouds. In this project SAR is the only model input because clouds hid about 68% of the province from optical satellites.

**NISAR**
The NASA–ISRO Synthetic Aperture Radar mission, the first satellite carrying both an L-band radar (NASA) and an S-band radar (ISRO). This project uses its L-band data.

**L-band**
Radar wavelength of about 24 cm. Longer wavelengths penetrate further into vegetation canopies and are less sensitive to small leaves than shorter ones (C-band, ~5.6 cm, used by Sentinel-1), so L-band "sees" stems, branches and the ground below crops.

**Frequency A / frequency B**
NISAR products can contain two sub-bands. Frequency A is the main one; this project uses frequency A only (20 m on the descending track, 10 m on the ascending track). Frequency B is coarser over this area (about 80 m) and is not used.

**GCOV (Geocoded polarimetric COVariance)**
NISAR's Level-2 product: radar backscatter that has been geocoded onto a map grid (here UTM 48N) and radiometrically terrain-corrected. It stores the polarimetric covariance terms; the diagonal terms `HHHH` and `HVHV` are the HH and HV backscatter power. See [NISAR data](/data/nisar/).

**VALIDATED / PROVISIONAL**
Maturity levels of NISAR products. VALIDATED products (here processing version CRID P05036, available from 21 October 2026) have passed calibration and validation; earlier PROVISIONAL products are not used in this project.

**CRID**
Composite Release ID: the processing version of a NISAR product (P05036 here).

**Track, ascending, descending**
A track is a repeating orbit path. Descending passes move north-to-south, ascending passes south-to-north, so the radar looks at the ground from opposite sides. In this project 22 October and 3 November are track 148 (descending) and 27 October is track 054 (ascending).

**Backscatter**
The part of the radar energy that returns to the sensor. Bright areas return a lot (buildings), dark areas return little (calm water).

**σ⁰ (sigma-naught) and γ⁰ (gamma-naught)**
Normalised measures of backscatter. σ⁰ normalises by ground area; γ⁰ normalises by the area seen perpendicular to the radar beam and is the convention used by terrain-corrected (RTC) products. GCOV provides γ⁰ plus a layer (`rtcGammaToSigmaFactor`) to convert to σ⁰. This project uses γ⁰ as delivered.

**RTC (Radiometric Terrain Correction)**
Correction of backscatter brightness for the effect of terrain slopes facing towards or away from the radar. Hưng Yên is almost flat, so the effect is small here.

**Polarisation: HH and HV**
The orientation of the radar wave's electric field. HH = transmitted horizontal, received horizontal (co-polarised); HV = transmitted horizontal, received vertical (cross-polarised). HV is produced mainly by multiple scattering in vegetation, so it is a good vegetation indicator. HV was the most useful polarisation in our classifier.

**dB (decibel)**
Logarithmic scale for backscatter: dB = 10·log10(linear power). A drop of 6 dB means the returned power fell to about a quarter. Typical values here: calm water below about −15 dB in HH; median HH over the AOI about −8 dB.

**Speckle**
Grainy, random-looking noise in every radar image, caused by interference of echoes from many scatterers within one pixel. It is not sensor noise and does not average out within one pixel; it is reduced by averaging several looks or neighbouring pixels.

**Looks / number of looks**
Independent samples averaged into one pixel. More looks means less speckle. GCOV gives the number of looks per pixel (median about 8.95 per 20 m pixel on our descending dates, about 4.64 per 10 m pixel on 27 October).

**ENL (Equivalent Number of Looks)**
The number of independent looks that would produce the observed speckle level. When neighbouring pixels are correlated, the ENL of a window is smaller than the simple sum of looks; our change detection corrects for this with the factor f ≈ 1.6–1.7.

**Specular reflection**
Mirror-like reflection from a smooth surface such as calm water: the radar signal bounces away from the satellite, so the surface appears very dark. This is why new open water shows a strong drop in both HH and HV.

**Double-bounce scattering**
The signal bounces off the ground and then off a vertical wall (or the reverse) and returns straight to the radar, like a corner reflector. It makes buildings very bright in HH, and depends on the building orientation relative to the look direction. Flooded vegetation can also cause double bounce.

**Volume scattering**
Multiple scattering inside a volume such as a crop canopy or tree crown. It produces a relatively strong HV signal and is typical of vegetation.

**Log-ratio change detection**
Comparing two radar images by the logarithm of their intensity ratio, r = ln(I₂/I₁). The log-ratio turns multiplicative speckle into an additive term with known statistics, which allows a statistical test. See [Change detection](/methods/change-detection/).

**Trigamma function ψ₁**
The second derivative of the logarithm of the gamma function. For Gamma-distributed intensity with L looks, the variance of ln(intensity) is ψ₁(L); this gives the expected spread of the log-ratio when nothing changes.

**z-score**
A difference divided by its expected standard deviation. In our change test, |z| > 5 is required in both HH and HV.

## Optical and geospatial terms

**Sentinel-2**
ESA's optical satellites (10–20 m). Used here only as a picture for drawing labels. See [Sentinel-2](/data/sentinel2/).

**Cloud Score+**
Google's per-pixel cloud and shadow quality score for Sentinel-2 (`cs_cdf`, 0–1). We keep pixels with cs_cdf ≥ 0.789.

**Median composite**
An image in which each pixel is the median of all clear observations in a time window, here 22 October–3 November 2026.

**Dynamic World**
Google's near-real-time 10 m land-cover product from Sentinel-2. It covers only 6.2% of our AOI in the study window and was not used.

**AOI (Area of Interest)**
The study area: the merged Hưng Yên province, 2,571.7 km² (geometric area). See [AOI](/data/aoi/).

**UTM 48N / EPSG:32648**
The map projection used for all rasters (metres, Universal Transverse Mercator zone 48 North).

**Pure cell**
A 20 m cell whose area is at least 80% one label class. Only pure cells are used as training and test samples.

## Machine-learning and accuracy terms

**Random Forest**
An ensemble of many decision trees, each trained on a random subset of the data and features; the trees vote. Our main model uses 300 trees and class weights balanced by class frequency.

**Overall accuracy (OA)**
Share of test samples classified correctly. Inflated when one class dominates (Water is 51% of our samples).

**Balanced accuracy (BA)**
Mean of the per-class recalls; each class counts equally. Our primary metric. Always predicting the majority class gives BA 25% for four classes.

**Recall, precision, F1**
Recall (producer's accuracy): share of the true members of a class that were found. Precision (user's accuracy): share of predictions of a class that were right. F1: harmonic mean of the two. Macro F1 averages F1 over classes.

**Cohen's kappa**
Agreement between prediction and reference corrected for chance agreement (0 = chance, 1 = perfect).

**Confusion matrix**
Table of true classes (rows) against predicted classes (columns). Our main confusion is Vegetation ↔ Bare land.

**Cross-validation (CV)**
Repeatedly splitting samples into training and test parts (folds) so every sample is tested once by a model that did not see it.

**Spatial block cross-validation**
Cross-validation in which samples are grouped by geographic blocks (here 5 km × 5 km) and each block goes entirely to one fold. It prevents test cells from sitting right next to training cells. See [Validation](/methods/validation/).

**Spatial leakage**
Over-optimistic accuracy caused by test samples being very close to, and therefore very similar to, training samples. A random per-cell split overestimates our BA by about 3 points.

**Buffer**
Removal of training samples within a given distance of test samples (250 m or 1 km in our tests), to further reduce leakage.

**Block bootstrap**
Estimating a confidence interval by resampling whole spatial blocks with replacement (2,000 times here) and recomputing the metric.

**McNemar's test**
A test of whether two classifiers make different errors on the same samples. Its p-values are optimistic when samples are spatially correlated.

**Permutation importance**
Drop in accuracy when one feature's values are randomly shuffled; a large drop means the model relies on that feature.

**Ablation**
Removing groups of features to see how much accuracy each group contributes.

**Learning curve**
Accuracy as a function of the amount of training data (here, number of polygons). Ours nearly saturates after about 300 polygons.

**Nested cross-validation**
Hyperparameter tuning inside an inner CV loop, with an outer CV loop that measures the tuned model on untouched data. Tuning improved BA by at most 0.5 points.

**Area of applicability (AOA)**
The part of the map where input features are similar enough to the training data for the model's CV accuracy to be meaningful (Meyer & Pebesma, 2021). 8.3% of our AOI is outside it.

**Dissimilarity index (DI)**
Distance from a cell to the nearest training sample in standardised, importance-weighted feature space, divided by the mean distance between training samples. Cells with DI above 0.105 are outside the AOA.

**Model agreement**
Number of models (out of 10) that predict the same class as the majority. All 10 agree on 65.9% of our AOI.

**Majority (modal) filter**
A post-processing filter that replaces each cell's class with the most frequent class in its neighbourhood, removing isolated "salt-and-pepper" pixels. Used only for display; its effect on accuracy is not measured.

**Blind test set**
Reference samples chosen at random and labelled without seeing the predictions. Ours (250 cells) was prepared but never labelled.

**Design-based area estimation**
Estimating class areas with confidence intervals from a probability sample of reference labels (Olofsson et al., 2014). Not possible here without a labelled blind test set, so our area shares are unvalidated pixel counts.
