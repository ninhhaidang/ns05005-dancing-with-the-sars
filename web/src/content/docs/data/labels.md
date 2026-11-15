---
title: Training labels
description: The 1,347 hand-drawn label polygons for Water, Vegetation, Bare land and Built-up, how they become training samples, their biases, and the unlabelled blind test set.
sidebar:
  order: 4
---

The land-cover classifier learns from **1,347 rectangular label polygons** drawn by the team. Each polygon marks an area that clearly belongs to one of four classes. Labels were drawn by eye on the 10 m [Sentinel-2 composite](/data/sentinel2/), so they exist only where that composite is cloud-free (about 32% of the AOI).

## Label classes and polygon counts

| Class code | Class (map name) | Source shapefile | Polygons | Median polygon area | Total area |
|---|---|---|---|---|---|
| 1 | Water | `water.shp` | 190 | 5,829 m² | 2.66 km² |
| 2 | Vegetation | `vegetation.shp` | 485 | 568 m² | 0.54 km² |
| 3 | Bare land | `bareland.shp` | 444 | 997 m² | 0.57 km² |
| 4 | Built-up (labelled as "building") | `building.shp` | 228 | 1,669 m² | 0.48 km² |
| | **Total** | | **1,347** | | **4.25 km²** |

- **Intended class meaning:** Water = open water (rivers, ponds, flooded fields). Vegetation = fields and trees with green cover. Bare land = soil without green cover, including recently harvested or ploughed fields. Built-up = dense buildings (towns, villages); the source layer is called "building".
- **Label coverage:** all polygons together cover only 4.25 km², about 0.17% of the 2,571.7 km² AOI.

## Label file and how it was made

- **Drawing:** teammates drew rectangles in ArcGIS Pro on top of the Sentinel-2 true-colour composite, one shapefile per class.
- **Merging:** `scripts/merge_label_polygons.py <shapefile folder>` merges the four shapefiles into `labeling/labels_polygon.gpkg`. It drops the Z dimension (PolygonZ → Polygon), repairs invalid geometries, converts everything to MultiPolygon, and assigns EPSG:32648 (the ArcGIS .prj file has WKT without an EPSG code). The original shapefiles are not modified.
- **Columns:** `poly_id` (unique id, used for grouping in cross-validation), `class_id` (1–4), `class_name`, `source` (origin shapefile), `area_m2`.
- **History:** earlier rounds of point labels (CSV files) were replaced by the polygons and deleted from the repository.

## From label polygons to training samples (pure 20 m cells)

The model works on the 20 m NISAR grid, so each polygon is converted into 20 m training cells (code: `scripts/sar_dataset.py`, function `samples`):

1. **Coverage fraction:** each 20 m cell is split into 8 × 8 sub-cells (2.5 m) and the fraction covered by each class is computed. (With 4 × 4 sub-cells the 80% threshold would effectively round to 100%, so 8 × 8 is required.)
2. **Purity threshold:** a cell becomes a sample only if **≥ 80%** of its area belongs to one class ("pure cell").
3. **Cap per polygon:** at most **20 cells per polygon** are kept (chosen at random, seed 0), so big water polygons do not dominate.
4. **Result:** **3,918 samples from 864 polygons**: Water 2,011, Vegetation 622, Bare land 660, Built-up 625.
5. **Unusable polygons:** **483 polygons (36%)** produce no sample because they are too small to fully contain a 400 m² cell. Most of them are vegetation polygons (vegetation's median polygon area is only 568 m²).

## Spatial clustering and imbalance of the labels

- **Clustered drawing:** polygons were drawn in same-class clusters. The median distance from a polygon to the nearest polygon of the *same* class is 102 m, to the nearest polygon of a *different* class 509 m. No polygons touch.
- **Few independent places:** the samples fall in 88 blocks of 5 × 5 km, but the 10 densest blocks hold 48% of all samples; each class occurs in only 33–45 blocks.
- **Regional imbalance:** Built-up has 618 samples in the northern half of the province and only 7 in the southern half. Vegetation has 209 samples in the western half and 413 in the eastern half.
- **Consequence:** cross-validation must split by spatial blocks, not by cell or polygon (see [Validation](/methods/validation/)), and the effective diversity of the label set is much lower than 3,918 cells suggests.

## Blind test set (prepared, not labelled)

- **File:** `labeling/blind_test_cells.gpkg`, layer `cells`, made by `scripts/make_blind_test.py` (random seed 20261114).
- **Design:** **250 cells of 20 m × 20 m** chosen by simple random sampling among cells that are inside the AOI, fully cloud-free in Sentinel-2 (all four 10 m pixels clear), at least 200 m from any training polygon, and at least 200 m from each other. The cells were chosen without looking at the predicted map, and predictions are not stored in the file, so labelling would be "blind".
- **Label codes:** 1 Water, 2 Vegetation, 3 Bare land, 4 Built-up, 0 = mixed or unclear, −1 = not yet labelled.
- **Status:** all 250 cells still have label −1. **The team decided not to label this set**, so there is **no independent accuracy estimate** for the map. The evaluation script `scripts/eval_blind.py` (accuracy with Wilson 95% intervals, confusion matrix, mixed-cell share) is ready but has never been run on real labels.

## Seeing labels and predictions together

The [land-cover view of the interactive map](/?view=landcover) shows the SAR-only prediction; the [confidence view](/?view=confidence) shows how many models agree and where SAR features are unlike anything in these labels (outside the area of applicability).
