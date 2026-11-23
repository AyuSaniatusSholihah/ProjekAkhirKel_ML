"""
Fungsi bersama untuk langkah OLS/Moran/EDA (src/utils.py).

Pra-pemrosesan di sini sengaja IDENTIK dengan load_and_preprocess_data() di 04_gwr_model.py:
  - koordinat bujur/lintang (EPSG:4326) -> config.CRS_PROYEKSI (UTM 49S), dibagi 1000 (satuan km)
  - y dari config.KOL_Y, X dari config.KOL_X
  - bila config.PUSATKAN_X: X dikurangi rata-rata kolom (mean-centering)
Kesamaan ini diuji oleh src/uji_konsistensi.py.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config


def muat_data():
    """Baca data/data_jawa.csv, validasi, dan kembalikan (df, coords_km, y, X)."""
    path = config.PATH_DATA_CSV
    if not path.exists():
        sys.exit(f"[X] Berkas data tidak ditemukan: {path}")
    df = pd.read_csv(path, sep=config.CSV_SEP, decimal=config.CSV_DESIMAL)

    wajib = [config.KOL_PROVINSI, config.KOL_NAMA, config.KOL_Y] + config.KOL_X + [config.KOL_LAT, config.KOL_LON]
    hilang = [c for c in wajib if c not in df.columns]
    if hilang:
        sys.exit(f"[X] Kolom tidak ditemukan di CSV: {hilang}")
    if df[wajib].isnull().any().any():
        sys.exit("[X] Ada nilai kosong (NaN) pada kolom wajib. Perbaiki data, jangan diimputasi.")
    if df.duplicated([config.KOL_PROVINSI, config.KOL_NAMA]).any():
        sys.exit("[X] Ada nama kabupaten/kota ganda dalam provinsi yang sama.")
    if len(df) != 119:
        sys.exit(f"[X] Jumlah baris = {len(df)}, seharusnya 119 (kab/kota se-Pulau Jawa).")

    import geopandas as gpd
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[config.KOL_LON], df[config.KOL_LAT]), crs="EPSG:4326")
    proj = gdf.to_crs(config.CRS_PROYEKSI)
    coords_km = np.column_stack([proj.geometry.x / 1000.0, proj.geometry.y / 1000.0])

    y = df[[config.KOL_Y]].values.reshape((-1, 1))
    X_raw = df[config.KOL_X].values
    X = X_raw - X_raw.mean(axis=0) if config.PUSATKAN_X else X_raw
    return df, coords_km, y, X


def bobot_knn(coords_km, k=None):
    """Bobot KNN (k = config.K_TETANGGA) pada koordinat km, baris distandarisasi. Memastikan tidak ada pulau."""
    import libpysal
    k = config.K_TETANGGA if k is None else k
    w = libpysal.weights.KNN.from_array(coords_km, k=k)
    w.transform = "r"
    if len(w.islands) > 0:
        sys.exit(f"[X] Bobot KNN memiliki pulau (tanpa tetangga): {w.islands}")
    return w


def moran(nilai, w, permutasi=999):
    """Moran's I dengan p-value normal dan permutasi. Seed = config.SEED (diset tepat sebelum permutasi)."""
    import esda
    np.random.seed(config.SEED)
    m = esda.Moran(np.asarray(nilai).ravel(), w, permutations=permutasi)
    return {"I": float(m.I), "E_I": float(m.EI), "z_norm": float(m.z_norm),
            "p_norm": float(m.p_norm), "p_sim": float(m.p_sim)}


def aicc_gaussian(rss, n, k):
    """
    AIC dan AICc model Gaussian dengan rumus yang SAMA dengan mgwr (mgwr.diagnostics.get_AICc):
        llf  = -n/2 * (log(2*pi) + log(RSS/n)) - n/2
        AIC  = -2*llf + 2*(k + 1)
        AICc = -2*llf + 2*n*(k + 1)/(n - k - 2)
    k = jumlah parameter termasuk intersep (OLS 3 prediktor: k = 4; GWR: k = tr(S) = ENP).
    """
    llf = -n / 2.0 * (np.log(2.0 * np.pi) + np.log(rss / n)) - n / 2.0
    aic = -2.0 * llf + 2.0 * (k + 1.0)
    aicc = -2.0 * llf + 2.0 * n * (k + 1.0) / (n - k - 2.0)
    return float(aic), float(aicc)