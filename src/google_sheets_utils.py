# src/google_sheets_utils.py

import os
import time
import pandas as pd

def export_to_google_sheets(data, sheet_name="Resume_Screening_Output", demo_mode=True):
    """
    Demo mode only: always writes CSV file to outputs/ and returns success message.
    The real Google Sheets integration is intentionally disabled for the challenge.
    """

    # Ensure folder
    os.makedirs("outputs", exist_ok=True)

    # Always DEMO export
    ts = int(time.time())
    out_path = os.path.join("outputs", f"google_sheets_export_{ts}.csv")

    try:
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
        data.to_csv(out_path, index=False)
    except Exception as e:
        return f"(Demo export failed: {e})"

    return f"✔ Exported results to Google Sheets (Demo Mode): {out_path}"
