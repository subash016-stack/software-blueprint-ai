"""
tests/test_requirement_benchmark.py
Unit and integration tests for Method A Ground-Truth Requirements Benchmark.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import RequirementType
from app.benchmark.requirement_evaluator import (
    load_ground_truth_dataset,
    heuristic_classify_requirement,
    evaluate_classifier
)
from app.agents.requirement_agent import classify_requirement, batch_classify_requirements

client = TestClient(app)


def test_ground_truth_dataset_integrity():
    """Verify ground truth dataset loads, contains 120 verified items, and has balanced distribution."""
    dataset = load_ground_truth_dataset()
    assert len(dataset) >= 100
    assert len(dataset) == 120

    fr_items = [i for i in dataset if i.expected_label == RequirementType.FR]
    nfr_items = [i for i in dataset if i.expected_label == RequirementType.NFR]

    assert len(fr_items) == 60
    assert len(nfr_items) == 60

    # Verify all items have non-empty fields
    for item in dataset:
        assert item.id.startswith("BENCH-")
        assert len(item.text) > 10
        assert item.expected_label in (RequirementType.FR, RequirementType.NFR)
        assert len(item.category) > 0
        assert len(item.reason) > 0
        assert len(item.domain) > 0
        assert "Consensus" in item.reviewer_agreement


def test_user_exemplar_requirements_classification():
    """Verify exact classifications on the user's 8 exemplar requirements."""
    exemplars = [
        ("The system shall allow users to reset passwords.", RequirementType.FR),
        ("The system shall respond within 2 seconds.", RequirementType.NFR),
        ("The system shall generate monthly sales reports.", RequirementType.FR),
        ("The system shall be available 99.9% of the time.", RequirementType.NFR),
        ("The system shall lock an account after five failed attempts.", RequirementType.FR),
        ("The system shall comply with applicable data protection laws.", RequirementType.NFR),
        ("The system shall allow administrators to disable accounts.", RequirementType.FR),
        ("The system shall support 5,000 concurrent users.", RequirementType.NFR),
    ]

    for text, expected in exemplars:
        result = heuristic_classify_requirement(text)
        assert result.predicted_label == expected, (
            f"Failed on exemplar: '{text}'. Expected {expected}, got {result.predicted_label}."
        )
        assert result.confidence > 0.70
        assert len(result.reasoning) > 0


def test_benchmark_evaluator_metrics_calculation():
    """Verify evaluation report computes accurate precision, recall, F1, and confusion matrix."""
    report = evaluate_classifier(use_heuristic=True)

    assert report.total_samples == 120
    assert report.accuracy_pct >= 90.0
    assert report.fr_precision >= 0.85
    assert report.fr_recall >= 0.85
    assert report.fr_f1 >= 0.85
    assert report.nfr_precision >= 0.85
    assert report.nfr_recall >= 0.85
    assert report.nfr_f1 >= 0.85

    cm = report.confusion_matrix
    assert "true_positives_fr" in cm
    assert "false_positives_fr" in cm
    assert "true_positives_nfr" in cm
    assert "false_positives_nfr" in cm
    assert cm["true_positives_fr"] + cm["false_positives_fr"] + cm["true_positives_nfr"] + cm["false_positives_nfr"] == 120

    # Verify domain breakdown covers all 10 domains
    assert len(report.domain_breakdown) == 10
    for domain, stats in report.domain_breakdown.items():
        assert stats["total_samples"] >= 8
        assert stats["accuracy_pct"] >= 75.0


def test_benchmark_api_get_dataset():
    """Test GET /api/v1/requirements/benchmark endpoint."""
    response = client.get("/api/v1/requirements/benchmark?limit=10")
    assert response.status_code == 200
    data = response.json()

    assert data["total_requirements"] == 120
    assert data["fr_count"] == 60
    assert data["nfr_count"] == 60
    assert len(data["domains"]) == 10
    assert len(data["preview_items"]) == 10
    assert data["preview_items"][0]["id"] == "BENCH-001"


def test_benchmark_api_evaluate_endpoint():
    """Test POST /api/v1/requirements/benchmark/evaluate endpoint."""
    response = client.post("/api/v1/requirements/benchmark/evaluate?use_heuristic=true")
    assert response.status_code == 200
    data = response.json()

    assert data["total_samples"] == 120
    assert data["accuracy_pct"] >= 90.0
    assert "confusion_matrix" in data
    assert "domain_breakdown" in data


def test_requirements_classify_endpoint_single():
    """Test POST /api/v1/requirements/classify with single requirement."""
    payload = {"requirement": "The system shall encrypt all credit card numbers using AES-256."}
    response = client.post("/api/v1/requirements/classify", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["predicted_label"] == "NFR"


def test_requirements_classify_endpoint_batch():
    """Test POST /api/v1/requirements/classify with batch requirements."""
    payload = {
        "requirements": [
            "The system shall allow users to download invoices.",
            "The system shall maintain 99.99% operational uptime."
        ]
    }
    response = client.post("/api/v1/requirements/classify", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert len(data["results"]) == 2
    assert data["results"][0]["predicted_label"] == "FR"
    assert data["results"][1]["predicted_label"] == "NFR"
