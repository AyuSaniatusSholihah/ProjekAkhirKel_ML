"""
Uji: pra-pemrosesan utils.py harus SAMA dengan 04_gwr_model.py (coords, y, X).
Catatan: meng-import 04_gwr_model.py menimpa output/gwr_model_execution.log (mode "w"); skrip ini
mencadangkan isi log lalu memulihkannya sehingga log Nia tidak hilang.
"""
import sys, importlib.util
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config, utils

log = config.OUTPUT_DIR / "gwr_model_execution.log"
cadangan = log.read_bytes() if log.exists() else None

spec = importlib.util.spec_from_file_location("gwr04", Path(__file__).resolve().parent / "04_gwr_model.py")
gwr04 = importlib.util.module_from_spec(spec); spec.loader.exec_module(gwr04)
_, c4, y4, X4 = gwr04.load_and_preprocess_data()
if cadangan is not None:
    log.write_bytes(cadangan)

_, c, y, X = utils.muat_data()
for nama, a, b in [("coords_km", c, c4), ("y", y, y4), ("X", X, X4)]:
    assert a.shape == b.shape and np.allclose(a, b, atol=1e-9), f"{nama} BERBEDA dari 04_gwr_model.py"
    print(f"[OK] {nama}: identik dengan 04_gwr_model.py {a.shape}")