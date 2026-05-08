# Bedtime Story Generator with LLM Judge

This project is a small prompt-engineering and agent-design assignment for generating bedtime stories appropriate for children ages **5 to 10**. The system takes a simple user story request, generates a calm age-appropriate bedtime story, evaluates it using an LLM judge, revises the story when needed, summarizes it for a parent, and supports up to two rounds of human feedback.

The goal is not only to produce a story, but to demonstrate how a simple LLM workflow can be structured into separate responsibilities: user input, story generation, quality evaluation, targeted revision, summarization, and user-directed changes.

---

## Problem Statement

The assignment asks for a Python script that can:

- Take any simple bedtime story request from a user.
- Use prompting to generate a story appropriate for ages 5–10.
- Incorporate an LLM judge to improve story quality.
- Provide a block diagram showing the interaction between the user, storyteller, judge, and any additional components.
- Keep the OpenAI model fixed as `gpt-3.5-turbo`.

---

## What This Project Does

This implementation builds a minimal but structured bedtime story generation pipeline:

1. **User provides a story request**  
   Example: `A story about a girl named Alice and her best friend Bob, who is a cat.`

2. **Storyteller prompt generates the first story**  
   The storyteller is instructed to create a gentle, age-appropriate bedtime story with a clear beginning, middle, and end.

3. **LLM judge evaluates the story**  
   The judge checks whether the story is suitable for children ages 5–10 and whether it works well as a bedtime story.

4. **Targeted revision is applied if needed**  
   If the judge finds issues, the story is revised based only on the flagged feedback instead of blindly regenerating from scratch. The automatic judge/revision loop is capped at two passes.

5. **Summary is generated for the parent**  
   The system writes a short two-sentence parent-facing summary.

6. **Human feedback can be applied**  
   The user can request up to two targeted changes. After each human revision, the judge checks the result and the system auto-fixes the story if required.

7. **Final story is shown to the user**  
   The final output is either the original passing story or the latest revised version.

---

## System Architecture

```text
              +----------------+
              |      User      |
              +-------+--------+
                      |
                      v
          +-----------+------------+
          | Storyteller Prompt     |
          | generate_story()       |
          +-----------+------------+
                      |
                      v
          +-----------+------------+
          | LLM Judge Prompt       |
          | judge_story()          |
          +-----------+------------+
                      |
          +-----------+------------+
          | Revision needed?       |
          +-----+-------------+----+
                | Yes         | No
                v             v
       +--------+--------+    +----------------+
       | Surgical Editor |    | Parent Summary |
       | revise_story()  |    | summarize()    |
       +--------+--------+    +-------+--------+
                |                     |
                | max 2 auto passes   v
                +----------------> +--+---------+
                                  | Story Shown |
                                  +--+---------+
                                     |
                                     v
                             +-------+--------+
                             | Human Feedback |
                             | max 2 rounds   |
                             +-------+--------+
                                     |
                          +----------+----------+
                          |                     |
                          v                     v
                   +------+-------+      +------+------+
                   | Keep Story   |      | Targeted    |
                   | and End      |      | Human Edit  |
                   +--------------+      +------+------+
                                                 |
                                                 v
                                         +-------+--------+
                                         | Judge + Fix if |
                                         | still needed   |
                                         +-------+--------+
                                                 |
                                                 v
                                         +-------+--------+
                                         | Updated Story  |
                                         +----------------+
```

---

## Prompting Strategy

The system separates the LLM workflow into clear roles instead of using one generic prompt for everything.

### 1. Storyteller

The storyteller is responsible for generating the story. It is guided to:

- Write for children ages 5–10.
- Use simple, warm, and imaginative language.
- Keep the tone calm and bedtime-friendly.
- Avoid scary, violent, or overly intense content.
- Resolve the story clearly.
- End with the main character feeling safe, peaceful, or ready for sleep.

### 2. Judge

The judge acts as a **Sleep & Logic Guardian**. Its job is to evaluate whether the story is actually suitable as a bedtime story, not just whether it is grammatically correct.

The judge checks for:

- **Moral preaching**: no explicit lessons or direct moralizing near the resolution.
- **Forward-looking endings**: no next-day anticipation or cliffhanger energy.
- **Direct address**: no speaking directly to the child listener.
- **Sleepy epilogue**: clear winding-down cues such as yawning, heavy eyes, slower breathing, and softness.
- **Emotional safety**: the protagonist ends safe and settled.
- **Circular ending**: the ending echoes the opening through setting, mood, image, or sensory detail.
- **Resolution**: the early problem is concretely resolved.
- **Bedtime calmness**: the final sentences are short, calm, and low-energy.
- **Faithfulness**: the story honors the user's requested character or theme.

### 3. Reviser

The reviser makes targeted edits based on the judge feedback. It is instructed not to rewrite the entire story unless necessary. This keeps the pipeline more controlled and avoids unnecessary changes to parts of the story that already work.

---

## Why Use a Judge?

A bedtime story has different requirements from a normal short story. A normal story can end with excitement, suspense, or a surprise. A bedtime story should usually do the opposite: it should resolve tension, reduce energy, and help the child feel calm.

The judge layer helps catch issues such as:

- The ending is too exciting.
- The story introduces a problem but does not resolve it.
- The vocabulary is too complex.
- The story has mild suspense that may not be ideal before sleep.
- The final paragraph does not transition the child toward rest.

---

## How to Run

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your OpenAI API key

Do **not** hardcode your API key in the source code.

```bash
export OPENAI_API_KEY="your_api_key_here"
```

For Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

### 4. Run the script

```bash
python main.py
```

Then enter a bedtime story request when prompted.

### 5. Run the UI

```bash
streamlit run app.py
```

The Streamlit UI provides a dark-mode control surface for generation, judge results, revision labels, parent summary, human feedback, a keep-current-story option, and session history.

---

## Example Input

```text
A story about a girl named Alice and her best friend Bob, who happens to be a cat.
```

## Example Output

The program generates a bedtime story, evaluates it using the judge, revises it if needed, summarizes it, and then allows up to two rounds of human feedback.

---

## Design Choices

### Fixed model

The assignment requires keeping the model as `gpt-3.5-turbo`, so the system is designed around prompt clarity rather than relying on a stronger reasoning model.

### Simple control flow

The project intentionally uses a small pipeline instead of a heavy framework. This makes the code easy to understand, explain, and modify. The Streamlit UI calls the same core functions as the CLI.

### Targeted revision instead of full regeneration

When the judge identifies a problem, the reviser focuses on the specific issue rather than generating a completely new story. This helps preserve good parts of the original output.

### Bedtime-specific quality criteria

The judge is not just checking general writing quality. It evaluates whether the story is actually appropriate for helping a child settle down before sleep.

---

## Limitations

The largest limitation is the required use of `gpt-3.5-turbo`. GPT-3.5 can produce good prose, but it is less reliable at strict structure following, multi-step reasoning, and consistent judge/editor separation.

In particular:

- It may not always follow complex JSON schemas reliably.
- It can occasionally revise more than the exact requested section.
- It may miss subtle bedtime-quality issues.
- It may produce inconsistent judge outputs across runs.
- It is weaker than newer reasoning models at maintaining role separation across planner, storyteller, judge, and reviser steps.

If a stronger thinking model were allowed, the system would likely produce more accurate judge decisions, better targeted revisions, and more consistent structured outputs.

---

## If I Had Two More Hours

If I had two more hours, I would improve the system in three areas: robustness, evaluation, and agent-readiness.

First, I would add a planner step before story generation. The planner would convert the raw user request into a structured story brief containing the target age range, characters, setting, emotional tone, conflict level, theme, and bedtime ending requirement. This would give the storyteller a cleaner plan to follow and reduce prompt drift.

Second, I would add category-specific generation strategies. For example, animal stories, friendship stories, fantasy stories, adventure stories, and moral stories could each have slightly different prompt configurations. This would make the stories feel more intentional instead of using one generic generation prompt for all requests.

Third, I would make the judge stricter and more testable. I would expand it into a stronger Sleep & Logic Guardian that checks plot resolution, calmness, safety, age-appropriateness, and whether the final scene helps the child transition toward sleep. I would also create automated sample tests for common failure cases, such as unresolved endings, scary content, overly energetic conclusions, and vocabulary that is too advanced.

I would also add lightweight session memory to avoid repeating the same themes, morals, character types, and endings across multiple runs. This would make the system feel more polished and useful for repeated bedtime story generation.

Finally, if this were extended into a real agentic system, I would move toward JSON-based contracts between each component: planner, storyteller, judge, and reviser. However, because `gpt-3.5-turbo` is not consistently reliable with complex structured outputs, I would keep the current version simpler and only introduce strict JSON schemas where they are truly needed.

---

## Future Improvements

- Add a structured story planner.
- Add YAML or JSON configuration files for story categories.
- Add structured parent controls in addition to free-form feedback, such as sliders for calmness and length.
- Add automated regression tests for judge behavior.
- Add retry handling for invalid judge responses.
- Add optional JSON output mode for agent orchestration.
- Add persistent session memory to avoid repetitive stories across different runs.
- Improve the README with sample before/after judge revisions.

---

## Security Note

The OpenAI API key is loaded from the `OPENAI_API_KEY` environment variable. It should never be committed to GitHub or hardcoded in the source code.

---

## Tech Stack

- Python
- OpenAI API
- Streamlit
- `gpt-3.5-turbo`
- Prompt-based story generation
- LLM-as-judge evaluation
- Targeted revision loop
- Human feedback loop
- Timestamped session logs
