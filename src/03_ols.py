"""
================================================================================
Modul 03: Model Regresi Linear OLS (03_ols.py)           Penanggung jawab: Naya
================================================================================
Model   : Y = b0 + b1*X1 + b2*X2 + b3*X3 + e   (Y dan X dibaca dari config.py)
Catatan : X dipusatkan (config.PUSATKAN_X), jadi b0 = rata-rata Y pada skor rata-rata
          ketiga pilar, BUKAN nilai Y pada skor nol. Slope b1-b3 tidak berubah oleh pemusatan.

Keluaran (output/tabel/), kontrak dengan April dan Nisa:
  tabel5_ols.csv, metrik_ols.csv, tabel6_asumsi_ols.csv, residual_ols.csv
Definisi yang disamakan dengan 04_gwr_model.py agar perbandingan OLS vs GWR adil:
  RSS = sum(e^2); RMSE = sqrt(RSS/n); MAE = mean(|e|);
  AIC/AICc = rumus mgwr (lihat utils.aicc_gaussian), k = 4 parameter.
Angka tidak dibulatkan saat disimpan; pembulatan hanya untuk tampilan di log.
================================================================================
"""
import sys
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_white, het_breuschpagan
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
import utils

LOG_FILE = config.OUTPUT_DIR / "ols_execution.log"
logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")])
log = logging.getLogger("OLS")
ALPHA = config.ALPHA


def keputusan(p, terpenuhi_bila_p_besar=True):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return ""
    ok = p >= ALPHA if terpenuhi_bila_p_besar else p < ALPHA
    return "terpenuhi" if ok else "tidak terpenuhi"


def main():
    log.info("=" * 78)
    log.info("  MODEL OLS (03_ols.py) | Y = %s | prediktor = %s", config.KOL_Y, ", ".join(config.KOL_X))
    log.info("=" * 78)

    # ---------- data ----------
    df, coords, y, X = utils.muat_data()
    n, p = X.shape
    k = p + 1                                      # parameter termasuk intersep (= ENP OLS)
    nama_param = ["b0_intercept"] + [f"b{i + 1}_{c}" for i, c in enumerate(config.KOL_X)]   # label sama dengan GWR
    log.info("[1/4] Data: n = %d, prediktor = %d, X dipusatkan = %s", n, p, config.PUSATKAN_X)

    # ---------- estimasi OLS ----------
    Xd = sm.add_constant(X)
    m = sm.OLS(y.ravel(), Xd).fit()
    resid = m.resid
    rss = float(np.sum(resid ** 2))
    rmse = float(np.sqrt(rss / n))
    mae = float(np.mean(np.abs(resid)))
    aic, aicc = utils.aicc_gaussian(rss, n, k)

    # verifikasi rumus AICc terhadap mgwr (GWR dengan bandwidth sangat besar = OLS)
    try:
        from mgwr.gwr import GWR
        aicc_mgwr = float(GWR(coords, y, X, bw=1e9, kernel="gaussian", fixed=True).fit().aicc)
        assert abs(aicc - aicc_mgwr) < 1e-6, f"AICc OLS ({aicc}) != AICc mgwr bandwidth besar ({aicc_mgwr})"
        log.info("[2/4] Verifikasi AICc: OLS = %.4f | mgwr (bw sangat besar) = %.4f -> SAMA", aicc, aicc_mgwr)
    except ImportError:
        log.warning("[2/4] mgwr tidak terpasang; verifikasi AICc dilewati.")

    # ---------- tabel5_ols.csv ----------
    ci = m.conf_int()
    vif = [np.nan] + [float(variance_inflation_factor(Xd, i)) for i in range(1, k)]
    tab5 = pd.DataFrame({
        "variabel": nama_param, "koefisien": m.params, "std_error": m.bse, "t": m.tvalues, "p_value": m.pvalues,
        "ci_lower": ci[:, 0], "ci_upper": ci[:, 1], "vif": vif,
    })
    tab5["sig"] = (tab5["p_value"] < ALPHA).astype(int)

    # ---------- metrik_ols.csv ----------
    metrik = pd.DataFrame([{
        "model": "OLS", "n": n, "k_prediktor": p, "ENP": k, "R2": m.rsquared, "Adj_R2": m.rsquared_adj,
        "F": m.fvalue, "p_F": m.f_pvalue, "df_num": int(m.df_model), "df_den": int(m.df_resid),
        "AIC": aic, "AICc": aicc, "RSS": rss, "RMSE": rmse, "MAE": mae,
    }])

    # ---------- tabel6_asumsi_ols.csv ----------
    z_resid = resid / resid.std(ddof=1)
    ks = stats.kstest(z_resid, "norm")
    sw = stats.shapiro(resid)
    jb = stats.jarque_bera(resid)
    wh = het_white(resid, Xd)
    bp = het_breuschpagan(resid, Xd)
    vif_maks = float(np.nanmax(vif))
    w = utils.bobot_knn(coords)
    log.info("[3/4] Bobot: knn | n=%d | pulau=%d (k = %d, baris distandarisasi, koordinat km)", n, len(w.islands), config.K_TETANGGA)
    mo = utils.moran(resid, w, permutasi=999)
    cat_moran = (f"KNN k={config.K_TETANGGA} pada koordinat km, row-standardized; 999 permutasi, seed {config.SEED}; "
                 f"z_norm = {mo['z_norm']:.4f}; p satu sisi (esda)")
    tab6 = pd.DataFrame([
        ["Kolmogorov-Smirnov (normalitas residual)", ks.statistic, ks.pvalue, keputusan(ks.pvalue),
         "residual dibagi simpangan baku sampel (ddof=1) vs N(0,1); parameter diestimasi dari sampel sehingga p cenderung longgar"],
        ["Shapiro-Wilk (normalitas residual)", sw.statistic, sw.pvalue, keputusan(sw.pvalue), "pembanding KS untuk n kecil"],
        ["Jarque-Bera (normalitas residual)", jb.statistic, jb.pvalue, keputusan(jb.pvalue), "berbasis skewness dan kurtosis"],
        ["White (homoskedastisitas)", wh[0], wh[1], keputusan(wh[1]), "statistik LM; H0 = ragam residual homogen"],
        ["Breusch-Pagan (homoskedastisitas)", bp[0], bp[1], keputusan(bp[1]), "statistik LM; H0 = ragam residual homogen"],
        ["VIF maksimum (multikolinearitas)", vif_maks, np.nan, "terpenuhi" if vif_maks < 10 else "tidak terpenuhi", "batas 10; tanpa p-value"],
        ["Moran's I residual (p normal)", mo["I"], mo["p_norm"], keputusan(mo["p_norm"]), cat_moran],
        ["Moran's I residual (p permutasi)", mo["I"], mo["p_sim"], keputusan(mo["p_sim"]), cat_moran],
    ], columns=["uji", "statistik", "p_value", "keputusan", "catatan"])

    # ---------- residual_ols.csv ----------
    s = np.sqrt(rss / (n - k))               # galat baku regresi; residual_std = residual / s
    tab_res = pd.DataFrame({
        "provinsi": df[config.KOL_PROVINSI].values, "kabupaten_kota": df[config.KOL_NAMA].values,
        "fitted": m.fittedvalues, "residual": resid, "residual_std": resid / s,
    })

    # ---------- simpan ----------
    out = config.OUTPUT_TABEL_DIR
    tab5.to_csv(out / "tabel5_ols.csv", index=False)
    metrik.to_csv(out / "metrik_ols.csv", index=False)
    tab6.to_csv(out / "tabel6_asumsi_ols.csv", index=False)
    tab_res.to_csv(out / "residual_ols.csv", index=False)

    # ---------- ringkasan di log ----------
    log.info("[4/4] HASIL (dibulatkan hanya untuk tampilan)")
    log.info("\n%s", tab5.round(4).to_string(index=False))
    log.info("\n  R2 = %.4f | Adj R2 = %.4f | F(%d,%d) = %.3f (p = %.2e)",
             m.rsquared, m.rsquared_adj, m.df_model, m.df_resid, m.fvalue, m.f_pvalue)
    log.info("  RSS = %.2f | RMSE = %.3f | MAE = %.3f | AIC = %.2f | AICc = %.2f | ENP = %d", rss, rmse, mae, aic, aicc, k)
    log.info("\n%s", tab6[["uji", "statistik", "p_value", "keputusan"]].round(4).to_string(index=False))
    z = (df[config.KOL_Y] - df[config.KOL_Y].mean()) / df[config.KOL_Y].std()
    ekstrem = df.assign(z=z).loc[z.abs() > 2, [config.KOL_NAMA, config.KOL_Y, "z"]]
    log.info("\n  Nilai ekstrem Y (|z| > 2):\n%s", ekstrem.round(2).to_string(index=False) if len(ekstrem) else "  (tidak ada)")
    log.info("\n  Berkas disimpan di: %s", out)
    log.info("  STATUS: SELESAI. tabel5_ols, metrik_ols, tabel6_asumsi_ols, residual_ols siap untuk April dan Nisa.")


if __name__ == "__main__":
    main()