import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def extract_document_data(
    document_text: str,
    document_type: str,
) -> Dict[str, Any]:
    """
    Extract structured information from OCR/document text using Groq.
    """

    if not document_text.strip():
        return {
            "success": False,
            "error": "Document text is empty",
            "data": {}
        }

    prompt = f"""
You are a document intelligence extraction system.

Document type:
{document_type}

Extract structured information from the following document text.

Return ONLY valid JSON.
Do not add markdown.
Do not add explanations.

Use this structure:

{{
    "document_type": "{document_type}",
    "vendor_name": null,
    "invoice_number": null,
    "invoice_date": null,
    "due_date": null,
    "currency": null,
    "subtotal": null,
    "tax": null,
    "discount": null,
    "total_amount": null,
    "line_items": [],
    "customer_name": null,
    "customer_id": null,
    "payment_terms": null
}}

Rules:
- If a field is not available, use null.
- Amounts must be numbers, not strings.
- Do not invent information.
- Preserve dates as written when possible.
- line_items should contain:
  description, quantity, unit_price, amount

Document text:
----------------
{document_text}
----------------
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise document extraction engine."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        data = json.loads(content)

        return {
            "success": True,
            "data": data
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON returned by AI: {str(e)}",
            "data": {}
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {}
        }
