from pathlib import Path
import numpy as np
import pandas as pd
from dbfread import DBF

# ---------------------------------------------------------
# Build merged household-level Susenas dataset for title 2:
# "Klasifikasi Defisit Kalori Rumah Tangga Berbasis AKG"
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "DATA SUSENAS"
OUT_CSV = ROOT / "Klasifikasi_Kalori_RT.csv"


def read_dbf(path: str | Path) -> pd.DataFrame:
    table = DBF(str(path), ignore_missing_memofile=True)
    return pd.DataFrame(iter(table))


def mode_or_nan(series: pd.Series) -> float:
    s = series.dropna()
    if s.empty:
        return np.nan
    return s.mode(dropna=True).iloc[0]


# 1) Load raw files
kp43 = read_dbf(DATA_DIR / "link 2" / "32_ssn_202403_kp_blok43.dbf")
rt = read_dbf(DATA_DIR / "link 1" / "b_34976_2025_05_14_11_09_07_ssn202403_kor_rt.dbf")
ind1 = read_dbf(DATA_DIR / "link 1" / "b_34976_2025_05_14_11_05_39_ssn202403_kor_ind1.dbf")
ind2 = read_dbf(DATA_DIR / "link 1" / "b_34976_2025_05_14_11_07_40_ssn202403_kor_ind2.dbf")
kp41 = read_dbf(DATA_DIR / "link 2" / "32_ssn_202403_kp_blok41.dbf")

# 2) Select needed columns
kp43_cols = [
    "URUT","WI1","WI2","R101","R102","R105","R203","R301",
    "FOOD","NONFOOD","EXPEND","KAPITA","KALORI_KAP","PROTE_KAP",
    "LEMAK_KAP","KARBO_KAP","WERT","WEIND"
]
rt_cols = [
    "URUT","PSU","SSU","STRATA","WI1","WI2","R101","R102","R105",
    "R1701","R1702","R1703","R1704","R1705","R1706","R1707","R1708",
    "R1801","R1802","R1803","R1804","R1805","R1806A","R1806B","R1807",
    "R1808","R1809A","R1809B","R1809C","R1809D","R1809E","R1810A","R1810B",
    "R1810C","R1811A","R1811B","R1812","R1813A","R1813B","R1813C","R1813D",
    "R1813E","R1814A","R1814B","R1814C","R1815A","R1815B","R1815C",
    "R2001A","R2001B","R2001C","R2001D","R2001E","R2001F",
    "R2202","R2203","R2207","R2209A","R2209B","R2209C","R2209D"
]
ind1_cols = [
    "URUT","PSU","SSU","STRATA","WI1","WI2","R101","R102","R105",
    "R401","R403","R404","R405","R407","R614","R707","R706",
    "R1207"
]
ind2_cols = [
    "URUT","R401","R1401","R1402","R1403","R1418"
]

kp43 = kp43[kp43_cols].copy()
rt = rt[rt_cols].copy()
ind1 = ind1[ind1_cols].copy()
ind2 = ind2[ind2_cols].copy()

# 3) Merge individual tables
ind = ind1.merge(ind2, on=["URUT", "R401"], how="left")

# 4) Prepare individual-level variables
ind["R405"] = pd.to_numeric(ind["R405"], errors="coerce")
ind["R407"] = pd.to_numeric(ind["R407"], errors="coerce")
ind["R614"] = pd.to_numeric(ind["R614"], errors="coerce")
ind["R707"] = pd.to_numeric(ind["R707"], errors="coerce")
ind["R706"] = pd.to_numeric(ind["R706"], errors="coerce")
ind["R1207"] = pd.to_numeric(ind["R1207"], errors="coerce")
ind["R1401"] = pd.to_numeric(ind["R1401"], errors="coerce")
if "R1418" in ind.columns:
    ind["R1418"] = pd.to_numeric(ind["R1418"], errors="coerce")

# Age in months:
# - use R1401 for under-five children
# - otherwise R407 * 12
ind["age_months"] = np.where(
    ind["R1401"].notna(),
    ind["R1401"],
    ind["R407"].mul(12)
)

# Household composition indicators
ind["is_balita"] = (ind["age_months"] < 60).astype(int)
ind["is_anak_5_17"] = ((ind["age_months"] >= 60) & (ind["age_months"] < 204)).astype(int)
ind["is_lansia_60plus"] = (ind["age_months"] >= 60 * 12).astype(int)
ind["is_perokok"] = ind["R1207"].isin([1, 2]).astype(int)

# JKN indicator: convert all R1101_* columns if present later; here not yet in first data file
# For title-2 starter dataset, keep raw individual table; household model can be expanded later.

# 5) Aggregate to household level
agg = (
    ind.groupby("URUT", as_index=True)
    .agg(
        n_art=("R401", "count"),
        n_balita=("is_balita", "sum"),
        n_anak_5_17=("is_anak_5_17", "sum"),
        n_lansia_60=("is_lansia_60plus", "sum"),
        n_perokok=("is_perokok", "sum"),
        mean_age_months=("age_months", "mean"),
        krt_sex=("R405", lambda s: mode_or_nan(s)),
        krt_age_yr=("R407", lambda s: mode_or_nan(s)),
        krt_edu=("R614", lambda s: mode_or_nan(s)),
        krt_job=("R707", lambda s: mode_or_nan(s)),
        krt_sector=("R706", lambda s: mode_or_nan(s))
    )
    .reset_index()
)

# 6) Compute cigarette spending from block 41
kp41 = kp41.copy()
# KLP values for tobacco expenditure follow the plan: 192, 193, 194, 195, 196, 197
kp41["KLP"] = pd.to_numeric(kp41.get("KLP", pd.Series(np.nan, index=kp41.index)), errors="coerce")
kp41["B41K10"] = pd.to_numeric(kp41.get("B41K10", pd.Series(np.nan, index=kp41.index)), errors="coerce")

rokok = kp41[kp41["KLP"].isin([192, 193, 194, 195, 196, 197])].copy()
rokok["rokok_bln"] = rokok["B41K10"].fillna(0) * (30 / 7)

rokok_agg = (
    rokok.groupby("URUT", as_index=True)[["rokok_bln"]]
    .sum()
    .reset_index()
    .rename(columns={"rokok_bln": "rokok_bln"})
)
rokok_agg["ada_rokok"] = (rokok_agg["rokok_bln"] > 0).astype(int)

# 7) Merge to household file
final = kp43.merge(rt, on=["URUT"], how="left")
final = final.merge(agg, on="URUT", how="left")
final = final.merge(rokok_agg, on="URUT", how="left")

# 8) Add a simple target placeholder for AKG classification logic
# This is intentionally kept raw so the next step can compute the precise AKG target.
final["defisit_akg"] = np.nan
final["kebutuhan_akg_rumahtangga"] = np.nan
final["konsumsi_akg_rumahtangga"] = np.nan

# 9) Save CSV
final.to_csv(OUT_CSV, index=False)
print(f"Saved merged dataset to: {OUT_CSV}")
print(final.shape)
print(final.columns[:20].tolist())
print(final.columns[-15:].tolist())
