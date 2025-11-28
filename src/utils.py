cat > src/utils.py <<'PY'
# src/utils.py
import os
import pandas as pd

def save_results_csv(results, out_path="outputs/results.csv"):
    df = pd.DataFrame(results)
    df.to_csv(out_path, index=False)
    return out_path

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
PY
