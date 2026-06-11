# The Structured Agent

Demonstrates **structured output parsing** using the Anthropic SDK and Pydantic — extracting validated, typed data from unstructured text via `client.messages.parse()`.

---

## What's Inside

| Script | Purpose |
|---|---|
| `structured_agent.py` | Tax Clause Helper — extracts Indian Tax Law clause details into a typed `TaxClause` model |
| `structured_agent_v2.py` | Invoice Data Extractor — parses unstructured invoice text into a validated `InvoiceData` model with a retry loop |

---

## Core Pattern

```python
from pydantic import BaseModel
import anthropic

class MyOutput(BaseModel):
    field_one: str
    field_two: float

client = anthropic.Anthropic()

response = client.messages.parse(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": "your input here"}],
    output_format=MyOutput,
    max_tokens=1024,
)

result = response.parsed_output  # typed, validated MyOutput instance
```

---

## v1 — Tax Clause Helper

Accepts a natural language query about Indian Tax Laws and returns structured clause information.

**Output schema:**
```
clause_number, clause_title, clause_description,
clause_impact, clause_recommendation, clause_status,
clause_date, clause_author
```

**Run:**
```bash
uv run python structured_agent.py
```

---

## v2 — Invoice Data Extractor

Extracts key fields from unstructured invoice text with custom Pydantic validators and an automatic retry loop.

**Output schema:**
```
invoice_number, date, vendor_gstin, total_amount
```

**Validators:**
- `vendor_gstin` — must be exactly 15 characters (Indian GSTIN format)
- `total_amount` — must be a positive numeric value

**Retry loop:** On validation failure, the error is embedded into the next API call so the model self-corrects — up to 3 attempts before raising a `ValueError`.

**Run:**
```bash
uv run python structured_agent_v2.py
```

---

## Setup

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

Create a `.env` file at the project root:
```
ANTHROPIC_API_KEY=your_api_key_here
```

---

## Stack

- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) — `client.messages.parse()` for structured output
- [Pydantic v2](https://docs.pydantic.dev/) — schema definition and field validation
- [uv](https://docs.astral.sh/uv/) — environment and dependency management
