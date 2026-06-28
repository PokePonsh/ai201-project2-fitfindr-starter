# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tool Inventory

Tool #1: search_listings
     Inputs: 
          1) description (str) - Short description of clothing item system is looking for.
          2) size (str|None) - Size of clothing item system is looking for. Is None when not searching by size.
          3) max_price (float|None) - The maximum price user is willing to pay for item. Is None when cost is not constrained.
     Output:
          list[dict] - List of the most relevent clothing items found in listings.json

Tool #2: suggest_outfit
     Inputs:
          1) new_item(dict) - The most relevent item found by search_listings (list[0]).
          2) wardrobe(dict) - List of items the user already owns.
     Output:
          Returns a string of 1-2 complete outfit suggestions using pieces from the user's wardrobe, and the new thrifted piece. -OR- Returns general fashion advice for the thrifted piece of clothing if the user has and empty wardrobe.

Tool #3: create_fit_card
     Inputs:
          1) outfit(str) - The outfit suggested by suggest_outfit
          2) new_item(dict) - The new item from search_listings.
     Outputs:
          Returns a string of a short "outfit of the day" type caption for the outfit from suggest_outfit. Also includes the information about the thrifted item, such as cost and where it was bought. -OR- In case wardrobe is empty, returns error string informing that the fit card could not be created due to not having clothes in the wardrobe.

---

## Interaction Walkthrough

<!-- Walk through a complete interaction step by step: natural language query → each tool call (and why) → final fit card.
     Walk through this carefully — it's how graders follow your agent's reasoning without a live demo.
     Use a specific example — do not leave this as a template. -->

**User query: **
Find me a vintage graphic tee for less than  40 dollars, and make me an outfit with it.

**Step 1 — Tool called:**
- Tool: search_listings
- Input: description= "vintage graphic tee", size= "medium", max_price = 40.
- Why this tool: This tool gets called first so that a piece of clothing fitting the description the user looks for can be found in order to build their new outfit.
- Output:

**Step 2 — Tool called:**
- Tool:
- Input:
- Why this tool:
- Output:

**Step 3 — Tool called:**
- Tool:
- Input:
- Why this tool:
- Output:

**Final output to user:**

---

## Error Handling and Fail Points

<!-- For each tool, describe the specific failure mode and what your agent does in response.
     This maps to the error handling section of the rubric (F5-C1). -->

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | | |
| `suggest_outfit` | | |
| `create_fit_card` | | |

---

## Spec Reflection

<!-- Answer both questions with at least 2–3 sentences each. -->

**One way planning.md helped during implementation:**

**One divergence from your spec, and why:**

---

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
