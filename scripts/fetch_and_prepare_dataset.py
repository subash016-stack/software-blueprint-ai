"""
scripts/fetch_and_prepare_dataset.py
Fetches the canonical PROMISE NFR software requirements dataset (Kaggle / Tera-PROMISE),
cleans and normalizes it, and combines it with our multi-domain benchmark dataset
to produce a unified training corpus for FR vs NFR classification.
"""

import csv
import json
import os
import re
import urllib.request
from typing import List, Dict

PROMISE_URL = "https://raw.githubusercontent.com/AleksandarMitrevski/se-requirements-classification/master/0-datasets/PROMISE_exp/PROMISE_exp.arff"

DATASETS_DIR = os.path.join("app", "benchmark", "datasets")
PROMISE_CSV_PATH = os.path.join(DATASETS_DIR, "promise_nfr_dataset.csv")
BENCHMARK_JSON_PATH = os.path.join(DATASETS_DIR, "requirements_ground_truth.json")
UNIFIED_CSV_PATH = os.path.join(DATASETS_DIR, "unified_requirements_train.csv")


def fetch_promise_dataset() -> List[Dict[str, str]]:
    """Downloads and parses the PROMISE_exp.arff dataset."""
    print(f"[1/3] Downloading PROMISE NFR dataset from {PROMISE_URL}...")
    try:
        req = urllib.request.Request(
            PROMISE_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching PROMISE dataset from remote: {e}")
        return []

    data_section = False
    records = []
    
    # Class mapping: F -> FR, everything else (PE, LF, US, A, SE, O, SC, PO, MN, FT, L) -> NFR
    class_names = {
        "F": "Functional",
        "A": "Availability",
        "LF": "Look & Feel",
        "MN": "Maintainability",
        "O": "Operational",
        "PE": "Performance",
        "PO": "Portability",
        "SC": "Scalability",
        "SE": "Security",
        "US": "Usability",
        "FT": "Fault Tolerance",
        "L": "Legal / Compliance"
    }

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("%"):
            continue
        if line.lower().startswith("@data"):
            data_section = True
            continue
        if not data_section:
            continue

        # Format: ProjectID, 'RequirementText', Class
        # Parse using regex matching: digit, quote, text, quote, comma, class
        m = re.match(r"^(\d+)\s*,\s*['\"]?(.*?)['\"]?\s*,\s*([A-Za-z]+)$", line)
        if m:
            pid, text, raw_class = m.groups()
            text = text.replace("''", "'").strip()
            if len(text) < 5:
                continue

            raw_class_clean = raw_class.strip().upper()
            is_functional = (raw_class_clean == "F")
            label = "FR" if is_functional else "NFR"
            category = class_names.get(raw_class_clean, "Quality Attribute")

            records.append({
                "source": "PROMISE_Kaggle",
                "project_id": pid,
                "text": text,
                "label": label,
                "raw_class": raw_class_clean,
                "category": category
            })

    print(f"Parsed {len(records)} requirements from PROMISE dataset.")
    return records


def load_benchmark_dataset() -> List[Dict[str, str]]:
    """Loads our 120-item multi-domain benchmark dataset."""
    print(f"[2/3] Loading multi-domain benchmark dataset from {BENCHMARK_JSON_PATH}...")
    if not os.path.exists(BENCHMARK_JSON_PATH):
        print(f"Warning: {BENCHMARK_JSON_PATH} not found.")
        return []

    with open(BENCHMARK_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = []
    for item in data:
        label = item.get("expected_label")
        if hasattr(label, "value"):
            label = label.value
        records.append({
            "source": "MultiDomain_Benchmark",
            "project_id": item.get("domain", "Domain"),
            "text": item.get("text", "").strip(),
            "label": str(label),
            "raw_class": str(label),
            "category": item.get("category", "General")
        })

    print(f"Loaded {len(records)} requirements from multi-domain benchmark.")
    return records


def build_unified_dataset():
    """Combines datasets and writes to CSV files."""
    os.makedirs(DATASETS_DIR, exist_ok=True)
    promise_data = fetch_promise_dataset()
    benchmark_data = load_benchmark_dataset()

    # Save PROMISE standalone CSV
    if promise_data:
        with open(PROMISE_CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["source", "project_id", "text", "label", "raw_class", "category"])
            writer.writeheader()
            writer.writerows(promise_data)
        print(f"Saved standalone PROMISE dataset to {PROMISE_CSV_PATH}")

    # Combine
    combined = []
    seen_texts = set()

    for r in promise_data + benchmark_data:
        normalized_text = r["text"].lower().strip()
        if normalized_text and normalized_text not in seen_texts:
            seen_texts.add(normalized_text)
            combined.append(r)

    print(f"[3/3] Saving unified dataset ({len(combined)} unique requirements) to {UNIFIED_CSV_PATH}...")
    with open(UNIFIED_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "project_id", "text", "label", "raw_class", "category"])
        writer.writeheader()
        writer.writerows(combined)

    # Class balance summary
    fr_count = sum(1 for r in combined if r["label"] == "FR")
    nfr_count = sum(1 for r in combined if r["label"] == "NFR")
    print(f"Dataset summary: Total = {len(combined)} | FR = {fr_count} ({fr_count/len(combined)*100:.1f}%) | NFR = {nfr_count} ({nfr_count/len(combined)*100:.1f}%)")


if __name__ == "__main__":
    build_unified_dataset()

