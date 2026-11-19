"""
Konfigurasi Analisis OLS vs GWR - Jawa Tengah 2024
Tim: Naya, Nia, April, Nisa
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_TABEL_DIR = OUTPUT_DIR / "tabel"
OUTPUT_GAMBAR_DIR = OUTPUT_DIR / "gambar"

# Pastikan direktori output tersedia
OUTPUT_TABEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_GAMBAR_DIR.mkdir(parents=True, exist_ok=True)

# Berkas Data
PATH_DATA_CSV = DATA_DIR / "data_jateng.csv"
PATH_DATA_XLSX = DATA_DIR / "data_jateng.xlsx"
PATH_GEOJSON = DATA_DIR / "jateng_kabkota.geojson"

# Definisi Kolom Dataset CSV
KOL_NAMA = "kabupaten_kota"
KOL_Y = "pdrb_per_kapita"
KOL_X = ["x1_infrastruktur", "x2_keterampilan", "x3_pemberdayaan"]
KOL_LAT = "lintang"
KOL_LON = "bujur"

# Format CSV
CSV_SEP = ","
CSV_DESIMAL = "."

# Konfigurasi GeoJSON (Bila ada)
KOL_GEO_NAMA = "NAME_2"
KOL_GEO_JENIS = None

# Parameter Statistik & Pemodelan
ALPHA = 0.05
CRS_PROYEKSI = "EPSG:32749"  # UTM Zone 49S (satuan meter/km)
BOBOT = "knn"
K_TETANGGA = 4
PUSATKAN_X = True
N_MONTE_CARLO = 500  # Naikkan ke 1000 untuk run naskah final
SEED = 42

# Batas Pencarian Bandwidth GWR Adaptif (Kritis untuk n=35)
GWR_MIN_NN = 6
GWR_MAX_NN = 35

# Kriteria Pemilihan Model Terbaik di Evaluasi
PILIH_BERDASARKAN = "AICc"
