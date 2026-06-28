"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os
import re

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()

# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    listings = load_listings()

    # Step 1: Filter by price and size
    filtered = []
    for item in listings:
        if max_price is not None and item["price"] > max_price:
            continue
        if size is not None:
            size_parts = size.lower().split()
            if not any(part in item["size"].lower() for part in size_parts):
               continue
        filtered.append(item)

    # Step 2: Score by keyword overlap with description
    STOPWORDS = {
        "a", "an", "the", "for", "and", "or", "with", "in", "of", "that", "is",
        "vintage", "great", "perfect", "classic", "good", "style", "wear"
    }
    keywords = set(re.findall(r'\b\w+\b', description.lower())) - STOPWORDS

    def score(item: dict) -> int:
        title_words    = set(re.findall(r'\b\w+\b', item["title"].lower()))
        tag_words      = set(re.findall(r'\b\w+\b', " ".join(item["style_tags"]).lower()))
        category_words = set(re.findall(r'\b\w+\b', item["category"].lower()))
        low_text       = " ".join([
            item["description"],
            " ".join(item["colors"]),
            item["brand"] or "",
        ]).lower()
        low_words = set(re.findall(r'\b\w+\b', low_text))

        return (
            sum(4 for kw in keywords if kw in title_words)    +
            sum(3 for kw in keywords if kw in category_words) +
            sum(2 for kw in keywords if kw in tag_words)      +
            sum(1 for kw in keywords if kw in low_words)
        )

    # Step 3: Drop zero-score items, sort by score descending, return top 3
    scored = [(item, score(item)) for item in filtered]
    scored = [(item, s) for item, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [item for item, _ in scored[:3]]
# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    client = _get_groq_client()

    # Empty wardrobe — return general styling advice
    if not wardrobe.get("items"):
        prompt = f"""You are a stylish and knowledgeable personal stylist.

A user is considering buying this thrifted item but hasn't set up their wardrobe yet:

Name: {new_item['title']}
Category: {new_item['category']}
Colors: {', '.join(new_item['colors'])}
Style tags: {', '.join(new_item['style_tags'])}
Description: {new_item['description']}

Give them general styling advice for this piece:
- What kinds of items pair well with it
- What aesthetic or vibe it suits
- Specific styling tips (tucking, layering, footwear, accessories)
- Who this piece would work best for

Be specific and helpful even without knowing their wardrobe."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content

    # Non-empty wardrobe — suggest specific outfit combinations
    wardrobe_lines = []
    for item in wardrobe["items"]:
        line = (
            f"- {item['name']} (category: {item['category']}, "
            f"colors: {', '.join(item['colors'])}, "
            f"style: {', '.join(item['style_tags'])})"
        )
        if item.get("notes"):
            line += f" — notes: {item['notes']}"
        wardrobe_lines.append(line)
    wardrobe_text = "\n".join(wardrobe_lines)

    new_item_text = (
        f"Name: {new_item['title']}\n"
        f"Category: {new_item['category']}\n"
        f"Colors: {', '.join(new_item['colors'])}\n"
        f"Style tags: {', '.join(new_item['style_tags'])}\n"
        f"Description: {new_item['description']}"
    )

    prompt = f"""You are a stylish and knowledgeable personal stylist helping someone build an outfit around a new thrifted piece.

Here is the new thrifted item the user is considering buying:
{new_item_text}

Here is what the user currently has in their wardrobe:
{wardrobe_text}

Suggest 1-2 complete outfits using the new thrifted item and specific pieces from the wardrobe above.
For each outfit:
- List exactly which wardrobe pieces to pair with the new item by name
- Explain how to style the outfit (tucking, layering, footwear, accessories, etc.)
- Describe the overall vibe or aesthetic the outfit achieves
- Give practical tips on what makes the combination work

Only suggest outfits using pieces explicitly listed in the wardrobe above.
If nothing in the wardrobe pairs well with the new item, say so clearly and explain why."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # Guard against empty or whitespace-only outfit string
    if not outfit or not outfit.strip():
        return "Error: outfit information is missing or incomplete. Unable to generate fit card."

    client = _get_groq_client()

    new_item_text = (
        f"Item name: {new_item['title']}\n"
        f"Price: ${new_item['price']}\n"
        f"Platform: {new_item['platform']}\n"
        f"Colors: {', '.join(new_item['colors'])}\n"
        f"Style tags: {', '.join(new_item['style_tags'])}"
    )

    prompt = f"""You are writing a casual, authentic OOTD (outfit of the day) caption for Instagram or TikTok.

Here is the outfit:
{outfit}

Here is the thrifted item that anchors the outfit:
{new_item_text}

Write a 2-4 sentence caption that:
- Feels like a real person wrote it, not a product description
- Mentions the item name, price, and platform naturally and only once each
- Captures the vibe of the outfit in specific, vivid terms
- Is casual, fun, and authentic
- Uses a different structure, opening, and tone every time — never start with "I" or "Just"
- Vary between first person, second person, or talking directly about the outfit
- Mix up the energy — sometimes hype, sometimes chill, sometimes storytelling

Write only the caption — no titles, no labels, no extra commentary."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.2,
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    results = search_listings("jeans", size=None, max_price=50.0)
    selected_item = results[0]
    wardrobe = get_example_wardrobe()
    outfit = suggest_outfit(selected_item, wardrobe)

    # Test Tool 3 success case
    fit_card = create_fit_card(outfit, selected_item)
    print("Fit Card:")
    print(fit_card)

    # Test Tool 3 error case
    error_result = create_fit_card("", selected_item)
    print(f"\nEmpty outfit returns error string: {'Error:' in error_result}")

    # Test variation — run it 3 times on the same input
    print("\nVariation test:")
    for i in range(3):
        card = create_fit_card(outfit, selected_item)
        print(f"\nRun {i+1}:")
        print(card)
