"""Vẽ toàn bộ hình của thí nghiệm bằng seaborn, song ngữ, từ CSV trong outputs/experiments và raster trong data/derived.

Không huấn luyện lại gì: chạy scripts/experiments.py trước để có CSV/raster, rồi chạy script này.
Ra:  outputs/experiments/vi/*.png  (tiếng Việt)
     outputs/experiments/en/*.png  (tiếng Anh) + outputs/experiments/en/tables/*.csv (bảng CSV đã dịch nhãn)
Logic (lọc/nhóm/màu) dựa trên nhãn tiếng Việt gốc trong CSV; chỉ chữ hiển thị được dịch qua TR, nên hai bộ hình luôn cùng số liệu.
Chạy: python -I scripts/plot_experiments.py [vi|en]   (mặc định: cả hai)
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, pandas as pd, rasterio
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from sklearn.metrics import confusion_matrix
from sar_dataset import ROOT, NAMES

OUT = ROOT / "outputs/experiments"; DER = ROOT / "data/derived"
K = [1, 2, 3, 4]; CLS = [NAMES[k] for k in K]
CLASS_COL = {"Nước": "#2f6db5", "Thực vật": "#4f9a3c", "Đất trống": "#d9a85b", "Đô thị": "#c4453c"}
sns.set_theme(context="notebook", style="whitegrid", font="Arial",
              rc={"axes.titleweight": "bold", "axes.titlesize": 13, "axes.labelsize": 11, "axes.titlepad": 10,
                  "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 9.5, "legend.frameon": False,
                  "axes.spines.top": False, "axes.spines.right": False, "grid.color": "#e6e6e6", "axes.edgecolor": "#888888"})
INK, MUTED = "#222222", "#6b6b6b"
FAMILY = {"Mốc: lớp đông nhất": "Mốc", "Cây quyết định (sâu 4)": "Cây đơn", "Maximum Likelihood (QDA)": "Thống kê cổ điển", "LDA": "Thống kê cổ điển",
          "Hồi quy logistic": "Tuyến tính", "k-NN (k=15)": "Láng giềng", "SVM (RBF)": "Kernel", "MLP (64-32)": "Mạng nơ-ron",
          "Random Forest": "Rừng cây", "Extra Trees": "Rừng cây", "HistGradientBoosting": "Boosting", "XGBoost": "Boosting",
          "LightGBM": "Boosting", "CatBoost": "Boosting"}
FAM_ORDER = ["Rừng cây", "Boosting", "Kernel", "Tuyến tính", "Mạng nơ-ron", "Láng giềng", "Thống kê cổ điển", "Cây đơn"]
FAM_COL = dict(zip(FAM_ORDER, sns.color_palette("Set2", len(FAM_ORDER))))

# ---- từ điển dịch nhãn dữ liệu (vi -> en); chuỗi không có trong từ điển giữ nguyên (tên mô hình tiếng Anh, tên đặc trưng) ----
TR = {
    # lớp phủ
    "Nước": "Water", "Thực vật": "Vegetation", "Đất trống": "Bare land", "Đô thị": "Built-up",
    # mô hình / họ mô hình
    "Mốc: lớp đông nhất": "Baseline: majority class", "Cây quyết định (sâu 4)": "Decision tree (depth 4)", "Hồi quy logistic": "Logistic regression",
    "Mốc": "Baseline", "Cây đơn": "Single tree", "Thống kê cổ điển": "Classical statistical", "Tuyến tính": "Linear", "Láng giềng": "Nearest neighbours",
    "Mạng nơ-ron": "Neural network", "Rừng cây": "Random forests",
    "Đồng thuận (lớp đa số)": "Consensus (majority class)",
    # cách kiểm chứng
    "Ngẫu nhiên theo ô (rò rỉ)": "Random by cell (leaky)", "Theo polygon": "By polygon", "Khối 1 km": "1 km blocks", "Khối 2 km": "2 km blocks",
    "Khối 5 km": "5 km blocks", "Khối 5 km + đệm 250 m": "5 km blocks + 250 m buffer", "Khối 5 km + đệm 1 km": "5 km blocks + 1 km buffer",
    "Khối 10 km": "10 km blocks", "Khối 20 km": "20 km blocks", "Chia Tây / Đông": "West / East split", "Chia Bắc / Nam": "North / South split",
    "4 góc phần tư": "4 quadrants",
    # bộ đặc trưng (E2) và nhóm
    "Đủ 12 đặc trưng": "All 12 features", "Chỉ HH (6)": "HH only (6)", "Chỉ HV (5)": "HV only (5)",
    "Một ngày 22/10 (HH, HV, HV-HH)": "Single date 22 Oct (HH, HV, HV−HH)", "Một ngày 27/10, quỹ đạo lên": "Single date 27 Oct (ascending)",
    "Một ngày 3/11": "Single date 3 Nov", "Hai ngày quỹ đạo xuống (22/10, 3/11)": "Two descending dates (22 Oct, 3 Nov)",
    "Chỉ trung bình (HH_tb, HV_tb, HV-HH)": "Means only (HH_mean, HV_mean, HV−HH)", "Bỏ kết cấu": "Without texture",
    "Bỏ độ lệch chuẩn thời gian": "Without temporal std",
    "Bỏ một nhóm": "One group removed", "Một phân cực": "Single polarisation", "Ít ngày ảnh": "Fewer dates", "Chỉ trung bình": "Means only",
    # đặc trưng, phân cực, vùng
    "HH_tb": "HH_mean", "HV_tb": "HV_mean", "Tỷ số HV−HH": "HV−HH ratio", "Vùng S2 sạch": "Clear S2 area", "Vùng mây": "Cloudy area",
}


def tr_df(df):
    """Bản tiếng Anh của một bảng: dịch ô chuỗi, tên cột và chỉ số theo TR."""
    def col(c):
        for v, e in TR.items():
            if c == v: return e
            if c.endswith("_" + v): return c[: -len(v)] + e
        return c
    out = df.copy()
    for c in out.columns:
        if pd.api.types.is_string_dtype(out[c]) or out[c].dtype == object: out[c] = out[c].map(lambda s: TR.get(s, s) if isinstance(s, str) else s)
    out.columns = [col(c) for c in out.columns]
    if pd.api.types.is_string_dtype(out.index) or out.index.dtype == object: out.index = [TR.get(i, i) for i in out.index]  # pandas 3: cột chữ có dtype str
    return out


def read2(p, f=2):
    with rasterio.open(p) as s:
        a = s.read(1, out_shape=(s.height // f, s.width // f), resampling=rasterio.enums.Resampling.nearest)
        b = s.bounds
    return a, (b.left / 1000, b.right / 1000, b.bottom / 1000, b.top / 1000)


def aoi_lines(ax):
    g = json.load(open(ROOT / "data/ref/aoi_32648.geojson"))["features"][0]["geometry"]
    for poly in g["coordinates"]:
        xy = np.array(poly[0]) / 1000; ax.plot(xy[:, 0], xy[:, 1], color="#333333", lw=0.6)


def draw(lang):
    EN = lang == "en"
    t = lambda vi, en: en if EN else vi                  # chữ hiển thị
    tr = (lambda s: TR.get(s, s)) if EN else (lambda s: s)  # nhãn dữ liệu
    D_OUT = OUT / lang; D_OUT.mkdir(parents=True, exist_ok=True)
    print(f"[{lang}]")

    def save(fig, name):
        fig.savefig(D_OUT / name, dpi=200, bbox_inches="tight", facecolor="white"); plt.close(fig); print("  ", name)

    def title(fig, ax, main, sub):
        x = ax.get_position().x0
        fig.text(x, 1.0, main, ha="left", va="bottom", fontsize=14, fontweight="bold", color=INK, transform=fig.transFigure)
        fig.text(x, 0.985, sub, ha="left", va="top", fontsize=10, color=MUTED, transform=fig.transFigure)

    def frame(ax):
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(False); ax.set_aspect("equal")
        for s in ax.spines.values(): s.set_visible(False)
        x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); bx, by = x0 + 0.04 * (x1 - x0), y0 + 0.04 * (y1 - y0)
        ax.plot([bx, bx + 10], [by, by], color=INK, lw=3, solid_capstyle="butt"); ax.text(bx + 5, by + 0.012 * (y1 - y0), "10 km", ha="center", va="bottom", fontsize=9)
        ax.annotate(t("B", "N"), xy=(x1 - 0.06 * (x1 - x0), y1 - 0.04 * (y1 - y0)), xytext=(x1 - 0.06 * (x1 - x0), y1 - 0.13 * (y1 - y0)), ha="center",
                    fontsize=11, fontweight="bold", arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))

    # ---------------- E1: so sánh mô hình ----------------
    S = pd.read_csv(OUT / "E1_models_summary.csv")
    base = S[S.model.str.startswith("Mốc")].iloc[0]
    S = S[~S.model.str.startswith("Mốc")].sort_values("BA_mean", ascending=False).reset_index(drop=True)
    rf = S[S.model == "Random Forest"].iloc[0]
    fig = plt.figure(figsize=(12, 6.2)); gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1], wspace=0.04)
    ax = fig.add_subplot(gs[0]); ax2 = fig.add_subplot(gs[1], sharey=ax)
    ax.axvspan(rf.BA_ci_lo * 100, rf.BA_ci_hi * 100, color="#c4453c", alpha=0.08, lw=0)
    yy = np.arange(len(S)) + 0.5   # tâm hàng trùng tâm ô heatmap
    for i, r in S.iterrows():
        c = FAM_COL[FAMILY[r.model]]; y0 = i + 0.5; isrf = r.model == "Random Forest"
        ax.plot([r.BA_ci_lo * 100, r.BA_ci_hi * 100], [y0, y0], color=c, lw=2.2, solid_capstyle="round")
        ax.scatter(r.BA_mean * 100, y0, s=95 if isrf else 70, color=c, edgecolor=INK if isrf else "white", lw=1.3, zorder=3)
        ax.text(r.BA_ci_hi * 100 + 0.25, y0, f"{r.BA_mean*100:.1f}", va="center", fontsize=9.5, color=INK)
    H = (S.set_index("model")[[f"F1_{c}" for c in CLS]] * 100); H.columns = [tr(c) for c in CLS]
    sns.heatmap(H, ax=ax2, annot=True, fmt=".1f", cmap="YlGnBu", vmin=80, vmax=100, cbar_kws={"label": "F1 (%)", "shrink": 0.8},
                linewidths=1.5, linecolor="white", annot_kws={"fontsize": 9})
    ax2.set_ylabel(""); ax2.tick_params(axis="y", left=False, labelleft=False); ax2.xaxis.tick_top(); ax2.set_xlabel("")
    ax2.set_title(t("F1 từng lớp", "Per-class F1"), fontsize=11, fontweight="bold", pad=24)
    ax.set_ylim(len(S), 0); ax.set_yticks(yy, [tr(m) for m in S.model]); ax.tick_params(axis="y", labelleft=True)
    ax.set_xlim(83.5, 98.5); ax.grid(axis="y", visible=False); ax.set_xlabel(t("Độ chính xác cân bằng lớp, BA (%)", "Balanced accuracy, BA (%)"))
    for tl in ax.get_yticklabels():
        if tl.get_text() == "Random Forest": tl.set_fontweight("bold")
    ax.text(rf.BA_ci_hi * 100 - 0.1, len(S) - 0.15, t("CI 95% của RF", "RF 95% CI"), color="#c4453c", fontsize=8.5, ha="right", va="bottom")
    fig.legend(handles=[Patch(color=FAM_COL[f], label=tr(f)) for f in FAM_ORDER if f in set(FAMILY[m] for m in S.model)],
               loc="upper left", bbox_to_anchor=(ax.get_position().x0, -0.01), ncol=8, fontsize=9, handlelength=1.2, columnspacing=1.2)
    ntop = int((S.BA_mean >= S.BA_mean.iloc[0] - 0.01).sum())
    title(fig, ax, t(f"{len(S)} mô hình: {ntop} mô hình đứng đầu chênh nhau dưới 1 điểm BA", f"{len(S)} models: the top {ntop} are within 1 BA point of each other"),
          t(f"BA và khoảng tin cậy 95% (bootstrap theo khối) · CV khối không gian 5 km, 5 fold × 5 lần lặp · cùng 12 đặc trưng SAR · mốc lớp đông nhất: {base.BA_mean*100:.0f}%",
            f"BA with 95% CI (block bootstrap) · 5 km spatial block CV, 5 folds × 5 repeats · same 12 SAR features · majority-class baseline: {base.BA_mean*100:.0f}%"))
    save(fig, "E1_models.png")

    oof_p = OUT / "E1_oof_rep0.csv"
    if oof_p.exists():
        O = pd.read_csv(oof_p); top = list(S.model[:3]) + (["Random Forest"] if "Random Forest" not in list(S.model[:3]) else [S.model[3]])
        fig, axs = plt.subplots(1, 4, figsize=(15, 4.3), sharey=True); fig.subplots_adjust(right=0.9, wspace=0.12)
        cax = fig.add_axes([0.915, 0.2, 0.01, 0.62])   # thanh màu riêng để 4 ô bằng nhau
        CL = [tr(c) for c in CLS]
        for k_, (ax, m) in enumerate(zip(axs, top)):
            cm = confusion_matrix(O.y, O[m], labels=K); pc = cm / cm.sum(1, keepdims=True) * 100
            lab = np.array([[f"{pc[i, j]:.0f}%\n{cm[i, j]}" for j in range(4)] for i in range(4)])
            sns.heatmap(pc, ax=ax, annot=lab, fmt="", cmap="Blues", vmin=0, vmax=100, cbar=(k_ == 3), cbar_ax=cax if k_ == 3 else None, square=True,
                        cbar_kws={"label": t("% theo hàng (nhãn thật)", "% of row (true class)")}, linewidths=1.5, linecolor="white", annot_kws={"fontsize": 9})
            ax.set_xticklabels(CL, rotation=30, ha="right"); ax.set_yticklabels(CL, rotation=0)
            ax.set_title(tr(m), fontsize=11.5, fontweight="bold" if m == "Random Forest" else "normal"); ax.set_xlabel(t("Dự đoán", "Predicted"))
        axs[0].set_ylabel(t("Nhãn thật", "True class"))
        cm = confusion_matrix(O.y, O["Random Forest"], labels=K); pc = cm / cm.sum(1, keepdims=True); sym = pc + pc.T; np.fill_diagonal(sym, 0)
        i, j = np.unravel_index(sym.argmax(), sym.shape)
        title(fig, axs[0], t(f"Nhầm lẫn chủ yếu giữa {CLS[i]} và {CLS[j]}", f"Most confusion is between {tr(CLS[i])} and {tr(CLS[j])}"),
              t("Ma trận nhầm (CV khối 5 km, lần lặp 0): % theo hàng và số ô · 3 mô hình đứng đầu và Random Forest",
                "Confusion matrices (5 km block CV, repeat 0): row % and cell counts · top 3 models and Random Forest"))
        save(fig, "E1_confusion_top4.png")
    else:
        print("   bỏ qua ma trận nhầm: chưa có E1_oof_rep0.csv (chạy experiments.py --only E1)")

    # ---------------- E2: loại bỏ đặc trưng ----------------
    A = pd.read_csv(OUT / "E2_ablation.csv"); full = A.BA[A.feature_set.str.startswith("Đủ")].iloc[0]
    grp = lambda s: ("Đủ 12 đặc trưng" if s.startswith("Đủ") else "Bỏ một nhóm" if s.startswith("Bỏ") else
                     "Một phân cực" if s.startswith("Chỉ H") else "Ít ngày ảnh" if ("ngày" in s.lower()) else "Chỉ trung bình")
    GC = {"Đủ 12 đặc trưng": "#3b6ea8", "Bỏ một nhóm": "#7fa7d1", "Một phân cực": "#e39b45", "Ít ngày ảnh": "#c4453c", "Chỉ trung bình": "#9c8ac0"}
    A["g"] = A.feature_set.map(grp); A = A.sort_values("BA", ascending=False).reset_index(drop=True)
    A["lab"] = A.feature_set.map(tr); A["glab"] = A.g.map(tr)
    fig, ax = plt.subplots(figsize=(10, 5.4))
    sns.barplot(data=A, y="lab", x=A.BA * 100, hue="glab", palette={tr(k): v for k, v in GC.items()}, dodge=False, ax=ax, width=0.7)
    ax.errorbar(A.BA * 100, np.arange(len(A)), xerr=A.BA_sd * 100, fmt="none", ecolor=INK, lw=1, capsize=2)
    for i, r in A.iterrows():
        d = (r.BA - full) * 100
        ax.text(r.BA * 100 + 0.35, i, f"{r.BA*100:.1f}" + ("" if abs(d) < 0.05 else f"  ({d:+.1f})"), va="center", fontsize=9.5, color=INK)
    ax.axvline(full * 100, color="#3b6ea8", ls="--", lw=1); ax.set_xlim(78, 97); ax.set_ylabel("")
    ax.set_xlabel(t("BA (%) · Random Forest, CV khối 5 km, 5 lần lặp", "BA (%) · Random Forest, 5 km block CV, 5 repeats"))
    ax.legend(title="", loc="lower right"); ax.grid(axis="y", visible=False)
    title(fig, ax, t("Đa thời gian và hai phân cực đóng góp nhiều nhất", "Multi-temporal data and both polarisations contribute most"),
          t("BA khi chỉ dùng một phần đặc trưng; số trong ngoặc = chênh lệch so với đủ 12 đặc trưng; vạch = độ lệch chuẩn qua 5 lần lặp",
            "BA with feature subsets; value in brackets = difference from all 12 features; bars = SD over 5 repeats"))
    save(fig, "E2_ablation.png")

    # ---------------- E3: độ quan trọng hoán vị ----------------
    P = pd.read_csv(OUT / "E3_permutation_importance.csv").sort_values("dBA_mean", ascending=False).reset_index(drop=True)
    pg = lambda f: "HV" if f.startswith(("HV_", "std_HV")) else "HH" if f.startswith(("HH_", "std_HH")) or f == "texture" else "Tỷ số HV−HH"
    P["g"] = P.feature.map(pg).map(tr); P["lab"] = P.feature.map(tr)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=P, y="lab", x=P.dBA_mean * 100, hue="g", palette={"HV": "#3b6ea8", "HH": "#e39b45", tr("Tỷ số HV−HH"): "#9c8ac0"}, dodge=False, ax=ax, width=0.7)
    ax.errorbar(P.dBA_mean * 100, np.arange(len(P)), xerr=P.dBA_sd_folds * 100, fmt="none", ecolor=INK, lw=1, capsize=2)
    ax.axvline(0, color=MUTED, lw=0.8); ax.set_ylabel(""); ax.grid(axis="y", visible=False)
    ax.set_xlabel(t("BA giảm (điểm %) khi xáo trộn một đặc trưng", "BA drop (points) when one feature is shuffled"))
    ax.legend(title=t("Phân cực", "Polarisation"), loc="lower right")
    title(fig, ax, t(f"{P.lab.iloc[0]} là đặc trưng quan trọng nhất", f"{P.lab.iloc[0]} is the most important feature"),
          t("Độ quan trọng hoán vị trên fold kiểm tra (RF, CV khối 5 km) · vạch = độ lệch chuẩn giữa 5 fold · đặc trưng tương quan chia nhau độ quan trọng",
            "Permutation importance on test folds (RF, 5 km block CV) · bars = SD across 5 folds · correlated features share importance"))
    save(fig, "E3_permutation_importance.png")

    # ---------------- E4: cách kiểm chứng ----------------
    V = pd.read_csv(OUT / "E4_validation_schemes.csv"); order = list(dict.fromkeys(V.scheme))
    V["slab"] = V.scheme.map(tr); V["mlab"] = V.model.map(tr); olab = [tr(s) for s in order]
    fig, ax = plt.subplots(figsize=(12.5, 5.4))
    zones = [(0, 1, t("Rò rỉ / lạc quan", "Leaky / optimistic"), "#fbe3e1"), (2, 8, t("Chia theo khối không gian", "Spatial blocks"), "#e6eef7"),
             (9, 11, t("Chia theo vùng lớn", "Large regions"), "#fdf1dc")]
    for a, b, lab, c in zones:
        ax.axvspan(a - 0.5, b + 0.5, color=c, lw=0, zorder=0); ax.text((a + b) / 2, 97.6, lab, ha="center", fontsize=9.5, color=MUTED)
    sns.pointplot(data=V, x="slab", y=V.BA * 100, hue="mlab", order=olab, ax=ax, markers=["o", "s", "D", "^"], linestyles="-",
                  palette=sns.color_palette("deep", V.model.nunique()), markersize=6, linewidth=1.8)
    ax.set_xticks(range(len(olab)), olab, rotation=32, ha="right"); ax.set_ylim(81, 98.5); ax.set_xlabel(""); ax.set_ylabel("BA (%)")
    i5 = order.index("Khối 5 km")
    ax.annotate(t("cách chia chính", "main scheme"), (i5, V[V.scheme == "Khối 5 km"].BA.min() * 100 - 0.4), (i5, 87.2),
                ha="center", fontsize=9, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.legend(title="", loc="lower left", ncol=4)
    title(fig, ax, t("Độ chính xác giảm khi tập kiểm tra càng xa tập huấn luyện", "Accuracy falls as test data get farther from training data"),
          t("Cùng dữ liệu và mô hình, chỉ đổi cách chia train/test · chia vùng lớn còn lẫn ảnh hưởng của nhãn phân bố lệch giữa các vùng",
            "Same data and models, only the train/test split changes · large-region splits are also affected by uneven label distribution across regions"))
    save(fig, "E4_validation_schemes.png")

    D = pd.read_csv(OUT / "E4_accuracy_by_distance.csv"); D = D[D.scheme.str.startswith("Khối")].copy()
    D["mid"] = np.where(np.isinf(D.hi), D.lo * 1.6, np.sqrt(np.maximum(D.lo, 10) * D.hi))
    fig, ax = plt.subplots(figsize=(8.5, 4.8)); pal = dict(zip(D.scheme.unique(), ["#3b6ea8", "#c4453c"]))
    for sch, g in D.groupby("scheme", sort=False):
        ax.plot(g.mid, g.BA * 100, color=pal[sch], lw=2, label=tr(sch), zorder=2)
        for _, r in g.iterrows():
            big = r.n >= 100
            ax.scatter(r.mid, r.BA * 100, s=60, color=pal[sch] if big else "white", edgecolor=pal[sch], lw=1.6, zorder=3)
            ax.text(r.mid, r.BA * 100 + (0.9 if sch.endswith("5 km") else -1.5), f"n={r.n}", fontsize=8, color=pal[sch], ha="center")
    ax.set_xscale("log"); ax.set_xticks([30, 100, 300, 1000, 3000, 10000], ["30 m", "100 m", "300 m", "1 km", "3 km", "10 km"]); ax.minorticks_off()
    ax.set_xlabel(t("Khoảng cách từ ô kiểm tra tới ô huấn luyện gần nhất (thang log)", "Distance from test cell to nearest training cell (log scale)"))
    ax.set_ylabel("BA (%)"); ax.set_ylim(86, 102); ax.legend(title=t("CV theo", "CV by"), loc="lower left")
    title(fig, ax, t("Trong CV khối, độ chính xác giảm khi ô kiểm tra xa nhãn hơn (đến khoảng 5 km)",
                     "In block CV, accuracy declines as test cells get farther from labels (up to about 5 km)"),
          t("Random Forest, lần lặp 0 · điểm rỗng: ít hơn 100 ô, kém tin cậy · 44% diện tích AOI cách nhãn trên 2 km",
            "Random Forest, repeat 0 · hollow points: fewer than 100 cells, less reliable · 44% of the AOI lies more than 2 km from any label"))
    save(fig, "E4_accuracy_by_distance.png")

    # ---------------- E5: đường học ----------------
    L = pd.read_csv(OUT / "E5_learning_curve.csv"); L["n_poly_tb"] = L.groupby("frac").n_poly.transform("mean")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    sns.lineplot(data=L, x="n_poly_tb", y=L.BA * 100, errorbar="sd", marker="o", ax=ax, color="#3b6ea8", linewidth=2.2, err_kws={"alpha": 0.18})
    for x, v in (L.groupby("n_poly_tb").BA.mean() * 100).items(): ax.text(x, v + 1.0, f"{v:.1f}", ha="center", fontsize=9, color=INK)
    ax.set_xlabel(t("Số polygon huấn luyện (trung bình mỗi fold)", "Training polygons (mean per fold)"))
    ax.set_ylabel(t("BA (%) trên fold kiểm tra", "BA (%) on test folds")); ax.set_ylim(78, 97)
    title(fig, ax, t("Thêm nhãn cùng kiểu gần như không cải thiện", "Adding more labels of the same kind barely helps"),
          t("Đường học, RF, CV khối 5 km × 3 lần lặp · vùng tô = ±1 độ lệch chuẩn giữa các fold",
            "Learning curve, RF, 5 km block CV × 3 repeats · band = ±1 SD across folds"))
    save(fig, "E5_learning_curve.png")

    # ---------------- E6: tinh chỉnh lồng ----------------
    T = pd.read_csv(OUT / "E6_nested_tuning.csv")
    fig, ax = plt.subplots(figsize=(8, 3.2))
    for i, r in T.iterrows():
        ax.plot([r.BA_default * 100, r.BA_tuned * 100], [i, i], color="#bbbbbb", lw=3, zorder=1)
        ax.scatter(r.BA_default * 100, i, s=90, color="#9aa5b1", zorder=2, label=t("Mặc định", "Default") if i == 0 else None)
        ax.scatter(r.BA_tuned * 100, i, s=90, color="#3b6ea8", zorder=3, label=t("Sau tinh chỉnh", "Tuned") if i == 0 else None)
        ax.text(max(r.BA_default, r.BA_tuned) * 100 + 0.12, i, f"{(r.BA_tuned-r.BA_default)*100:+.1f} " + t("điểm", "pts"), va="center", fontsize=9.5)
    ax.set_yticks(range(len(T)), [tr(m) for m in T.model]); ax.set_ylim(len(T) - 0.4, -0.6); ax.set_xlim(92, 95); ax.set_xlabel("BA (%)")
    ax.grid(axis="y", visible=False); ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=2)
    mx = (T.BA_tuned - T.BA_default).abs().max() * 100
    title(fig, ax, t(f"Tinh chỉnh siêu tham số thay đổi BA tối đa {mx:.1f} điểm", f"Hyperparameter tuning changes BA by at most {mx:.1f} points"),
          t("CV lồng: ngoài = khối 5 km, trong = GroupKFold 3 theo khối, chọn theo BA",
            "Nested CV: outer = 5 km blocks, inner = 3-fold GroupKFold by block, selected by BA"))
    save(fig, "E6_nested_tuning.png")

    # ---------------- E7: diện tích + đồng thuận ----------------
    Ar = pd.read_csv(OUT / "E7_area_by_model.csv")
    mode_r = rasterio.open(DER / "landcover_model_mode.tif").read(1); nval = (mode_r > 0).sum()
    cons = {"model": "Đồng thuận (lớp đa số)", **{c: (mode_r == k).sum() / nval * 100 for k, c in zip(K, CLS)}}
    Ar = pd.concat([pd.DataFrame([cons]), Ar], ignore_index=True)
    fig, ax = plt.subplots(figsize=(11, 5.6)); left = np.zeros(len(Ar)); ylab = [tr(m) for m in Ar.model]
    for c in CLS:
        ax.barh(ylab, Ar[c], left=left, color=CLASS_COL[c], label=tr(c), height=0.72, edgecolor="white", lw=1)
        for i, (l, v) in enumerate(zip(left, Ar[c])):
            if v >= 4: ax.text(l + v / 2, i, f"{v:.1f}", ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        left += Ar[c].values
    ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xlabel(t("% diện tích AOI", "% of AOI area")); ax.grid(axis="y", visible=False)
    ax.get_yticklabels()[0].set_fontweight("bold"); ax.axhline(0.5, color=INK, lw=0.8)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    title(fig, ax, t("Tỷ lệ diện tích ổn định giữa các mô hình, nhưng chưa được kiểm chứng", "Area shares are stable across models, but not validated"),
          t("% diện tích dự đoán của từng lớp trên toàn AOI · mọi mô hình học từ cùng tập nhãn nên có thể cùng thiên lệch",
            "Predicted share of each class over the AOI · all models learn from the same labels and may share the same bias"))
    save(fig, "E7_area_by_model.png")

    PA = pd.read_csv(OUT / "E7_pairwise_agreement.csv", index_col=0).iloc[1:, :-1]   # bỏ hàng đầu/cột cuối vốn trống
    PA.index = [tr(m) for m in PA.index]; PA.columns = [tr(m) for m in PA.columns]
    fig, ax = plt.subplots(figsize=(9, 7.5))
    sns.heatmap(PA, mask=np.triu(np.ones_like(PA, bool), k=1), annot=True, fmt=".0f", cmap="rocket_r", vmin=70, vmax=100, square=True, ax=ax,
                cbar_kws={"label": t("% ô AOI cùng lớp", "% of AOI cells in agreement"), "shrink": 0.75}, linewidths=1, linecolor="white", annot_kws={"fontsize": 9})
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right"); ax.set_xlabel(""); ax.set_ylabel("")
    title(fig, ax, t("Mô hình dạng cây gần nhau, LDA và QDA khác biệt nhất", "Tree-based models agree most; LDA and QDA differ most"),
          t("% ô trong AOI mà hai mô hình dự đoán cùng một lớp", "% of AOI cells where two models predict the same class"))
    save(fig, "E7_pairwise_agreement.png")

    # ---------------- bản đồ ----------------
    cmap_lc = ListedColormap([CLASS_COL[c] for c in CLS]); norm_lc = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5], 4)
    agree, ext = read2(DER / "landcover_model_agreement.tif"); mode2, _ = read2(DER / "landcover_model_mode.tif")
    fig, axs = plt.subplots(1, 2, figsize=(15, 8.2))
    axs[0].imshow(np.ma.masked_equal(mode2, 0), cmap=cmap_lc, norm=norm_lc, extent=ext, interpolation="nearest"); aoi_lines(axs[0]); frame(axs[0])
    axs[0].legend(handles=[Patch(color=CLASS_COL[c], label=f"{tr(c)} ({(mode_r==k).sum()/nval*100:.1f}%)") for k, c in zip(K, CLS)],
                  loc="upper right", bbox_to_anchor=(1.0, 0.86), title=t("Lớp đa số (10 mô hình)", "Majority class (10 models)"),
                  title_fontsize=10, frameon=True, framealpha=0.9)
    axs[0].set_title(t("Bản đồ lớp phủ đồng thuận", "Consensus land-cover map"), fontsize=12.5)
    cm_ag = ListedColormap(sns.color_palette("RdYlGn", 6)); norm_ag = BoundaryNorm([0.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5], 6)
    im = axs[1].imshow(np.ma.masked_equal(agree, 0), cmap=cm_ag, norm=norm_ag, extent=ext, interpolation="nearest"); aoi_lines(axs[1]); frame(axs[1])
    cb = fig.colorbar(im, ax=axs[1], shrink=0.6, fraction=0.035, pad=0.01, ticks=[3, 6, 7, 8, 9, 10]); cb.ax.set_yticklabels(["≤5", "6", "7", "8", "9", "10"])
    cb.set_label(t("Số mô hình đồng ý với lớp đa số (/10)", "Models agreeing with the majority class (/10)"))
    pa = (agree == 10).sum() / (agree > 0).sum() * 100
    axs[1].set_title(t(f"Mức đồng thuận: cả 10 mô hình cùng lớp ở {pa:.1f}% AOI", f"Agreement: all 10 models agree on {pa:.1f}% of the AOI"), fontsize=12.5)
    title(fig, axs[0], t("Bản đồ lớp phủ chỉ từ SAR NISAR và độ tin cậy giữa các mô hình", "Land cover from NISAR SAR only, with between-model agreement"),
          t("Lưới 20 m, tỉnh Hưng Yên · 10 mô hình huấn luyện trên cùng 3.918 ô nhãn · diện tích chưa hiệu chỉnh, lớp Đô thị kém tin cậy nhất",
            "20 m grid, Hưng Yên province · 10 models trained on the same 3,918 labelled cells · areas not bias-corrected; Built-up is the least reliable class"))
    save(fig, "E7_agreement_map.png")

    E8 = pd.read_csv(OUT / "E8_area_of_applicability.csv").iloc[0]
    di, ext = read2(DER / "aoa_dissimilarity.tif"); thr = E8.threshold
    fig = plt.figure(figsize=(18, 7.6)); gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.55], wspace=0.22)
    a0, a1, a2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
    im = a0.imshow(di, cmap="mako_r", vmin=0, vmax=2 * thr, extent=ext, interpolation="nearest"); aoi_lines(a0); frame(a0)
    cb = fig.colorbar(im, ax=a0, shrink=0.55, fraction=0.035, pad=0.01, extend="max"); cb.ax.axhline(thr, color="#c4453c", lw=2)
    cb.set_label(t("Chỉ số khác biệt DI", "Dissimilarity index DI"))
    a0.set_title(t("Khác biệt so với mẫu huấn luyện (DI)", "Dissimilarity to training data (DI)"), fontsize=12.5)
    lc2, _ = read2(DER / "landcover_sar_20m.tif")
    a1.imshow(np.ma.masked_equal(lc2, 0) > 0, cmap=ListedColormap(["#dcdcdc"]), extent=ext, interpolation="nearest")
    a1.imshow(np.ma.masked_where(~(di > thr), np.ones_like(di)), cmap=ListedColormap(["#c4453c"]), extent=ext, interpolation="nearest")
    aoi_lines(a1); frame(a1)
    a1.set_title(t(f"Ngoài vùng áp dụng (DI > {thr:.2f}): {E8.outside_pct:.1f}% AOI", f"Outside the area of applicability (DI > {thr:.2f}): {E8.outside_pct:.1f}% of AOI"), fontsize=12.5)
    a1.legend(handles=[Patch(color="#c4453c", label=t("Ngoài vùng áp dụng", "Outside AOA")), Patch(color="#dcdcdc", label=t("Trong vùng áp dụng", "Inside AOA"))],
              loc="upper right", bbox_to_anchor=(1.0, 0.86), frameon=True, framealpha=0.9)
    B = pd.DataFrame({"g": [tr("Vùng S2 sạch"), tr("Vùng mây")] + [tr(c) for c in CLS],
                      "pct": [E8.outside_clear_pct, E8.outside_cloudy_pct] + [E8[f"outside_pred_{c}"] for c in CLS]})
    sns.barplot(data=B, y="g", x="pct", hue="g", palette=["#8fa9c7", "#5a7896"] + [CLASS_COL[c] for c in CLS], ax=a2, legend=False, width=0.65)
    for i, v in enumerate(B.pct): a2.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9.5)
    a2.axvline(E8.outside_pct, color=MUTED, ls="--", lw=1); a2.text(E8.outside_pct + 0.3, 5.45, t("toàn AOI", "whole AOI"), fontsize=8.5, color=MUTED)
    a2.set_xlim(0, max(B.pct) * 1.25); a2.set_ylabel(""); a2.grid(axis="y", visible=False); a2.axhline(1.5, color=MUTED, lw=0.8)
    a2.set_xlabel(t("% ô nằm ngoài vùng áp dụng", "% of cells outside the AOA"))
    a2.set_title(t("Theo vùng và theo lớp dự đoán", "By area and by predicted class"), fontsize=12.5)
    title(fig, a0, t(f"Mô hình áp dụng được ở {100-E8.outside_pct:.0f}% diện tích tỉnh, vùng mây cũng như vùng sạch",
                     f"The model is applicable to {100-E8.outside_pct:.0f}% of the province, in cloudy and clear areas alike"),
          t("Area of Applicability (Meyer & Pebesma 2021): khoảng cách trong không gian đặc trưng SAR, trọng số = độ quan trọng hoán vị; DI đo mức giống mẫu huấn luyện, không đo độ đúng",
            "Area of Applicability (Meyer & Pebesma 2021): distance in SAR feature space weighted by permutation importance; DI measures similarity to training data, not correctness"))
    save(fig, "E8_area_of_applicability.png")


def export_tables():
    """Bảng CSV tiếng Anh (dịch nhãn và tên cột) vào en/tables; CSV gốc tiếng Việt giữ nguyên ở outputs/experiments."""
    d = OUT / "en/tables"; d.mkdir(parents=True, exist_ok=True); print("[en/tables]")
    for p in sorted(OUT.glob("*.csv")):
        df = pd.read_csv(p, index_col=0 if p.name == "E7_pairwise_agreement.csv" else None)
        tr_df(df).to_csv(d / p.name, index=p.name == "E7_pairwise_agreement.csv"); print("  ", p.name)


langs = [a for a in sys.argv[1:] if a in ("vi", "en")] or ["vi", "en"]
for lg in langs: draw(lg)
if "en" in langs: export_tables()
print("xong")
