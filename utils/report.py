# utils/report.py
from db.db_utils import list_logs
from jinja2 import Template
from pathlib import Path

HTML_TEMPLATE = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>PHM Runs</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;padding:18px}
.run{border:1px solid #ddd;padding:12px;margin-bottom:12px;border-radius:6px}
.fail{color:#c00}
.pass{color:#080}
pre{background:#f6f6f6;padding:10px;border-radius:4px;overflow:auto}
</style>
</head>
<body>
  <h1>PHM Recent Runs</h1>
  {% for r in runs %}
    <div class="run">
      <div><strong>ID:</strong> {{ r['id'] }} &nbsp; <strong>Time:</strong> {{ r['timestamp'] }}</div>
      <div><strong>Agent:</strong> {{ r['agent'] }} &nbsp; <strong>Error:</strong> <span class="{{ 'fail' if r['error_type'] else 'pass' }}">{{ r['error_type'] or 'OK' }}</span></div>
      <div><strong>Prompt:</strong><pre>{{ r['prompt'] }}</pre></div>
      <div><strong>Response:</strong><pre>{{ r['response'] }}</pre></div>
      {% if r['fix_suggestion'] %}
        <div><strong>Suggestion:</strong><pre>{{ r['fix_suggestion'] }}</pre></div>
      {% endif %}
    </div>
  {% endfor %}
</body></html>
"""

def generate_html(out_path: str = "reports/report.html", limit: int = 50):
    Path("reports").mkdir(parents=True, exist_ok=True)
    rows = list_logs(limit)
    rendered = Template(HTML_TEMPLATE).render(runs=rows)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(rendered)
    return out_path
