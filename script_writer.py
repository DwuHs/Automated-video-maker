"""
Step 1 — Script Generation using Google Gemini Flash (free tier).
Generates a short-form monologue script in Old Man Gerald's voice,
plus a YouTube title and description.
"""

import os
import google.generativeai as genai

# Brand hashtags that are always appended to every video description.
# Sourced from the README's recommended TikTok/YouTube caption list.
BRAND_HASHTAGS = [
    # Core brand tags
    "#finance",
    "#money",
    "#investing",
    "#genz",
    "#oldmangerald",
    "#Shorts",
    # README lines 290–293
    "#personalfinance",
    "#moneytips",
    "#financialliteracy",
    "#moneyadvice",
    "#financetok",
    "#moneyhacks",
    "#financialfreedom",
    "#investing101",
    "#genzfinance",
    "#adulting",
    "#adulting101",
    "#moneyforbeginners",
    "#collegestudent",
    "#broke",
    "#firstjob",
    "#twenties",
    "#learnontiktok",
    "#didyouknow",
    "#fyp",
    "#foryou",
    "#viral",
    "#storytime",
    "#explainedbyai",
    "#financefacts",
    "#emergency",
    "#budgetfriendly",
    "#budgeting",
    "#budget",
    "#financetips",
]


def generate_script(topic: str) -> dict:
    """
    Generate a script, YouTube title, and description for a given finance topic.

    Args:
        topic: The financial topic to explain (e.g., "credit cards").

    Returns:
        dict with keys: 'script', 'title', 'description'
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    # --- System prompt encoding Old Man Gerald's personality ---
    system_prompt = """You are writing a script for a character named "Old Man Gerald" — an extremely grumpy, 
hilariously cranky old man who made his money the old-fashioned way and is DEEPLY annoyed that he has to 
explain basic financial concepts to Gen Z. He speaks in short-form vertical videos (YouTube Shorts / TikTok).

CHARACTER VOICE — Gerald is:
- AGGRESSIVELY grumpy and sarcastic. He acts like explaining finance is physically painful. Every word counts — no rambling, no pausing.
- Bitingly sarcastic on every line — sharp wit and deadpan frustration. No drawn-out jokes.
- Hilariously dramatic — he treats Gen Z financial mistakes like war crimes.
- He uses sharp, out-of-pocket comparisons (e.g., "You're trying to build a financial future on a foundation made entirely of Klarna payments and iced coffee.")
- He is highly impatient and FAST. He fires off the explanation quickly, grumbling the whole way through.
- He throws in short, punchy old man reactions — things like "Ugh", "Pfft", "Hmph", "Good grief", "Bah", "Gah!", "Lord help me".
- He is an "annoyed expert" — he knows his stuff cold, he just hates that you don't.
- Despite his grumpiness, the financial advice is the primary focus and must be accurate.

- DISRUPTIVE HOOK: High-energy, immediate call-out of a financial mistake or pain point.
- Rapid-fire roasting of bad financial habits.
- Rhetorical questions dripping with disbelief.
- Mock outrage — short and punchy, not drawn out.

SCRIPT STRUCTURE:
1. HOOK (first 3 seconds): A high-energy, disruptive opening that immediately calls out a financial mistake or pain point. Gerald should sound like he's at his limit.
2. RANT/EXPLANATION (middle): The concept explained concisely but clearly, interrupted by punchy grumbles and disbelief. NO FILLER.
3. ENDING: A final "out of pocket" sign-off where he angrily demands the viewer to like and subscribe before suddenly ending the video.

CONSTRAINTS:
- Script must be 85-110 words (up to 40 seconds when read aloud).
- CRITICAL: Limit analogies and out-of-pocket jokes to exactly 2 per script to avoid excessive ranting about unrelated topics.
- MUST be concise — avoid random anecdotes or verbal filler like "Wait, what was I saying?".
- Financial information must be the CORE of the script (at least 70% of the text).
- CRITICAL: Do NOT use stage directions. Write everything as spoken text. Use "!" for sudden bursts of volume.
- CRITICAL: Do NOT use ellipses (...) or any punctuation that creates pauses. Write continuously flowing text to eliminate random pauses.
- Keep the energy HIGH, FAST, and BREVITY-FOCUSED. Gerald wants to explain this and leave."""

    # --- Generate the script ---
    script_prompt = f"""{system_prompt}

Write a script about: "{topic}"

Return ONLY the monologue script text. No stage directions, no action markers in asterisks or brackets,
no character names, no quotation marks wrapping the whole thing. Just the exact words Gerald would say out loud.
Remember: if Gerald would scoff, write "Pfft" or "Hmph" — do NOT write *scoffs*."""

    script_response = model.generate_content(script_prompt)
    script_text = script_response.text.strip()

    # --- Generate YouTube title ---
    title_prompt = f"""You are writing a YouTube Shorts title for a video by "Old Man Gerald" — a grumpy 
old man who explains finance to Gen Z.

The video topic is: "{topic}"

Write ONE punchy, clickable title that:
- Is under 60 characters
- Would make someone stop scrolling
- Matches Old Man Gerald's grumpy personality
- Includes relevant keywords

Return ONLY the title text, nothing else."""

    title_response = model.generate_content(title_prompt)
    title_text = title_response.text.strip().strip('"').strip("'")

    # Ensure title is under 60 characters
    if len(title_text) > 60:
        title_text = title_text[:57] + "..."

    # --- Generate YouTube description ---
    desc_prompt = f"""Write a YouTube Shorts description for a video by "Old Man Gerald" about "{topic}".

Include:
1. A one-line summary of what the video covers
2. A call to action (follow/subscribe)
3. 5-8 relevant finance hashtags

Keep it under 300 characters total. Return ONLY the description text."""

    desc_response = model.generate_content(desc_prompt)
    description_text = desc_response.text.strip()

    # Ensure all brand hashtags are present in the description.
    # Collect any that the AI didn't already include and append them.
    missing_hashtags = [
        tag for tag in BRAND_HASHTAGS
        if tag.lower() not in description_text.lower()
    ]
    if missing_hashtags:
        description_text += "\n" + " ".join(missing_hashtags)

    print(f"✅ Script generated ({len(script_text.split())} words)")
    print(f"✅ Title: {title_text}")

    return {
        "script": script_text,
        "title": title_text,
        "description": description_text,
    }
