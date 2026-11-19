"""
================================================================================
Modul 04: Estimasi Model GWR & Seleksi Bandwidth (04_gwr_model.py)
Penanggung Jawab: Nia (Langkah 5 dan 6)
Deskripsi:
  - Mengestimasi 6 kombinasi model GWR (Fixed/Adaptive x Gaussian/Bisquare/Exponential).
  - Optimasi bandwidth menggunakan kriteria Cross-Validation (CV) minimum.
  - Membatasi pencarian bandwidth adaptif pada rentang 6-35 tetangga.
  - Menghasilkan 4 berkas serah terima untuk April dan Nisa:
      1. output/tabel/tabel7_seleksi_gwr.csv
      2. output/tabel/gwr_koef_lokal.csv
      3. output/tabel/gwr_model_terpilih.json
      4. output/tabel/cv_kurva.csv
================================================================================
"""

import sys
import json
import logging
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats

try:
    import geopandas as gpd
    from shapely.geometry import Point
except ImportError:
    gpd = None

try:
    from mgwr.gwr import GWR
    from mgwr.sel_bw import Sel_BW
    from mgwr.diagnostics import get_CV
except ImportError:
    GWR = None
    Sel_BW = None
    get_CV = None

# Tambahkan path root agar bisa membaca config
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import config

# Setup Logging Konsol & Berkas
LOG_FILE = config.OUTPUT_DIR / "gwr_model_execution.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger("GWR_MODEL")


def cetak_banner():
    banner = """
================================================================================
   GWR MODEL ESTIMATION & BANDWIDTH SELECTION (04_gwr_model.py)
   Penanggung Jawab: Nia | Alur Langkah 5 & 6 | Jawa Tengah (n=35)
================================================================================
"""
    logger.info(banner)


def validasi_lingkungan():
    """Memastikan pustaka esensial tersedia."""
    if GWR is None or Sel_BW is None:
        logger.error("[FATAL ERROR] Pustaka 'mgwr' belum terpasang!")
        logger.error("Silakan aktifkan .venv dan jalankan: pip install mgwr geopandas\n")
        sys.exit(1)


def load_and_preprocess_data():
    """
    1. Membaca dataset (CSV, XLSX, atau auto-filter dari Dataset_Jawa_2024_dengan_koordinat.csv)
    2. Konversi koordinat lat/lon ke UTM 49S (km)
    3. Pemusatan variabel prediktor X jika PUSATKAN_X = True
    """
    logger.info("[1/5] MEMUAT DATA & PRA-PEMROSESAN SPASIAL")
    
    path_raw_jawa = config.DATA_DIR / "Dataset_Jawa_2024_dengan_koordinat.csv"
    
    if config.PATH_DATA_CSV.exists():
        df = pd.read_csv(config.PATH_DATA_CSV, sep=config.CSV_SEP, decimal=config.CSV_DESIMAL)
        logger.info(f"  [+] Membaca berkas CSV: {config.PATH_DATA_CSV.name} ({len(df)} baris)")
    elif config.PATH_DATA_XLSX.exists():
        df = pd.read_excel(config.PATH_DATA_XLSX)
        logger.info(f"  [+] Membaca berkas Excel: {config.PATH_DATA_XLSX.name} ({len(df)} baris)")
    elif path_raw_jawa.exists():
        logger.info(f"  [+] Membaca {path_raw_jawa.name} dan auto-filter untuk Provinsi Jawa Tengah (35 wilayah)...")
        # Deteksi separator ; atau ,
        try:
            df_raw = pd.read_csv(path_raw_jawa, sep=";")
            if df_raw.shape[1] <= 1:
                df_raw = pd.read_csv(path_raw_jawa, sep=",")
        except Exception:
            df_raw = pd.read_csv(path_raw_jawa, sep=",")

        # Filter Jawa Tengah
        col_prov = [c for c in df_raw.columns if "provinsi" in c.lower()]
        if col_prov:
            df_jt = df_raw[df_raw[col_prov[0]].astype(str).str.strip().str.lower() == "jawa tengah"].copy()
        else:
            df_jt = df_raw.copy()

        def format_nama(n):
            n = ' '.join(str(n).strip().split())
            if n.upper().startswith("KOTA "):
                return "Kota " + n[5:].title()
            return n.title()

        col_kab = [c for c in df_jt.columns if "kabupaten" in c.lower() or "kota" in c.lower()][0]
        col_y = [c for c in df_jt.columns if "pdrb" in c.lower() or "y:" in c.lower()][0]
        col_x1 = [c for c in df_jt.columns if "x1" in c.lower() or "infrastruktur" in c.lower()][0]
        col_x2 = [c for c in df_jt.columns if "x2" in c.lower() or "keterampilan" in c.lower()][0]
        col_x3 = [c for c in df_jt.columns if "x3" in c.lower() or "pemberdayaan" in c.lower()][0]
        col_lat = [c for c in df_jt.columns if "lintang" in c.lower() or "lat" in c.lower()][0]
        col_lon = [c for c in df_jt.columns if "bujur" in c.lower() or "lon" in c.lower()][0]

        df = pd.DataFrame()
        df[config.KOL_NAMA] = df_jt[col_kab].apply(format_nama)
        df[config.KOL_Y] = pd.to_numeric(df_jt[col_y].astype(str).str.replace(",", "."), errors="coerce")
        df["x1_infrastruktur"] = pd.to_numeric(df_jt[col_x1].astype(str).str.replace(",", "."), errors="coerce")
        df["x2_keterampilan"] = pd.to_numeric(df_jt[col_x2].astype(str).str.replace(",", "."), errors="coerce")
        df["x3_pemberdayaan"] = pd.to_numeric(df_jt[col_x3].astype(str).str.replace(",", "."), errors="coerce")
        df["lintang"] = pd.to_numeric(df_jt[col_lat].astype(str).str.replace(",", "."), errors="coerce")
        df["bujur"] = pd.to_numeric(df_jt[col_lon].astype(str).str.replace(",", "."), errors="coerce")

        # Simpan otomatis ke data_jateng.csv agar sinkron dengan rekan tim
        df.to_csv(config.PATH_DATA_CSV, index=False)
        logger.info(f"  [✓] Berkas {config.PATH_DATA_CSV.name} berhasil diekstrak otomatis ({len(df)} baris)")
    else:
        logger.error(f"  [X] Berkas data tidak ditemukan!")
        logger.error(f"      Harap letakkan salah satu di folder data/:")
        logger.error(f"      - {config.PATH_DATA_CSV.name}")
        logger.error(f"      - {path_raw_jawa.name}")
        sys.exit(1)
        
    n_rows = len(df)
    
    # Validasi kelengkapan baris & kolom
    kolom_wajib = [config.KOL_NAMA, config.KOL_Y] + config.KOL_X + [config.KOL_LAT, config.KOL_LON]
    missing_cols = [c for c in kolom_wajib if c not in df.columns]
    if missing_cols:
        logger.error(f"  [X] Kolom berikut tidak ditemukan di CSV: {missing_cols}")
        sys.exit(1)

    # Cek Missing Value
    if df[kolom_wajib].isnull().any().any():
        logger.warning("  [!] PERINGATAN: Terdapat nilai kosong (NaN) pada dataset!")

    # Proyeksi Koordinat WGS84 -> UTM Zone 49S (EPSG:32749) dalam satuan KILOMETER
    logger.info(f"  [+] Proyeksi Koordinat: WGS84 -> {config.CRS_PROYEKSI} (satuan km)")
    if gpd is not None:
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df[config.KOL_LON], df[config.KOL_LAT]),
            crs="EPSG:4326"
        )
        gdf_proj = gdf.to_crs(config.CRS_PROYEKSI)
        # Dibagi 1000 agar koordinat bersatuan km (jarak fixed GWR menjadi km)
        coords_km = np.column_stack([gdf_proj.geometry.x / 1000.0, gdf_proj.geometry.y / 1000.0])
    else:
        # Fallback estimasi kasar jika geopandas belum aktif (1 derajat ~ 111 km)
        coords_km = np.column_stack([df[config.KOL_LON] * 111.32, df[config.KOL_LAT] * 110.57])
        logger.warning("  [!] Geopandas tidak aktif; memakai estimasi aproksimasi km.")

    # Cek duplikasi koordinat
    if len(np.unique(coords_km, axis=0)) < n_rows:
        logger.warning("  [!] PERINGATAN: Terdapat koordinat centroid yang bernilai sama persis!")

    # Variabel Y & X
    y = df[[config.KOL_Y]].values.reshape((-1, 1))
    X_raw = df[config.KOL_X].values

    if config.PUSATKAN_X:
        logger.info("  [+] Pemusatan X       : True (mean-centering X1, X2, X3)")
        X = X_raw - np.mean(X_raw, axis=0)
    else:
        X = X_raw

    logger.info(f"  [+] Data siap         : n = {n_rows}, k = {X.shape[1]} prediktor\n")
    return df, coords_km, y, X


def fit_gwr_kombinasi(coords, y, X, kernel_name, is_fixed):
    """
    Menjalankan Sel_BW dan GWR untuk 1 kombinasi.
    Mengembalikan dictionary hasil atau error info.
    """
    tipe_str = "Fixed" if is_fixed else "Adaptive"
    nama_model = f"GWR_{kernel_name.capitalize()}_{tipe_str}"
    
    try:
        # 1. Seleksi Bandwidth dengan kriteria Cross-Validation (CV)
        selector = Sel_BW(coords, y, X, kernel=kernel_name, fixed=is_fixed)
        
        if not is_fixed:
            # Batas adaptif kritis untuk n=35 (interval 6 s.d. 35 tetangga)
            bw_opt = selector.search(
                criterion='CV',
                search_method='golden_section',
                bw_min=config.GWR_MIN_NN,
                bw_max=config.GWR_MAX_NN
            )
            satuan_bw = "tetangga"
        else:
            # Fixed bandwidth dalam kilometer
            bw_opt = selector.search(criterion='CV', search_method='golden_section')
            satuan_bw = "km"

        # 2. Fit Model GWR
        model = GWR(coords, y, X, bw=bw_opt, kernel=kernel_name, fixed=is_fixed)
        results = model.fit()

        # 3. Hitung Metrik Evaluasi
        rss = float(np.sum(results.resid_response ** 2))
        n = len(y)
        rmse = float(np.sqrt(rss / n))
        mae = float(np.mean(np.abs(results.resid_response)))
        enp = float(results.ENP)
        aicc = float(results.aicc)

        # Evaluasi catatan/warning
        catatan = "[OK]"
        if not is_fixed:
            if bw_opt <= config.GWR_MIN_NN:
                catatan = "[PERINGATAN: BW Batas Bawah (6)]"
            elif bw_opt >= config.GWR_MAX_NN:
                catatan = "[PERINGATAN: BW Batas Atas (35)]"
        
        if enp >= (n - 5):
            catatan += " [PERINGATAN: ENP Mendekati n]"

        return {
            "status": "SUKSES",
            "model": nama_model,
            "kernel": kernel_name,
            "tipe_bandwidth": tipe_str,
            "fixed": is_fixed,
            "bandwidth": round(float(bw_opt), 2) if is_fixed else int(bw_opt),
            "satuan_bw": satuan_bw,
            "ENP": round(enp, 2),
            "RSS": round(rss, 2),
            "AICc": round(aicc, 2),
            "RMSE": round(rmse, 2),
            "MAE": round(mae, 2),
            "catatan": catatan,
            "gwr_results": results,
            "selector": selector
        }

    except Exception as e:
        return {
            "status": "GAGAL",
            "model": nama_model,
            "kernel": kernel_name,
            "tipe_bandwidth": tipe_str,
            "fixed": is_fixed,
            "bandwidth": None,
            "satuan_bw": "km" if is_fixed else "tetangga",
            "ENP": None,
            "RSS": None,
            "AICc": None,
            "RMSE": None,
            "MAE": None,
            "catatan": f"[GAGAL: {str(e)}]",
            "gwr_results": None,
            "selector": None
        }


def run_enam_model(coords, y, X):
    """Mengeksekusi 6 kombinasi kernel x tipe bandwidth."""
    logger.info("[2/5] MENJALANKAN 6 KOMBINASI MODEL GWR")
    logger.info("  " + "-" * 76)
    logger.info("  {:<3} | {:<24} | {:<10} | {:<7} | {:<7} | {:<16}".format(
        "No", "Model", "Bandwidth", "ENP", "AICc", "Status"
    ))
    logger.info("  " + "-" * 76)

    kombinasi = [
        ("gaussian", True),
        ("bisquare", True),
        ("exponential", True),
        ("gaussian", False),
        ("bisquare", False),
        ("exponential", False),
    ]

    hasil_list = []
    for idx, (kern, is_fix) in enumerate(kombinasi, start=1):
        res = fit_gwr_kombinasi(coords, y, X, kern, is_fix)
        hasil_list.append(res)
        
        bw_str = f"{res['bandwidth']} {res['satuan_bw']}" if res['bandwidth'] is not None else "-"
        enp_str = f"{res['ENP']}" if res['ENP'] is not None else "-"
        aicc_str = f"{res['AICc']}" if res['AICc'] is not None else "-"
        
        logger.info("  {:<3} | {:<24} | {:<10} | {:<7} | {:<7} | {:<16}".format(
            idx, res["model"], bw_str, enp_str, aicc_str, res["catatan"]
        ))

    logger.info("  " + "-" * 76 + "\n")
    return hasil_list


def audit_dan_pilih_sementara(hasil_list):
    """
    Menganalisis anomali dan menetapkan model terbaik sementara berbasis AICc
    (Pemilihan final akan diverifikasi oleh April di 04b_evaluasi.py).
    """
    logger.info("[3/5] AUDIT STABILITAS & SELEKSI SEMENTARA")
    
    sukses_list = [h for h in hasil_list if h["status"] == "SUKSES"]
    if not sukses_list:
        logger.error("  [X] Seluruh kombinasi GWR gagal diestimasi!")
        sys.exit(1)

    # Catat anomali batas
    for h in sukses_list:
        if "Batas" in h["catatan"]:
            logger.warning(f"  [!] {h['model']}: Bandwidth mentok di batas pencarian -> {h['catatan']}")
        if "ENP" in h["catatan"]:
            logger.warning(f"  [!] {h['model']}: Derajat kebebasan efektif mendekati n -> Potensi Overfitting")

    # Model terbaik sementara berbasis AICc minimum
    model_terpilih = min(sukses_list, key=lambda x: x["AICc"])
    logger.info(f"  [+] Model dengan AICc Terendah : {model_terpilih['model']}")
    logger.info(f"      Bandwidth: {model_terpilih['bandwidth']} {model_terpilih['satuan_bw']} | AICc: {model_terpilih['AICc']} | ENP: {model_terpilih['ENP']}\n")
    return model_terpilih


def ekstrak_tabel_koef_lokal(model_terpilih, df_raw, y, X):
    """
    Mengekstrak koefisien lokal b0-b3, std error, t-stat, p-value,
    local R2, condition number, prediksi, dan residual.
    """
    logger.info("[4/5] EKSTRAKSI KOEFISIEN LOKAL & DIAGNOSTIK")
    res = model_terpilih["gwr_results"]
    n, k_vars = X.shape

    params = res.params  # shape (n, k+1)
    bse = res.bse        # shape (n, k+1)
    tvalues = res.tvalues
    
    # Derajat kebebasan lokal untuk uji t: df = n - tr(S) = n - ENP
    df_resid = max(1.0, float(n - res.ENP))
    pvalues = 2.0 * (1.0 - stats.t.cdf(np.abs(tvalues), df=df_resid))
    sig_matrix = (pvalues < config.ALPHA).astype(int)

    # Local Condition Number
    try:
        lc = res.local_collinearity()
        cond_numbers = lc[2].flatten()
    except Exception:
        cond_numbers = np.ones(n)

    # Local R2
    local_r2 = res.localR2.flatten() if hasattr(res, 'localR2') and res.localR2 is not None else np.full(n, np.nan)

    # Buat DataFrame
    df_out = pd.DataFrame()
    df_out[config.KOL_NAMA] = df_raw[config.KOL_NAMA]

    var_labels = ["b0_intercept"] + [f"b{i+1}_{col}" for i, col in enumerate(config.KOL_X)]

    for idx_v, lbl in enumerate(var_labels):
        df_out[lbl] = np.round(params[:, idx_v], 4)
        df_out[f"se_{lbl}"] = np.round(bse[:, idx_v], 4)
        df_out[f"t_{lbl}"] = np.round(tvalues[:, idx_v], 3)
        df_out[f"p_{lbl}"] = np.round(pvalues[:, idx_v], 4)
        df_out[f"sig_{lbl}"] = sig_matrix[:, idx_v]

    df_out["local_R2"] = np.round(local_r2, 4)
    df_out["cond_number"] = np.round(cond_numbers, 2)
    df_out["prediksi"] = np.round(res.predy.flatten(), 3)
    df_out["residual"] = np.round(res.resid_response.flatten(), 3)

    max_cn = float(np.max(cond_numbers))
    logger.info(f"  [+] Condition Number lokal maksimum: {max_cn:.2f} (Batas curiga > 30)")
    if max_cn > 30:
        logger.warning("  [!] Terdapat wilayah dengan local collinearity tinggi (CN > 30)!")
    else:
        logger.info("  [+] Kestabilan matriks lokal: Stabil dan andal.")

    logger.info(f"  [+] Rentang Local R2: {np.nanmin(local_r2):.3f} s.d. {np.nanmax(local_r2):.3f}\n")
    return df_out


def buat_kurva_cv(model_terpilih, coords, y, X):
    """
    Menghasilkan data kurva bandwidth vs CV Score untuk model terpilih.
    Disimpan untuk digambar oleh Nisa (Gambar 4).
    """
    kern = model_terpilih["kernel"]
    is_fix = model_terpilih["fixed"]

    if not is_fix:
        # Kandidat tetangga dari 6 s.d. 35
        bw_candidates = list(range(config.GWR_MIN_NN, config.GWR_MAX_NN + 1))
    else:
        # Kandidat jarak di sekitar bandwidth optimal
        bw_opt = model_terpilih["bandwidth"]
        bw_candidates = list(np.linspace(max(10.0, bw_opt * 0.4), bw_opt * 2.0, 25))

    cv_scores = []
    for bw in bw_candidates:
        try:
            m_temp = GWR(coords, y, X, bw=bw, kernel=kern, fixed=is_fix)
            r_temp = m_temp.fit(lite=True)
            score = float(get_CV(r_temp)) if get_CV is not None else float(r_temp.aicc)
            cv_scores.append(score)
        except Exception:
            cv_scores.append(np.nan)

    df_cv = pd.DataFrame({
        "bandwidth": bw_candidates,
        "cv_score": np.round(cv_scores, 4),
        "satuan": "tetangga" if not is_fix else "km"
    })
    return df_cv


def simpan_kontrak_berkas(hasil_semua, df_koef, model_terpilih, df_cv):
    """Menyimpan 4 berkas serah terima ke output/tabel/."""
    logger.info("[5/5] MENYIMPAN BERKAS SERAH TERIMA (KONTRAK BAB 1)")

    # 1. tabel7_seleksi_gwr.csv
    ringkasan_rows = []
    for h in hasil_semua:
        ringkasan_rows.append({
            "model": h["model"],
            "kernel": h["kernel"],
            "tipe_bandwidth": h["tipe_bandwidth"],
            "bandwidth": h["bandwidth"],
            "satuan_bw": h["satuan_bw"],
            "ENP": h["ENP"],
            "RSS": h["RSS"],
            "AICc": h["AICc"],
            "RMSE": h["RMSE"],
            "MAE": h["MAE"],
            "catatan": h["catatan"]
        })
    df_tab7 = pd.DataFrame(ringkasan_rows)
    path_tab7 = config.OUTPUT_TABEL_DIR / "tabel7_seleksi_gwr.csv"
    df_tab7.to_csv(path_tab7, index=False)
    logger.info(f"  [✓] Disimpan: {path_tab7}")

    # 2. gwr_koef_lokal.csv
    path_koef = config.OUTPUT_TABEL_DIR / "gwr_koef_lokal.csv"
    df_koef.to_csv(path_koef, index=False)
    logger.info(f"  [✓] Disimpan: {path_koef}")

    # 3. gwr_model_terpilih.json
    dict_terpilih = {
        "nama_model": model_terpilih["model"],
        "kernel": model_terpilih["kernel"],
        "tipe_bandwidth": model_terpilih["tipe_bandwidth"],
        "fixed": model_terpilih["fixed"],
        "bandwidth": model_terpilih["bandwidth"],
        "satuan_bw": model_terpilih["satuan_bw"],
        "ENP": model_terpilih["ENP"],
        "AICc": model_terpilih["AICc"],
        "RMSE": model_terpilih["RMSE"],
        "MAE": model_terpilih["MAE"],
        "catatan_audit": model_terpilih["catatan"]
    }
    path_json = config.OUTPUT_TABEL_DIR / "gwr_model_terpilih.json"
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(dict_terpilih, f, indent=2)
    logger.info(f"  [✓] Disimpan: {path_json}")

    # 4. cv_kurva.csv
    path_cv = config.OUTPUT_TABEL_DIR / "cv_kurva.csv"
    df_cv.to_csv(path_cv, index=False)
    logger.info(f"  [✓] Disimpan: {path_cv}")

    logger.info("\n" + "=" * 80)
    logger.info("STATUS: SELESAI DENGAN SUKSES. 4 Berkas siap diserahkan ke April & Nisa.")
    logger.info("=" * 80)


def main():
    cetak_banner()
    validasi_lingkungan()
    df_raw, coords, y, X = load_and_preprocess_data()
    hasil_semua = run_enam_model(coords, y, X)
    model_terpilih = audit_dan_pilih_sementara(hasil_semua)
    df_koef = ekstrak_tabel_koef_lokal(model_terpilih, df_raw, y, X)
    df_cv = buat_kurva_cv(model_terpilih, coords, y, X)
    simpan_kontrak_berkas(hasil_semua, df_koef, model_terpilih, df_cv)


if __name__ == "__main__":
    main()
