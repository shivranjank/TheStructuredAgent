import os
import pydantic
from pydantic import BaseModel
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

class TaxClause(BaseModel):
    clause_number: int
    clause_title: str
    clause_description: str
    clause_impact: str
    clause_recommendation: str
    clause_status: str
    clause_date: str
    clause_author: str

print(f"{'='*50}")
print("Welcome to the Tax Clause Helper. Please enter the tax Clause details you want to analyze.")
print(f"{'='*50}")

user_input = input("What are you looking for today from Indian Tax Laws?")

parsed_message = client.messages.parse(
    model="claude-sonnet-4-5",
    temperature=1,
    system="You are a Tax Clause Helper. Your role is to understand the tax Clause details asked by the user. Analyze the tax Clause details and provide the user with the most relevant information, also provide the summary of the tax Clause details.",

    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_input
                }
            ]
        }
    ],
    max_tokens=1024,
    output_format = TaxClause,
    thinking={
        "type": "disabled"
    }
)

output = parsed_message.parsed_output
for field, value in output.model_dump().items():
    print(f"{field}: {value}")