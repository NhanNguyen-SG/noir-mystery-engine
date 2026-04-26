from dotenv import load_dotenv
load_dotenv()

from shiny import App, ui, render, reactive
from src.agents.detective import investigate
from src.agents.witness import retrieve_context
from src.agents.narrator import narrate
from src.tools.clue_scorer import score_clues
from src.agents.orchestrator import OrchestratorOutput

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style("""
        /* ── Reset & base ─────────────────────────────────────────────── */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background: #0d0d0d;
            color: #e8e0d0;
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 16px;
            line-height: 1.6;
            min-height: 100vh;
        }

        /* ── Header ───────────────────────────────────────────────────── */
        .noir-header {
            text-align: center;
            padding: 36px 20px 24px;
            background: linear-gradient(180deg, #1a1008 0%, #0d0d0d 100%);
            border-bottom: 1px solid #3a2e1a;
        }
        .noir-title {
            font-size: 2.6rem;
            letter-spacing: 6px;
            color: #f0c040;
            text-shadow: 0 0 30px #c9a84c99, 0 2px 4px #000;
            font-weight: normal;
        }
        .noir-subtitle {
            font-size: 0.85rem;
            letter-spacing: 3px;
            color: #7a6a50;
            margin-top: 6px;
            text-transform: uppercase;
        }

        /* ── Sidebar ──────────────────────────────────────────────────── */
        .bslib-sidebar-layout > .sidebar {
            background: #111008 !important;
            border-right: 1px solid #2a2010 !important;
            padding: 24px 20px !important;
        }

        .scene-label {
            display: block;
            color: #c9a84c;
            font-size: 0.75rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        textarea.form-control {
            background: #0a0a0a !important;
            color: #e8e0d0 !important;
            border: 1px solid #3a2e1a !important;
            border-radius: 4px;
            font-family: 'Georgia', serif;
            font-size: 0.92rem;
            line-height: 1.65;
            padding: 12px 14px;
            resize: vertical;
        }
        textarea.form-control:focus {
            border-color: #c9a84c !important;
            outline: none !important;
            box-shadow: 0 0 0 2px #c9a84c22 !important;
        }
        textarea.form-control::placeholder {
            color: #4a3e28 !important;
            font-style: italic;
        }

        .btn-noir {
            display: block;
            width: 100%;
            margin-top: 16px;
            padding: 13px 16px;
            background: #c9a84c;
            color: #0d0d0d;
            font-family: 'Georgia', serif;
            font-size: 0.85rem;
            font-weight: bold;
            letter-spacing: 3px;
            text-transform: uppercase;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
        }
        .btn-noir:hover:not(:disabled) {
            background: #e0c060;
            transform: translateY(-1px);
        }
        .btn-noir:disabled { opacity: 0.5; cursor: not-allowed; }

        /* ── Step feed ────────────────────────────────────────────────── */
        .step-feed {
            margin-top: 24px;
            border-top: 1px solid #2a2010;
            padding-top: 16px;
        }
        .step-feed-title {
            font-size: 0.7rem;
            letter-spacing: 2px;
            color: #5a4a30;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .step {
            display: flex;
            gap: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #1e1a10;
        }
        .step:last-child { border-bottom: none; }
        .step-icon { font-size: 1rem; width: 22px; flex-shrink: 0; padding-top: 1px; }
        .step-body { flex: 1; min-width: 0; }
        .step-name {
            font-size: 0.8rem;
            font-weight: bold;
            letter-spacing: 1px;
            color: #c9a84c;
        }
        .step-msg {
            font-size: 0.8rem;
            color: #9a8a70;
            margin-top: 1px;
        }

        /* state colours */
        .step-running  .step-name { color: #60a5fa; }
        .step-running  .step-msg  { animation: flicker 1.6s ease-in-out infinite; }
        .step-complete .step-name::after { content: "  ✓"; color: #4ade80; font-weight: normal; font-size: 0.75rem; }
        .step-error    .step-name::after { content: "  ✗"; color: #f87171; font-weight: normal; font-size: 0.75rem; }

        @keyframes flicker { 0%,100%{opacity:1} 50%{opacity:0.45} }

        /* ── Main panel ───────────────────────────────────────────────── */
        .bslib-sidebar-layout > .main {
            background: #0d0d0d;
            padding: 28px 32px !important;
        }

        .placeholder-msg {
            margin-top: 100px;
            text-align: center;
            color: #3a3020;
            font-style: italic;
            font-size: 1rem;
            letter-spacing: 1px;
        }

        /* ── Story card ───────────────────────────────────────────────── */
        .story-card {
            background: #111008;
            border: 1px solid #2a2010;
            border-top: 3px solid #c9a84c;
            border-radius: 4px;
            padding: 28px 32px;
        }
        .story-title {
            font-size: 1.7rem;
            color: #f0c040;
            font-style: italic;
            font-weight: normal;
            margin-bottom: 20px;
            line-height: 1.3;
        }

        /* meta grid */
        .meta-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 24px;
        }
        .meta-cell {
            background: #0a0a0a;
            border-left: 3px solid #3a2e1a;
            border-radius: 3px;
            padding: 10px 14px;
        }
        .meta-cell-label {
            font-size: 0.68rem;
            letter-spacing: 2px;
            color: #5a4a30;
            text-transform: uppercase;
        }
        .meta-cell-value {
            font-size: 0.95rem;
            color: #e8e0d0;
            margin-top: 3px;
        }

        /* story body */
        .section-rule { border: none; border-top: 1px solid #2a2010; margin: 22px 0; }
        .section-label {
            font-size: 0.7rem;
            letter-spacing: 3px;
            color: #5a4a30;
            text-transform: uppercase;
            margin-bottom: 14px;
        }
        .story-body {
            font-size: 1rem;
            color: #d8d0c0;
            line-height: 1.95;
            white-space: pre-wrap;
        }

        /* verdict */
        .verdict-box {
            margin-top: 22px;
            padding: 14px 18px;
            background: #0a0a0a;
            border-left: 4px solid #c9a84c;
            border-radius: 3px;
        }
        .verdict-label {
            font-size: 0.68rem;
            letter-spacing: 2px;
            color: #5a4a30;
            text-transform: uppercase;
        }
        .verdict-text {
            font-size: 1rem;
            color: #f0c040;
            font-style: italic;
            margin-top: 5px;
            line-height: 1.5;
        }

        /* error */
        .error-box {
            margin-top: 14px;
            padding: 12px 16px;
            background: #160808;
            border: 1px solid #5a1010;
            border-radius: 4px;
            color: #f87171;
            font-size: 0.85rem;
        }
        """)
    ),

    # Header
    ui.div(
        ui.tags.h1("🎩  NOIR MYSTERY ENGINE", class_="noir-title"),
        ui.tags.p("WHERE EVERY CRIME SCENE TELLS A STORY", class_="noir-subtitle"),
        class_="noir-header",
    ),

    ui.layout_sidebar(
        ui.sidebar(
            ui.tags.span("Describe the crime scene:", class_="scene-label"),
            ui.input_text_area(
                "scene",
                label=None,
                placeholder=(
                    "A wealthy banker was found dead in his locked study\n"
                    "at midnight. The window was open despite the rain.\n"
                    "A half-empty glass of whiskey sat on the desk next\n"
                    "to a torn letter…"
                ),
                height="260px",
                width="100%",
            ),
            ui.input_action_button("run_btn", "🔍  Begin Investigation", class_="btn-noir"),
            ui.output_ui("error_ui"),
            ui.output_ui("steps_ui"),
            bg="#111008",
            width=330,
        ),
        ui.output_ui("results_ui"),
    ),
)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

def server(input, output, session):
    steps      = reactive.value([])
    result_val = reactive.value(None)
    loading    = reactive.value(False)
    error_val  = reactive.value(None)

    # ── helpers ──────────────────────────────────────────────────────────
    def add_step(icon, name, msg):
        s = list(steps.get())
        s.append({"icon": icon, "name": name, "msg": msg, "status": "running"})
        steps.set(s)

    def finish_step(index, msg, ok=True):
        s = list(steps.get())
        if index < len(s):
            s[index] = {**s[index], "status": "complete" if ok else "error", "msg": msg}
            steps.set(s)

    # ── main async handler ────────────────────────────────────────────────
    @reactive.effect
    @reactive.event(input.run_btn)
    async def do_investigation():
        scene = input.scene().strip()
        if not scene:
            return

        loading.set(True)
        steps.set([])
        result_val.set(None)
        error_val.set(None)

        try:
            # ── Step 0: Detective ────────────────────────────────────────
            add_step("🔍", "Detective", "Examining the crime scene for physical evidence…")
            clues = await investigate(scene)
            finish_step(0, f"Found {len(clues.clues)} clues — suspect: {clues.prime_suspect}")

            # ── Step 1: Witness ──────────────────────────────────────────
            add_step("📚", "Witness", "Searching the noir archive for similar cases…")
            clue_text = " ".join(c.description for c in clues.clues)
            witness_findings = await retrieve_context(clue_text)
            finish_step(1, f"Retrieved {len(witness_findings.passages)} relevant passages")

            # ── Step 2: Analyst ──────────────────────────────────────────
            add_step("📋", "Analyst", "Weighing the evidence by importance…")
            scored = score_clues([c.description for c in clues.clues])
            top = scored[0] if scored else None
            finish_step(2, f"Top clue scored {top.score}/10" if top else "No clues to rank")

            # ── Step 3: Narrator ─────────────────────────────────────────
            add_step("✍️", "Narrator", "Writing the noir story…")
            story = await narrate(scene, clues, witness_findings)
            finish_step(3, f'Wrote "{story.title}"')

            result_val.set(OrchestratorOutput(
                story=story,
                clues_found=len(clues.clues),
                top_clue=top.description if top else "none",
                prime_suspect=clues.prime_suspect,
            ))

        except Exception as e:
            error_val.set(str(e))
            s = list(steps.get())
            for i in reversed(range(len(s))):
                if s[i]["status"] == "running":
                    s[i]["status"] = "error"
                    break
            steps.set(s)
        finally:
            loading.set(False)

    # ── outputs ───────────────────────────────────────────────────────────
    @output
    @render.ui
    def error_ui():
        err = error_val()
        if err:
            return ui.div(f"⚠️  {err}", class_="error-box")
        return ui.div()

    @output
    @render.ui
    def steps_ui():
        current = steps.get()
        if not current:
            return ui.div()

        rows = []
        for step in current:
            rows.append(
                ui.div(
                    ui.div(step["icon"], class_="step-icon"),
                    ui.div(
                        ui.div(step["name"], class_="step-name"),
                        ui.div(step["msg"],  class_="step-msg"),
                        class_="step-body",
                    ),
                    class_=f"step step-{step['status']}",
                )
            )

        return ui.div(
            ui.div("Agent Activity", class_="step-feed-title"),
            *rows,
            class_="step-feed",
        )

    @output
    @render.ui
    def results_ui():
        r = result_val()

        if r is None:
            if not loading() and not steps.get():
                return ui.div(
                    "Enter a crime scene and begin the investigation.",
                    class_="placeholder-msg",
                )
            return ui.div()

        return ui.div(
            ui.div(
                ui.tags.h2(f'"{r.story.title}"', class_="story-title"),

                ui.div(
                    ui.div(
                        ui.div("Setting",       class_="meta-cell-label"),
                        ui.div(r.story.setting, class_="meta-cell-value"),
                        class_="meta-cell",
                    ),
                    ui.div(
                        ui.div("Prime Suspect", class_="meta-cell-label"),
                        ui.div(r.prime_suspect, class_="meta-cell-value"),
                        class_="meta-cell",
                    ),
                    ui.div(
                        ui.div("Top Clue",  class_="meta-cell-label"),
                        ui.div(r.top_clue,  class_="meta-cell-value"),
                        class_="meta-cell",
                    ),
                    ui.div(
                        ui.div("Clues Found",       class_="meta-cell-label"),
                        ui.div(str(r.clues_found),  class_="meta-cell-value"),
                        class_="meta-cell",
                    ),
                    class_="meta-grid",
                ),

                ui.tags.hr(class_="section-rule"),
                ui.div("The Story", class_="section-label"),
                ui.tags.p(r.story.full_story, class_="story-body"),

                ui.div(
                    ui.div("Verdict",         class_="verdict-label"),
                    ui.div(r.story.verdict,   class_="verdict-text"),
                    class_="verdict-box",
                ),
                class_="story-card",
            ),
        )


app = App(app_ui, server)
