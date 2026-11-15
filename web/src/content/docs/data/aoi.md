---
title: Area of interest (AOI)
description: The boundary of the merged Hưng Yên province used to clip every dataset, its area and how it is handled.
sidebar:
  order: 2
---

The area of interest (AOI) of the project is the whole of **Hưng Yên province, Vietnam, as it exists after the 2025 administrative merger**: the former Hưng Yên province plus the former Thái Bình province, merged under the name Hưng Yên.

## AOI boundary file

- **File:** `data/ref/aoi.geojson` (provided by the team; treated as the authoritative boundary and never edited).
- **Structure:** one GeoJSON feature whose geometry is a **MultiPolygon of 8 parts**, in geographic coordinates (EPSG:4326).
- **Attributes in the file:** province name Hưng Yên, merged from "Hưng Yên, Thái Bình", province code 33, population 3,567,943, administrative area 2,514.81 km², 104 administrative units (11 wards, 93 communes), seat at Phố Hiến.
- **Projected copy:** `scripts/clip_gee_s2.py` also writes `data/ref/aoi_32648.geojson`, the same boundary in UTM 48N, for convenient display in QGIS.
- **Bounding box (approximate):** 105.89°E to 106.66°E, 20.25°N to 21.01°N.

## AOI area: 2,571.7 km² versus 2,514.81 km²

- **Geometric area of the boundary:** 2,571.7 km² when the polygon is projected to UTM 48N (2,572.6 km² measured on the ellipsoid). On the 20 m analysis grid this is 6,429,330 cells × 400 m² = **2,571.7 km²**. All percentages of the AOI on this site use this value.
- **Administrative area attribute:** the boundary file states 2,514.81 km². This official statistic and the geometric area of the polygon differ by about 2%. The difference was not reconciled; it may come from a different survey basis or boundary generalisation.

## How the AOI is used in processing

- **Clipping NISAR:** `scripts/crop_gcov.py` projects the AOI polygon to UTM 48N (EPSG:32648) before cutting, then sets all pixels outside the polygon to nodata. Because the reprojection is done at cutting time, the fact that the original file is in EPSG:4326 has no effect on the result.
- **Check:** the valid-data footprint of all three NISAR dates coincides exactly with the AOI rasterised on the UTM grid.
- **Clipping Sentinel-2:** `scripts/clip_gee_s2.py` clips the 10 m Sentinel-2 composite with the same polygon (pixels outside = 0).
- **Pitfall avoided:** an earlier version of the code read only the first feature of a multi-feature GeoJSON and silently lost part of the boundary. The current file has exactly one feature (this was checked), so reading the first feature reads the whole boundary.

## Landscape inside the AOI

Hưng Yên lies in the low, flat Red River Delta. The landscape is a fine mosaic of rice paddies, vegetable and fruit fields, fish and shrimp ponds, villages surrounded by trees and gardens, towns and industrial zones, rivers, canals and dykes. Water in fields and ponds is actively managed (flooded and drained) by farmers, which is what the [change detection](/methods/change-detection/) looks for. Terrain is almost flat, so radar terrain effects are small.

See the boundary on the [interactive map](/?view=overview).
