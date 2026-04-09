# backend/ai_service.py
# Handles AI review generation using the Mistral AI API

import httpx
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------------------------------------------------------
# Mistral AI Configuration
# -------------------------------------------------------
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "your_mistral_api_key_here")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-small-latest"   # Fast and cost-efficient model


async def generate_review(
    customer_name: str,
    service: str,
    rating: int,
    existing_reviews: list[str]
) -> str:
    """
    Generate a unique, personalized Google review using Mistral AI.

    Args:
        customer_name:    Name of the customer
        service:          Service or test the customer took
        rating:           Star rating (4 or 5)
        existing_reviews: Last 10-20 reviews to avoid duplicates

    Returns:
        A 2-3 line AI-generated review as a string.
    """

    # -------------------------------------------------------
    # Build the prompt with context from existing reviews
    # -------------------------------------------------------
    existing_reviews_text = ""
    if existing_reviews:
        reviews_list = "\n".join(f"- {r}" for r in existing_reviews)
        existing_reviews_text = f"""
EXISTING REVIEWS (DO NOT REPEAT THESE):
{reviews_list}

Make sure your new review is completely different in wording, structure, and opening phrase from all the above.
""".strip()

    prompt = f"""You are helping a customer write a genuine Google review for Brain Checker, a professional brain health testing center.

CUSTOMER DETAILS:
- Name: {customer_name}
- Service/Test Taken: {service}
- Star Rating: {rating}/5

{existing_reviews_text}

INSTRUCTIONS:
1. Write a Google review in the customer's voice (first-person)
2. Keep it to 2-3 sentences only
3. Make it sound natural and human — NOT robotic or generic
4. Mention the specific service or test if possible
5. Express genuine satisfaction appropriate for a {rating}-star experience
6. Do NOT use clichés like "highly recommend" or "five stars" at the start
7. Do NOT include the star rating number in the text
8. Do NOT add quotation marks around the review
9. Return ONLY the review text, nothing else

Write the review now:"""

    # -------------------------------------------------------
    # Call Mistral AI API
    # -------------------------------------------------------
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MISTRAL_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 200,
        "temperature": 0.85,     # Higher temperature = more creative, less repetitive
        "top_p": 0.95,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            MISTRAL_API_URL,
            headers=headers,
            json=payload
        )

        # Check for API errors
        if response.status_code != 200:
            error_detail = response.text
            print(f"[AI] ❌ Mistral API error {response.status_code}: {error_detail}")
            raise Exception(f"Mistral API returned {response.status_code}: {error_detail}")

        data = response.json()

        # Extract the generated text from the response
        review_text = data["choices"][0]["message"]["content"].strip()

        # Clean up any stray quotation marks
        review_text = review_text.strip('"').strip("'").strip()

        print(f"[AI] ✅ Generated review for {customer_name}: {review_text[:60]}...")
        return review_text
