import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.financial_validation_service import validate_invoice


def test_invoice_total_reconciles_pass():
    data = {
        "subtotal": 100.0,
        "tax_amount": 10.0,
        "discount": 0.0,
        "total_amount": 110.0,
    }
    result = validate_invoice(data)
    assert result["overall_status"] == "PASS"


def test_invoice_total_mismatch_fails():
    data = {
        "subtotal": 100.0,
        "tax_amount": 10.0,
        "discount": 0.0,
        "total_amount": 999.0,
    }
    result = validate_invoice(data)
    assert result["overall_status"] == "FAIL"
    assert len(result["issues"]) > 0


def test_missing_fields_are_skipped_not_invented():
    data = {"subtotal": None, "tax_amount": None, "total_amount": None}
    result = validate_invoice(data)
    assert result["overall_status"] == "SKIPPED"
