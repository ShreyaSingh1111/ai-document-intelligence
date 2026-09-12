from typing import Any, Dict, List, Optional


TOLERANCE = 0.01


def _number(value: Any) -> Optional[float]:
    """Convert a value to float safely."""
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _check(
    name: str,
    formula: str,
    operands: Dict[str, Any],
    calculated_value: Optional[float],
    reported_value: Optional[float],
) -> Dict[str, Any]:
    """
    Create a consistent validation result.
    """

    if calculated_value is None or reported_value is None:
        return {
            "name": name,
            "formula": formula,
            "operands": operands,
            "calculated_value": calculated_value,
            "reported_value": reported_value,
            "variance": None,
            "status": "SKIPPED",
            "reason": "Required values are missing or unreadable.",
        }

    variance = round(calculated_value - reported_value, 2)

    status = "PASS" if abs(variance) <= TOLERANCE else "FAIL"

    return {
        "name": name,
        "formula": formula,
        "operands": operands,
        "calculated_value": round(calculated_value, 2),
        "reported_value": round(reported_value, 2),
        "variance": variance,
        "status": status,
    }


def validate_invoice(data: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    issues: List[str] = []

    subtotal = _number(data.get("subtotal"))
    tax = _number(data.get("tax_amount"))
    discount = _number(data.get("discount"))
    total = _number(data.get("total_amount"))

    if discount is None:
        discount = 0.0

    # subtotal + tax - discount = total
    if subtotal is not None and tax is not None and total is not None:
        calculated_total = subtotal + tax - discount

        result = _check(
            name="invoice_total_check",
            formula="subtotal + tax_amount - discount",
            operands={
                "subtotal": subtotal,
                "tax_amount": tax,
                "discount": discount,
            },
            calculated_value=calculated_total,
            reported_value=total,
        )

        checks.append(result)

        if result["status"] == "FAIL":
            issues.append("Invoice total does not reconcile with subtotal, tax and discount.")

    # Validate line items when available
    line_items = data.get("line_items", [])

    if isinstance(line_items, list) and line_items:

        calculated_subtotal = 0.0
        valid_line_items = False

        for index, item in enumerate(line_items, start=1):
            if not isinstance(item, dict):
                continue

            quantity = _number(item.get("quantity"))
            unit_price = _number(item.get("unit_price"))
            amount = _number(item.get("amount"))

            if quantity is None or unit_price is None:
                continue

            valid_line_items = True
            expected_amount = quantity * unit_price

            line_check = _check(
                name=f"line_item_{index}_check",
                formula="quantity × unit_price = amount",
                operands={
                    "quantity": quantity,
                    "unit_price": unit_price,
                },
                calculated_value=expected_amount,
                reported_value=amount,
            )

            checks.append(line_check)

            if line_check["status"] == "FAIL":
                issues.append(
                    f"Line item {index} quantity × unit price does not match amount."
                )

            calculated_subtotal += expected_amount

        if valid_line_items and subtotal is not None:
            subtotal_check = _check(
                name="line_items_subtotal_check",
                formula="sum(quantity × unit_price) = subtotal",
                operands={
                    "calculated_line_items_total": round(calculated_subtotal, 2)
                },
                calculated_value=calculated_subtotal,
                reported_value=subtotal,
            )

            checks.append(subtotal_check)

            if subtotal_check["status"] == "FAIL":
                issues.append(
                    "Sum of invoice line items does not reconcile with subtotal."
                )

    failed_checks = [c for c in checks if c["status"] == "FAIL"]

    if failed_checks:
        overall_status = "FAIL"
    elif checks:
        overall_status = "PASS"
    else:
        overall_status = "SKIPPED"

    return {
        "checks": checks,
        "overall_status": overall_status,
        "issues": issues,
    }


def validate_balance_sheet(data: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    issues: List[str] = []

    assets = _number(data.get("total_assets"))
    liabilities = _number(data.get("total_liabilities"))
    equity = _number(data.get("total_equity"))

    if assets is not None and liabilities is not None and equity is not None:

        calculated_assets = liabilities + equity

        result = _check(
            name="balance_sheet_check",
            formula="total_liabilities + total_equity = total_assets",
            operands={
                "total_liabilities": liabilities,
                "total_equity": equity,
            },
            calculated_value=calculated_assets,
            reported_value=assets,
        )

        checks.append(result)

        if result["status"] == "FAIL":
            issues.append(
                "Total liabilities plus equity does not reconcile with total assets."
            )

    status = "FAIL" if any(c["status"] == "FAIL" for c in checks) else (
        "PASS" if checks else "SKIPPED"
    )

    return {
        "checks": checks,
        "overall_status": status,
        "issues": issues,
    }


def validate_profit_loss(data: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    issues: List[str] = []

    revenue = _number(data.get("revenue"))
    cogs = _number(data.get("cost_of_sales"))
    gross_profit = _number(data.get("gross_profit"))

    if revenue is not None and cogs is not None and gross_profit is not None:

        result = _check(
            name="gross_profit_check",
            formula="revenue - cost_of_sales = gross_profit",
            operands={
                "revenue": revenue,
                "cost_of_sales": cogs,
            },
            calculated_value=revenue - cogs,
            reported_value=gross_profit,
        )

        checks.append(result)

        if result["status"] == "FAIL":
            issues.append(
                "Revenue minus cost of sales does not reconcile with gross profit."
            )

    operating_expenses = _number(data.get("operating_expenses"))
    operating_profit = _number(data.get("operating_profit"))

    if (
        gross_profit is not None
        and operating_expenses is not None
        and operating_profit is not None
    ):
        result = _check(
            name="operating_profit_check",
            formula="gross_profit - operating_expenses = operating_profit",
            operands={
                "gross_profit": gross_profit,
                "operating_expenses": operating_expenses,
            },
            calculated_value=gross_profit - operating_expenses,
            reported_value=operating_profit,
        )

        checks.append(result)

        if result["status"] == "FAIL":
            issues.append(
                "Gross profit minus operating expenses does not reconcile with operating profit."
            )

    status = "FAIL" if any(c["status"] == "FAIL" for c in checks) else (
        "PASS" if checks else "SKIPPED"
    )

    return {
        "checks": checks,
        "overall_status": status,
        "issues": issues,
    }


def validate_cash_flow(data: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    issues: List[str] = []

    operating = _number(data.get("operating_cash_flow"))
    investing = _number(data.get("investing_cash_flow"))
    financing = _number(data.get("financing_cash_flow"))
    net_change = _number(data.get("net_change_in_cash"))

    if (
        operating is not None
        and investing is not None
        and financing is not None
        and net_change is not None
    ):
        calculated_change = operating + investing + financing

        result = _check(
            name="cash_flow_change_check",
            formula=(
                "operating_cash_flow + investing_cash_flow "
                "+ financing_cash_flow = net_change_in_cash"
            ),
            operands={
                "operating_cash_flow": operating,
                "investing_cash_flow": investing,
                "financing_cash_flow": financing,
            },
            calculated_value=calculated_change,
            reported_value=net_change,
        )

        checks.append(result)

        if result["status"] == "FAIL":
            issues.append(
                "Cash flow components do not reconcile with net change in cash."
            )

    opening_cash = _number(data.get("opening_cash"))
    closing_cash = _number(data.get("closing_cash"))

    if opening_cash is not None and net_change is not None and closing_cash is not None:

        result = _check(
            name="closing_cash_check",
            formula="opening_cash + net_change_in_cash = closing_cash",
            operands={
                "opening_cash": opening_cash,
                "net_change_in_cash": net_change,
            },
            calculated_value=opening_cash + net_change,
            reported_value=closing_cash,
        )

        checks.append(result)

        if result["status"] == "FAIL":
            issues.append(
                "Opening cash plus net change does not reconcile with closing cash."
            )

    status = "FAIL" if any(c["status"] == "FAIL" for c in checks) else (
        "PASS" if checks else "SKIPPED"
    )

    return {
        "checks": checks,
        "overall_status": status,
        "issues": issues,
    }


def validate_financial_data(
    document_type: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:

    document_type = document_type.lower().strip()

    if document_type == "invoice":
        return validate_invoice(data)

    if document_type in {"balance_sheet", "balance sheet"}:
        return validate_balance_sheet(data)

    if document_type in {"profit_loss", "profit and loss", "p&l"}:
        return validate_profit_loss(data)

    if document_type in {"cash_flow", "cash flow", "cash flow statement"}:
        return validate_cash_flow(data)

    return {
        "checks": [],
        "overall_status": "SKIPPED",
        "issues": [
            f"Financial validation is not implemented for document type: {document_type}"
        ],
    }