"""
AI-Powered Insurance Claims Document Intake Pipeline
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

DOCUMENT_TYPES = {
    "police_report":  {"label": "Police / Incident Report",   "priority": 1,  "icon": "📋"},
    "medical_bill":   {"label": "Medical Bill / Statement",   "priority": 2,  "icon": "🏥"},
    "damage_photo":   {"label": "Damage Photograph",          "priority": 3,  "icon": "📷"},
    "estimate":       {"label": "Repair Estimate",            "priority": 4,  "icon": "🔧"},
    "correspondence": {"label": "Correspondence / Letter",    "priority": 5,  "icon": "✉️"},
    "unknown":        {"label": "Unclassified Document",      "priority": 99, "icon": "❓"},
}


def classify_document(file_path: str) -> dict:
    name = Path(file_path).name.lower()
    ext  = Path(file_path).suffix.lower()
    if ext in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"):
        doc_type, confidence = "damage_photo", 0.95
    elif "police" in name or "incident" in name or "report" in name:
        doc_type, confidence = "police_report", 0.92
    elif "medical" in name or "bill" in name or "hospital" in name:
        doc_type, confidence = "medical_bill", 0.90
    elif "estimate" in name or "quote" in name:
        doc_type, confidence = "estimate", 0.88
    else:
        doc_type, confidence = "unknown", 0.40
    return {
        "file_path":     file_path,
        "file_name":     Path(file_path).name,
        "document_type": doc_type,
        "type_label":    DOCUMENT_TYPES[doc_type]["label"],
        "confidence":    confidence,
        "icon":          DOCUMENT_TYPES[doc_type]["icon"],
        "needs_review":  confidence < 0.85,
    }


def extract_from_police_report(file_path: str) -> dict:
    return {
        "extraction_method":   "AI Document Parser v1.0 (POC - simulated)",
        "report_number":       "BPD-2026-041200387",
        "date_of_incident":    "2026-04-12",
        "time_of_incident":    "02:35",
        "incident_type":       "Wind/Hail Storm Damage",
        "location":            "4521 Maple Creek Dr, Boise, ID 83702",
        "reporting_officer":   "Officer David M. Torres",
        "badge_number":        "BPD-4412",
        "property_owner":      "Robert J. Henderson",
        "owner_phone":         "(208) 555-0147",
        "narrative_summary":   (
            "Severe thunderstorm with 65 mph winds and golf-ball-sized hail. "
            "Damage to roof, siding, windows, landscaping. Large oak tree fell on "
            "detached garage. Water intrusion in master bedroom."
        ),
        "estimated_damage":    47250.00,
        "witnesses": [
            {"name": "Susan K. Park",   "phone": "(208) 555-0198"},
            {"name": "Michael R. Dunn", "phone": "(208) 555-0234"},
        ],
        "responding_units":    ["Engine 7", "BPD Unit 22", "Ada County Emergency Mgmt"],
        "weather_reference":   "NWS Boise Office – Severe Thunderstorm Warning #0412-026",
        "fields_extracted":    13,
        "extraction_confidence": 0.94,
    }


def extract_from_medical_bill(file_path: str) -> dict:
    return {
        "extraction_method":  "AI Document Parser v1.0 (POC - simulated)",
        "facility":           "St. Luke's Regional Medical Center",
        "facility_address":   "190 E. Bannock St, Boise, ID 83712",
        "patient_name":       "Robert J. Henderson",
        "patient_dob":        "1978-03-14",
        "account_number":     "SLH-2026-88401",
        "date_of_service":    "2026-04-12",
        "attending_physician":"Dr. Sarah M. Kim, MD",
        "diagnosis_codes": [
            {"code": "S40.011A", "description": "Contusion right shoulder"},
            {"code": "S51.811A", "description": "Laceration right forearm"},
        ],
        "line_items": [
            {"code": "99283", "description": "Emergency Dept Visit – Moderate", "amount": 1245.00},
            {"code": "73030", "description": "X-Ray, Shoulder (2 views)",        "amount":  385.00},
            {"code": "29105", "description": "Splint Application, Long Arm",     "amount":  290.00},
            {"code": "99070", "description": "Supplies / Materials",              "amount":  125.00},
        ],
        "total_charges":        2045.00,
        "injury_context":       "Sustained during storm event while securing property",
        "fields_extracted":     11,
        "extraction_confidence": 0.91,
    }


def analyze_damage_photo(file_path: str) -> dict:
    name = Path(file_path).name.lower()
    analyses = {
        "roof": {
            "analysis_method":   "AI Vision Damage Detector v1.0 (POC - simulated)",
            "photo_description": "Exterior overview showing roof, fallen tree, and hail damage",
            "damage_items": [
                {"item": "Roof shingles",   "damage_type": "Missing/displaced",          "severity": "Major",    "area_affected": "~40% of roof surface"},
                {"item": "Detached garage", "damage_type": "Structural (fallen tree)",   "severity": "Major",    "area_affected": "Roof and north wall"},
                {"item": "Windows",         "damage_type": "Cracked glass",               "severity": "Moderate", "area_affected": "2 of 4 visible windows"},
                {"item": "Landscaping",     "damage_type": "Uprooted tree, hail debris", "severity": "Moderate", "area_affected": "Front yard"},
            ],
            "overall_severity": "MAJOR",
            "confidence": 0.89,
        },
        "hail": {
            "analysis_method":   "AI Vision Damage Detector v1.0 (POC - simulated)",
            "photo_description": "Close-up of vinyl siding showing hail impact dents",
            "damage_items": [
                {"item": "Vinyl siding", "damage_type": "Hail dents/impacts", "severity": "Moderate", "area_affected": "~25 visible impact points"},
                {"item": "Vinyl siding", "damage_type": "Cracking",           "severity": "Moderate", "area_affected": "2 visible cracks"},
            ],
            "overall_severity": "MODERATE",
            "confidence": 0.92,
        },
        "water": {
            "analysis_method":   "AI Vision Damage Detector v1.0 (POC - simulated)",
            "photo_description": "Interior showing ceiling water stain, wall damage, wet carpet",
            "damage_items": [
                {"item": "Ceiling",     "damage_type": "Water stain/saturation", "severity": "Major",    "area_affected": "~3ft diameter area"},
                {"item": "Wall paint",  "damage_type": "Peeling/bubbling",        "severity": "Moderate", "area_affected": "Below leak area"},
                {"item": "Carpet",      "damage_type": "Water saturation",        "severity": "Major",    "area_affected": "~8ft x 6ft section"},
            ],
            "overall_severity": "MAJOR",
            "confidence": 0.87,
        },
        "vehicle": {
            "analysis_method":   "AI Vision Damage Detector v1.0 (POC - simulated)",
            "photo_description": "Vehicle showing hail damage to hood and cracked windshield",
            "damage_items": [
                {"item": "Vehicle hood", "damage_type": "Hail dents", "severity": "Major", "area_affected": "~40 impact points"},
                {"item": "Windshield",   "damage_type": "Cracked",    "severity": "Major", "area_affected": "Multiple crack lines"},
            ],
            "overall_severity": "MAJOR",
            "confidence": 0.93,
        },
    }
    for key, analysis in analyses.items():
        if key in name:
            return analysis
    return {
        "analysis_method":   "AI Vision Damage Detector v1.0 (POC - simulated)",
        "photo_description": "Damage photo — requires manual review",
        "damage_items":      [],
        "overall_severity":  "UNKNOWN",
        "confidence":        0.50,
    }


def generate_claim_summary(classifications, extractions, photo_analyses):
    police_data, medical_data = None, None
    for ext in extractions:
        if "report_number" in ext:
            police_data = ext
        if "facility" in ext:
            medical_data = ext

    all_damage_items = []
    severity_counts = {"Major": 0, "Moderate": 0, "Minor": 0}
    for analysis in photo_analyses:
        for item in analysis.get("damage_items", []):
            all_damage_items.append(item)
            sev = item.get("severity", "Unknown")
            if sev in severity_counts:
                severity_counts[sev] += 1

    if severity_counts["Major"] >= 3:
        overall = "SEVERE"
    elif severity_counts["Major"] >= 1:
        overall = "MAJOR"
    elif severity_counts["Moderate"] >= 2:
        overall = "MODERATE"
    else:
        overall = "MINOR"

    summary = {
        "claim_intake_timestamp": datetime.now().isoformat(),
        "pipeline_version":       "AI Claims Intake POC v1.0",
        "processing_time_seconds": 2.3,
        "claim_info": {
            "claim_number":    "CLM-2026-004817",
            "policy_number":   "HO-FB-2024-991203",
            "line_of_business": "Homeowners",
            "loss_type":       police_data.get("incident_type", "Unknown") if police_data else "Unknown",
            "loss_date":       police_data.get("date_of_incident", "")    if police_data else "",
            "loss_time":       police_data.get("time_of_incident", "")    if police_data else "",
            "loss_location":   police_data.get("location", "")            if police_data else "",
        },
        "insured": {
            "name":    police_data.get("property_owner", "") if police_data else "",
            "phone":   police_data.get("owner_phone", "")    if police_data else "",
            "address": police_data.get("location", "")       if police_data else "",
        },
        "damage_summary": {
            "overall_severity":   overall,
            "total_damage_items": len(all_damage_items),
            "severity_breakdown": severity_counts,
            "damage_items":       all_damage_items,
            "preliminary_estimate": police_data.get("estimated_damage", 0) if police_data else 0,
        },
        "medical_summary": {
            "has_bodily_injury":    medical_data is not None,
            "total_medical_charges": medical_data.get("total_charges", 0)      if medical_data else 0,
            "diagnosis_codes":       medical_data.get("diagnosis_codes", [])   if medical_data else [],
            "injury_context":        medical_data.get("injury_context", "")    if medical_data else "",
        },
        "documents_processed": {
            "total":          len(classifications),
            "by_type":        {},
            "needing_review": sum(1 for c in classifications if c.get("needs_review")),
        },
        "flags": [],
        "guidewire_ready": {
            "format":        "ClaimCenter REST API v10",
            "status":        "Ready for import",
            "mapped_fields": 28,
        },
    }

    for c in classifications:
        t = c["document_type"]
        summary["documents_processed"]["by_type"][t] = summary["documents_processed"]["by_type"].get(t, 0) + 1

    if overall in ("SEVERE", "MAJOR"):
        summary["flags"].append({
            "type":    "HIGH_SEVERITY",
            "message": f"Claim assessed as {overall} severity — prioritize assignment",
            "level":   "warning",
        })
    if medical_data:
        summary["flags"].append({
            "type":    "BODILY_INJURY",
            "message": f"Bodily injury reported — medical charges: ${medical_data['total_charges']:,.2f}",
            "level":   "alert",
        })
    if severity_counts["Major"] >= 3:
        summary["flags"].append({
            "type":    "MULTIPLE_STRUCTURES",
            "message": "Multiple major damage items — consider field inspection",
            "level":   "warning",
        })
    if any(c.get("needs_review") for c in classifications):
        summary["flags"].append({
            "type":    "LOW_CONFIDENCE",
            "message": "One or more documents had low classification confidence",
            "level":   "info",
        })
    return summary


def to_guidewire_format(summary):
    claim   = summary["claim_info"]
    insured = summary["insured"]
    damage  = summary["damage_summary"]
    medical = summary["medical_summary"]

    gw_payload = {
        "data": {
            "attributes": {
                "claimNumber":  claim["claim_number"],
                "policyNumber": claim["policy_number"],
                "lossDate":     claim["loss_date"],
                "lossType": {
                    "code": "WaterDamage" if "water" in claim["loss_type"].lower() else "WindAndHail",
                    "name": claim["loss_type"],
                },
                "lossCause": {"code": "weather_storm", "name": "Weather - Severe Storm"},
                "lossLocation": {
                    "addressLine1": insured["address"].split(",")[0] if insured["address"] else "",
                    "city":         "Boise",
                    "state":        "ID",
                    "postalCode":   "83702",
                },
                "reporter": {
                    "displayName":  insured["name"],
                    "primaryPhone": insured["phone"],
                },
                "severity": {
                    "code": damage["overall_severity"].lower(),
                    "name": damage["overall_severity"],
                },
                "description": (
                    f"AI-processed claim intake: {damage['total_damage_items']} damage items identified "
                    f"across {summary['documents_processed']['total']} documents. "
                    f"Overall severity: {damage['overall_severity']}. "
                    f"Preliminary estimate: ${damage['preliminary_estimate']:,.2f}."
                ),
            },
            "exposures": [],
        }
    }

    gw_payload["data"]["exposures"].append({
        "exposureType":   "PropertyDamage",
        "lossParty":      "insured",
        "severity":       damage["overall_severity"].lower(),
        "description":    f"{damage['total_damage_items']} damage items identified by AI analysis",
        "estimatedAmount": damage["preliminary_estimate"],
    })

    if medical["has_bodily_injury"]:
        gw_payload["data"]["exposures"].append({
            "exposureType":   "BodilyInjury",
            "lossParty":      "insured",
            "description":    medical["injury_context"],
            "diagnosisCodes": [d["code"] for d in medical["diagnosis_codes"]],
            "medicalCharges": medical["total_medical_charges"],
        })

    return gw_payload


def run_pipeline(input_dir: str) -> dict:
    input_path = Path(input_dir)
    all_files = []
    for pattern in ("**/*.pdf", "**/*.png", "**/*.jpg", "**/*.jpeg", "**/*.tif"):
        all_files.extend(input_path.glob(pattern))
    all_files.sort()

    if not all_files:
        return {"error": f"No documents found in {input_dir}"}

    print(f"\n{'='*60}")
    print(f"  AI CLAIMS DOCUMENT INTAKE PIPELINE")
    print(f"  Processing {len(all_files)} documents from {input_dir}")
    print(f"{'='*60}\n")

    print("Step 1: Document Classification\n" + "-"*40)
    classifications = []
    for f in all_files:
        result = classify_document(str(f))
        classifications.append(result)
        status = "✅" if not result["needs_review"] else "⚠️  NEEDS REVIEW"
        print(f"  {result['icon']}  {result['file_name']}")
        print(f"     → {result['type_label']} (confidence: {result['confidence']:.0%}) {status}")

    print(f"\nStep 2: Data Extraction\n" + "-"*40)
    extractions, photo_analyses = [], []
    for cls in classifications:
        if cls["document_type"] == "police_report":
            data = extract_from_police_report(cls["file_path"])
            extractions.append(data)
            print(f"  📋 Police Report: {data['fields_extracted']} fields extracted (confidence: {data['extraction_confidence']:.0%})")
        elif cls["document_type"] == "medical_bill":
            data = extract_from_medical_bill(cls["file_path"])
            extractions.append(data)
            print(f"  🏥 Medical Bill:  {data['fields_extracted']} fields extracted (confidence: {data['extraction_confidence']:.0%})")
        elif cls["document_type"] == "damage_photo":
            data = analyze_damage_photo(cls["file_path"])
            photo_analyses.append(data)
            print(f"  📷 Photo Analysis: {len(data.get('damage_items', []))} damage items found — Severity: {data['overall_severity']} (confidence: {data['confidence']:.0%})")

    print(f"\nStep 3: Claim Summary Generation\n" + "-"*40)
    summary = generate_claim_summary(classifications, extractions, photo_analyses)
    damage = summary["damage_summary"]
    print(f"  Overall Severity:    {damage['overall_severity']}")
    print(f"  Damage Items:        {damage['total_damage_items']}")
    print(f"  Preliminary Estimate: ${damage['preliminary_estimate']:,.2f}")
    print(f"  Medical Charges:     ${summary['medical_summary']['total_medical_charges']:,.2f}")
    print(f"  Documents Processed: {summary['documents_processed']['total']}")

    print(f"\nStep 4: Guidewire Export\n" + "-"*40)
    gw_export = to_guidewire_format(summary)
    print(f"  Format:        {summary['guidewire_ready']['format']}")
    print(f"  Mapped Fields: {summary['guidewire_ready']['mapped_fields']}")
    print(f"  Exposures:     {len(gw_export['data']['exposures'])}")
    print(f"  Status:        ✅ {summary['guidewire_ready']['status']}")

    if summary["flags"]:
        print(f"\n⚠️  FLAGS FOR ADJUSTER REVIEW\n" + "-"*40)
        for flag in summary["flags"]:
            icon = "🔴" if flag["level"] == "alert" else "🟡" if flag["level"] == "warning" else "ℹ️"
            print(f"  {icon} [{flag['type']}] {flag['message']}")

    print(f"\n{'='*60}")
    print(f"  ✅ Pipeline complete — ready for ClaimCenter import")
    print(f"{'='*60}\n")

    return {
        "classifications":  classifications,
        "extractions":      extractions,
        "photo_analyses":   photo_analyses,
        "summary":          summary,
        "guidewire_export": gw_export,
    }


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent / "data"
    results = run_pipeline(str(base))

    output_dir = base.parent / "output"
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "claim_summary.json", "w") as f:
        json.dump(results["summary"], f, indent=2, default=str)
    with open(output_dir / "guidewire_export.json", "w") as f:
        json.dump(results["guidewire_export"], f, indent=2, default=str)
    with open(output_dir / "full_pipeline_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Results saved to {output_dir}/")
