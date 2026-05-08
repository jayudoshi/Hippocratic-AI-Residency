import glob
import html
import os
import re
from datetime import datetime

import streamlit as st


APP_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_HUMAN_ROUNDS = 2


st.set_page_config(
    page_title="Bedtime Story Pipeline",
    page_icon="moon",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
<style>
:root {
    --bg: #080a10;
    --panel: #10131d;
    --panel-2: #151927;
    --line: #252b3b;
    --muted: #8b93a7;
    --soft: #c8cedc;
    --text: #f2f5fb;
    --accent: #8fb8ff;
    --accent-2: #8de0c7;
    --warn: #f6c177;
    --bad: #ff8a8a;
    --good: #8de0a6;
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(143, 184, 255, 0.11), transparent 34rem),
        linear-gradient(180deg, #080a10 0%, #0a0d14 45%, #080a10 100%);
    color: var(--text);
}

#MainMenu, header, footer { visibility: hidden; }
.block-container {
    max-width: 1240px;
    padding: 2rem 2rem 4rem !important;
}

h1, h2, h3, p { letter-spacing: 0; }

.hero {
    border: 1px solid rgba(143, 184, 255, 0.18);
    background: linear-gradient(135deg, rgba(21, 25, 39, 0.94), rgba(12, 15, 24, 0.96));
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.eyebrow {
    color: var(--accent-2);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.hero h1 {
    color: var(--text);
    font-size: clamp(2rem, 4vw, 3.8rem);
    line-height: 1.02;
    margin: 0;
    font-weight: 760;
}
.hero p {
    color: var(--soft);
    max-width: 760px;
    margin: 0.85rem 0 0;
    font-size: 1rem;
    line-height: 1.65;
}

.panel {
    border: 1px solid var(--line);
    background: rgba(16, 19, 29, 0.88);
    border-radius: 8px;
    padding: 1rem;
}
.section-title {
    color: var(--text);
    font-size: 0.88rem;
    font-weight: 750;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0 0.85rem;
}
.muted {
    color: var(--muted);
    font-size: 0.88rem;
    line-height: 1.55;
}
.tiny {
    color: var(--muted);
    font-size: 0.75rem;
    line-height: 1.4;
}

.pipeline-line {
    color: var(--soft);
    border: 1px solid rgba(143, 184, 255, 0.14);
    background: rgba(16, 19, 29, 0.74);
    border-radius: 8px;
    padding: 0.75rem 0.9rem;
    margin: 1rem 0;
    font-size: 0.84rem;
    line-height: 1.55;
}

.story {
    border: 1px solid rgba(143, 184, 255, 0.17);
    background: #10131d;
    border-radius: 8px;
    padding: 1.35rem;
}
.story-title {
    color: var(--text);
    font-family: Georgia, "Times New Roman", serif;
    font-size: 1.6rem;
    line-height: 1.2;
    margin: 0 0 1rem;
}
.story p {
    color: #dbe1ee;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 1.05rem;
    line-height: 1.82;
    margin: 0 0 1rem;
}

.summary {
    border-left: 3px solid var(--accent-2);
    background: rgba(141, 224, 199, 0.08);
    border-radius: 0 8px 8px 0;
    padding: 0.95rem 1rem;
    color: var(--soft);
    line-height: 1.6;
}
.revision-note {
    border: 1px solid var(--line);
    background: rgba(16, 19, 29, 0.76);
    border-radius: 8px;
    padding: 0.8rem 0.9rem;
    margin-bottom: 0.7rem;
}
.revision-label {
    color: var(--accent-2);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.revision-note p {
    color: var(--muted);
    margin: 0.35rem 0 0;
    font-size: 0.86rem;
    line-height: 1.45;
}

.judge-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 0.75rem;
    align-items: start;
    border-bottom: 1px solid rgba(37, 43, 59, 0.8);
    padding: 0.8rem 0;
}
.judge-row:last-child { border-bottom: 0; }
.judge-name {
    color: var(--text);
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.judge-detail {
    color: var(--muted);
    font-size: 0.82rem;
    line-height: 1.45;
    margin-top: 0.25rem;
}
.badge {
    border-radius: 999px;
    padding: 0.22rem 0.55rem;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.08em;
}
.pass { background: rgba(141, 224, 166, 0.12); color: var(--good); border: 1px solid rgba(141, 224, 166, 0.35); }
.fail { background: rgba(255, 138, 138, 0.12); color: var(--bad); border: 1px solid rgba(255, 138, 138, 0.35); }
.unknown { background: rgba(246, 193, 119, 0.12); color: var(--warn); border: 1px solid rgba(246, 193, 119, 0.35); }

.stTextInput input, .stTextArea textarea {
    background: #0d1018 !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(143, 184, 255, 0.16) !important;
}
.stButton button {
    border-radius: 8px !important;
    border: 1px solid rgba(143, 184, 255, 0.38) !important;
    background: linear-gradient(135deg, #8fb8ff, #8de0c7) !important;
    color: #071018 !important;
    font-weight: 800 !important;
}
.stButton button:hover {
    border-color: rgba(242, 245, 251, 0.55) !important;
    box-shadow: 0 10px 26px rgba(143, 184, 255, 0.18) !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 0.4rem;
    border-bottom: 1px solid var(--line);
}
.stTabs [data-baseweb="tab"] {
    color: var(--muted);
    border-radius: 8px 8px 0 0;
    padding: 0.65rem 1rem;
}
.stTabs [aria-selected="true"] {
    color: var(--text) !important;
    background: var(--panel) !important;
}
[data-testid="metric-container"] {
    border: 1px solid var(--line);
    background: rgba(16, 19, 29, 0.84);
    border-radius: 8px;
    padding: 0.85rem;
}

@media (max-width: 900px) {
    .block-container { padding: 1rem !important; }
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_pipeline():
    try:
        import main as pipeline_main

        return {
            "available": True,
            "error": "",
            "generate_story": pipeline_main.generate_story,
            "judge_story": pipeline_main.judge_story,
            "revise_story": pipeline_main.revise_story,
            "summarize_story": pipeline_main.summarize_story,
            "logger": pipeline_main.logger,
        }
    except Exception as exc:
        return {"available": False, "error": str(exc)}


def escape(value: str) -> str:
    return html.escape(value or "", quote=True)


def word_count(text: str) -> int:
    return len((text or "").split())


def story_parts(story: str) -> tuple[str, list[str]]:
    blocks = [part.strip() for part in re.split(r"\n\s*\n", story or "") if part.strip()]
    if not blocks:
        return "", []
    first = blocks[0]
    if len(first) <= 90 and first.count(".") <= 1:
        return first, blocks[1:]
    return "", blocks


def render_story(story: str):
    title, paragraphs = story_parts(story)
    title_html = f'<div class="story-title">{escape(title)}</div>' if title else ""
    para_html = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in paragraphs)
    if not para_html and story:
        para_html = f"<p>{escape(story)}</p>"
    st.markdown(f'<div class="story">{title_html}{para_html}</div>', unsafe_allow_html=True)


def render_flow():
    st.markdown(
        """
        <div class="pipeline-line">
            <strong>Actual main.py flow:</strong>
            User Input -> Generation -> Judge -> Revision if required (max 2) -> Summary -> Human Feedback (max 2) -> Revise -> Judge -> Auto-fix if required -> Summary / End
        </div>
        """,
        unsafe_allow_html=True,
    )


def parse_revision_needed(reasoning: str) -> str:
    for line in (reasoning or "").splitlines():
        if "REVISION NEEDED" in line.upper():
            if "YES" in line.upper():
                return "YES"
            if "NO" in line.upper():
                return "NO"
    return "UNKNOWN"


def add_revision_event(kind: str, note: str):
    st.session_state.revision_events.append({"kind": kind, "note": note})


def render_revision_events():
    if not st.session_state.revision_events:
        st.caption("No revisions have been applied in this UI session.")
        return

    rows = []
    for index, event in enumerate(st.session_state.revision_events, start=1):
        kind = event["kind"]
        label = "Human revision" if kind == "human" else "Auto revision"
        rows.append(
            f"""
            <div class="revision-note">
                <div class="revision-label">{escape(label)} {index}</div>
                <p>{escape(event["note"])}</p>
            </div>
            """
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def parse_judge_dimensions(reasoning: str) -> list[dict]:
    dimensions = []
    matches = list(re.finditer(r"(?m)^(\d+)\.\s+([A-Z_]+)\s*$", reasoning or ""))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(reasoning)
        body = (reasoning or "")[start:end].strip()
        body = body.split("REVISION NEEDED:", 1)[0].strip()
        upper = body.upper()
        if re.search(r"\*\*PASS\*\*|\bPASS\b", upper):
            verdict = "PASS"
        elif re.search(r"\*\*FAIL\*\*|\bFAIL\b", upper):
            verdict = "FAIL"
        else:
            verdict = "UNKNOWN"
        clean = re.sub(r"\*{0,2}\b(PASS|FAIL)\b\*{0,2}", "", body, flags=re.IGNORECASE)
        clean = re.sub(r"\s+", " ", clean).strip()
        dimensions.append(
            {
                "name": match.group(2).replace("_", " ").title(),
                "verdict": verdict,
                "detail": clean[:260] + ("..." if len(clean) > 260 else ""),
            }
        )
    return dimensions


def render_judge(reasoning: str):
    revision_needed = parse_revision_needed(reasoning)
    if revision_needed == "NO":
        st.success("Judge verdict: no revision needed.")
    elif revision_needed == "YES":
        st.warning("Judge verdict: revision needed.")
    else:
        st.info("Judge verdict unavailable.")

    dimensions = parse_judge_dimensions(reasoning)
    if not dimensions:
        st.code(reasoning or "No judge output available.", language="text")
        return

    rows = []
    for dim in dimensions:
        verdict = dim["verdict"].lower()
        badge_class = verdict if verdict in {"pass", "fail"} else "unknown"
        rows.append(
            f"""
            <div class="judge-row">
                <div>
                    <div class="judge-name">{escape(dim["name"])}</div>
                    <div class="judge-detail">{escape(dim["detail"])}</div>
                </div>
                <span class="badge {badge_class}">{escape(dim["verdict"])}</span>
            </div>
            """
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def find_log_files() -> list[str]:
    files = []
    for path in glob.glob(os.path.join(APP_DIR, "story_*.log")):
        try:
            if os.path.getsize(path) == 0:
                continue
            with open(path, encoding="utf-8") as handle:
                preview = handle.read(4000)
            if "Pipeline started" in preview or "FULL GENERATED STORY:" in preview:
                files.append(path)
        except OSError:
            continue
    return sorted(files, reverse=True)


def format_log_filename(path: str) -> str:
    name = os.path.basename(path)
    match = re.match(r"story_(\d{8})_(\d{6})\.log$", name)
    if not match:
        return name
    day, time = match.groups()
    stamp = datetime.strptime(day + time, "%Y%m%d%H%M%S")
    return stamp.strftime("%b %d, %Y %I:%M %p")


def extract_blocks(content: str, marker: str) -> list[str]:
    blocks = []
    marker_re = re.compile(
        rf"^\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}:\d{{2}},\d{{3}} \| INFO \| {re.escape(marker)}\s*$",
        re.MULTILINE,
    )
    starts = list(marker_re.finditer(content))
    timestamp_re = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \| ", re.MULTILINE)
    for start_match in starts:
        start = start_match.end()
        next_timestamp = timestamp_re.search(content, start)
        end = next_timestamp.start() if next_timestamp else len(content)
        blocks.append(content[start:end].strip())
    return blocks


def parse_log_file(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        content = handle.read()

    session = {
        "path": path,
        "user_request": "",
        "generated_story": "",
        "judge_reviews": [],
        "revisions": [],
        "summary": "",
        "word_count": 0,
        "auto_revision_count": 0,
        "human_round_count": 0,
        "final_story": "",
    }

    user_match = re.search(r"\| INFO \| Pipeline started \| input:\s*(.*)", content)
    if not user_match:
        user_match = re.search(r"\| INFO \| User input:\s*(.*)", content)
    session["user_request"] = user_match.group(1).strip() if user_match else ""

    generated = extract_blocks(content, "FULL GENERATED STORY:")
    revised = extract_blocks(content, "FULL REVISED STORY:")
    judges = extract_blocks(content, "FULL JUDGE REASONING:")

    session["generated_story"] = generated[0] if generated else ""
    session["judge_reviews"] = [{"reasoning": item} for item in judges]
    session["final_story"] = revised[-1] if revised else session["generated_story"]

    summary_matches = re.findall(r"\| INFO \| Summary:\s*(.*)", content)
    session["summary"] = summary_matches[-1].strip() if summary_matches else ""

    count_match = re.search(r"\| INFO \| Pipeline complete \| word count:\s*(\d+)", content)
    if count_match:
        session["word_count"] = int(count_match.group(1))

    auto_matches = re.findall(r"\| INFO \| Auto revision\s+(\d+)", content)
    session["auto_revision_count"] = max([int(item) for item in auto_matches], default=0)

    feedbacks = re.findall(r"\| INFO \| Human feedback round\s+\d+:\s*(.*)", content)
    session["human_round_count"] = len(feedbacks)

    for index, story in enumerate(revised):
        is_human = index >= session["auto_revision_count"] and feedbacks
        feedback_index = index - session["auto_revision_count"]
        session["revisions"].append(
            {
                "type": "human" if is_human else "auto",
                "feedback": feedbacks[feedback_index] if is_human and feedback_index < len(feedbacks) else "",
                "story": story,
            }
        )

    return session


def reset_generation_state():
    for key in [
        "story",
        "summary",
        "judge_raw",
        "original_request",
        "human_rounds_used",
        "auto_revisions",
        "revision_events",
        "finished",
        "pipeline_done",
    ]:
        st.session_state.pop(key, None)
    st.session_state.human_rounds_used = 0
    st.session_state.auto_revisions = 0
    st.session_state.revision_events = []
    st.session_state.finished = False
    st.session_state.pipeline_done = False


def run_initial_pipeline_for_ui(pipeline: dict, user_request: str) -> tuple[str, str, int]:
    logger = pipeline["logger"]
    logger.info(f"Pipeline started | input: {user_request}")

    story = pipeline["generate_story"](user_request)
    max_revisions = 2
    revision_count = 0
    judge_reasoning = ""

    while revision_count < max_revisions:
        logger.info(f"Auto judge pass {revision_count + 1}/{max_revisions}")
        needs_revision, judge_reasoning = pipeline["judge_story"](user_request, story)

        if not needs_revision:
            logger.info("Story passed auto judge")
            break

        revision_count += 1
        logger.info(f"Auto revision {revision_count}/{max_revisions}")
        story = pipeline["revise_story"](story, judge_reasoning)

    if revision_count == max_revisions:
        logger.warning("Max auto revisions reached")
        _, judge_reasoning = pipeline["judge_story"](user_request, story)

    logger.info(f"Pipeline complete | word count: {len(story.split())}")
    return story, judge_reasoning, revision_count


def build_auto_revision_events(count: int) -> list[dict]:
    return [
        {
            "kind": "auto",
            "note": f"Judge requested repair pass {index} during the initial generation pipeline.",
        }
        for index in range(1, count + 1)
    ]


for key, value in {
    "story": "",
    "summary": "",
    "judge_raw": "",
    "original_request": "",
    "human_rounds_used": 0,
    "auto_revisions": 0,
    "revision_events": [],
    "finished": False,
    "pipeline_done": False,
}.items():
    st.session_state.setdefault(key, value)


pipeline = load_pipeline()

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">Bedtime AI Pipeline</div>
        <h1>Generate, judge, revise, and inspect every bedtime story run.</h1>
        <p>A dark, focused control surface for the full storytelling pipeline: request intake, story generation, LLM quality review, automatic repair, parent summary, human feedback, and session history.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

render_flow()

if not pipeline["available"]:
    st.error(f"Pipeline import failed: {pipeline['error']}")
    st.stop()


tab_generate, tab_history = st.tabs(["Generate", "History"])


with tab_generate:
    left, right = st.columns([0.95, 1.55], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="section-title">Story Request</div>', unsafe_allow_html=True)
            request = st.text_area(
                "Story request",
                placeholder="Example: a train called Tom who helps a lonely bird",
                label_visibility="collapsed",
                height=128,
            )
            st.caption(
                'Blank requests become "surprise me". The UI uses the exact gpt-3.5-turbo pipeline in main.py.'
            )
            generate = st.button("Run pipeline", use_container_width=True)

        st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="section-title">Current Run</div>', unsafe_allow_html=True)
            if st.session_state.pipeline_done:
                c1, c2 = st.columns(2)
                c1.metric("Words", word_count(st.session_state.story))
                c2.metric("Auto revisions", st.session_state.auto_revisions)
                st.metric("Feedback rounds", st.session_state.human_rounds_used)
                st.caption(st.session_state.original_request)
            else:
                st.caption("No active run yet.")

    if generate:
        reset_generation_state()
        user_request = request.strip() or "surprise me"
        st.session_state.original_request = user_request

        with right:
            with st.status("Running the pipeline...", expanded=True) as status:
                st.write("User Input -> Generation")
                st.write("Judge -> Revision if required, max two passes")
                story, judge_raw, auto_revisions = run_initial_pipeline_for_ui(
                    pipeline,
                    user_request,
                )

                st.write("Summary")
                summary = pipeline["summarize_story"](story)

                st.session_state.story = story
                st.session_state.judge_raw = judge_raw
                st.session_state.summary = summary
                st.session_state.auto_revisions = auto_revisions
                st.session_state.revision_events = build_auto_revision_events(auto_revisions)
                st.session_state.pipeline_done = True
                status.update(label="Pipeline complete.", state="complete")
        st.rerun()

    with right:
        if st.session_state.pipeline_done:
            top1, top2, top3 = st.columns(3)
            top1.metric("Final words", word_count(st.session_state.story))
            top2.metric("Judge verdict", parse_revision_needed(st.session_state.judge_raw))
            top3.metric("Human rounds left", MAX_HUMAN_ROUNDS - st.session_state.human_rounds_used)

            st.markdown('<div class="section-title">Final Story</div>', unsafe_allow_html=True)
            render_story(st.session_state.story)

            st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
            with st.expander("Quality review", expanded=True):
                render_judge(st.session_state.judge_raw)

            with st.expander("Revision log", expanded=False):
                render_revision_events()

            st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Parent Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="summary">{escape(st.session_state.summary)}</div>', unsafe_allow_html=True)

            if not st.session_state.finished and st.session_state.human_rounds_used < MAX_HUMAN_ROUNDS:
                st.markdown('<div class="section-title">Human Feedback</div>', unsafe_allow_html=True)
                feedback = st.text_input(
                    "Requested change",
                    placeholder="Example: make the ending calmer, but keep Tom as the main character",
                    label_visibility="collapsed",
                    key=f"feedback_{st.session_state.human_rounds_used}",
                )
                action_col, done_col = st.columns(2)
                with action_col:
                    apply_feedback = st.button("Apply feedback", use_container_width=True)
                with done_col:
                    keep_story = st.button("No feedback, keep current story", use_container_width=True)

                if keep_story:
                    st.session_state.finished = True
                    st.rerun()

                if apply_feedback and feedback.strip():
                    with st.status("Applying feedback...", expanded=True) as status:
                        st.write("Human Feedback -> Revise")
                        revised = pipeline["revise_story"](
                            st.session_state.story,
                            "HUMAN FEEDBACK:\n"
                            f"{feedback.strip()}\n\n"
                            "Apply only the requested changes. Preserve the existing story structure, "
                            "characters, title, and sleepy ending unless the feedback explicitly changes them.",
                        )
                        st.write("Judge")
                        needs_revision, judge_raw = pipeline["judge_story"](
                            st.session_state.original_request,
                            revised,
                        )
                        if needs_revision:
                            st.write("Auto-fix because judge required it")
                            revised = pipeline["revise_story"](revised, judge_raw)
                            _, judge_raw = pipeline["judge_story"](
                                st.session_state.original_request,
                                revised,
                            )
                        st.write("Refreshing the displayed summary.")
                        summary = pipeline["summarize_story"](revised)

                        st.session_state.story = revised
                        st.session_state.judge_raw = judge_raw
                        st.session_state.summary = summary
                        st.session_state.human_rounds_used += 1
                        add_revision_event(
                            "human",
                            f"Round {st.session_state.human_rounds_used}: {feedback.strip()}",
                        )
                        if needs_revision:
                            add_revision_event(
                                "auto",
                                "Judge requested an automatic repair after that human feedback round.",
                            )
                        status.update(label="Feedback applied.", state="complete")
                    st.rerun()
                elif apply_feedback:
                    st.warning("Type feedback first, or choose 'No feedback, keep current story'.")
            elif st.session_state.finished:
                st.success("Current story kept. No more feedback will be applied.")
            else:
                st.info("Maximum feedback rounds reached for this session.")
        else:
            with st.container(border=True):
                st.markdown('<div class="section-title">Preview</div>', unsafe_allow_html=True)
                st.caption(
                    "Run the pipeline to see the story, judge verdict, summary, and feedback controls here."
                )


with tab_history:
    logs = find_log_files()
    if not logs:
        st.info("No story logs found yet.")
    else:
        selected = st.selectbox(
            "Session log",
            logs,
            format_func=format_log_filename,
            label_visibility="collapsed",
        )
        session = parse_log_file(selected)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Request", session["user_request"][:28] + ("..." if len(session["user_request"]) > 28 else ""))
        m2.metric("Auto revisions", session["auto_revision_count"])
        m3.metric("Human rounds", session["human_round_count"])
        m4.metric("Final words", session["word_count"] or word_count(session["final_story"]))

        if session["summary"]:
            st.markdown(f'<div class="summary">{escape(session["summary"])}</div>', unsafe_allow_html=True)

        h1, h2, h3, h4 = st.tabs(["Generated", "Judge Reviews", "Revisions", "Final Story"])

        with h1:
            if session["generated_story"]:
                render_story(session["generated_story"])
            else:
                st.info("No generated story block found in this log.")

        with h2:
            if session["judge_reviews"]:
                for index, review in enumerate(session["judge_reviews"], start=1):
                    st.markdown(f'<div class="section-title">Review {index}</div>', unsafe_allow_html=True)
                    render_judge(review["reasoning"])
                    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
            else:
                st.info("No judge reviews found in this log.")

        with h3:
            if session["revisions"]:
                for index, revision in enumerate(session["revisions"], start=1):
                    label = "Human revision" if revision["type"] == "human" else "Auto revision"
                    st.markdown(f'<div class="section-title">{escape(label)} {index}</div>', unsafe_allow_html=True)
                    if revision["feedback"]:
                        st.markdown(
                            f"""
                            <div class="revision-note">
                                <div class="revision-label">Human feedback</div>
                                <p>{escape(revision["feedback"])}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    elif revision["type"] == "auto":
                        st.caption("Automatically revised because the judge required changes.")
                    render_story(revision["story"])
                    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
            else:
                st.info("No revisions in this session.")

        with h4:
            if session["final_story"]:
                render_story(session["final_story"])
            else:
                st.info("No final story available in this log.")
