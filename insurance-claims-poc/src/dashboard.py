"""
Flask web app that serves the Claims Intake Dashboard.
Runs the pipeline and displays results in an interactive HTML viewer.

Usage:
    cd insurance-claims-poc
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python src/generate_sample_data.py   # generate sample PDFs + photos
    cd src && python dashboard.py        # open http://localhost:5050
"""

import json
from pathlib import Path
from flask import Flask, render_template_string, send_from_directory, jsonify

from intake_pipeline import run_pipeline

app = Flask(__name__)

BASE_DIR  = Path(__file__).resolve().parent.parent
DATA_DIR  = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
PHOTOS_DIR = DATA_DIR / "sample_photos"

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Claims Intake Dashboard — POC</title>
<style>
:root {
  --primary: #1a3a6b; --primary-light: #2a5298; --accent: #e8a838;
  --danger: #dc3545;  --success: #28a745; --warning: #ffc107; --info: #17a2b8;
  --bg: #f4f6f9; --card-bg: #ffffff; --text: #2d3748; --text-muted: #718096; --border: #e2e8f0;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: var(--bg); color: var(--text); line-height: 1.6; }
.header { background: linear-gradient(135deg, var(--primary), var(--primary-light));
          color: white; padding: 20px 32px; display: flex; justify-content: space-between;
          align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.15); }
.header h1 { font-size: 1.5rem; font-weight: 600; }
.header .subtitle { font-size: 0.85rem; opacity: 0.8; margin-top: 2px; }
.header .badge { background: var(--accent); color: var(--primary); padding: 6px 16px;
                 border-radius: 20px; font-weight: 700; font-size: 0.85rem; }
.container { max-width: 1400px; margin: 0 auto; padding: 24px; }
.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
             gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--card-bg); border-radius: 12px; padding: 20px;
             box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-left: 4px solid var(--primary); }
.stat-card.severity-severe { border-left-color: var(--danger); }
.stat-card .stat-label  { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;
                           color: var(--text-muted); margin-bottom: 4px; }
.stat-card .stat-value  { font-size: 1.8rem; font-weight: 700; color: var(--primary); }
.stat-card .stat-detail { font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; }
.stat-card .stat-value.danger { color: var(--danger); }
.flags-section { margin-bottom: 24px; }
.flag { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 8px;
        margin-bottom: 8px; font-size: 0.9rem; font-weight: 500; }
.flag.alert   { background: #fff5f5; border: 1px solid #fed7d7; color: #c53030; }
.flag.warning { background: #fffbeb; border: 1px solid #fef3c7; color: #92400e; }
.flag.info    { background: #ebf8ff; border: 1px solid #bee3f8; color: #2b6cb0; }
.main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
@media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }
.card { background: var(--card-bg); border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08); overflow: hidden; }
.card-header { background: var(--primary); color: white; padding: 14px 20px;
               font-size: 0.95rem; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.card-body { padding: 20px; }
.doc-item { display: flex; align-items: center; padding: 10px 0;
            border-bottom: 1px solid var(--border); gap: 12px; }
.doc-item:last-child { border-bottom: none; }
.doc-icon { font-size: 1.4rem; }
.doc-info { flex: 1; }
.doc-name { font-weight: 600; font-size: 0.9rem; }
.doc-type { font-size: 0.8rem; color: var(--text-muted); }
.doc-confidence { font-size: 0.75rem; padding: 3px 10px; border-radius: 12px; font-weight: 600; }
.conf-high { background: #c6f6d5; color: #22543d; }
.conf-med  { background: #fefcbf; color: #744210; }
.conf-low  { background: #fed7d7; color: #742a2a; }
.damage-item { padding: 10px 0; border-bottom: 1px solid var(--border); }
.damage-item:last-child { border-bottom: none; }
.damage-header { display: flex; justify-content: space-between; align-items: center; }
.damage-name { font-weight: 600; font-size: 0.9rem; }
.severity-badge { font-size: 0.75rem; padding: 3px 10px; border-radius: 12px;
                  font-weight: 700; text-transform: uppercase; }
.sev-major    { background: #fed7d7; color: #742a2a; }
.sev-moderate { background: #fefcbf; color: #744210; }
.sev-minor    { background: #c6f6d5; color: #22543d; }
.damage-detail { font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; }
.photo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.photo-thumb { border-radius: 8px; overflow: hidden; border: 2px solid var(--border);
               cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
.photo-thumb:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.photo-thumb img { width: 100%; height: 160px; object-fit: cover; }
.photo-caption { padding: 8px 10px; font-size: 0.75rem; color: var(--text-muted); background: #f8fafc; }
.photo-sev { display: inline-block; font-size: 0.65rem; padding: 2px 6px;
             border-radius: 8px; font-weight: 700; margin-left: 4px; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; font-size: 0.75rem; text-transform: uppercase;
                  color: var(--text-muted); padding: 8px 0; border-bottom: 2px solid var(--border); }
.data-table td { padding: 8px 0; font-size: 0.85rem; border-bottom: 1px solid var(--border); }
.data-table .amount { text-align: right; font-weight: 600; }
.data-table .total-row { font-weight: 700; background: #f8fafc; }
.data-table .total-row td { padding: 10px 0; border-top: 2px solid var(--primary); }
.json-block { background: #1e293b; color: #e2e8f0; border-radius: 8px; padding: 16px;
              font-family: 'SF Mono', 'Fira Code', monospace; font-size: 0.8rem;
              overflow-x: auto; max-height: 400px; overflow-y: auto; line-height: 1.5; }
.lightbox { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.85); z-index: 1000;
            justify-content: center; align-items: center; cursor: pointer; }
.lightbox.active { display: flex; }
.lightbox img { max-width: 90vw; max-height: 90vh; border-radius: 8px; box-shadow: 0 0 40px rgba(0,0,0,0.5); }
.pipeline-indicator { display: flex; align-items: center; gap: 24px; padding: 16px 24px;
                       background: var(--card-bg); border-radius: 12px; margin-bottom: 24px;
                       box-shadow: 0 1px 3px rgba(0,0,0,0.08); flex-wrap: wrap; }
.pipeline-step { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; }
.step-check { color: var(--success); font-weight: 700; }
.step-arrow { color: var(--text-muted); }
.footer { text-align: center; padding: 24px; color: var(--text-muted); font-size: 0.8rem; }
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>AI Claims Intake Dashboard</h1>
    <div class="subtitle">Insurance Document Processing POC — Guidewire ClaimCenter Integration</div>
  </div>
  <div class="badge">{{ summary.claim_info.claim_number }}</div>
</div>

<div class="container">
  <div class="pipeline-indicator">
    <div class="pipeline-step"><span class="step-check">✓</span> Document Classification</div>
    <span class="step-arrow">→</span>
    <div class="pipeline-step"><span class="step-check">✓</span> AI Data Extraction</div>
    <span class="step-arrow">→</span>
    <div class="pipeline-step"><span class="step-check">✓</span> Damage Analysis</div>
    <span class="step-arrow">→</span>
    <div class="pipeline-step"><span class="step-check">✓</span> Claim Summary</div>
    <span class="step-arrow">→</span>
    <div class="pipeline-step"><span class="step-check">✓</span> Guidewire Export</div>
  </div>

  <div class="stats-row">
    <div class="stat-card severity-severe">
      <div class="stat-label">Overall Severity</div>
      <div class="stat-value danger">{{ summary.damage_summary.overall_severity }}</div>
      <div class="stat-detail">{{ summary.damage_summary.total_damage_items }} damage items identified</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Documents Processed</div>
      <div class="stat-value">{{ summary.documents_processed.total }}</div>
      <div class="stat-detail">{{ summary.documents_processed.needing_review }} need review</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Property Damage Estimate</div>
      <div class="stat-value">${{ "{:,.0f}".format(summary.damage_summary.preliminary_estimate) }}</div>
      <div class="stat-detail">Preliminary — from police report</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Medical Charges</div>
      <div class="stat-value">${{ "{:,.0f}".format(summary.medical_summary.total_medical_charges) }}</div>
      <div class="stat-detail">{{ summary.medical_summary.diagnosis_codes|length }} diagnosis codes</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Processing Time</div>
      <div class="stat-value">{{ summary.processing_time_seconds }}s</div>
      <div class="stat-detail">vs ~45 min manual</div>
    </div>
  </div>

  {% if summary.flags %}
  <div class="flags-section">
    {% for flag in summary.flags %}
    <div class="flag {{ flag.level }}">
      <span>{% if flag.level == 'alert' %}🔴{% elif flag.level == 'warning' %}🟡{% else %}ℹ️{% endif %}</span>
      <span><strong>{{ flag.type }}:</strong> {{ flag.message }}</span>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  <div class="main-grid">
    <!-- Documents Classified -->
    <div class="card">
      <div class="card-header">📁 Documents Classified</div>
      <div class="card-body">
        {% for doc in classifications %}
        <div class="doc-item">
          <span class="doc-icon">{{ doc.icon }}</span>
          <div class="doc-info">
            <div class="doc-name">{{ doc.file_name }}</div>
            <div class="doc-type">{{ doc.type_label }}</div>
          </div>
          <span class="doc-confidence {% if doc.confidence >= 0.9 %}conf-high{% elif doc.confidence >= 0.8 %}conf-med{% else %}conf-low{% endif %}">
            {{ "%.0f"|format(doc.confidence * 100) }}%
          </span>
        </div>
        {% endfor %}
      </div>
    </div>

    <!-- AI Damage Assessment -->
    <div class="card">
      <div class="card-header">🔍 AI Damage Assessment</div>
      <div class="card-body">
        {% for item in summary.damage_summary.damage_items %}
        <div class="damage-item">
          <div class="damage-header">
            <span class="damage-name">{{ item.item }}</span>
            <span class="severity-badge sev-{{ item.severity|lower }}">{{ item.severity }}</span>
          </div>
          <div class="damage-detail">{{ item.damage_type }} — {{ item.area_affected }}</div>
        </div>
        {% endfor %}
      </div>
    </div>

    <!-- Photo Evidence -->
    <div class="card">
      <div class="card-header">📷 Photo Evidence &amp; Analysis</div>
      <div class="card-body">
        <div class="photo-grid">
          {% for photo in photo_analyses %}
          <div class="photo-thumb" onclick="openLightbox('{{ photo.image_path }}')">
            <img src="{{ photo.image_path }}" alt="{{ photo.photo_description }}">
            <div class="photo-caption">
              {{ photo.photo_description[:60] }}...
              <span class="photo-sev sev-{{ photo.overall_severity|lower }}">{{ photo.overall_severity }}</span>
            </div>
          </div>
          {% endfor %}
        </div>
      </div>
    </div>

    <!-- Medical Bill -->
    <div class="card">
      <div class="card-header">🏥 Medical Bill Extraction</div>
      <div class="card-body">
        {% if medical_data %}
        <p style="font-size:0.85rem; margin-bottom:12px;">
          <strong>{{ medical_data.facility }}</strong><br>
          Patient: {{ medical_data.patient_name }} | DOS: {{ medical_data.date_of_service }}<br>
          Physician: {{ medical_data.attending_physician }}
        </p>
        <table class="data-table">
          <thead><tr><th>Code</th><th>Description</th><th style="text-align:right">Amount</th></tr></thead>
          <tbody>
            {% for item in medical_data.line_items %}
            <tr><td>{{ item.code }}</td><td>{{ item.description }}</td><td class="amount">${{ "{:,.2f}".format(item.amount) }}</td></tr>
            {% endfor %}
            <tr class="total-row">
              <td></td><td><strong>TOTAL</strong></td>
              <td class="amount">${{ "{:,.2f}".format(medical_data.total_charges) }}</td>
            </tr>
          </tbody>
        </table>
        <p style="font-size:0.8rem; color:var(--text-muted); margin-top:12px;">
          <strong>Diagnosis:</strong>
          {% for d in medical_data.diagnosis_codes %}
            {{ d.code }} ({{ d.description }}){% if not loop.last %}, {% endif %}
          {% endfor %}
        </p>
        {% endif %}
      </div>
    </div>

    <!-- Extracted Claim Info -->
    <div class="card">
      <div class="card-header">📋 Extracted Claim Information</div>
      <div class="card-body">
        {% if police_data %}
        <table class="data-table">
          <tbody>
            <tr><td><strong>Report #</strong></td><td>{{ police_data.report_number }}</td></tr>
            <tr><td><strong>Date/Time</strong></td><td>{{ police_data.date_of_incident }} at {{ police_data.time_of_incident }}</td></tr>
            <tr><td><strong>Incident Type</strong></td><td>{{ police_data.incident_type }}</td></tr>
            <tr><td><strong>Location</strong></td><td>{{ police_data.location }}</td></tr>
            <tr><td><strong>Officer</strong></td><td>{{ police_data.reporting_officer }} ({{ police_data.badge_number }})</td></tr>
            <tr><td><strong>Insured</strong></td><td>{{ police_data.property_owner }}</td></tr>
            <tr><td><strong>Estimate</strong></td><td>${{ "{:,.2f}".format(police_data.estimated_damage) }}</td></tr>
            <tr><td><strong>Weather Ref</strong></td><td style="font-size:0.8rem">{{ police_data.weather_reference }}</td></tr>
          </tbody>
        </table>
        <p style="font-size:0.8rem; color:var(--text-muted); margin-top:12px;">
          <strong>Narrative:</strong> {{ police_data.narrative_summary }}
        </p>
        {% endif %}
      </div>
    </div>

    <!-- Guidewire Export -->
    <div class="card">
      <div class="card-header">⚡ Guidewire ClaimCenter Export</div>
      <div class="card-body">
        <p style="font-size:0.85rem; margin-bottom:12px; color:var(--text-muted);">
          Ready for import via ClaimCenter REST API v10 — {{ summary.guidewire_ready.mapped_fields }} fields mapped
        </p>
        <div class="json-block"><pre>{{ guidewire_json }}</pre></div>
      </div>
    </div>
  </div>
</div>

<div class="lightbox" id="lightbox" onclick="closeLightbox()">
  <img id="lightbox-img" src="" alt="Full size photo">
</div>

<div class="footer">
  AI Claims Intake POC v1.0 — Built for Farm Bureau Insurance Demo<br>
  Processed {{ summary.documents_processed.total }} documents in {{ summary.processing_time_seconds }}s
  (estimated manual time: 45+ minutes)
</div>

<script>
function openLightbox(src) {
  document.getElementById('lightbox-img').src = src;
  document.getElementById('lightbox').classList.add('active');
}
function closeLightbox() {
  document.getElementById('lightbox').classList.remove('active');
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeLightbox(); });
</script>
</body>
</html>
"""


@app.route("/photos/<path:filename>")
def serve_photo(filename):
    return send_from_directory(str(PHOTOS_DIR), filename)


@app.route("/")
def dashboard():
    results = run_pipeline(str(DATA_DIR))

    photo_files = sorted(PHOTOS_DIR.glob("*.png"))
    for i, analysis in enumerate(results["photo_analyses"]):
        if i < len(photo_files):
            analysis["image_path"] = f"/photos/{photo_files[i].name}"

    police_data, medical_data = None, None
    for ext in results["extractions"]:
        if "report_number" in ext:
            police_data = ext
        if "facility" in ext:
            medical_data = ext

    gw_json = json.dumps(results["guidewire_export"], indent=2, default=str)
    return render_template_string(
        DASHBOARD_HTML,
        summary=results["summary"],
        classifications=results["classifications"],
        photo_analyses=results["photo_analyses"],
        police_data=police_data,
        medical_data=medical_data,
        guidewire_json=gw_json,
    )


@app.route("/api/results")
def api_results():
    results = run_pipeline(str(DATA_DIR))
    return jsonify(results)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "="*60)
    print("  AI Claims Intake Dashboard")
    print("  Open http://localhost:5050 in your browser")
    print("="*60 + "\n")
    app.run(debug=True, port=5050)
