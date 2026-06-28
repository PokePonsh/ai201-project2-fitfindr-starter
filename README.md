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
- Output: outputs dict of most relevent items found by the search

**Step 2 — Tool called:**
- Tool: suggest_outfit
- Input: new_item= session["search_results"](dict output from search_listings), wardrobe= session["wardrobe"]
- Why this tool: This tool is used next, as it takes the thrifted item found, and creates the best possible outfits using the thrifted items, and the items in the wardrobe.
- Output: This outputs a string containing the information of the outfit that it created.

**Step 3 — Tool called:**
- Tool: create_fit_card
- Input: outfit= session["outfit_suggestion"](the string created from suggest_outfit) new_item= session["search_results"](dict output from search_listings)
- Why this tool: This tool is called here in order to generate the needed fit card, as only now do we have all the information needed to create the fit card for the outfit.
- Output: This outputs a string containing the fit card, which includes the blurb about the outfit, and information about the thrifted way in a stylized way.

**Final output to user:**
The final output to the user is in three parts, part one: the information about the thrifted piece in an understandable way for a human reader. Part two: the outfit suggestion passed through an llm to inform the user of the outfits they can make with the thrifted piece, and how to style them. Part three: the fit card, which is readable for humans and stylized, ready to share with others as is.
---

## Error Handling and Fail Points

<!-- For each tool, describe the specific failure mode and what your agent does in response.
     This maps to the error handling section of the rubric (F5-C1). -->

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | No item fits the user's specifications| Returns an error message informing them that no such items exist, and suggests to them on how to improve their search to find a thriftable clothing item|
| `suggest_outfit` | The wardrobe is empty| Returns the piece of clothing, and general fashion advice about the item, rather than creating outfits.|
| `create_fit_card` | The wardrobe is empty| Returns error that says that the wardrobe is empty, so no fit card could be made, since no new outfit was generated.|

---

## Spec Reflection

<!-- Answer both questions with at least 2–3 sentences each. -->

**One way planning.md helped during implementation:**
Planning.md helped me during implementation as I knew exactly what to expect as the output from each tool. This allowed me to build and test them individually to ensure they worked before moving on to the next tool. This testing and knowing how to connect them using the agent, as I planned in planning.md then helped me to much more easily combine the tools with the agent rather than trying to edit my functions to make them work with the agent retroactively.
**One divergence from your spec, and why:**
One divergence from my specs was the exact way that my flow chart worked. This was done as what I initially planned for my agent to do did not actually end up working properly, as there were instances where a problem needed a solution that my initial structure would not allow for, so I modified the exact way in which the agent worked, though the overall structure remained quite similar to my original.

---

## AI Usage

One instance in which I used AI was the creation of my create_outfit function. I provided claude, my planning for tool #2, and my flowchart. Initially it appeared to make the program exactly how I wanted it, after some simple debugging, but after testing further, I discovered that it had not included what to do if nothing was in the wardrobe correctly, so I revised the code it wrote in order to ensure that it did, in fact, behave in the way I wanted it to.

Another instance in which I used AI was during the testing phase of each of my tools before creating my agent. To do this, I provided it the necessary things to test, and told it to use pytest as suggested in the examples. While it did make a complete test for my tools, it had not implemented it correctly so that it gave an error when ran. I then fixed this issue to ensure that the testing could be done properly.

---

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
