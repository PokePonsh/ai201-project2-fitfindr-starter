# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
This tool is used to find the piece of clothing the user is looking for. It intakes the information the user provided about what they are looking for. It finds the 3 most relevent pieces of clothing from the thrifiting list provided based on the user's request, and then returns the most relevent out of the clothes it found.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): This is used for general descriptions of the clothes the user is looking for. This include a description of the clothing piece needed whether it is vague such as "pants" or somewhat specific "jeans" to very specific pieces of clothing such as "sleeveless vintage tiedye crop-top".
- `size` (str): This is the field that is used for the size of clothing the user needs. It includes both shirt and outerwear sizes such as "M" or "medium" for clothing sizes, and "w40, l38" for pant sizes and beyond.
- `max_price` (float): This is the parameter that stores the most amount of money the user is willing to pay for the piece of clothing. No items that cost more than this value should be considered when searching for items for the user.

**What it returns:**
The return for this tool will be the Id number of the piece of thrifted clothing. Since this tool does not output anything to the user if something is found, then the only thing that need to actually be returned from the tool if it succeeds is the ID number of the thrifted piece, so that it can be passed to the next tools the agent will go through.

**What happens if it fails or returns nothing:**
If no listings match, the tool should inform the agent, which will then stop the remaining program from continuing. It will then output what went wrong to the user, and suggest a correction that can be made in the search for better results if possible. This can include increasing the budget they were looking within, looking for something slightly less specific.

---

### Tool 2: suggest_outfit

**What it does:**
This tool intakes the item ID for the previous item, and the contents of the user's wardrobe. Once it has this information, it created an stylish outfit for the user using the new piece of clothing, and what they have in their closet. Beyond creating the outfit itself, the tool should also explain how to style the outfit so that it looks the best, and not just suggest which pieces to wear in the outfit.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): This is the ID value(s) of the piece of clothing that the program suggests for the user. It should use the ID to find the outfit, the outfit's details, and use them during the creation of the outfit.
- `wardrobe` (dict): This is the list of all the clothing that the user has availible to them in their wardrobe. It should be used to build a stylish outfit with the new thrifted item.

**What it returns:**
This program should return a suggested outfit and styling for that outfit to the used using natural language.

**What happens if it fails or returns nothing:**
If no outfit can be made using the thrifted clothing and the items in the user's wardrobe, the user should be informed that nothing that they have will go well with the new piece of clothing, or that a whole outfit cannot be created from their wardrobe and the thrifted item. Additionally, if there is no item in the user's wardrobe, the program should inform the user that they have not updated their wardrobe and that it is currently empty. In both of these cases, the program should end and not continue to the next tool.

---

### Tool 3: create_fit_card

**What it does:**
This tool functions to create a short description of the outfit. It includes the new item thrifted, its price, and where it was gotten from. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): This is what is created in tool #2. It is the string of text that describes the user's new outfit, and how it should be styled.
- `new_item` (dict): This is the information gathered from tool #1 about which piece of clothing in the outfit was thrifted.

**What it returns:**
This should return a short piece of text with a short blurb (less than a sentence) about the outfit, and the some information about the thrifted item.

**What happens if it fails or returns nothing:**
The outfit data that the tool recieves should not be incomplete in any way as it should not be called if one of the previous tools didn't work, but if in some way an error like this does occur the program should end and the user should get the information that there was something wrong about the outfit information.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
Starting at the beginning, after calling search_listing with the provided constraints the agent should then check if the tool succesfully produced a thriftable item, or returned a blank. If the tool returned a blank rather than a thriftable item, the program should send an error message to the user that states that nothing could be found, and then end the program early. If however seach_listing did return a thriftable item, this item is then passed onto the suggest_outfit tool to create an outfit using the item. If suggest_outfit failed at generating an outfit, the user should be informed of this, and the reason why(for instance if their wardrobe is empty) should also be told to the user; the program should then end. If however an outfit was created by suggest_outfit, the outfit is stored for both returning to the user, and to be passed into create_fit_card. When the fit card is generated, the suggested item, suggested outfit, and the fit card should be returned to the user for their use.

---

## State Management

**How does information from one tool get passed to the next?**
It will be stored as variables that will be passed along to one another, mainly through the ID code for thrifting, and strings for the outfit.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Stop program, send error to user informing them that there was no clothing item that fits their description |
| suggest_outfit | Wardrobe is empty | Stop program, send error to user that their wardrobe is empty, so outfit cannot be created.|
| create_fit_card | Outfit input is missing or incomplete | Cancel create_fit_card, rerun suggest_outfit to recreate or create new outfit before returning to user.|

---

## Architecture

  User input                                                                              
      │                                                                                   
      │                                                                                   
      ▼                                                                                   
Planning Loop ────────────────────────────────────────────────────────────────────┐       
      │                                                                           │       
      ├─► search_listings(description, size, max_price)                           │       
      │         │ results=[]                                                      │       
      │         ├────► [ERROR] "No item matching description found..." ─► return  │       
      │         │                                                                 │       
      │         │ results=[item,...]                                              │       
      │         ▼                                                                 │       
      │     Session: Selected_item = results[0]                                   │       
      │         │                                                                 │       
      │         │                                                                 │       
      ├──►  suggest_outfit(selected_item, wardrobe) ◄──────────────────────┐      │       
      │         │                                                          │      │       
      │         ├───►  [ERROR] "No items in wardrobe..." ─► return         │      │       
      │         │                                                          │      │       
      │     Session: outfit_suggestion = "..."                             │      │       
      │         │                                                          │      │       
      │         │                                                          │      │       
      │         │                                                          │      │       
      └──►  create_fit_card(outfit_suggestion, selected_item)              │      │       
                │                                                          │      │       
                ├───►  [Error] (no outfit suggestion)──────────────────────┘      │       
                │                                                                 │       
            Session: fit_card = "..."                                             │       
                │                                                                 │       
                ▼                                                                 └───────
            Return session                                                                

---

## AI Tool Plan

I'll use claude code to create each tool individually. For each tool I'll create, I'll input my tool planning, and input my overall flowchart at the beginning for context for how everything should connect. Ill input the preexisting programs from data_loader file, and from there ask it to build me each tool in a way that follows each specification from my description. After it does this, I will test each tool via entering 4 queries to ensure it behaves in the way that I want it to. I will then repeat this step for my other two tools, and connect them in order to create my full project.

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
The first thing the agent does is find the most relevent thrifted clothing based on the input prompt usinng the search_listings tool. In this case It would input vintage white tee, and max price of $30.

**Step 2:**
From step one, there should have been a return of the best thriftable item that fits into the provided parameters. In that case, the agent would then call the suggested_outfit tool with both the input of the previous step's clothing item, and the user's wardrobe. This will then output the best outfit that can be made with the availible pieces, and how to style the outfit. However, if there is no output from step one, then the agent stops the program, informs the user that nothing matched their search results, and provides information on how to prevent this issue from happening again.

**Step 3:**
If suggested outfits is ran, then it uses the new suggested outfit to create an fit card. It would intake the outfit suggestions, and the new piece of clothing found, and output a short tidbit about the outfit and the thrifting process. This does not happen if step 1 fails, as step two cut the whole program.

**Final output to user:**
The user sees two outputted results. They see the item the agent suggested for them, as well as how to style it with their existing wardrobe, and the used sees the created fit card produced. However, if no thriftable item is found uusing the search_listing tool, the user then sees that no items were found for what they were looking for, and, if possible, a suggestion on how to change their prompt to find a piece of clothing that they are looking for.
