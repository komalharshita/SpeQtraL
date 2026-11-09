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
return ONLY a valid, read-only SQLite SELECT query with no explanation, no markdown, no code fences.
Use the listed relationships to join tables when needed. Try to answer using the available tables,
columns, relationships, and reasonable aggregations before giving up. Return the fallback only when
the requested information truly cannot be derived from the available data:
SELECT 'I cannot answer this question with the available data' AS message;

HINTS:
- Date columns are stored as text in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format. Use JULIANDAY()
  for date comparisons or elapsed time, and strftime() to group or extract date parts.
- An order is delivered late when order_delivered_customer_date > order_estimated_delivery_date.
  Only delivered orders have delivery dates; check for NULL dates when comparing.
- Join products to category_translation on product_category_name for English category names.
- Revenue is SUM(price) from order_items; do not include freight_value unless asked.
- Add LIMIT 20 unless the question asks for all rows.

EXAMPLES:
Question: Which state has the most orders?
SQL: SELECT c.customer_state, COUNT(o.order_id) AS order_count
     FROM orders o JOIN customers c ON o.customer_id = c.customer_id
     GROUP BY c.customer_state ORDER BY order_count DESC LIMIT 1;

Question: Which 5 product categories generated the most revenue?
SQL: SELECT COALESCE(ct.product_category_name_english, p.product_category_name) AS category,
            SUM(oi.price) AS revenue
     FROM order_items oi JOIN products p ON oi.product_id = p.product_id
     LEFT JOIN category_translation ct
       ON p.product_category_name = ct.product_category_name
     GROUP BY category ORDER BY revenue DESC LIMIT 5;

Question: How many orders were delivered late?
SQL: SELECT COUNT(order_id) AS late_order_count FROM orders
     WHERE order_status = 'delivered'
       AND order_delivered_customer_date IS NOT NULL
       AND order_estimated_delivery_date IS NOT NULL
       AND JULIANDAY(order_delivered_customer_date) > JULIANDAY(order_estimated_delivery_date);

Question: What is the average review score by state?
SQL: SELECT c.customer_state, ROUND(AVG(r.review_score), 2) AS average_review_score
     FROM order_reviews r JOIN orders o ON r.order_id = o.order_id
     JOIN customers c ON o.customer_id = c.customer_id
     GROUP BY c.customer_state ORDER BY average_review_score DESC LIMIT 20;

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