"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

from tools import search_listings, suggest_outfit, create_fit_card


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    import re

    # Step 1: Initialize session
    session = _new_session(query, wardrobe)

    # Step 2: Parse the query for description, size, and max_price
    # Extract max_price — look for patterns like "under $30", "less than $50", "$25"
    price_match = re.search(r'(?:under|less than|max|below)?\s*\$?\s*(\d+(?:\.\d+)?)', query, re.IGNORECASE)
    max_price = float(price_match.group(1)) if price_match else None

    # Extract size — requires "size" keyword or standalone size token
    size_match = re.search(r'\bsize\s+([A-Za-z0-9\/]+(?:\s*L\d{2})?)\b', query, re.IGNORECASE)
    size = size_match.group(1) if size_match else None

    # Extract description — remove price and size mentions to get clean keywords
    description = query
    if price_match:
        description = description.replace(price_match.group(0), "")
    if size_match:
        description = description.replace(size_match.group(0), "")
    description = re.sub(
    r"\b(?:i'm|i|size|under|less than|max|below|looking|for|a|an|the|mostly|wear|what's|out|there|how|would|style|it|and|what|s)\b",
    '', description, flags=re.IGNORECASE
)
    description = re.sub(r'\s+', ' ', description).strip()

    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    # Step 3: Call search_listings()
    session["search_results"] = search_listings(description, size, max_price)

    if not session["search_results"]:
        session["error"] = (
            f"No listings found matching '{description}'"
            + (f" in size {size}" if size else "")
            + (f" under ${max_price}" if max_price else "")
            + ". Try broadening your search — use a less specific description, "
            "a larger size range, or increase your budget."
        )
        return session

    # Step 4: Select top result
    session["selected_item"] = session["search_results"][0]

    # Step 5: Call suggest_outfit()
    session["outfit_suggestion"] = suggest_outfit(session["selected_item"], wardrobe)

    if not session["outfit_suggestion"]:
        session["error"] = (
            "Your wardrobe appears to be empty. Please add items to your wardrobe "
            "so FitFindr can suggest outfits with your new thrifted piece."
        )
        return session

    # Step 6: Call create_fit_card()
    session["fit_card"] = create_fit_card(session["outfit_suggestion"], session["selected_item"])

    if session["fit_card"].startswith("Error:"):
        session["error"] = session["fit_card"]
        session["fit_card"] = None
        return session

    # Step 7: Return session
    return session

# ── CLI test ──────────────────────────────────────────────────────────────────

# if __name__ == "__main__":
#     from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

#     print("=== Happy path: graphic tee ===\n")
#     session = run_agent(
#         query="looking for a vintage graphic tee under $30",
#         wardrobe=get_example_wardrobe(),
#     )
#     if session["error"]:
#         print(f"Error: {session['error']}")
#     else:
#         print(f"Found: {session['selected_item']['title']}")
#         print(f"\nOutfit: {session['outfit_suggestion']}")
#         print(f"\nFit card: {session['fit_card']}")

#     print("\n\n=== No-results path ===\n")
#     session2 = run_agent(
#         query="designer ballgown size XXS under $5",
#         wardrobe=get_example_wardrobe(),
#     )
#     print(f"Error message: {session2['error']}")

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe
    import json

    session = run_agent(
        query="I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?",
        wardrobe=get_example_wardrobe(),
    )

    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        # Verify selected_item is the same dict passed into suggest_outfit
        print("=== selected_item ===")
        print(json.dumps(session["selected_item"], indent=2))

        # Verify outfit_suggestion is what went into create_fit_card
        print("\n=== outfit_suggestion ===")
        print(session["outfit_suggestion"])

        print("\n=== fit_card ===")
        print(session["fit_card"])

        # Verify state flow — confirm no hardcoded values
        print("\n=== State flow verification ===")
        print(f"selected_item title:       {session['selected_item']['title']}")
        print(f"parsed description:        {session['parsed']['description']}")
        print(f"parsed size:               {session['parsed']['size']}")
        print(f"parsed max_price:          {session['parsed']['max_price']}")
        print(f"outfit_suggestion is str:  {isinstance(session['outfit_suggestion'], str)}")
        print(f"outfit_suggestion is set:  {session['outfit_suggestion'] is not None}")
        print(f"fit_card is str:           {isinstance(session['fit_card'], str)}")
        print(f"fit_card is set:           {session['fit_card'] is not None}")
        print(f"error is None:             {session['error'] is None}")