import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_document_data(text: str, document_type: str) -> dict:
    prompt = f"""
You are a financial document extraction system.

Document type:
{document_type}

Extract ALL meaningful information visible in the document.

Rules:
1. Do not invent or infer values.
2. If a value is missing, use null.
3. Preserve reported numbers exactly where possible.
4. Extract tables and line items when present.
5. Include source text and page number as evidence whenever possible.
6. Return ONLY valid JSON.
7. Do not add explanations outside JSON.

Return this structure:

{{
    "fields": {{
        "field_name": {{
            "value": "extracted value or null",
            "evidence": {{
                "source_text": "supporting text",
                "page_number": 1
            }}
        }}
    }},
    "tables": [
        {{
            "table_name": "name",
            "rows": []
        }}
    ]
}}

Document text:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        return json.loads(content)

    except json.JSONDecodeError:
        return {
            "error": "AI returned invalid JSON",
            "raw_response": content
        }

    except Exception as e:
        return {
            "error": f"Extraction failed: {str(e)}"
        }