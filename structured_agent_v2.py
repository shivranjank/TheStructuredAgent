import os
from pydantic import BaseModel, field_validator, ValidationError
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ---------------------------------------------------------------------------
# Pydantic model with explicit validation rules
# ---------------------------------------------------------------------------

class InvoiceData(BaseModel):
    invoice_number: str
    date: str
    vendor_gstin: str
    total_amount: float

    @field_validator("vendor_gstin")
    @classmethod
    def gstin_must_be_15_chars(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 15:
            raise ValueError(
                f"GSTIN must be exactly 15 characters, got {len(v)} ('{v}')"
            )
        return v

    @field_validator("total_amount")
    @classmethod
    def total_amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(
                f"total_amount must be a positive numeric value, got {v}"
            )
        return v


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RETRIES = 3

SYSTEM_PROMPT = """You are an expert Invoice Data Extractor.

Extract the following fields from the invoice text and return them as a JSON object:
- invoice_number : The invoice or bill number (string)
- date           : The invoice date as-is (string)
- vendor_gstin   : The vendor's GST Identification Number — MUST be EXACTLY 15 characters
- total_amount   : The final payable amount as a plain number (no ₹/$, commas, or text)

Critical constraints:
1. vendor_gstin MUST be exactly 15 characters (e.g., 29ABCDE1234F1Z5).
2. total_amount MUST be a numeric value only (e.g., 109150.00, not "₹1,09,150").

Return ONLY the JSON object with these four fields — no markdown, no explanation."""

# ---------------------------------------------------------------------------
# Extractor with retry loop
# ---------------------------------------------------------------------------

def extract_invoice_data(invoice_text: str) -> InvoiceData:
    """
    Extract key invoice fields from unstructured text.

    Uses client.messages.parse() with a Pydantic BaseModel (InvoiceData) as
    the sole schema definition — no raw JSON schema is written by hand.

    Retry loop:
      - parse() derives the JSON schema from InvoiceData and calls the API.
      - The response is validated by InvoiceData's field_validators.
      - On ValidationError the error is embedded into the next user message
        and the call is retried (up to MAX_RETRIES times).
      - Raises ValueError after MAX_RETRIES failed attempts.
    """
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n{'=' * 50}")
        print(f"Attempt {attempt} of {MAX_RETRIES}")
        print("=" * 50)

        # On retry, embed the previous validation error into the user message
        # so the model knows exactly what to fix.
        if last_error is None:
            user_content = f"Extract invoice data from the following text:\n\n{invoice_text}"
        else:
            user_content = (
                f"Extract invoice data from the following text:\n\n{invoice_text}\n\n"
                f"Your previous attempt failed validation with these errors:\n{last_error}\n\n"
                "Please correct the issues and try again."
            )

        try:
            response = client.messages.parse(
                model="claude-sonnet-4-5",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_content}],
                output_format=InvoiceData,
            )
            invoice = response.parsed_output
            print(f"Model output:\n{response.content[0].text if response.content else ''}")
            print("\nValidation passed!")
            return invoice

        except ValidationError as exc:
            last_error = exc
            print(f"\nValidation failed: {exc}")

            if attempt == MAX_RETRIES:
                print(f"\nAll {MAX_RETRIES} attempts exhausted.")

    raise ValueError(
        f"Failed to extract valid invoice data after {MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Sample invoice (used when running this file directly)
# ---------------------------------------------------------------------------

SAMPLE_INVOICE = """
TAX INVOICE

Invoice No.: INV-2024-00892
Invoice Date: 15-Mar-2024

Vendor Details:
  Company : Apex Tech Solutions Pvt. Ltd.
  GSTIN   : 29ABCDE1234F1Z5
  Address : 14, MG Road, Bengaluru - 560001

Bill To:
  Company : GlobalCore Industries
  GSTIN   : 27XYZPQ5678G2A3

Item Description              Qty     Rate        Amount
---------------------------------------------------------
Laptop (Dell Inspiron 15)      2    45,000.00    90,000.00
Wireless Mouse                 5       500.00     2,500.00
---------------------------------------------------------
Sub Total                                        92,500.00
CGST @ 9%                                         8,325.00
SGST @ 9%                                         8,325.00
---------------------------------------------------------
Total Amount Payable                            109,150.00

Amount in Words: One Lakh Nine Thousand One Hundred and Fifty Rupees Only
"""

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Invoice Data Extractor")
    print("=" * 50)

    try:
        invoice = extract_invoice_data(SAMPLE_INVOICE)

        print("\n" + "=" * 50)
        print("EXTRACTED INVOICE DATA")
        print("=" * 50)
        for field, value in invoice.model_dump().items():
            print(f"{field}: {value}")

    except ValueError as e:
        print(f"\nFailed: {e}")
