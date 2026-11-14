# NISAR L-band Change Detection and Land Cover Mapping

*Phát hiện biến động và phân loại lớp phủ bằng ảnh NISAR băng L*

| | |
|---|---|
| **Competition / Cuộc thi** | NASA Space Apps Challenge 2026 |
| **Challenge / Đề bài** | [Dancing with the SARs](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/) |
| **Entry title / Tên bài thi** | NISAR L-band Change Detection and Land Cover Mapping |
| **Team / Đội thi** | 2936-ThanhNoi (team ID NS05005) |
| **Members / Thành viên** | Ninh Hải Đăng (team lead), Phạm Minh Quang, Lê Toàn Thắng |
| **Website** | https://dwts.ninhhaidang.com ([map](https://dwts.ninhhaidang.com/map/), [AI assistant](https://dwts.ninhhaidang.com/chat/), [Tiếng Việt](https://dwts.ninhhaidang.com/vi/)) |

We use three **NISAR L-band GCOV** acquisitions (VALIDATED, CRID P05036: 22 Oct, 27 Oct and 3 Nov 2026) over **Hưng Yên province, Vietnam** (the province after the 2025 merger with Thái Bình). In this period only about 32% of the province had a cloud-free Sentinel-2 view, so we use radar to do two things:

1. **Detect water-management changes**, using a speckle-aware log-ratio test on the 22 Oct → 3 Nov pair. 99.89% of the province shows no significant change. The largest change is a block of about 1.6 km² of new water beside a river, where HH and HV both fall by about 6 dB; its cause is not verified.
2. **Map 4 land-cover classes from SAR only** (water, vegetation, bare soil, built-up). A Random Forest on 12 SAR features is trained from 1,347 label polygons. It reaches about 93% balanced accuracy on pure 20 m cells under 5 km spatial-block cross-validation. This is **not** a map-level accuracy, and there is no independent test set.

The honest caveats, eight experiments (E1–E8) and the full method are documented on the website.

## Repository

| Path | Content |
|---|---|
| `scripts/` | Python pipeline: `crop_gcov.py` → `change_detection.py` → `train_classifier.py` → `experiments.py` → `plot_experiments.py`; then `postprocess_landcover.py`, `build_web.py` |
| `outputs/` | Figures, result tables, experiment reports (`experiments/en/REPORT.md`, `experiments/vi/BAO_CAO.md`) |
| `labeling/` | Training label polygons and the (unlabelled) blind test cells |
| `web/` | Website: Astro + Starlight docs (EN/VI), MapLibre map, chatbot API |
| `deploy/` | Docker Compose, Caddy, `sync.sh` for the home server |
| `data/` | Not in git. NISAR GCOV is downloaded from ASF DAAC; see the [Reproduce](https://dwts.ninhhaidang.com/reproduce/) page |

## Data and acknowledgements

NISAR is a joint NASA–ISRO mission; the data comes from the Alaska Satellite Facility DAAC. Sentinel-2 imagery (ESA Copernicus) was used only to draw training labels. The website base map is Esri World Imagery (Esri, Maxar, Earthstar Geographics, and the GIS User Community).
