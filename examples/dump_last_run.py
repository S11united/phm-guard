# examples/dump_last_run.py
import json
from db.db_utils import last_log
from pathlib import Path

p = last_log()
if not p:
    print("No runs found.")
else:
    out = Path("examples/last_run.json")
    out.write_text(json.dumps(p, indent=2, ensure_ascii=False))
    print("Wrote", out)
