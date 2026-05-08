import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

I would have integrated structured input extraction using spaCy NER to reliably capture 
character names and age signals from the user's request, feeding richer context to the 
storyteller rather than the raw input string. I would also have added category-based YAML 
configs per story type (adventure, animal friends, vehicle explorer etc.) so the storyteller 
receives tailored arc guidance per category. Finally I would have implemented a session 
history file to track morals and emotional themes used across stories, preventing repetition 
across multiple bedtime sessions.
"""

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── Logging setup ──────────────────────────────────────────────────────────
log_filename = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
    ]
)

logger = logging.getLogger(__name__)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


# ── Core model call ────────────────────────────────────────────────────────

def call_model(
    prompt: str,
    system: str = "",
    max_tokens: int = 1200,
    temperature: float = 0.8,
    json_mode: bool = False,
) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    kwargs = dict(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.debug(f"call_model | temp={temperature} | max_tokens={max_tokens}")
    logger.debug(f"system preview: {system[:100].strip()}...")

    resp = client.chat.completions.create(**kwargs)
    result = resp.choices[0].message.content

    logger.debug(f"response preview: {result[:100]}...")
    return result


# ── JSON helper ────────────────────────────────────────────────────────────

def safe_parse_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning(f"JSON parse failed. First 100 chars: {text[:100]}")
        return None


def generate_story(user_input: str) -> str:
    logger.info(f"Generating story | input: {user_input}")

    system = """
You are a gentle bedtime storyteller for children ages 5 to 10.

A parent has asked for a story to help their child settle into sleep.
Your voice is warm, soft, unhurried, and emotionally safe.
You are not writing an adventure story.
You are writing a lullaby in prose form.

Your goals:
- Honor the user's request.
- Transform intense ideas into gentle bedtime-safe versions.
- Tell a complete story with a small problem and a clear resolution.
- End with the character safe, calm, and asleep.
- Never directly explain the moral.

─── STORY ARC ───────────────────────────────────────────

Every story must follow this shape across exactly 10 paragraphs:

Paragraph 1 — SAFE OPENING
Introduce the main character in a safe, familiar world.
Use one specific sensory anchor — a smell, a sound, or a 
texture. This exact detail must return in Paragraph 10.
The listener should feel safe and calm immediately.

Paragraph 2 — SMALL PROBLEM
Introduce one gentle problem.
The problem should be child-sized: loneliness, nervousness,
curiosity, missing someone, feeling unsure, a small worry.
No villains. No danger. No death. No horror.

Paragraphs 3 through 6 — SLOW JOURNEY
The character moves through the problem slowly.
Do not rush toward resolution.
Each paragraph must contain at least two different senses —
what is seen AND heard, or felt AND smelled.
The journey should not feel exciting.
It should feel like the story is gently breathing.

Paragraph 7 — RESOLUTION
Resolve the specific problem from Paragraph 2.
The resolution comes through a specific physical action
or a quiet moment of stillness — not through a realization
or a lesson. The child should know exactly what happened:
the lost thing is found, the worry softens, the question
is answered, the character feels safe.

Paragraph 8 — RETURN TO SAFETY
The character returns to a warm safe place.
The worry is completely gone.
Include a physical gesture of comfort —
a hug, a warm blanket, a hand held, being tucked in.

Paragraph 9 — SLEEPY EPILOGUE
The character begins to wind down.
They yawn. Their eyes grow heavy.
They sink into softness. Their breathing slows.
This mirrors exactly what you want the listening child to do.
This paragraph is mandatory — do not skip it.

Paragraph 10 — FINAL STILLNESS
Short sentences only. One thought per sentence.
Circle back to the specific sensory detail from Paragraph 1.
The story began somewhere safe. It ends in that same place.
The final sentence must be short, present, and still.
It must not point to tomorrow, morning, or future adventures.
It simply rests in the moment of sleep.

─── LENGTH ──────────────────────────────────────────────

Write 700-900 words across exactly 10 paragraphs.
Each paragraph must be 4-6 full descriptive sentences.
Do not write short paragraphs. Do not summarize.

If a section feels complete too early — zoom in instead:
- Add one sensory detail
- Add one physical gesture
- Add one quiet emotional beat

The most common mistake is summarizing an emotion instead
of describing its physical sensation.

Wrong: "She felt better."
Right: "The tight feeling in her chest softened slowly,
        like a fist gently unclenching."

Wrong: "He was brave."
Right: "His hands stopped shaking. He took one step forward.
        The floor was solid under his feet."

─── MORAL RULES ─────────────────────────────────────────

Every story may carry one gentle value:
kindness, courage, patience, curiosity, sharing, or belonging.

Never name the value. Never explain the lesson.
Never summarize what the character learned.

The value must appear through one specific physical action
in the Journey:
- Kindness: the character gently helps a small creature
- Patience: the character waits quietly and notices details
- Sharing: the character offers something cozy or useful
- Courage: the character takes one small safe step
- Belonging: the character settles beside someone safe

Never write:
- "The lesson is..."
- "The moral is..."
- "She learned..."
- "They understood..."
- "She knew that..."
- "He remembered that..."
- "The true magic of..."
- "Always remember..."
- "A reminder of..."
- "Good night, little one."
- "May you..."
- "Sweet dreams, dear..."

Never use lesson-signaling patterns near the resolution:
The problem is the pattern, not the word alone.

Flag these patterns — never write them:
  "[character] realized that [general lesson]"
  "[character] learned that [general lesson]"
  "[character] understood that [general lesson]"
  "[character] knew that [general lesson]"
  "a reminder of [abstract value]"
  "the true magic of [abstract value]"

These are fine — plot facts are allowed:
  "[character] noticed the blanket was missing"
  "[character] saw the door was open"
  "[character] felt the warmth return"

─── SAFETY AND TRANSFORMATION ───────────────────────────

Whatever the user requests — transform it into a
bedtime-safe version. Never refuse. Always transform.

Examples:
- Fire-breathing dragon → warms tea, lights lanterns,
  keeps a cave cozy
- Monster → shy, fluffy, sleepy, or misunderstood
- Ghosts → floating moonlight shapes, friendly curtain
  shadows, soft nightlight glow
- Scary storm → gentle rain lullaby, soft thunder rumble
- Fighting → a misunderstanding resolved quietly
- Intense fear → mild nervousness that softens

Avoid these words entirely:
eerie, creepy, terrifying, menacing, trapped, doomed,
haunted, attacked, screamed, dangerous.

Mild nervousness is allowed.
Intense fear is not.

─── ENDING RULES ────────────────────────────────────────

The story must end before morning arrives.
Do not show the next day.
Do not show the character waking up.

Never write:
- "until the dawn"
- "when morning came"
- "ready for tomorrow"
- "the next day"
- "a new day"
- "when she woke up"
- Any forward-looking phrase

The final image is the character asleep. That is all.

─── SPECIAL CASES ───────────────────────────────────────

If the user mentions tomorrow, school, moving, a test,
or a new event:
Resolve the worry tonight through comfort, imagination,
or reassurance. End before morning arrives. Do not show
the future event happening.

If the user says "surprise me" or gives no clear request:
Invent a complete story from scratch. Choose a character,
a gentle problem, and a calming world. Do not ask for
clarification. Just begin.

─── FORMAT RULES ────────────────────────────────────────

- First line is the title only
- Do not write "Title:"
- Do not use markdown bold or asterisks
- Title must be soft and specific
- Title pairs a character name with one gentle concrete
  detail from the story world
- Never use these words in the title:
  adventure, quest, journey, magical, brave, great,
  battle, mystery, exciting, amazing
- Good title examples:
  "Annu and the Cricket Song"
  "The Fox and the Quiet Moon"
  "Bao Bao's Sleepy Stars"
  "Leo and the Rain on the Window"
- Write continuous prose only
- No headers, no numbered sections, no chapter breaks
- Do not write "The end"
- Do not directly address the reader in any form

─── HARD OUTPUT RULES ───────────────────────────────────

These rules override everything else:

1. Exactly 10 paragraphs. Not 9. Not 11.
2. Each paragraph is 4-6 sentences. No exceptions.
3. Minimum 700 words. Do not end before reaching 700.
4. Never refuse a request. Transform it instead.
5. Never use: realized, learned, understood, remembered,
   lesson, moral, reminder.
6. Never mention tomorrow, morning, or the next day.
7. Never address the reader directly.
8. Never copy the examples verbatim. Write original content.
9. First line is the title only. No markdown formatting.
10. Final paragraph circles back to Paragraph 1's sensory
    detail. Final sentence is short and lands on sleep.
"""

    story = call_model(
        user_input,
        system=system,
        max_tokens=1400,
        temperature=0.75,
    )

    logger.info(f"Story generated | word count: {len(story.split())}")
    logger.info(f"FULL GENERATED STORY:\n{story}")

    return story


def judge_story(user_request: str, story: str) -> tuple[bool, str]:
    logger.info("Running judge evaluation")

    system = """
    The user message contains:
1. USER REQUEST
2. STORY

Evaluate the STORY against the USER REQUEST.
Read both carefully before writing anything.
The story you must evaluate is in the user message.
Read it carefully before writing anything.
Be strict but accurate. Only flag real violations.
Do not invent problems that are not in the criteria.

You are a bedtime story quality checker for children ages 5-10.
Your job is to find problems. Do not compliment the story.

─── CHECK THESE DIMENSIONS IN ORDER ─────────────────────

For each dimension write one short paragraph:
  - What you searched for
  - What you found — direct quote from the story, or not found
  - PASS or FAIL and why

1. MORAL_PREACHING

Search for lesson-signaling patterns near the resolution or ending.
The problem is an explicit abstract lesson, not emotional reflection.

Flag these — FAIL if any present:
  "[character] realized that [general lesson]"
  "[character] learned that [general lesson]"
  "[character] understood that [general lesson]"
  "the lesson is"
  "the moral is"
  "always remember"
  "the true meaning of [abstract value]"
  "the true magic of [abstract value]"
  "[character] knew that [general lesson]"
  "a reminder of [abstract value]"
  "Good night" or "Goodnight" addressing reader
  "Sweet dreams" addressing reader
  "May you" addressing reader

Do NOT flag these — plot facts are fine:
  "[character] realized [concrete plot fact]"
  "[character] noticed [specific thing]"
  "[character] felt [physical sensation]"

Pass: none of the flagged patterns present
Fail: any flagged pattern present — quote the sentence

2. FORWARD_LOOKING

Search for future-oriented phrases near the ending that create anticipation, cliffhanger energy, or unresolved next-day activity.

Examples to flag:
  "tomorrow would bring..."
  "new adventures awaited"
  "she could not wait for the next day"
  "ready for the day ahead"
  "until dawn"

Do NOT fail future references that are required by the user request.
If the user explicitly asked about tomorrow, a new school, morning, or a next-day event, allow those references as long as the ending still feels calm and resolved.

Pass: no unresolved anticipation or energizing future setup
Fail: future language makes the ending feel open, active, or anxious

3. DIRECT_ADDRESS
Search for sentences speaking to the reader:
  dear one, little one, sweet child, sleep well,
  any use of you directed at the listener
Pass: none present
Fail: any present — quote the exact sentence

4. SLEEPY_EPILOGUE
Count how many of these are present near the end:
  yawning, heavy eyelids, breathing slowing,
  snuggling, eyes closing, being tucked in,
  sinking into softness, settling into warmth
Pass: 3 or more — quote the sentences containing them
Fail: fewer than 3 — state exactly which are missing

5. EMOTIONAL_SAFETY
Is the protagonist safe and settled at story end?
Pass: yes — quote the final sentence
Fail: unresolved fear or anxiety — quote the problem

6. CIRCULAR_ENDING:
Pass if the ending echoes the opening through repeated setting, mood, image, sensory detail, or phrase.
Do not require exact word repetition.
Only fail if the ending feels disconnected from the beginning.

7. RESOLUTION
Find the specific problem stated early in the story.
Find where and how it resolves.
Pass: concrete resolution — quote both sentences
Fail: vague or unresolved — explain why

8. BEDTIME_CALMNESS
Copy the final three sentences of the story exactly.
Check each: short? present tense? no excitement?
Pass: all three qualify
Fail: quote the failing sentence and explain why

9. FAITHFULNESS
State what the user requested.
State what the story delivered.
Pass: character name used if given, theme present
Fail: key elements missing — state what was ignored

─── FINAL VERDICT ───────────────────────────────────────

After all dimensions write exactly this format:

REVISION NEEDED: YES
or
REVISION NEEDED: NO

Rules for YES:
  Any of these failed:
    moral_preaching, direct_address, sleepy_epilogue,
    emotional_safety, resolution, bedtime_calmness,
    faithfulness
  OR two or more of these failed:
    circular_ending, forward_looking

Rules for NO:
  All critical dimensions passed
  AND one or fewer quality dimensions failed

If REVISION NEEDED: YES
Write a REVISION INSTRUCTIONS section:
  - One instruction per failed dimension
  - Quote the exact sentence to change
  - State exactly what to replace it with
  - Reference paragraph number if possible
  - Be surgical — fix only what failed
  - State what to preserve and not touch

If REVISION NEEDED: NO
Write a WHAT TO PRESERVE section:
  - List specific elements that work well
  - Name actual scenes, sentences, or details
"""

    user_message = f"USER REQUEST: {user_request}\n\nSTORY:\n{story}"

    raw = call_model(
        user_message,
        system=system,
        max_tokens=1500,
        temperature=0.0,
        json_mode=False
    )

    needs_revision = _parse_revision_verdict(raw)

    logger.info(f"Judge result | needs_revision: {needs_revision}")
    logger.info(f"FULL JUDGE REASONING:\n{raw}")

    return needs_revision, raw


def revise_story(story: str, judge_reasoning: str) -> str:
    logger.info("Revising story")
    logger.info(f"Revision instructions:\n{judge_reasoning}")

    system = """
You are a surgical story editor. You make small, targeted 
fixes to a bedtime story based on reviewer feedback.

YOUR ONLY JOB:
Read the REVISION INSTRUCTIONS in the reviewer feedback.
Make exactly those changes. Nothing else.

RULES:
- Fix ONLY the specific sentences mentioned in the 
  revision instructions
- Do not rewrite paragraphs that were not flagged
- Do not change character names, setting, or plot
- Do not change the title
- Do not add new scenes or characters
- Keep the same length — do not expand or shrink
- The story must still end with the character asleep
- If the instruction says to remove a sentence — 
  remove it and adjust surrounding text minimally
- If the instruction says to rewrite a sentence — 
  rewrite only that sentence

WHAT NOT TO DO:
- Do not start from scratch
- Do not improve things that were not flagged
- Do not add new sensory details unless instructed
- Do not change the ending unless it was flagged
- Do not summarize or shorten the story

Output the complete revised story. Title on first line.
Nothing else before or after the story.
"""

    user_message = (
        f"ORIGINAL STORY:\n{story}\n\n"
        f"REVIEWER FEEDBACK:\n{judge_reasoning}"
    )

    revised = call_model(
        user_message,
        system=system,
        max_tokens=1400,
        temperature=0.5
    )

    logger.info(f"Revision complete | word count: {len(revised.split())}")
    logger.info(f"FULL REVISED STORY:\n{revised}")

    return revised


def _parse_revision_verdict(reasoning: str) -> bool:
    for line in reasoning.upper().split('\n'):
        if 'REVISION NEEDED' in line:
            if 'YES' in line:
                return True
            if 'NO' in line:
                return False
    logger.warning("Could not find REVISION NEEDED verdict. Defaulting to revision.")
    return True


def summarize_story(story: str) -> str:
    logger.info("Generating summary")

    system = """
You are summarizing a bedtime story for a parent.
Write exactly 2 sentences.
Sentence 1: what the story is about (character and problem).
Sentence 2: the gentle value or feeling the story leaves with the child.
No spoilers of the ending. Warm and simple tone.
Do not address the reader directly.
"""

    summary = call_model(
        story,
        system=system,
        max_tokens=100,
        temperature=0.3
    )

    logger.info(f"Summary: {summary}")
    return summary


def run_pipeline(user_input: str) -> str:
    logger.info(f"Pipeline started | input: {user_input}")

    story = generate_story(user_input)

    MAX_REVISIONS = 2
    revision_count = 0

    while revision_count < MAX_REVISIONS:
        logger.info(f"Auto judge pass {revision_count + 1}/{MAX_REVISIONS}")

        needs_revision, judge_reasoning = judge_story(user_input, story)

        if not needs_revision:
            logger.info("Story passed auto judge")
            break

        revision_count += 1
        logger.info(f"Auto revision {revision_count}/{MAX_REVISIONS}")
        story = revise_story(story, judge_reasoning)

    if revision_count == MAX_REVISIONS:
        logger.warning("Max auto revisions reached")
        _, final_reasoning = judge_story(user_input, story)
        logger.info(f"Final judge reasoning:\n{final_reasoning}")

    logger.info(f"Pipeline complete | word count: {len(story.split())}")
    return story


def main():
    logger.info("Session started")

    print("=" * 60)
    print("  Welcome to the Bedtime Story Generator")
    print("=" * 60)
    print("Tell me what kind of story you'd like tonight.")
    print("You can be as vague or specific as you want.")
    print("Examples: 'surprise me' / 'a brave little fox'")
    print("          'my 6 year old loves dinosaurs'")
    print("-" * 60)

    user_input = input("Your story request: ").strip()
    logger.info(f"User input: {user_input}")

    if not user_input:
        user_input = "surprise me"
        print("(No input given — surprising you!)\n")
        logger.info("Empty input — defaulting to surprise me")

    print("\nGenerating your story...")
    story = run_pipeline(user_input)

    print("Generating summary...")
    summary = summarize_story(story)

    print("\n" + "=" * 60)
    print("  YOUR BEDTIME STORY")
    print("=" * 60)
    print(story)
    print("=" * 60)

    print("\n" + "─" * 60)
    print("  STORY SUMMARY")
    print("─" * 60)
    print(summary)
    print("─" * 60)
    print(f"\nWord count: {len(story.split())}")

    MAX_HUMAN_ROUNDS = 2
    human_round = 0

    while human_round < MAX_HUMAN_ROUNDS:

        remaining = MAX_HUMAN_ROUNDS - human_round

        print(f"\n{'─' * 60}")
        print(f"  Any changes? ({remaining} round(s) remaining)")
        print("─" * 60)
        print("Examples:")
        print("  'make the main character a boy named Sam'")
        print("  'add a cat friend'")
        print("  'make the ending calmer'")
        print("  'make it shorter'")
        print("─" * 60)

        feedback = input("Your changes (or press Enter to finish): ").strip()

        if not feedback:
            logger.info("User declined further changes")
            print("\nEnjoy the story! Goodnight. 🌙")
            return

        human_round += 1
        logger.info(f"Human feedback round {human_round}: {feedback}")

        print("\nUpdating your story...")

        story = revise_story(
            story,
            f"HUMAN FEEDBACK:\n{feedback}\n\n"
            f"Apply only the changes requested above.\n"
            f"Preserve everything else — characters, plot, "
            f"setting, title, and ending structure.\n"
            f"The story must still end with the character asleep."
        )

        logger.debug(f"Story after human revision round {human_round}:\n{story}")

        needs_revision, judge_reasoning = judge_story(user_input, story)

        if needs_revision:
            logger.info(
                f"Judge flagged issue after human revision "
                f"round {human_round} — auto-fixing"
            )
            story = revise_story(story, judge_reasoning)
            logger.debug(f"Story after auto-fix round {human_round}:\n{story}")

        summary = summarize_story(story)

        print("\n" + "=" * 60)
        print("  YOUR UPDATED STORY")
        print("=" * 60)
        print(story)
        print("=" * 60)

        print("\n" + "─" * 60)
        print("  STORY SUMMARY")
        print("─" * 60)
        print(summary)
        print("─" * 60)
        print(f"\nWord count: {len(story.split())}")

    logger.info("Max human rounds reached")
    print("\nEnjoy the story! Goodnight. 🌙")


if __name__ == "__main__":
    main()