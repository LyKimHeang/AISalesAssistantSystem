import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

client = Groq(api_key=api_key)


def get_ai_response(customer_question, all_products, conversation_history=None):
    """
    Passes the full product catalog + conversation history to the AI
    so it can recommend, compare, and remember context within a session.
    """

    # ── Build catalog context ──────────────────────────────────────────────────
    # p: id[0] name[1] category[2] stock[3] price[4] image_url[5] description[6]
    if all_products:
        lines = []
        for p in all_products:
            stock_label = f"{p[3]} in stock" if p[3] > 0 else "OUT OF STOCK"
            line = (f"• {p[1]}  |  Category: {p[2]}  |  "
                    f"Price: ${p[4]:.2f}  |  {stock_label}")
            if len(p) > 6 and p[6]:
                line += f"\n  Info: {p[6]}"
            lines.append(line)
        catalog = "\n".join(lines)
    else:
        catalog = "No products available at this time."

    system_prompt = f"""You are a friendly AI sales assistant for a tech accessories store.
Help customers find products, make recommendations, compare items, and answer questions about the shop.

Complete product catalog:
{catalog}

Guidelines:
- Only recommend products that exist in the catalog above
- If a product is out of stock, say so and suggest an in-stock alternative if one exists
- For open questions like "what's good for gaming?" suggest relevant products from the catalog
- Keep replies friendly and concise (2-4 sentences max)
- If asked something unrelated to shopping or tech, politely redirect back to the shop
- Use conversation history to understand follow-up questions (e.g. "how much is it?" refers to the last product discussed)"""

    # ── Build messages: system + history (last 10) + current question ──────────
    messages = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        for msg in conversation_history[-10:]:
            if msg.get('role') in ('user', 'assistant') and msg.get('content'):
                messages.append({"role": msg['role'], "content": str(msg['content'])})

    messages.append({"role": "user", "content": customer_question})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Sorry, I'm having trouble right now. Please try again later. (Error: {e})"