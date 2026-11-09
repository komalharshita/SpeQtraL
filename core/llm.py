import os
from groq import Groq
from dotenv import load_dotenv
import core.schema

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

MODEL = "openai/gpt-oss-20b"


def _require_client() -> Groq:
    if client is None:
        raise RuntimeError(
            "Missing GROQ_API_KEY. Create a .env file from .env.example and add your Groq API key."
        )
    return client


def generate_sql(user_question: str) -> str:
    schema = core.schema.get_schema_string()
    system_prompt = f"""You are a SQL expert. Given a SQLite database schema and a question, 
return ONLY a valid SQLite SQL query with no explanation, no markdown, no code fences.
If you cannot answer the question with the available schema, return: SELECT 'I cannot answer this question with the available data' AS message;

Database schema:
{schema}"""

    response = _require_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0,  # 0 = deterministic — important for SQL generation
    )
    return response.choices[0].message.content.strip()


def generate_insight(question: str, result_preview: str) -> str:
    response = _require_client().chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"Question: {question}\n\nData result (first few rows):\n{result_preview}\n\nWrite one sentence summarising the key business insight from this data. Be specific — include the actual number or finding."
        }],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()