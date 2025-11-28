# src/notion_db_utils.py

import os
import json
import time

def save_to_notion(records, database_id="NOTION_DB_ID_PLACEHOLDER", demo_mode=True):
    """
    Demo mode only: always writes JSON file to outputs/ and returns success message.
    Real Notion integration disabled for challenge.
    """

    os.makedirs("outputs", exist_ok=True)

    ts = int(time.time())
    out_path = os.path.join("outputs", f"notion_export_{ts}.json")

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"(Demo Notion export failed: {e})"

    return f"✔ Saved results to Notion DB (Demo Mode): {out_path}"
