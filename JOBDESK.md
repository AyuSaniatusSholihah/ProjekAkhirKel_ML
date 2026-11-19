# Pembagian Tugas (JOBDESK.md) - Analisis OLS vs GWR Jateng 2024

Proyek: Analisis OLS vs GWR Pengaruh Pilar IMDI 2024 terhadap Indeks Pembangunan Manusia (IPM) 2024 di 119 Kabupaten/Kota se-Pulau Jawa.

---

## 1. Naya — Model OLS, Data, EDA & Moran's I (Langkah 1–4)
- **Skrip:** `01_eksplorasi.py`, `02_moran.py`, `03_ols.py`
- **Output Serah Terima:**
  - `data/data_jawa.csv`
  - `output/tabel/tabel5_ols.csv`
  - `output/tabel/metrik_ols.csv`
  - `output/tabel/tabel6_asumsi_ols.csv`
  - `output/tabel/residual_ols.csv`

---

## 2. Nia — Model GWR & Seleksi Bandwidth (Langkah 5 & 6)
- **Skrip:** `04_gwr_model.py`
- **Tugas:**
  - Estimasi 6 kombinasi kernel x bandwidth type (Fixed km & Adaptive NN).
  - Optimasi bandwidth Cross-Validation (CV) minimum.
  - Interval pencarian adaptif 10–119 tetangga.
  - Proyeksi koordinat ke UTM Zone 49S (km).
- **Output Serah Terima:**
  - `output/tabel/tabel7_seleksi_gwr.csv`
  - `output/tabel/gwr_koef_lokal.csv`
  - `output/tabel/gwr_model_terpilih.json`
  - `output/tabel/cv_kurva.csv`

---

## 3. April — Evaluasi Model & Uji Hipotesis (Langkah 7)
- **Skrip:** `04b_evaluasi.py`
- **Tugas:**
  - Seleksi model terbaik berbasis AICc minimum ($\Delta\text{AICc} < 4$ setara).
  - Uji F GWR vs OLS.
  - Uji Heterogenitas Spasial per variabel (Monte Carlo permutasi lokasi, 500/1000 iterasi, SEED 42).
  - Diagnostik kestabilan: Condition number lokal (< 30), VIF lokal (< 10), Moran's I residual GWR.
- **Output Serah Terima:**
  - `output/tabel/gwr_ringkasan.json`
  - `output/tabel/tabel8_ringkasan_koef.csv`
  - `output/tabel/tabel9_signifikansi.csv`
  - `output/tabel/tabel10_perbandingan.csv`

---

## 4. Nisa — Interpretasi & Visualisasi Spasial (Langkah 8)
- **Skrip:** `05_peta.py`, `06_kmeans_opsional.py`
- **Tugas:**
  - Peta sebaran spasial koefisien lokal $X_1, X_2, X_3$ (wilayah tidak signifikan diarsir abu-abu).
  - Peta Local $R^2$ dan kurva CV.
  - Narasi profil wilayah (wilayah terkuat, terlemah, dan tidak signifikan per pilar).
  - Opsional: Klasterisasi koefisien lokal K-Means.
- **Output Serah Terima:**
  - `output/gambar/gambar2_3_persebaran.png`
  - `output/gambar/gambar4_kurva_cv.png`
  - `output/gambar/gambar5_koef_x1.png`
  - `output/gambar/gambar6_koef_x2.png`
  - `output/gambar/gambar7_koef_x3.png`
  - `output/gambar/gambar8_local_r2.png`
  - `output/gambar/gambar9_kmeans.png`
