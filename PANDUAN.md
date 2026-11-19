# Panduan Lengkap (Revisi): OLS vs GWR Digitalisasi dan Indeks Pembangunan Manusia (IPM) Pulau Jawa

**Topik:** Pilar IMDI 2024 (*Infrastruktur dan Ekosistem, Keterampilan, Pemberdayaan*) terhadap Indeks Pembangunan Manusia (IPM) 2024, 119 kabupaten/kota se-Pulau Jawa.  
**Tanggal Revisi:** 19 November 2026  
**Pasangan Berkas:** `data_jawa.csv`, `README.md`, `JOBDESK.md`.

---

### Yang Berubah dari Versi Sebelumnya
1. Variabel dependen ($Y$) diperbarui menjadi **IPM (Indeks Pembangunan Manusia) 2024** dan cakupan wilayah diperluas ke **seluruh kabupaten/kota di Pulau Jawa ($n = 119$)** dari `Dataset_Jawa_2024_IPM.csv` / `data_jawa.csv`.
2. Pekerjaan dibagi ke empat anggota.
3. `04_gwr.py` dipecah dua (`04_gwr_model.py` dan `04b_evaluasi.py`).
4. Prompt AI dibuat per orang plus prompt gabungan.
5. Kontrak berkas serah terima antar anggota diperjelas.

---

## Bab 0. Baca Dulu

### Status Pengujian (Jujur)
Kode di paket asli diuji dengan data simulasi (Python 3.12), belum dengan data IMDI/BPS asli. Pemecahan `04_gwr.py` menjadi `04_gwr_model.py` dan `04b_evaluasi.py` belum ditulis dan belum diuji; itu tugas **Nia** dan **April** di Bab 4. Angka contoh yang pernah muncul di buku lama berasal dari simulasi dan **tidak boleh masuk naskah**.

### Cek Awal Data Asli (Bukan Hasil Final)
OLS cepat dengan tiga pilar:
- $R^2 \approx 0{,}54$, $\text{Adj } R^2 \approx 0{,}50$.
- VIF semua di bawah 2.
- Hanya $X_1$ yang signifikan, $X_2$ dan $X_3$ tidak.
- Tiga wilayah ekstrem pada $Y$: **Kota Semarang, Kota Surakarta, Kudus** ($|z| > 2$).
- *Catatan:* Hasil final tetap harus keluar dari *pipeline* resmi.

### Hal yang Harus Disamakan di Naskah

| Hal | Temuan | Tindakan |
| :--- | :--- | :--- |
| **Satuan Y** | Dataset memakai IPM (Indeks Pembangunan Manusia, skala 0–100) | Tulis IPM 2024, skala indeks komposit BPS |
| **Label X1** | Sumber menamai "Infrastruktur dan Ekosistem" | Samakan penamaan di naskah |
| **Nilai Ekstrem Y** | Kota Semarang, Kota Surakarta, Kudus ($|z| > 2$ dan $> 3$) | Catat dan bahas sebagai nilai ekstrem/outlier |
| **Koordinat** | Sudah ada di CSV (centroid) | Lewati `00_isi_koordinat.py` |

---

## Bab 1. Pembagian Tugas

| Anggota | Tugas | Langkah Alur | Skrip Milik |
| :--- | :--- | :---: | :--- |
| **Naya** | Model OLS (usulan: plus data, EDA, Moran's I) | 1, 2, 3, 4 | `01_eksplorasi.py`, `02_moran.py`, `03_ols.py` |
| **Nia** | Model GWR | 5, 6 | `04_gwr_model.py` |
| **April** | Evaluasi model | 7 | `04b_evaluasi.py` |
| **Nisa** | Interpretasi dan visualisasi | 8 | `05_peta.py`, `06_kmeans_opsional.py` |

*Langkah 1, 2, dan Moran's I belum disepakati pemiliknya; usulan di atas silakan diubah bila diperlukan.*

> **Alur Serah Terima:** Naya $\rightarrow$ Nia $\rightarrow$ April $\rightarrow$ Nisa.  
> Orang berikutnya baru bisa mulai penuh setelah keluaran orang sebelumnya final, tetapi bisa menyiapkan kode lebih dulu memakai data simulasi.

### Kontrak Berkas Serah Terima
Semua berkas disimpan di folder `output/tabel/` kecuali dinyatakan lain. **Jangan ubah nama berkas dan kolom tanpa konfirmasi ke penerima.**

| Pemilik | Berkas | Isi Minimal | Dibaca Oleh |
| :--- | :--- | :--- | :--- |
| **Naya** | `data/data_jawa.csv` | 119 baris, 8 kolom (provinsi, nama, Y/ipm, X1–X3, lintang, bujur) | Semua |
| **Naya** | `tabel5_ols.csv` | Koefisien, std. error, $t$, $p$, VIF | April, Nisa |
| **Naya** | `metrik_ols.csv` | $R^2$, Adj $R^2$, $F$, AICc, AIC, MAE, RMSE, RSS | April |
| **Naya** | `tabel6_asumsi_ols.csv` | KS, Shapiro-Wilk, White, VIF maks, Moran's I residual | April |
| **Naya** | `residual_ols.csv` | Wilayah, fitted, residual | April, Nisa |
| **Nia** | `tabel7_seleksi_gwr.csv` | 6 model: bandwidth, ENP, RSS, AICc, RMSE, MAE *(baris OLS ditambah April)* | April, Nisa |
| **Nia** | `gwr_koef_lokal.csv` | $b_0$–$b_3$, $t$ per koefisien, `sig_`, `local_R2`, `cond_number`, prediksi, residual | April, Nisa |
| **Nia** | `gwr_model_terpilih.json` | Nama model, kernel, fixed/adaptif, bandwidth, ENP | April, Nisa |
| **Nia** | `cv_kurva.csv` | Bandwidth dan skor CV untuk model terbaik | Nisa |
| **April** | `gwr_ringkasan.json` | $F$, $p_F$, $df$, Moran's I residual GWR, `cond_number_maks`, `vif_lokal_maks` | Nisa |
| **April** | `tabel8_ringkasan_koef.csv` | Min, Q1, median, Q3, maks koefisien lokal plus OLS | Nisa |
| **April** | `tabel9_signifikansi.csv` | $p$ Monte Carlo, Homogen/Heterogen, % signifikan positif/negatif | Nisa |
| **April** | `tabel10_perbandingan.csv` | OLS vs GWR terbaik | Nisa |
| **Nisa** | `output/gambar/*.png` | `gambar2_3` sampai `gambar9` | Naskah |

*Catatan:* `residual_ols.csv`, `gwr_model_terpilih.json`, dan `cv_kurva.csv` adalah berkas tambahan yang diperlukan karena pemecahan skrip; jika paket asli sudah menyimpannya dengan nama lain, pakai nama itu dan perbarui tabel ini.

---

## Bab 2. Persiapan Lingkungan (Semua Anggota)

Gunakan **Python 3.10 sampai 3.12** (disarankan **3.12, 64-bit**), VS Code dengan ekstensi Python dan Pylance (Rainbow CSV opsional).

1. Ekstrak `gwr-jateng.zip` ke jalur pendek tanpa spasi (contoh: `C:\proyek\gwr-jateng`).
2. Buka VS Code: **File > Open Folder**, pilih folder `gwr-jateng`.
3. Buka terminal baru:

**Windows (PowerShell):**
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
*(Bila "running scripts is disabled": jalankan `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, lalu ulangi baris Activate).*

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Tekan `Ctrl+Shift+P` > **Python: Select Interpreter** > pilih `.venv`.
5. Verifikasi instalasi:
```bash
python -c "import numpy, pandas, scipy, statsmodels, esda, libpysal, mgwr, geopandas, mapclassify, sklearn, matplotlib; print('SEMUA PUSTAKA OK')"
```

### Git
- Satu cabang per orang: `naya/ols`, `nia/gwr`, `april/evaluasi`, `nisa/visualisasi`.
- Merge ke `main` lewat pull request, jangan push langsung.
- Berkas bersama (`config.py`, `utils.py`, `requirements.txt`) diubah hanya setelah kabar ke grup.
- `data_jawa.csv` hanya diubah oleh pemegang data.

---

## Bab 3. Data

Letakkan `data_jawa.csv` (atau `Dataset_Jawa_2024_IPM.csv`) di `data/`.  
**Format:** UTF-8, titik desimal, 119 baris, tanpa sel kosong.

| Kolom | Isi |
| :--- | :--- |
| `provinsi` | Nama provinsi di Pulau Jawa (Banten, DKI, Jabar, Jateng, DIY, Jatim) |
| `kabupaten_kota` | Kabupaten polos (contoh: `Tegal`), kota berawalan `Kota` (contoh: `Kota Tegal`) |
| `ipm` | $Y$, Indeks Pembangunan Manusia 2024 (skala 0–100) |
| `x1_infrastruktur` | $X_1$, skor pilar IMDI 2024 |
| `x2_keterampilan` | $X_2$, skor pilar IMDI 2024 |
| `x3_pemberdayaan` | $X_3$, skor pilar IMDI 2024 |
| `lintang`, `bujur` | Centroid, derajat desimal |

- Pasangan nama kembar (`Magelang`, `Pekalongan`, `Tegal`, `Semarang`) sudah dibedakan lewat awalan `Kota`. Bila nanti memakai GeoJSON, cek `KOL_GEO_NAMA` dan `KOL_GEO_JENIS` di `config.py`; kode berhenti dengan pesan jelas bila ada nama ganda.
- Peta poligon dan bobot queen butuh `data/jateng_kabkota.geojson` (GADM level 2, geoBoundaries, atau batas BPS/BIG; periksa lisensi). Tanpa GeoJSON, peta berupa titik dan bobot otomatis KNN.
- Sebelum analisis asli, jalankan uji coba dengan data simulasi (salin cadangan CSV asli dulu), lalu kembalikan data asli dan kosongkan `output/`.

---

## Bab 4. Panduan per Anggota

### 4.1 Naya: Model OLS (Langkah 1 sampai 4)
- **Tujuan:** Data final, EDA, Moran's I, OLS beserta diagnostik, sebagai dasar pembanding GWR.
- **Kerjakan:**
  1. Validasi data (Bab 3), catat wilayah ekstrem.
  2. `python src/01_eksplorasi.py` (statistik deskriptif, korelasi, peta sebaran).
  3. `python src/02_moran.py` (Moran's I untuk Y, X1–X3). Indikator benar: `Bobot: knn | n=35 | pulau=0`.
  4. `python src/03_ols.py`. Pastikan keluaran sesuai kontrak di Bab 1, termasuk `residual_ols.csv`.
- **Cara Membaca:**
  - VIF di bawah 10 berarti multikolinearitas aman.
  - Kolmogorov-Smirnov longgar pada $n = 35$, jadi Shapiro-Wilk disertakan sebagai pembanding.
  - Moran's I residual OLS yang signifikan positif adalah dasar memakai GWR; bila tidak signifikan, tulis apa adanya dan jangan mengubah bobot demi signifikansi.
  - $X$ dipusatkan, sehingga intersep adalah nilai $Y$ pada skor rata-rata, bukan pada skor nol.
- **Selesai Bila:** Semua berkas Naya di kontrak ada dan terisi, Tabel 3–6 siap, dan PR `naya/ols` sudah di-merge.

### 4.2 Nia: Model GWR (Langkah 5 dan 6)
- **Tujuan:** Mengestimasi GWR dengan Weighted Least Squares, memilih bandwidth, dan menyerahkan koefisien lokal.
- **Kerjakan:**
  1. Bersama April, pecah `04_gwr.py` menjadi `04_gwr_model.py` (estimasi dan bandwidth) dan `04b_evaluasi.py` (evaluasi) dalam satu commit awal.
  2. Jalankan enam kombinasi: fixed dan adaptive, masing-masing kernel Gaussian, Bisquare, Exponential.
  3. Bandwidth dipilih dengan Cross Validation minimum. Adaptif dicari di interval 6 sampai 35 tetangga (batas bawah bawaan mgwr, $40 + 2k$, melebihi $n = 35$ sehingga model adaptif gagal bila dibiarkan bawaan). Jarak Euclidean pada koordinat UTM 49S (EPSG:32749), fixed dalam km.
  4. Simpan `tabel7_seleksi_gwr.csv`, `gwr_koef_lokal.csv`, `gwr_model_terpilih.json`, `cv_kurva.csv`.
- **Cara Membaca:**
  - Waspadai bandwidth di batas pencarian (adaptif 6 berarti terlalu lokal, 35 berarti praktis global).
  - Waspadai ENP mendekati $n$: RMSE sangat kecil dengan ENP besar adalah tanda overfitting, bukan model bagus.
  - Baris `[GAGAL]` biasanya akibat koordinat duplikat atau variabel hampir konstan.
- **Selesai Bila:** Enam model jalan atau kegagalannya terdokumentasi, empat berkas serah terima ada, dan bandwidth di batas pencarian sudah dicatat untuk April.

### 4.3 April: Evaluasi Model (Langkah 7)
- **Tujuan:** Menilai GWR terhadap OLS dan menetapkan model terbaik.
- **Kerjakan:**
  1. Gabungkan `metrik_ols.csv` (Naya) dan `tabel7_seleksi_gwr.csv` (Nia): AICc, MAE, RMSE, RSS, ENP. AICc OLS dihitung dengan rumus yang sama dengan mgwr agar adil.
  2. Model terbaik = AICc minimum (ubah `PILIH_BERDASARKAN` bila ada alasan, dan tulis alasannya). Selisih AICc kurang dari 4 dianggap setara; cetak model setaranya.
  3. Uji F GWR vs OLS dengan $df_{\text{GWR}} = n - \text{tr}(S)$. Uji heterogenitas per variabel dengan Monte Carlo permutasi lokasi (bandwidth tetap, $p = (\text{jumlah acakan dengan variasi} \ge \text{asli} + 1) / (\text{iterasi} + 1)$); 500 iterasi untuk uji, 1000 untuk run final, `SEED 42`.
  4. Signifikansi lokal: $p$ dua sisi di bawah `ALPHA 0.05` (setara $p < 0{,}025$ satu sisi); sediakan versi $t$ kritis terkoreksi sebagai uji ketahanan.
  5. Diagnostik: Moran's I residual GWR, condition number lokal (curiga bila di atas 30), VIF lokal (di bawah 10).
  6. Tulis `gwr_ringkasan.json`, `tabel8_ringkasan_koef.csv`, `tabel9_signifikansi.csv`, `tabel10_perbandingan.csv`.
- **Cara Membaca:**
  - Dengan $n = 35$ daya uji rendah: hasil Homogen berarti bukti variasi tidak cukup, bukan bukti variasi tidak ada.
  - Intersep heterogen itu umum dan bukan temuan utama. Bila perbaikan GWR kecil, laporkan jujur.
- **Selesai Bila:** Model terbaik di `gwr_ringkasan.json` cocok dengan baris AICc terkecil (atau alasan penyimpangan tertulis) dan Tabel 7–10 siap.

### 4.4 Nisa: Interpretasi dan Visualisasi (Langkah 8)
- **Tujuan:** Mengubah keluaran menjadi gambar dan narasi interpretasi.
- **Kerjakan:**
  1. `python src/05_peta.py`: peta koefisien lokal X1–X3 (wilayah tidak signifikan abu-abu), peta $R^2$ lokal, kurva CV, serta prediksi dan residual.
  2. Narasi per wilayah dari `gwr_koef_lokal.csv`: wilayah terkuat, terlemah, dan tidak signifikan untuk tiap pilar.
  3. (Opsional) `python src/06_kmeans_opsional.py` untuk klaster koefisien lokal dan Silhouette Score.
  4. Gambar disimpan ke `output/gambar` (tidak dibuka sebagai jendela).
- **Cara Membaca:**
  - Peta dan persentase signifikan menunjukkan keterkaitan, bukan sebab-akibat.
  - Jangan menebak mekanisme dari nama wilayah; beri penjelasan hanya sebagai kemungkinan dan tandai bila butuh data tambahan.
  - Jangan menggambar peta dari model selain yang ditetapkan April.
- **Selesai Bila:** Gambar 2–9 ada, narasi 4.7 dan 4.8 tertulis, dan beberapa wilayah sudah dicocokkan manual antara gambar dan CSV.

---

## Bab 5. Menjalankan Pipeline Gabungan

**Urutan wajib:** `01`, `02`, `03`, `04_gwr_model`, `04b_evaluasi`, `05`, `(06)`.  
`run_all.py` harus diperbarui dengan urutan ini (Nia dan April bertanggung jawab setelah pemecahan). Atau satu klik: **Run and Debug** (`Ctrl+Shift+D`), pilih "Jalankan seluruh pipeline (run_all)", tekan `F5`.

**Tanda berhasil:**  
1. Baris log: `Bobot: knn | n=35 | pulau=0`.
2. Enam baris model GWR.
3. Keterangan `Model terbaik (AICc minimum)`.
4. Baris status `SELESAI`.

### Pengaturan di `src/config.py`

| Pengaturan | Default | Fungsi |
| :--- | :--- | :--- |
| `KOL_NAMA`, `KOL_Y`, `KOL_X`, `KOL_LAT`, `KOL_LON` | sesuai CSV | nama kolom data |
| `CSV_SEP`, `CSV_DESIMAL` | `,` dan `.` | ubah ke `;` dan `,` bila CSV berlokal Indonesia |
| `KOL_GEO_NAMA`, `KOL_GEO_JENIS` | `NAME_2`, `None` | kolom nama/jenis di GeoJSON |
| `ALPHA` | `0.05` | taraf signifikansi |
| `CRS_PROYEKSI` | `EPSG:32749` | UTM 49S, jarak dalam km |
| `BOBOT`, `K_TETANGGA` | `knn`, `4` | bobot Moran's I; queen butuh GeoJSON |
| `PUSATKAN_X` | `True` | X dipusatkan agar matriks lokal stabil |
| `N_MONTE_CARLO` | `500` | naikkan ke 1000 untuk run final |
| `SEED` | `42` | catat di naskah |

*Catatan:* `PILIH_BERDASARKAN` (AICc, RMSE, atau RSS) ada di `04b_evaluasi.py` setelah pemecahan.

---

## Bab 6. Aturan Keputusan dan Cara Menulis ke Naskah

| Bagian Naskah | Yang Ditulis agar Sama dengan Kode |
| :--- | :--- |
| **3.3 bobot Moran's I** | KNN $k = 4$ atau queen, terstandardisasi baris |
| **3.4 dan Tabel 5** | X dipusatkan; intersep = Y pada skor rata-rata; sebut KS dan Shapiro-Wilk sebagai pembanding |
| **3.6 jarak** | Euclidean pada UTM 49S dalam km; fixed dalam km; adaptif = jumlah tetangga (10 sampai 119) |
| **3.7 uji per variabel** | Monte Carlo permutasi lokasi, bukan uji F Leung (atau gunakan alat lain bila jurnal menuntut) |
| **3.7 autokorelasi residual GWR** | Moran's I pada residual, bukan uji Leung dkk. |
| **3.7 uji t lokal** | dua sisi $p < \alpha$, setara $p < \alpha/2$ satu sisi |
| **3.7 dan 4.4 model terbaik** | kriteria utama (default AICc minimum) |
| **3.1 data** | Y = IPM 2024; X1 = Infrastruktur dan Ekosistem |

### Peta Berkas ke Naskah
- **Tabel 3:** `tabel3_deskriptif.csv`
- **Tabel 4:** `tabel4_moran.csv` *(pilih satu: p_value normal atau p_sim permutasi)*
- **Tabel 5:** `tabel5_ols.csv` dan `metrik_ols.csv`
- **Tabel 6:** `tabel6_asumsi_ols.csv`
- **Tabel 7:** `tabel7_seleksi_gwr.csv`
- **Tabel 8–10:** `tabel8` sampai `tabel10`
- **Gambar 2–3:** `gambar2_3_persebaran.png`
- **Gambar 4:** `gambar4_kurva_cv.png`
- **Gambar 5–7:** Peta koefisien lokal ($X_1, X_2, X_3$)
- **Gambar 8:** `gambar8_local_r2.png`
- **Gambar 9:** `gambar9_kmeans.png` *(opsional)*

---

## Bab 7. Prompt AI

Dipakai di asisten AI VS Code yang bisa membaca folder proyek (Claude Code, Copilot Chat, dll.). Bila tidak bisa, tempel isi CSV yang relevan. Tempel P0 di awal setiap sesi baru, lalu pakai prompt sesuai peranmu.

### P0. Konteks Tetap (Semua Anggota)
```text
Peran: asisten analis data untuk naskah jurnal tim kami.
Proyek: folder proyek (Python, VS Code). Analisis OLS vs GWR hubungan tiga pilar IMDI 2024
(X1 Infrastruktur dan Ekosistem, X2 Keterampilan Digital, X3 Pemberdayaan) dengan Indeks Pembangunan Manusia
IPM 2024 (Y) di 119 kabupaten/kota se-Pulau Jawa, data cross-section.

Pembagian tim: Naya = data, EDA, Moran's I, OLS; Nia = model GWR dan bandwidth; April = evaluasi model;
Nisa = interpretasi dan visualisasi. Saya adalah: [nama dan peran saya]. Kerjakan hanya bagian peran saya
dan jangan mengubah berkas milik orang lain.

Aturan tetap:
1. Hanya gunakan angka dari berkas di output/tabel dan output/gambar. Jangan mengarang, memperkirakan,
   atau membulatkan sendiri. Bila angka tidak ada, katakan tidak ada.
2. Jangan mengubah kode di src/ kecuali saya minta. Usulkan perubahan dan alasannya dulu.
3. Hubungan yang ditemukan adalah keterkaitan, bukan sebab-akibat.
4. n = 119 kabupaten/kota se-Pulau Jawa, sebut hasil bersifat empiris spasial.
5. Bahasa Indonesia akademik, ringkas.
6. Bila hasil tidak mendukung dugaan, laporkan apa adanya.
7. Jangan mengubah pilihan analisis (kernel, kriteria bandwidth, ALPHA, jenis bobot, SEED) hanya untuk
   menghindari error atau mengejar signifikansi; tanyakan dulu.

Baca README.md, JOBDESK.md, dan src/config.py, lalu ringkas pemahamanmu dalam 5 kalimat sebelum mengerjakan apa pun.

Cek hasil: ringkasan menyebut OLS vs GWR, 119 wilayah se-Pulau Jawa, tiga pilar, IPM 2024, dan peranmu.
```

### P1. Verifikasi Lingkungan (Semua)
```text
Jalankan di terminal (venv .venv harus aktif):
python -c "import numpy, pandas, scipy, statsmodels, esda, libpysal, mgwr, geopandas, mapclassify, sklearn, matplotlib; print('OK')"
Bila ada error, diagnosis penyebabnya dan beri perintah perbaikan satu per satu. Jangan menginstal apa pun di luar .venv.
```

### Prompt Naya

#### N1. Validasi Data
```text
Periksa data/data_jawa.csv tanpa mengubahnya: (a) tepat 119 baris, (b) tidak ada sel kosong, (c) tidak ada
nama ganda di provinsi yang sama, (d) skor X1-X3 di rentang 1-100 dan IPM di rentang 0-100, (e) lintang antara
-9.0 dan -5.5 serta bujur antara 105.0 dan 115.0, (f) wilayah ekstrem (|z| > 2 dan > 3). Laporkan sebagai tabel temuan.
Jangan memperbaiki data; saya yang memutuskan.
```

#### N2. EDA (Subbab 4.1)
```text
Jalankan python src/01_eksplorasi.py. Dari tabel3_deskriptif.csv, korelasi.csv, dan gambar2_3_persebaran.png,
tulis narasi Subbab 4.1 (maksimal 2 paragraf): (a) wilayah dengan IPM tertinggi dan terendah,
(b) pola tiap pilar dan apakah wilayah ber-IPM tinggi juga bernilai pilar tinggi, (c) kesimpulan awal bahwa
hubungan tampak berbeda antarwilayah atau tidak. Bahas nilai ekstrem Y. Tandai kalimat yang bersandar pada
gambar, bukan tabel.
```

#### N3. Moran's I (Subbab 4.2, Tabel 4)
```text
Jalankan python src/02_moran.py. Dari tabel4_moran.csv tulis interpretasi Subbab 4.2: variabel mana yang
berautokorelasi spasial signifikan pada 5%, arahnya, dan implikasinya untuk memilih model spasial. Sebutkan
jenis bobot (lihat config.py) dan bedakan p_value (normal) dari p_sim (permutasi); tanyakan padaku mana
yang dilaporkan.
```

#### N4. OLS dan Diagnostik (Subbab 4.3, Tabel 5–6)
```text
Jalankan python src/03_ols.py. Dari tabel5_ols.csv, tabel6_asumsi_ols.csv, dan metrik_ols.csv:
(1) susun Tabel 5 dengan ** untuk p < 0.05 dan * untuk p < 0.10, (2) tulis pembahasan 4.3: variabel signifikan,
arah koefisien, R2 dan Adj R2, (3) tulis interpretasi Tabel 6: asumsi mana yang terpenuhi dan apakah
Moran's I residual signifikan. X dipusatkan, jadi intersep = nilai Y pada skor rata-rata pilar; jangan
menafsirkannya sebagai IPM pada skor nol. Pastikan residual_ols.csv tersimpan untuk April dan Nisa.

Cek hasil: tanda bintang cocok dengan kolom p_value; Moran's I residual menentukan apakah argumen GWR masih berdiri.
```

### Prompt Nia

#### G1. Pecah Skrip
```text
Baca src/04_gwr.py. Usulkan (jangan langsung ubah) cara memecahnya menjadi 04_gwr_model.py (estimasi enam
kombinasi GWR dan pemilihan bandwidth, bagian Nia) dan 04b_evaluasi.py (uji F, Monte Carlo, diagnostik,
penetapan model terbaik, bagian April). Tulis daftar fungsi yang pindah, berkas perantara yang harus
disimpan (tabel7_seleksi_gwr.csv, gwr_koef_lokal.csv, gwr_model_terpilih.json, cv_kurva.csv), dan perubahan
yang diperlukan di run_all.py. Tunggu persetujuan saya.
```

#### G2. Estimasi dan Bandwidth (Subbab 4.4 Bagian Awal)
```text
Jalankan python src/04_gwr_model.py. Dari tabel7_seleksi_gwr.csv laporkan: (1) apakah ada kombinasi yang gagal
([GAGAL]) dan dugaan penyebabnya, (2) bandwidth tiap model dan mana yang jatuh di batas pencarian
(adaptif 6 atau 35), (3) model dengan ENP mendekati n 35, (4) apakah koordinat duplikat atau variabel hampir
konstan. Jangan menetapkan model terbaik; itu tugas April. Pastikan gwr_koef_lokal.csv berisi b0-b3, t, sig_,
local_R2, cond_number, prediksi, dan residual.
```

### Prompt April

#### A1. Seleksi dan Evaluasi (Subbab 4.4 dan 4.6, Tabel 7 dan 10)
```text
Jalankan python src/04b_evaluasi.py. Dari tabel7_seleksi_gwr.csv, metrik_ols.csv, dan gwr_ringkasan.json:
(1) bandingkan enam model GWR dan OLS pada AICc, ENP, RMSE, MAE, bandwidth, (2) tetapkan model terbaik
menurut AICc minimum dan sebut model setara (selisih AICc < 4), (3) tandai bandwidth di batas pencarian dan
ENP mendekati n, (4) jangan memilih hanya berdasarkan RMSE. Tulis narasi 4.4 dan satu kalimat alasan pilihan
akhir. Susun juga perbandingan GWR vs OLS pada AICc, MAE, RMSE, Adj R2, Moran's I residual (Subbab 4.6).
```

#### A2. Uji F, Heterogenitas, Kestabilan (Subbab 4.5, Tabel 8–9)
```text
Dari tabel8_ringkasan_koef.csv, tabel9_signifikansi.csv, dan gwr_ringkasan.json, tulis Subbab 4.5: rentang
koefisien lokal, apakah tanda berbeda antarwilayah, hasil uji F GWR vs OLS, hasil Homogen/Heterogen per
variabel (Monte Carlo) dengan persentase wilayah signifikan. Periksa condition number maksimum (< 30) dan
VIF lokal maksimum (< 10), serta Moran's I residual GWR. Bila perbaikan GWR kecil, katakan jujur dan kaitkan
dengan n = 35. Hasil Homogen pada n = 35 berarti bukti variasi tidak cukup, bukan bukti variasi tidak ada.
Untuk run final pastikan N_MONTE_CARLO = 1000 dan SEED = 42.
```

### Prompt Nisa

#### V1. Peta dan Koefisien Lokal (Subbab 4.7)
```text
Jalankan python src/05_peta.py. Dari gwr_koef_lokal.csv, gwr_model_terpilih.json, dan gambar5-8 di
output/gambar, untuk tiap pilar (X1, X2, X3) sebutkan wilayah dengan koefisien signifikan terkuat, terlemah,
dan wilayah tidak signifikan (kolom sig_b1, sig_b2, sig_b3). Jangan menebak mekanisme dari nama wilayah.
Beri penjelasan hanya sebagai kemungkinan dan tandai bila butuh data tambahan. Pastikan peta memakai model
yang ditetapkan April.

Cek hasil: buka sendiri gambar 5-7 dan cocokkan beberapa wilayah dengan CSV.
```

#### V2. Implikasi dan K-Means (Subbab 4.8 dan 4.9)
```text
Dari hasil Subbab 4.5 sampai 4.7 rumuskan Subbab 4.8: pilar yang koefisiennya homogen dan signifikan luas,
pilar yang heterogen dan perlu disesuaikan per kelompok wilayah, dan wilayah dengan koefisien tidak
signifikan. Tegaskan ini keterkaitan, bukan sebab-akibat. Untuk Subbab 4.9: hanya bila saya sudah menjalankan
python src/06_kmeans_opsional.py, tulis hasil dari kmeans_klaster.csv dan Silhouette Score yang tercetak;
bila belum, katakan bagian ini dihapus.
```

### Prompt Gabungan (Penanggung Jawab Naskah)

#### K1. Abstrak dan Kesimpulan
```text
Isi placeholder [ ] di Abstrak dan Bab 5 hanya dari berkas output. Untuk placeholder yang tidak bisa diisi,
jangan menebak: keluarkan daftar placeholder tersisa beserta data yang dibutuhkan. Urutan kesimpulan
mengikuti tujuan penelitian di Pendahuluan.
```

#### K2. Sinkronisasi Metode Naskah dengan Kode
```text
Bandingkan Bab 3 naskah dengan kode di src/ (config.py, 02, 03, 04_gwr_model, 04b_evaluasi). Buat tabel
[bagian naskah | yang tertulis | yang dikerjakan kode | usulan kalimat pengganti]. Perhatikan: jenis bobot
Moran's I, X dipusatkan, jarak km pada UTM 49S, bandwidth adaptif 10-119, uji heterogenitas (Monte Carlo,
bukan F Leung), uji autokorelasi residual GWR (Moran's I), uji t dua sisi, kriteria model terbaik, dan
satuan Y (IPM skala 0–100). Jangan mengubah naskah, hanya usulkan.
```

#### K3. Audit Akhir Angka dan Klaim (Wajib)
```text
Untuk setiap angka di Bab 4 dan 5 naskah (koefisien, p-value, AICc, RMSE, persentase wilayah, bandwidth),
cari sumbernya di output/. Keluarkan tabel [angka | lokasi di naskah | berkas dan kolom sumber | cocok atau
tidak]. Tandai angka tanpa sumber. Lalu tandai kalimat bernada sebab-akibat ('menyebabkan', 'meningkatkan',
'berdampak') agar diubah menjadi bahasa keterkaitan.
```

#### D1. Template Debug (Siapa Pun, Kapan Pun Error)
```text
Saya menjalankan: [perintah]. OS: [Windows/macOS/Linux]. Versi Python: [python --version].
Pesan error lengkap:
[tempel seluruh pesan, jangan dipotong]

Lakukan: (1) jelaskan penyebab dalam 2 kalimat, (2) beri satu perbaikan minimal, (3) beri cara memverifikasi
bahwa sudah beres. Jangan mengubah pilihan analisis hanya untuk menghindari error; bila perlu, tanyakan dulu.
```

#### Pola Menulis Prompt Sendiri
Tahap + berkas sumber + keluaran yang diminta + batasan.  
*Contoh:* "Dari tabel9_signifikansi.csv, tulis 1 paragraf Subbab 4.5 tentang X2. Hanya pakai angka dari berkas itu. Jangan menyimpulkan sebab-akibat."  
*Hindari:* "analisis datanya" (terlalu longgar) dan "buat hasil yang signifikan" (mendorong rekayasa).

---

## Bab 8. Troubleshooting

| Gejala | Penyebab | Solusi |
| :--- | :--- | :--- |
| `python`/`py` tidak dikenali | belum masuk PATH | pasang ulang dengan centang Add python.exe to PATH, buka ulang VS Code |
| *Running scripts is disabled* | kebijakan PowerShell | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, aktifkan venv lagi |
| `ModuleNotFoundError` | interpreter bukan `.venv` | Select Interpreter ke `.venv`; `pip install -r requirements.txt` |
| pip gagal membangun geopandas/shapely | Python terlalu baru atau 32-bit | pakai Python 3.12 64-bit; upgrade pip |
| Hanya 1 kolom terbaca | CSV titik koma | `CSV_SEP = ";"`, `CSV_DESIMAL = ","` |
| Kolom bukan angka / sel kosong | koma desimal, pemisah ribuan, data kosong | seragamkan angka, lengkapi data |
| Nama ganda atau tidak cocok dengan GeoJSON | kabupaten dan kota kembar, ejaan beda | awalan `Kota` di CSV; isi `KOL_GEO_JENIS`; cek nama GeoJSON |
| Kolom `NAME_2` tidak ada | GeoJSON memakai kolom lain | ubah `KOL_GEO_NAMA` |
| Bobot queen butuh GeoJSON / pulau > 0 | tidak ada peta atau geometri bermasalah | pakai `knn` atau perbaiki geometri |
| `[GAGAL]` GWR | koordinat duplikat atau variabel hampir konstan | periksa data; kombinasi lain tetap jalan |
| `LinAlgError: singular matrix` | kolinear sempurna atau duplikat | cek `korelasi.csv` dan VIF di `tabel5_ols.csv` |
| Berkas serah terima tidak ditemukan | skrip sebelumnya belum dijalankan atau nama berbeda | jalankan sesuai urutan; cocokkan dengan kontrak Bab 1 |
| Hasil GWR hampir sama dengan OLS | bandwidth besar atau hubungan homogen | bukan error; laporkan jujur |
| Gambar tidak muncul | disimpan ke berkas | buka `output/gambar` |
| Karakter aneh pada nama | CSV bukan UTF-8 | simpan ulang UTF-8 |

---

## Bab 9. Checklist Sebelum Submit

### Data dan Replikasi
- [ ] `data_jawa.csv` berisi data asli, 119 baris, sumber dan tahun tercatat; variabel Y IPM 2024 ditulis
- [ ] Uji coba simulasi sudah dilakukan, data asli dikembalikan, `output/` dibersihkan
- [ ] `N_MONTE_CARLO = 1000` untuk run final; `SEED 42` dicatat di naskah
- [ ] `pip freeze > requirements-lock.txt` setelah run final

### Per Anggota
- [ ] **Naya:** berkas OLS, EDA, Moran's I sesuai kontrak; bobot dan jenis p-value Moran's I ditetapkan
- [ ] **Nia:** enam model jalan, bandwidth di batas pencarian dicatat, empat berkas serah terima ada
- [ ] **April:** model terbaik tertulis dengan alasan, uji F, Monte Carlo, diagnostik kestabilan lengkap
- [ ] **Nisa:** Gambar 2–9 lengkap, narasi 4.7 dan 4.8 selesai, wilayah dicocokkan manual dengan CSV

### Naskah
- [ ] Semua penyesuaian Bab 6 masuk ke Bab 3 naskah
- [ ] Placeholder terisi (nama penulis, referensi, ringkasan Abstrak)
- [ ] K3 selesai: setiap angka punya sumber di `output/`
- [ ] Kalimat sebab-akibat sudah diganti bahasa keterkaitan; keterbatasan $n = 35$ dan data cross-section disebut
- [ ] Pernyataan penggunaan AI diisi sesuai kenyataan (nama alat, tujuan, tinjauan penuh oleh penulis); cek ketentuan jurnal

---

## Keterbatasan Paket
1. Kode diuji dengan data simulasi dan poligon buatan; perilaku pada data asli baru terlihat saat dijalankan. Pemecahan `04_gwr.py` belum diuji.
2. Uji heterogenitas memakai Monte Carlo permutasi lokasi dan autokorelasi residual GWR memakai Moran's I, berbeda dari uji F dan uji Leung dkk. di artikel acuan; tulis sesuai kenyataan.
3. Dua keterbatasan pustaka `mgwr` diakali di kode (batas bawah bandwidth adaptif dan Monte Carlo bawaan yang crash); versi `mgwr` berbeda bisa mengubah perilaku.
4. Hasil numerik dapat sedikit berbeda antarversi pustaka dan sistem operasi.
5. Dengan $n = 35$ dan tiga prediktor, estimasi lokal rentan tidak stabil dan uji bertenaga rendah; semua hasil eksploratif.
6. Paket ini membantu menjalankan analisis, bukan menggantikan pemahaman. Tiap anggota harus bisa menjelaskan tahapnya kepada penguji atau reviewer.

---

## Lampiran A. Perintah Ringkas

```bash
# Sekali di awal
py -3.12 -m venv .venv                 # Windows
python3 -m venv .venv                  # macOS/Linux

.venv\Scripts\Activate.ps1             # Windows
source .venv/bin/activate              # macOS/Linux

pip install -r requirements.txt

# Setiap kali kerja (aktifkan venv dulu)
python src/run_all.py                  # seluruh pipeline
python src/03_ols.py                   # satu tahap saja (urutan wajib dijaga)
```

---

## Lampiran B. Isi `gwr_ringkasan.json`

| Kunci | Arti |
| :--- | :--- |
| `model_terbaik`, `kernel`, `fixed`, `bandwidth` | model GWR terpilih; bandwidth km (fixed) atau jumlah tetangga (adaptif) |
| `F`, `p_F`, `df_num`, `df_den` | uji F GWR vs OLS |
| `t_kritis_terkoreksi` | $t$ kritis terkoreksi untuk uji ketahanan (kolom `sigk_`) |
| `moran_resid_gwr`, `p_moran_resid_gwr` | Moran's I residual GWR dan $p$-value |
| `cond_number_maks`, `n_cn_lebih_30` | condition number lokal maksimum dan jumlah wilayah di atas 30 |
| `vif_lokal_maks` | VIF lokal maksimum |
