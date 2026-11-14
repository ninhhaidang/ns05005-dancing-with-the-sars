"""Thí nghiệm so sánh cho bộ phân loại lớp phủ chỉ dùng SAR (nhãn polygon, ô 20 m thuần).

CHỈ SỐ CHÍNH (chốt trước khi chạy): độ chính xác cân bằng lớp (BA) theo CV khối không gian 5 km, 5 fold x 5 lần lặp.
Mọi mô hình dùng chung các fold. Siêu tham số mặc định hợp lý, KHÔNG tinh chỉnh trên chính CV này (E6 tinh chỉnh lồng riêng).

E1 So sánh mô hình (BA, OA, F1 macro, kappa, F1 từng lớp; CI 95% bootstrap theo khối; hiệu so với RF; McNemar)
E2 Loại bỏ đặc trưng (ablation) với Random Forest
E3 Độ quan trọng hoán vị (permutation importance) trên fold kiểm tra
E4 Cách kiểm chứng: ngẫu nhiên theo ô -> theo polygon -> khối 1/2/5/10/20 km -> chia vùng Tây/Đông, Bắc/Nam, 4 góc
E5 Đường học (số polygon huấn luyện -> BA)
E6 Tinh chỉnh siêu tham số lồng (nested CV) cho RF, SVM, LightGBM/HistGB
E7 Mức bản đồ: huấn luyện trên toàn bộ mẫu, dự đoán toàn AOI, so diện tích từng lớp giữa mô hình và bản đồ đồng thuận

Ra: outputs/experiments/*.csv, *.png; data/derived/landcover_model_{agreement,mode}.tif
Chạy: /Users/ninhhaidang/miniconda3/envs/dwts/bin/python -I scripts/experiments.py [--only E1,E4]
"""
import sys, time, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, pandas as pd, rasterio
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix, f1_score
from sklearn.model_selection import GridSearchCV, GroupKFold, StratifiedGroupKFold, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.class_weight import compute_sample_weight
from statsmodels.stats.contingency_tables import mcnemar
from sar_dataset import ROOT, NAMES, FNAMES, load

warnings.filterwarnings("ignore")
ONLY = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
run = lambda e: ONLY is None or e in ONLY
OUT = ROOT / "outputs/experiments"; OUT.mkdir(parents=True, exist_ok=True)
K = [1, 2, 3, 4]; R = 5; SEED = 0
t0 = time.time()
d = load(verbose=False)
xs, y, rows, cols, poly = d["xs"], d["y"], d["rows"], d["cols"], d["poly"]
blk = lambda km: (rows // (km * 50)) * 10000 + cols // (km * 50)
B5 = blk(5)
print(f"mẫu {len(y)} | " + ", ".join(f"{NAMES[k]} {(y == k).sum()}" for k in K) + f" | polygon {len(np.unique(poly))} | khối 5 km {len(np.unique(B5))} | {time.time()-t0:.0f}s")


# ---------------- mô hình ----------------
class Enc(BaseEstimator, ClassifierMixin):
    """Bọc mô hình cần nhãn 0..n-1 (XGBoost/LightGBM/CatBoost) và cân bằng lớp bằng sample_weight."""
    def __init__(self, est=None, balance=True): self.est, self.balance = est, balance
    def fit(self, X, y):
        self.classes_ = np.unique(y); yi = np.searchsorted(self.classes_, y)
        sw = compute_sample_weight("balanced", yi) if self.balance else None
        self.est_ = clone(self.est).fit(X, yi, sample_weight=sw); return self
    def predict(self, X): return self.classes_[np.asarray(self.est_.predict(X)).astype(int).ravel()]
    def predict_proba(self, X): return self.est_.predict_proba(X)

MODELS = {
    "Mốc: lớp đông nhất": lambda: DummyClassifier(strategy="most_frequent"),
    "Cây quyết định (sâu 4)": lambda: DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=SEED),
    "Maximum Likelihood (QDA)": lambda: QuadraticDiscriminantAnalysis(priors=[.25] * 4, reg_param=1e-3),
    "LDA": lambda: LinearDiscriminantAnalysis(priors=[.25] * 4),
    "Hồi quy logistic": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, class_weight="balanced")),
    "k-NN (k=15)": lambda: make_pipeline(StandardScaler(), KNeighborsClassifier(15)),
    "SVM (RBF)": lambda: make_pipeline(StandardScaler(), SVC(C=10, gamma="scale", class_weight="balanced")),
    "MLP (64-32)": lambda: make_pipeline(StandardScaler(), MLPClassifier((64, 32), max_iter=1000, early_stopping=True, random_state=SEED)),
    "Random Forest": lambda: RandomForestClassifier(300, min_samples_leaf=2, class_weight="balanced", random_state=SEED, n_jobs=-1),
    "Extra Trees": lambda: ExtraTreesClassifier(300, min_samples_leaf=2, class_weight="balanced", random_state=SEED, n_jobs=-1),
    "HistGradientBoosting": lambda: HistGradientBoostingClassifier(class_weight="balanced", random_state=SEED),
}
try:
    from xgboost import XGBClassifier
    MODELS["XGBoost"] = lambda: Enc(XGBClassifier(n_estimators=400, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                                                   tree_method="hist", n_jobs=8, random_state=SEED, verbosity=0))
except Exception as e: print("không dùng được xgboost:", str(e)[:80])
try:
    from lightgbm import LGBMClassifier
    MODELS["LightGBM"] = lambda: Enc(LGBMClassifier(n_estimators=400, learning_rate=0.05, num_leaves=31, subsample=0.8, subsample_freq=1,
                                                     colsample_bytree=0.8, random_state=SEED, n_jobs=8, verbose=-1))
except Exception as e: print("không dùng được lightgbm:", str(e)[:80])
try:
    from catboost import CatBoostClassifier
    MODELS["CatBoost"] = lambda: Enc(CatBoostClassifier(iterations=500, depth=6, learning_rate=0.05, random_seed=SEED, verbose=0, thread_count=8))
except Exception as e: print("không dùng được catboost:", str(e)[:80])


# ---------------- tiện ích ----------------
def ba_fast(yt, yp):
    return np.mean([(yp[yt == k] == k).mean() for k in K if (yt == k).any()])

def metrics(yt, yp):
    f1c = f1_score(yt, yp, labels=K, average=None, zero_division=0)
    return dict(BA=ba_fast(yt, yp), OA=accuracy_score(yt, yp), F1_macro=f1c.mean(), kappa=cohen_kappa_score(yt, yp),
                **{f"F1_{NAMES[k]}": f for k, f in zip(K, f1c)})

def oof(make, X, splits):
    p = np.zeros(len(y), int); seen = np.zeros(len(y), bool)
    for a, b in splits: p[b] = make().fit(X[a], y[a]).predict(X[b]); seen[b] = True
    return p, seen

def sgkf(groups, r, k=5): return list(StratifiedGroupKFold(k, shuffle=True, random_state=r).split(xs, y, groups))

def boot_blocks(preds, n=2000, seed=SEED):
    """BA bootstrap theo khối 5 km (lấy lại khối có hoàn lại). preds: dict tên -> dự đoán OOF."""
    ub = np.unique(B5); idx = [np.where(B5 == b)[0] for b in ub]; rng = np.random.default_rng(seed)
    res = {m: np.empty(n) for m in preds}
    for i in range(n):
        ii = np.concatenate([idx[j] for j in rng.integers(0, len(ub), len(ub))])
        for m, p in preds.items(): res[m][i] = ba_fast(y[ii], p[ii])
    return res

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"figure.dpi": 110, "font.size": 9})
COL = ["#2b6cb0", "#68a03f", "#d6b370", "#c0392b"]


# ================= E0: kiểm tra dữ liệu / nguy cơ rò rỉ =================
if run("E0"):
    print("\n=== E0 Kiểm tra dữ liệu: polygon sát nhau, phân bố mẫu theo khối, phân tầng fold ===")
    import pyogrio
    from shapely import wkb, STRtree
    meta, fid, gw, fl = pyogrio.raw.read(ROOT / "labeling/labels_polygon.gpkg"); C = np.array(dict(zip(meta["fields"], fl))["class_id"])
    geoms = [wkb.loads(bytes(w)) for w in gw]; tree = STRtree(geoms); rec = []
    for i, g in enumerate(geoms):
        cand = [j for j in tree.query(g.buffer(1000)) if j != i]
        ds = [(g.distance(geoms[j]), C[j] == C[i]) for j in cand]
        rec.append(dict(cls=C[i], d_any=min([a for a, _ in ds], default=np.inf), d_same=min([a for a, s in ds if s], default=np.inf),
                        d_other=min([a for a, s in ds if not s], default=np.inf)))
    Q = pd.DataFrame(rec); Q.to_csv(OUT / "E0_polygon_nearest.csv", index=False)
    for col, lab in [("d_any", "polygon bất kỳ"), ("d_same", "polygon CÙNG lớp"), ("d_other", "polygon KHÁC lớp")]:
        print(f"  khoảng cách tới {lab:18s} gần nhất: chạm (0 m) {(Q[col]==0).mean()*100:4.1f}% | ≤20 m {(Q[col]<=20).mean()*100:4.1f}% | "
              f"≤100 m {(Q[col]<=100).mean()*100:4.1f}% | ≤500 m {(Q[col]<=500).mean()*100:4.1f}% | trung vị {np.median(Q[col][np.isfinite(Q[col])]):.0f} m")
    vc = pd.Series(B5).value_counts()
    print(f"  mẫu trên {len(vc)} khối 5 km: trung vị {vc.median():.0f} ô/khối, khối lớn nhất {vc.max()} ô; 10 khối đông nhất chứa {vc.iloc[:10].sum()/len(y)*100:.0f}% mẫu")
    print("  số khối 5 km có mẫu của từng lớp: " + ", ".join(f"{NAMES[k]} {len(np.unique(B5[y==k]))}" for k in K))
    print("  số mẫu từng lớp trong mỗi fold kiểm tra (CV khối 5 km, lần 0):")
    for i, (a, b) in enumerate(sgkf(B5, 0)): print(f"    fold {i}: " + " ".join(f"{NAMES[k]} {(y[b]==k).sum():4d}" for k in K))


# ================= E1: so sánh mô hình =================
if run("E1"):
    print("\n=== E1 So sánh mô hình: CV khối 5 km, 5 fold x %d lần ===" % R)
    splits = [sgkf(B5, r) for r in range(R)]
    rows_, oof0, times = [], {}, {}
    for name, make in MODELS.items():
        t = time.time()
        for r in range(R):
            p, _ = oof(make, xs, splits[r]); rows_.append(dict(model=name, rep=r, **metrics(y, p)))
            if r == 0: oof0[name] = p
        times[name] = (time.time() - t) / (R * 5)
        m = pd.DataFrame([x for x in rows_ if x["model"] == name])
        print(f"  {name:26s} BA {m.BA.mean()*100:5.1f} ± {m.BA.std()*100:3.1f} | OA {m.OA.mean()*100:5.1f} | F1 {m.F1_macro.mean()*100:5.1f} | kappa {m.kappa.mean():.3f} | {times[name]:.2f}s/fit")
    df = pd.DataFrame(rows_); df.to_csv(OUT / "E1_models_by_repeat.csv", index=False)
    boot = boot_blocks(oof0)
    ref = "Random Forest"; summ = []
    for name in MODELS:
        m = df[df.model == name]; diff = boot[name] - boot[ref]
        tab = np.array([[np.sum((oof0[ref] == y) & (oof0[name] == y)), np.sum((oof0[ref] == y) & (oof0[name] != y))],
                        [np.sum((oof0[ref] != y) & (oof0[name] == y)), np.sum((oof0[ref] != y) & (oof0[name] != y))]])
        pval = mcnemar(tab, exact=False, correction=True).pvalue if name != ref else np.nan
        summ.append(dict(model=name, BA_mean=m.BA.mean(), BA_sd_repeats=m.BA.std(), BA_ci_lo=np.percentile(boot[name], 2.5), BA_ci_hi=np.percentile(boot[name], 97.5),
                         OA=m.OA.mean(), F1_macro=m.F1_macro.mean(), kappa=m.kappa.mean(),
                         **{c: m[c].mean() for c in df.columns if c.startswith("F1_") and c != "F1_macro"},
                         dBA_vs_RF=diff.mean(), dBA_ci_lo=np.percentile(diff, 2.5), dBA_ci_hi=np.percentile(diff, 97.5),
                         mcnemar_p_vs_RF=pval, sec_per_fit=times[name]))
    S = pd.DataFrame(summ).sort_values("BA_mean", ascending=False); S.to_csv(OUT / "E1_models_summary.csv", index=False)
    print("\n  Xếp hạng theo BA (CI 95% bootstrap theo khối | hiệu BA so với RF, CI 95% | McNemar p, lạc quan vì mẫu tương quan không gian):")
    for _, s in S.iterrows():
        print(f"  {s.model:26s} {s.BA_mean*100:5.1f} [{s.BA_ci_lo*100:4.1f}-{s.BA_ci_hi*100:4.1f}] | Δ {s.dBA_vs_RF*100:+5.1f} [{s.dBA_ci_lo*100:+4.1f},{s.dBA_ci_hi*100:+4.1f}] | p={s.mcnemar_p_vs_RF:.3g}")
    # hình: BA từng mô hình
    fig, ax = plt.subplots(figsize=(7, 0.35 * len(S) + 1)); S2 = S.iloc[::-1]
    ax.barh(S2.model, S2.BA_mean * 100, color=["#c0392b" if m == ref else "#4a6fa5" for m in S2.model])
    ax.errorbar(S2.BA_mean * 100, range(len(S2)), xerr=[(S2.BA_mean - S2.BA_ci_lo) * 100, (S2.BA_ci_hi - S2.BA_mean) * 100], fmt="none", ecolor="k", capsize=2, lw=1)
    ax.axvline(25, ls=":", c="gray"); ax.set_xlabel("Độ chính xác cân bằng lớp (%), CV khối 5 km; vạch = CI 95% bootstrap theo khối")
    ax.set_xlim(0, 100); ax.set_title("E1. So sánh mô hình (cùng 12 đặc trưng SAR, cùng fold)"); fig.tight_layout(); fig.savefig(OUT / "E1_models.png")
    # hình: ma trận nhầm (chuẩn hóa theo hàng) cho 4 mô hình tốt nhất
    top = [m for m in S.model if not m.startswith("Mốc")][:4]
    fig, axs = plt.subplots(1, len(top), figsize=(3.2 * len(top), 3.2))
    for ax, m in zip(np.atleast_1d(axs), top):
        cm = confusion_matrix(y, oof0[m], labels=K, normalize="true") * 100
        ax.imshow(cm, cmap="Blues", vmin=0, vmax=100)
        for i in range(4):
            for j in range(4): ax.text(j, i, f"{cm[i, j]:.0f}", ha="center", va="center", color="w" if cm[i, j] > 60 else "k")
        ax.set_xticks(range(4), [NAMES[k] for k in K], rotation=45, ha="right"); ax.set_yticks(range(4), [NAMES[k] for k in K]); ax.set_title(m, fontsize=9)
    fig.suptitle("Ma trận nhầm (% theo hàng = nhãn thật), CV khối 5 km lần lặp 0"); fig.tight_layout(); fig.savefig(OUT / "E1_confusion_top4.png")
    print(f"  [{time.time()-t0:.0f}s]")


# ================= E2: loại bỏ đặc trưng =================
if run("E2"):
    print("\n=== E2 Loại bỏ đặc trưng (Random Forest, CV khối 5 km, 5 lần) ===")
    I = {n: i for i, n in enumerate(FNAMES)}
    def cols_(*names): return lambda X: X[:, [I[n] for n in names]]
    def day(dd): return lambda X: np.c_[X[:, I[f"HH_{dd}"]], X[:, I[f"HV_{dd}"]], X[:, I[f"HV_{dd}"]] - X[:, I[f"HH_{dd}"]]]
    SETS = {
        "Đủ 12 đặc trưng": lambda X: X,
        "Chỉ HH (6)": cols_("HH_1022", "HH_1027", "HH_1103", "HH_tb", "std_HH", "texture"),
        "Chỉ HV (5)": cols_("HV_1022", "HV_1027", "HV_1103", "HV_tb", "std_HV"),
        "Một ngày 22/10 (HH, HV, HV-HH)": day("1022"),
        "Một ngày 27/10, quỹ đạo lên": day("1027"),
        "Một ngày 3/11": day("1103"),
        "Hai ngày quỹ đạo xuống (22/10, 3/11)": cols_("HH_1022", "HH_1103", "HV_1022", "HV_1103"),
        "Chỉ trung bình (HH_tb, HV_tb, HV-HH)": cols_("HH_tb", "HV_tb", "HV-HH"),
        "Bỏ kết cấu": lambda X: np.delete(X, I["texture"], 1),
        "Bỏ độ lệch chuẩn thời gian": lambda X: np.delete(X, [I["std_HH"], I["std_HV"]], 1),
    }
    splits = [sgkf(B5, r) for r in range(R)]; out = []
    for name, f in SETS.items():
        Xf = f(xs); v = [metrics(y, oof(MODELS["Random Forest"], Xf, splits[r])[0]) for r in range(R)]
        m = pd.DataFrame(v); out.append(dict(feature_set=name, n_feat=Xf.shape[1], BA=m.BA.mean(), BA_sd=m.BA.std(), OA=m.OA.mean(), F1_macro=m.F1_macro.mean(),
                                            **{c: m[c].mean() for c in m.columns if c.startswith("F1_") and c != "F1_macro"}))
        print(f"  {name:38s} ({Xf.shape[1]:2d}) BA {m.BA.mean()*100:5.1f} ± {m.BA.std()*100:3.1f} | " + " ".join(f"{NAMES[k]} {m['F1_'+NAMES[k]].mean()*100:4.1f}" for k in K))
    A = pd.DataFrame(out); A.to_csv(OUT / "E2_ablation.csv", index=False)
    fig, ax = plt.subplots(figsize=(7, 4)); A2 = A.iloc[::-1]
    ax.barh(A2.feature_set, A2.BA * 100, xerr=A2.BA_sd * 100, color="#4a6fa5", capsize=2); ax.set_xlim(40, 100)
    ax.set_xlabel("BA (%), RF, CV khối 5 km (vạch = độ lệch chuẩn qua 5 lần lặp)"); ax.set_title("E2. Đóng góp của nhóm đặc trưng")
    fig.tight_layout(); fig.savefig(OUT / "E2_ablation.png"); print(f"  [{time.time()-t0:.0f}s]")


# ================= E3: độ quan trọng hoán vị =================
if run("E3"):
    print("\n=== E3 Độ quan trọng hoán vị (RF, trên fold kiểm tra, giảm BA khi xáo trộn 1 đặc trưng) ===")
    imp = []
    for a, b in sgkf(B5, 0):
        m = MODELS["Random Forest"]().fit(xs[a], y[a])
        r = permutation_importance(m, xs[b], y[b], scoring="balanced_accuracy", n_repeats=10, random_state=SEED, n_jobs=-1)
        imp.append(r.importances_mean)
    imp = np.array(imp); PERM_W = np.clip(imp.mean(0), 0, None); P = pd.DataFrame(dict(feature=FNAMES, dBA_mean=imp.mean(0), dBA_sd_folds=imp.std(0))).sort_values("dBA_mean", ascending=False)
    P.to_csv(OUT / "E3_permutation_importance.csv", index=False)
    for _, s in P.iterrows(): print(f"  {s.feature:9s} {s.dBA_mean*100:5.2f} ± {s.dBA_sd_folds*100:4.2f} điểm BA")
    print("  (đặc trưng tương quan mạnh với nhau thì độ quan trọng riêng lẻ bị chia nhỏ; xem thêm E2)")
    fig, ax = plt.subplots(figsize=(6, 4)); P2 = P.iloc[::-1]
    ax.barh(P2.feature, P2.dBA_mean * 100, xerr=P2.dBA_sd_folds * 100, color="#4a6fa5", capsize=2)
    ax.set_xlabel("BA giảm (điểm %) khi xáo trộn đặc trưng"); ax.set_title("E3. Độ quan trọng hoán vị (RF, fold kiểm tra)")
    fig.tight_layout(); fig.savefig(OUT / "E3_permutation_importance.png"); print(f"  [{time.time()-t0:.0f}s]")


# ================= E4: cách kiểm chứng =================
if run("E4"):
    print("\n=== E4 Ảnh hưởng của cách kiểm chứng (cùng dữ liệu, cùng mô hình) ===")
    E4M = [m for m in ["Random Forest", "LightGBM" if "LightGBM" in MODELS else "HistGradientBoosting", "SVM (RBF)", "Hồi quy logistic"] if m in MODELS]
    def halves(v):
        mid = np.median(v); a = np.where(v < mid)[0]; b = np.where(v >= mid)[0]; return [(a, b), (b, a)]
    def quads():
        q = (rows >= np.median(rows)).astype(int) * 2 + (cols >= np.median(cols)).astype(int)
        return [(np.where(q != i)[0], np.where(q == i)[0]) for i in range(4)]
    from scipy.spatial import cKDTree
    XY = np.c_[cols * 20.0, rows * 20.0]
    def buffered(sp, buf):
        """Bỏ các ô TRAIN cách ô TEST gần nhất < buf m (chặn rò rỉ qua cửa sổ làm trơn 3x3 / kết cấu 7x7 ở ranh giới khối)."""
        return [(a[cKDTree(XY[b]).query(XY[a])[0] >= buf], b) for a, b in sp]
    SCH = [("Ngẫu nhiên theo ô (rò rỉ)", lambda r: list(StratifiedKFold(5, shuffle=True, random_state=r).split(xs, y)), 3),
           ("Theo polygon", lambda r: sgkf(poly, r), 3),
           ("Khối 1 km", lambda r: sgkf(blk(1), r), 3), ("Khối 2 km", lambda r: sgkf(blk(2), r), 3), ("Khối 5 km", lambda r: sgkf(B5, r), 3),
           ("Khối 5 km + đệm 250 m", lambda r: buffered(sgkf(B5, r), 250), 3), ("Khối 5 km + đệm 1 km", lambda r: buffered(sgkf(B5, r), 1000), 3),
           ("Khối 10 km", lambda r: sgkf(blk(10), r), 3), ("Khối 20 km", lambda r: sgkf(blk(20), r), 3),
           ("Chia Tây / Đông", lambda r: halves(cols), 1), ("Chia Bắc / Nam", lambda r: halves(rows), 1), ("4 góc phần tư", lambda r: quads(), 1)]
    out = []; DIST = {}
    for sname, mk, reps in SCH:
        sp0 = mk(0); dd = np.full(len(y), np.nan)
        for a, b in sp0: dd[b] = cKDTree(XY[a]).query(XY[b])[0]
        for mname in E4M:
            v = []
            for r in range(reps):
                sp = sp0 if r == 0 else mk(r); p, seen = oof(MODELS[mname], xs, sp); v.append(metrics(y[seen], p[seen]))
                if r == 0 and mname == "Random Forest": DIST[sname] = (dd, p)
            m = pd.DataFrame(v); out.append(dict(scheme=sname, model=mname, BA=m.BA.mean(), OA=m.OA.mean(), F1_macro=m.F1_macro.mean(), reps=reps,
                                                 median_dist_test_to_train_m=np.nanmedian(dd)))
        print(f"  {sname:24s} (k/c test→train trung vị {np.nanmedian(dd):6.0f} m) " + " | ".join(f"{mn} {o['BA']*100:5.1f}" for mn, o in zip(E4M, out[-len(E4M):])))
    # độ chính xác theo khoảng cách tới ô train gần nhất (RF, lần 0)
    bins = [0, 30, 100, 500, 2000, 5000, np.inf]; rowsd = []
    print("  RF: BA theo khoảng cách từ ô test tới ô train gần nhất (m):")
    for sname in ["Ngẫu nhiên theo ô (rò rỉ)", "Theo polygon", "Khối 5 km", "Khối 20 km"]:
        dd, p = DIST[sname]; s = f"    {sname:24s}"
        for lo, hi in zip(bins[:-1], bins[1:]):
            mm = (dd >= lo) & (dd < hi)
            if mm.sum() >= 30: s += f" [{lo:.0f}-{hi:.0f}) {ba_fast(y[mm], p[mm])*100:4.1f} (n={mm.sum()})"; rowsd.append(dict(scheme=sname, lo=lo, hi=hi, n=mm.sum(), BA=ba_fast(y[mm], p[mm])))
        print(s)
    pd.DataFrame(rowsd).to_csv(OUT / "E4_accuracy_by_distance.csv", index=False)
    V = pd.DataFrame(out); V.to_csv(OUT / "E4_validation_schemes.csv", index=False)
    # số mẫu từng lớp mỗi nửa vùng (để biết lớp nào bị thiếu khi chia vùng)
    for nm, v in [("Tây/Đông", cols), ("Bắc/Nam", rows)]:
        mid = np.median(v); print(f"  mẫu theo lớp, {nm}: " + " ; ".join(f"{NAMES[k]} {((y==k)&(v<mid)).sum()}/{((y==k)&(v>=mid)).sum()}" for k in K))
    fig, ax = plt.subplots(figsize=(8, 4)); order = [s for s, _, _ in SCH]
    for mname in E4M:
        sub = V[V.model == mname].set_index("scheme").loc[order]; ax.plot(range(len(order)), sub.BA * 100, "o-", label=mname)
    ax.set_xticks(range(len(order)), order, rotation=35, ha="right"); ax.set_ylabel("BA (%)"); ax.legend(fontsize=8)
    ax.set_title("E4. Độ chính xác phụ thuộc mức độ độc lập không gian giữa train và test"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(OUT / "E4_validation_schemes.png"); print(f"  [{time.time()-t0:.0f}s]")


# ================= E5: đường học =================
if run("E5"):
    print("\n=== E5 Đường học: tỷ lệ polygon dùng để huấn luyện (RF, CV khối 5 km, 3 lần) ===")
    FR = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]; out = []
    for r in range(3):
        rng = np.random.default_rng(100 + r)
        for a, b in sgkf(B5, r):
            up = np.unique(poly[a])
            for f in FR:
                keep = rng.choice(up, max(int(round(f * len(up))), 4), replace=False); aa = a[np.isin(poly[a], keep)]
                if len(np.unique(y[aa])) < 4: continue
                p = MODELS["Random Forest"]().fit(xs[aa], y[aa]).predict(xs[b]); out.append(dict(rep=r, frac=f, n_poly=len(keep), n_cells=len(aa), BA=ba_fast(y[b], p)))
    L = pd.DataFrame(out); L.to_csv(OUT / "E5_learning_curve.csv", index=False)
    G = L.groupby("frac").agg(n_poly=("n_poly", "mean"), BA=("BA", "mean"), sd=("BA", "std"))
    for f, s in G.iterrows(): print(f"  {f*100:4.0f}% polygon (~{s.n_poly:4.0f}) -> BA {s.BA*100:5.1f} ± {s.sd*100:3.1f}")
    fig, ax = plt.subplots(figsize=(5.5, 3.8)); ax.errorbar(G.n_poly, G.BA * 100, yerr=G.sd * 100, fmt="o-", capsize=3)
    ax.set_xlabel("Số polygon huấn luyện (trung bình mỗi fold)"); ax.set_ylabel("BA (%) trên fold kiểm tra"); ax.grid(alpha=.3)
    ax.set_title("E5. Đường học (RF, CV khối 5 km)"); fig.tight_layout(); fig.savefig(OUT / "E5_learning_curve.png"); print(f"  [{time.time()-t0:.0f}s]")


# ================= E6: tinh chỉnh lồng =================
if run("E6"):
    print("\n=== E6 Tinh chỉnh siêu tham số lồng: ngoài = CV khối 5 km (lần 0), trong = GroupKFold 3 theo khối ===")
    GB = "LightGBM" if "LightGBM" in MODELS else "HistGradientBoosting"
    GRIDS = {"Random Forest": {"max_features": ["sqrt", 0.5, 1.0], "min_samples_leaf": [1, 2, 5]},
             "SVM (RBF)": {"svc__C": [1, 10, 100], "svc__gamma": ["scale", 0.03, 0.3]}}
    GRIDS[GB] = ({"est__num_leaves": [15, 31, 63], "est__learning_rate": [0.03, 0.1]} if GB == "LightGBM"
                 else {"max_leaf_nodes": [15, 31, 63], "learning_rate": [0.03, 0.1]})
    out = []
    for mname, grid in GRIDS.items():
        pd_, pt_, chosen = np.zeros(len(y), int), np.zeros(len(y), int), []
        for a, b in sgkf(B5, 0):
            pd_[b] = MODELS[mname]().fit(xs[a], y[a]).predict(xs[b])
            gs = GridSearchCV(MODELS[mname](), grid, cv=GroupKFold(3), scoring="balanced_accuracy", n_jobs=1).fit(xs[a], y[a], groups=B5[a])
            pt_[b] = gs.predict(xs[b]); chosen.append(str(gs.best_params_))
        out.append(dict(model=mname, BA_default=ba_fast(y, pd_), BA_tuned=ba_fast(y, pt_), chosen=" | ".join(chosen)))
        print(f"  {mname:22s} mặc định {out[-1]['BA_default']*100:5.1f} -> tinh chỉnh {out[-1]['BA_tuned']*100:5.1f} | tham số chọn mỗi fold: {chosen}")
    pd.DataFrame(out).to_csv(OUT / "E6_nested_tuning.csv", index=False); print(f"  [{time.time()-t0:.0f}s]")


# ================= E7: mức bản đồ =================
if run("E7"):
    print("\n=== E7 Mức bản đồ: huấn luyện trên toàn bộ mẫu, dự đoán toàn AOI ===")
    ref_r, X, aoi = d["ref"], d["X"], d["aoi"]; idx = np.where(aoi); XA = X[idx]
    E7M = [m for m in ["Random Forest", "Extra Trees", "HistGradientBoosting", "XGBoost", "LightGBM", "CatBoost", "MLP (64-32)",
                       "Hồi quy logistic", "LDA", "Maximum Likelihood (QDA)"] if m in MODELS]
    P = np.zeros((len(E7M), len(idx[0])), np.uint8); area = []
    for i, m in enumerate(E7M):
        mdl = MODELS[m]().fit(xs, y)
        for s in range(0, len(idx[0]), 1_000_000): P[i, s:s + 1_000_000] = mdl.predict(XA[s:s + 1_000_000])
        area.append(dict(model=m, **{NAMES[k]: (P[i] == k).mean() * 100 for k in K}))
        print(f"  {m:26s} " + " ".join(f"{NAMES[k]} {(P[i]==k).mean()*100:5.1f}%" for k in K) + f" [{time.time()-t0:.0f}s]")
    Ar = pd.DataFrame(area); Ar.to_csv(OUT / "E7_area_by_model.csv", index=False)
    cnt = np.stack([(P == k).sum(0) for k in K]); mode = (cnt.argmax(0) + 1).astype(np.uint8); agree = cnt.max(0).astype(np.uint8)
    pair = np.array([[(P[i] == P[j]).mean() * 100 for j in range(len(E7M))] for i in range(len(E7M))])
    pd.DataFrame(pair, index=E7M, columns=E7M).round(1).to_csv(OUT / "E7_pairwise_agreement.csv")
    full = len(E7M)
    print(f"  ô mà cả {full} mô hình cùng lớp: {(agree == full).mean()*100:.1f}% AOI | ≤ {full//2} mô hình đồng ý: {(agree <= full//2).mean()*100:.1f}%")
    print("  diện tích theo bản đồ đồng thuận (lớp đa số): " + " ".join(f"{NAMES[k]} {(mode==k).mean()*100:.1f}%" for k in K))
    print(f"  khoảng diện tích giữa các mô hình (min-max %): " + " ; ".join(f"{NAMES[k]} {Ar[NAMES[k]].min():.1f}-{Ar[NAMES[k]].max():.1f}" for k in K))
    prof = ref_r.profile; prof.update(dtype="uint8", nodata=0, compress="deflate", predictor=2)
    for nm, arr in [("agreement", agree), ("mode", mode)]:
        o = np.zeros(ref_r.shape, np.uint8); o[idx] = arr
        with rasterio.open(ROOT / f"data/derived/landcover_model_{nm}.tif", "w", **prof) as f: f.write(o, 1)
    fig, ax = plt.subplots(figsize=(7, 0.4 * len(E7M) + 1.2)); left = np.zeros(len(E7M))
    for k, c in zip(K, COL): ax.barh(E7M, Ar[NAMES[k]], left=left, color=c, label=NAMES[k]); left += Ar[NAMES[k]].values
    ax.invert_yaxis(); ax.set_xlabel("% diện tích AOI"); ax.legend(ncol=4, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    ax.set_title("E7. Tỷ lệ diện tích dự đoán theo mô hình (chưa hiệu chỉnh)", pad=22); fig.tight_layout(); fig.savefig(OUT / "E7_area_by_model.png")
    o = np.full(ref_r.shape, np.nan, np.float32); o[idx] = agree
    fig, ax = plt.subplots(figsize=(7, 8)); im = ax.imshow(o[::2, ::2], cmap="RdYlGn", vmin=1, vmax=full, interpolation="nearest")
    plt.colorbar(im, ax=ax, shrink=0.6, label=f"số mô hình đồng ý với lớp đa số (/{full})"); ax.axis("off")
    ax.set_title("E7. Mức đồng thuận giữa các mô hình"); fig.tight_layout(); fig.savefig(OUT / "E7_agreement_map.png")
    print(f"  [{time.time()-t0:.0f}s]")

# ================= E8: vùng áp dụng được (Area of Applicability) =================
if run("E8"):
    print("\n=== E8 Vùng áp dụng được (Meyer & Pebesma 2021): ô AOI có đặc trưng SAR khác xa mẫu huấn luyện ===")
    from scipy.spatial import cKDTree
    from scipy.spatial.distance import pdist
    from rasterio.warp import reproject, Resampling
    ref_r, X, aoi = d["ref"], d["X"], d["aoi"]; idx = np.where(aoi)
    if "PERM_W" in globals() and PERM_W.sum() > 0: w = PERM_W; print("  trọng số = độ quan trọng hoán vị (E3)")
    else: w = MODELS["Random Forest"]().fit(xs, y).feature_importances_; print("  trọng số = độ quan trọng impurity của RF (chạy E3 để dùng hoán vị)")
    mu, sd = xs.mean(0), xs.std(0); Zt = (xs - mu) / sd * w
    rng = np.random.default_rng(SEED); dbar = pdist(Zt[rng.choice(len(Zt), min(3000, len(Zt)), replace=False)]).mean()
    di_cv = np.zeros(len(y)); p_cv = np.zeros(len(y), int)
    for a, b in sgkf(B5, 0):
        di_cv[b] = cKDTree(Zt[a]).query(Zt[b])[0] / dbar; p_cv[b] = MODELS["Random Forest"]().fit(xs[a], y[a]).predict(xs[b])
    q1, q3 = np.percentile(di_cv, [25, 75]); thr = q3 + 1.5 * (q3 - q1)
    print(f"  ngưỡng DI (râu trên boxplot của DI trong CV khối 5 km) = {thr:.3f}")
    qs = np.quantile(di_cv, [0, .25, .5, .75, 1])
    print("  BA CV theo nhóm DI (tứ phân vị): " + " | ".join(f"[{lo:.2f}-{hi:.2f}] {ba_fast(y[(di_cv>=lo)&(di_cv<=hi)], p_cv[(di_cv>=lo)&(di_cv<=hi)])*100:.1f}"
                                                     for lo, hi in zip(qs[:-1], qs[1:])))
    tree = cKDTree(Zt); ZA = (X[idx] - mu) / sd * w; di = np.empty(len(ZA), np.float32)
    for s in range(0, len(ZA), 500_000): di[s:s + 500_000] = tree.query(ZA[s:s + 500_000], workers=-1)[0] / dbar
    outside = di > thr
    g = rasterio.open(ROOT / "data/s2/gee_10m/S2_composite_10m_aoi.tif"); G = g.read()
    vm = ((G[5] > 0) & (G[:5] != 0).all(0)).astype("f4"); fr = np.zeros(ref_r.shape, "f4")
    reproject(vm, fr, src_transform=g.transform, src_crs=g.crs, dst_transform=ref_r.transform, dst_crs=ref_r.crs, resampling=Resampling.average)
    clear = fr[idx] >= 0.5
    print(f"  ngoài vùng áp dụng: {outside.mean()*100:.1f}% AOI | vùng S2 sạch (nơi có nhãn): {outside[clear].mean()*100:.1f}% | vùng mây: {outside[~clear].mean()*100:.1f}%")
    print(f"  DI trung vị: vùng sạch {np.median(di[clear]):.3f}, vùng mây {np.median(di[~clear]):.3f}")
    mp = rasterio.open(ROOT / "data/derived/landcover_sar_20m.tif").read(1)[idx]
    print("  % ngoài vùng áp dụng theo lớp dự đoán (RF): " + " ".join(f"{NAMES[k]} {outside[mp==k].mean()*100:.1f}%" for k in K))
    pd.DataFrame([dict(threshold=thr, outside_pct=outside.mean() * 100, outside_clear_pct=outside[clear].mean() * 100, outside_cloudy_pct=outside[~clear].mean() * 100,
                       **{f"outside_pred_{NAMES[k]}": outside[mp == k].mean() * 100 for k in K})]).to_csv(OUT / "E8_area_of_applicability.csv", index=False)
    prof = ref_r.profile; prof.update(dtype="float32", nodata=np.nan, compress="deflate", predictor=3)
    o = np.full(ref_r.shape, np.nan, np.float32); o[idx] = di
    with rasterio.open(ROOT / "data/derived/aoa_dissimilarity.tif", "w", **prof) as f: f.write(o, 1); f.update_tags(aoa_threshold=str(thr))
    fig, axs = plt.subplots(1, 2, figsize=(12, 7))
    im = axs[0].imshow(o[::2, ::2], cmap="magma_r", vmin=0, vmax=max(2 * thr, np.nanpercentile(o, 99))); plt.colorbar(im, ax=axs[0], shrink=.6, label="DI")
    axs[0].set_title("Chỉ số khác biệt DI so với mẫu huấn luyện"); axs[0].axis("off")
    m2 = np.full(ref_r.shape, np.nan); m2[idx] = outside; axs[1].imshow(m2[::2, ::2], cmap="RdYlGn_r", vmin=0, vmax=1, interpolation="nearest")
    axs[1].set_title(f"Ngoài vùng áp dụng (đỏ, DI > {thr:.2f}): {outside.mean()*100:.1f}% AOI"); axs[1].axis("off")
    fig.suptitle("E8. Vùng áp dụng được của mô hình RF"); fig.tight_layout(); fig.savefig(OUT / "E8_area_of_applicability.png")
    print(f"  [{time.time()-t0:.0f}s]")

print(f"\nxong sau {time.time()-t0:.0f}s; kết quả ở {OUT}")
