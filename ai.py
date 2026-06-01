import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load .env using absolute path so it always works on Windows
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# Connect to Groq using the key from your .env file
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check that your .env file has the key.")

client = Groq(api_key=api_key)


def get_ai_response(customer_question, product_result):
    """
    Takes the customer's question and the database result,
    then returns a natural AI-generated reply.
    """

    # Build a description from whatever the database returned
    if product_result:
        product_info = (
            f"Product Name : {product_result[1]}\n"
            f"Stock        : {product_result[2]} units available\n"
            f"Price        : ${product_result[3]:.2f}"
        )
    else:
        product_info = "This product was not found in our inventory."

    # System prompt tells the AI how to behave
    system_prompt = """You are a friendly and helpful sales assistant for an online store.
Your job is to answer customer questions about product availability and pricing.
Always base your answer ONLY on the product information you are given.
Keep your reply short (2-3 sentences), polite, and professional."""

    # User message combines the question + real product data from DB
    user_message = (
        f"Customer question: \"{customer_question}\"\n\n"
        f"Product information from our database:\n{product_info}\n\n"
        f"Please answer the customer based on this information."
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # Free, fast Llama 3 model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Sorry, I'm having trouble answering right now. Please try again later. (Error: {e})"
