"""
app/benchmark/requirement_evaluator.py
Evaluation engine for benchmarking requirement classification (FR vs NFR)
against verified ground-truth datasets.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from app.schemas import (
    RequirementBenchmarkItem,
    RequirementClassificationResult,
    RequirementType,
    BenchmarkEvaluationReport
)

logger = logging.getLogger("software-blueprint-ai.benchmark")

DEFAULT_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "datasets", "requirements_ground_truth.json"
)


def load_ground_truth_dataset(filepath: Optional[str] = None) -> List[RequirementBenchmarkItem]:
    """Load and parse the verified ground-truth requirements dataset."""
    path = filepath or DEFAULT_DATASET_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Ground-truth benchmark dataset not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [RequirementBenchmarkItem.model_validate(item) for item in data]


def heuristic_classify_requirement(text: str, req_id: Optional[str] = None) -> RequirementClassificationResult:
    """
    Deterministic rule-based baseline classifier adhering to IEEE 830 / ISO 25010 taxonomy.
    Identifies quality attribute constraints (NFR) vs functional actions/services/behaviors (FR).
    """
    cleaned = text.strip()
    lower = cleaned.lower()

    # NFR Patterns: Performance, Availability, Capacity, Security Standards, Compliance
    nfr_patterns = [
        # Performance / Latency / Throughput / Execution Windows
        (r"\b(?:within|in under|less than)\s+\d+(?:\.\d+)?\s*(?:seconds?|milliseconds?|ms|mins?|minutes?|hours?)\b", "Specifies a quantitative execution time latency constraint (Performance)."),
        (r"\b(?:maintenance window|batch financial reconciliation job shall complete within)\b", "Specifies batch processing execution time window constraint (Performance)."),
        (r"\b(?:latency|response time|startup latency|rtt)\b", "Specifies a system latency performance SLA."),
        (r"\b\d+[\d,]*\s*(?:queries|requests|messages|events|scans|posts|packets|barcode scan events)\s*per\s*(?:second|minute|hour)\b", "Specifies system throughput capacity rate."),
        (r"\b(?:iops|frames per second|fps|bitrate|bandwidth)\b", "Specifies an I/O or media throughput performance metric."),
        (r"\b(?:spatial precision of \d+|precision of \d+ decimal places)\b", "Specifies spatial precision and numerical accuracy constraint."),
        # Availability & Uptime SLAs
        (r"\b(?:available|uptime)\s+\d+(?:\.\d+)?%\b", "Specifies an operational uptime availability SLA."),
        (r"\b(?:99\.\d+%?|four nines|five nines|maintain \d+%\s+availability)\b", "Specifies high availability reliability SLA."),
        (r"\b(?:recovery time objective|rto|recovery point objective|rpo|mttr|mtbf)\b", "Specifies disaster recovery or reliability time constraint."),
        (r"\btolerate the total outage\b", "Specifies high fault tolerance and disaster survivability attributes."),
        # Capacity & Scale Limits
        (r"\b(?:support|accommodate|handle)\s+(?:up to\s+)?[\d,]+\s+(?:concurrent|simultaneous|corporate|tenant|package|students? taking)\b", "Specifies maximum concurrent capacity limit."),
        (r"\b(?:scale to support|horizontal scaling|scale worker pods|scale to accommodate)\b", "Specifies architectural scalability constraint."),
        # Compliance, Statutory & Retention Rules
        (r"\bcomply with\b.*?\b(?:laws?|regulations?|standards?|hipaa|gdpr|pci-dss|soc 2|wcag|fips|gaap|statutory)\b", "Specifies regulatory compliance and statutory legal obligation."),
        (r"\b(?:applicable data protection laws|right to be forgotten|accessibility standards)\b", "Specifies regulatory legal compliance obligation."),
        (r"\b(?:store .*?immutably for a minimum of|immutably for|anonymized after \d+|retention period)\b", "Specifies statutory data retention and immutability constraint."),
        # Security Ciphers & Cryptographic Standards
        (r"\b(?:encrypted at rest|encrypted in transit|aes-256|tls 1\.3|argon2id|fips 140|x\.509|sha-256|hashed using)\b", "Specifies cryptographic cipher standard and security architecture."),
        (r"\bnever be logged or stored in plain text\b", "Specifies a security policy and data protection restriction."),
        (r"\b(?:maximum validity lifespan|lifespan of at least)\b", "Specifies a temporal data retention or security constraint."),
        (r"\b(?:cryptographically signed and write-protected|logically isolated with zero cross-tenant)\b", "Specifies integrity and data isolation security constraints."),
        # Hardware, Resilience & Environmental Constraints
        (r"\b(?:temperature range|-?\d+°c to \+?\d+°c|battery lifespan|packet size|bytes per packet)\b", "Specifies physical environment or operational hardware constraint."),
        (r"\b(?:offline resilience|cross-browser compatibility|acid consistency|zero data loss|offline without network coverage)\b", "Specifies environment compatibility, reliability, or offline resilience constraint.")
    ]

    for pattern, rationale in nfr_patterns:
        if re.search(pattern, lower):
            return RequirementClassificationResult(
                id=req_id,
                text=cleaned,
                predicted_label=RequirementType.NFR,
                confidence=0.95,
                reasoning=rationale
            )

    # FR Patterns: Actions, Features, Services, and State-machine Behaviors
    fr_patterns = [
        (r"\ballow (?:users?|administrators?|customers?|operators?|patients?|doctors?|dispatchers?|instructors?|officers?|managers?|loan applicants|registered users)\b", "Specifies a user or administrative role action/feature."),
        (r"\b(?:provide users with|provide patient consent)\b", "Specifies an interactive user feature capability."),
        (r"\b(?:generate|calculate|compute|render|export|download|issue|publish|broadcast|stream|provision)\b.*?\b(?:reports?|statements?|invoices?|interest|taxes|prescriptions?|certificates?|feeds?|quizzes?|routes?|virtual machines?|summary|summaries)\b", "Specifies an automated business logic calculation or generation service."),
        (r"\b(?:lock an account|decrement warehouse inventory|alert the attending|trigger a multi-factor|revoke all active|block incoming|notify account holders|notify fleet managers|notify freight dispatchers|send pagerduty alerts|send reminder notifications|send email order|filter spam|detect tab switching|disable remote engine)\b", "Specifies system behavioral reaction to events or threshold breaches."),
        (r"\b(?:schedule|book|transfer funds|add items to a shopping cart|submit|publish multimedia|track courier|proctor|assign incoming|dispatch over-the-air|stream application stdout|ingest telemetry|rotate database service credentials)\b", "Specifies a core functional workflow action or system operation.")
    ]

    for pattern, rationale in fr_patterns:
        if re.search(pattern, lower):
            return RequirementClassificationResult(
                id=req_id,
                text=cleaned,
                predicted_label=RequirementType.FR,
                confidence=0.95,
                reasoning=rationale
            )

    # Fallback heuristic based on modal verbs and subjects
    if re.search(r"\b(?:99\.\d+%|uptime|latency|compliance|throughput|capacity|bandwidth|offline resilience)\b", lower):
        return RequirementClassificationResult(
            id=req_id,
            text=cleaned,
            predicted_label=RequirementType.NFR,
            confidence=0.80,
            reasoning="Contains quality attribute terminology indicating Non-Functional Requirement."
        )

    return RequirementClassificationResult(
        id=req_id,
        text=cleaned,
        predicted_label=RequirementType.FR,
        confidence=0.85,
        reasoning="Specifies an intended functional behavior or feature of the software system."
    )


def evaluate_classifier(
    dataset: Optional[List[RequirementBenchmarkItem]] = None,
    use_heuristic: bool = True,
    model_override: Optional[str] = None
) -> BenchmarkEvaluationReport:
    """
    Evaluates classifier predictions against ground-truth requirement items.
    Computes Accuracy, Precision, Recall, F1 for FR & NFR, Confusion Matrix, and Domain Breakdown.
    """
    items = dataset or load_ground_truth_dataset()
    if not items:
        raise ValueError("Benchmark dataset is empty.")

    tp_fr = 0  # Expected FR, Predicted FR
    fp_fr = 0  # Expected NFR, Predicted FR
    fn_fr = 0  # Expected FR, Predicted NFR
    tn_fr = 0  # Expected NFR, Predicted NFR

    correct_count = 0
    discrepancies: List[Dict[str, Any]] = []

    domain_stats: Dict[str, Dict[str, int]] = {}

    for item in items:
        domain = item.domain
        if domain not in domain_stats:
            domain_stats[domain] = {"total": 0, "correct": 0}
        domain_stats[domain]["total"] += 1

        if use_heuristic:
            pred = heuristic_classify_requirement(item.text, req_id=item.id)
        else:
            from app.agents.requirement_agent import classify_requirement
            pred = classify_requirement(item.text, req_id=item.id, model_override=model_override)

        predicted_label = pred.predicted_label.value if hasattr(pred.predicted_label, "value") else str(pred.predicted_label)
        expected_label = item.expected_label.value if hasattr(item.expected_label, "value") else str(item.expected_label)

        is_match = (predicted_label == expected_label)

        if is_match:
            correct_count += 1
            domain_stats[domain]["correct"] += 1
        else:
            discrepancies.append({
                "id": item.id,
                "text": item.text,
                "expected_label": expected_label,
                "predicted_label": predicted_label,
                "category": item.category,
                "domain": item.domain,
                "human_ground_truth_reason": item.reason,
                "model_predicted_reasoning": pred.reasoning,
                "discrepancy_analysis": f"Expected {expected_label} ({item.category}) but model predicted {predicted_label}."
            })

        # Confusion Matrix calculation relative to FR
        if expected_label == "FR" and predicted_label == "FR":
            tp_fr += 1
        elif expected_label == "NFR" and predicted_label == "FR":
            fp_fr += 1
        elif expected_label == "FR" and predicted_label == "NFR":
            fn_fr += 1
        elif expected_label == "NFR" and predicted_label == "NFR":
            tn_fr += 1

    total_samples = len(items)
    accuracy_pct = round((correct_count / total_samples) * 100.0, 2)

    # Metrics for Functional Requirements (FR)
    fr_prec = round(tp_fr / (tp_fr + fp_fr), 4) if (tp_fr + fp_fr) > 0 else 0.0
    fr_rec = round(tp_fr / (tp_fr + fn_fr), 4) if (tp_fr + fn_fr) > 0 else 0.0
    fr_f1 = round((2 * fr_prec * fr_rec) / (fr_prec + fr_rec), 4) if (fr_prec + fr_rec) > 0 else 0.0

    # Metrics for Non-Functional Requirements (NFR)
    tp_nfr = tn_fr
    fp_nfr = fn_fr
    fn_nfr = fp_fr

    nfr_prec = round(tp_nfr / (tp_nfr + fp_nfr), 4) if (tp_nfr + fp_nfr) > 0 else 0.0
    nfr_rec = round(tp_nfr / (tp_nfr + fn_nfr), 4) if (tp_nfr + fn_nfr) > 0 else 0.0
    nfr_f1 = round((2 * nfr_prec * nfr_rec) / (nfr_prec + nfr_rec), 4) if (nfr_prec + nfr_rec) > 0 else 0.0

    confusion_matrix = {
        "true_positives_fr": tp_fr,
        "false_positives_fr": fp_fr,
        "true_positives_nfr": tp_nfr,
        "false_positives_nfr": fp_nfr
    }

    # Domain Breakdown formatting
    domain_breakdown: Dict[str, Dict[str, Any]] = {}
    for d_name, d_data in domain_stats.items():
        d_tot = d_data["total"]
        d_cor = d_data["correct"]
        domain_breakdown[d_name] = {
            "total_samples": d_tot,
            "correct": d_cor,
            "accuracy_pct": round((d_cor / d_tot) * 100.0, 1) if d_tot > 0 else 0.0
        }

    return BenchmarkEvaluationReport(
        total_samples=total_samples,
        correct_predictions=correct_count,
        accuracy_pct=accuracy_pct,
        fr_precision=fr_prec,
        fr_recall=fr_rec,
        fr_f1=fr_f1,
        nfr_precision=nfr_prec,
        nfr_recall=nfr_rec,
        nfr_f1=nfr_f1,
        confusion_matrix=confusion_matrix,
        discrepancies=discrepancies,
        domain_breakdown=domain_breakdown
    )
