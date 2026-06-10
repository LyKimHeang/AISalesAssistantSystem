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


def get_ai_response(customer_question, product_result):

    # Column order: id[0] | name[1] | category[2] | stock[3] | price[4] | image_url[5] | description[6]
    if product_result:
        description = product_result[6] if len(product_result) > 6 and product_result[6] else None
        product_info = (
            f"Product Name : {product_result[1]}\n"
            f"Category     : {product_result[2]}\n"
            f"Stock        : {product_result[3]} units available\n"
            f"Price        : ${product_result[4]:.2f}\n"
        )
        if description:
            product_info += f"Description  : {description}"
    else:
        product_info = "This product was not found in our inventory."

    system_prompt = """You are a friendly and helpful sales assistant for a tech accessories store.
Your job is to answer customer questions about product availability and pricing.
Always base your answer ONLY on the product information you are given.
Keep your reply short (2-3 sentences), polite, and professional."""

    user_message = (
        f"Customer question: \"{customer_question}\"\n\n"
        f"Product information from our database:\n{product_info}\n\n"
        f"Please answer the customer based on this information."
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
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