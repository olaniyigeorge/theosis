# Theosis — AI Product Design Document

**A trustworthy AI-native Scripture platform where every claim is traceable back to biblical evidence.**

Version 1 · 4-week build · One shippable, user-facing AI feature per week

---

## How to read this document

This is not a traditional PRD. A traditional PRD answers *what are we building*. This document answers:

- Why does AI exist in this feature?
- What context does the AI receive, and where does it come from?
- How is the AI's output verified before a user ever sees it?
- Where does a human intervene, and what do they see when they do?
- How do we know, numerically, if this got better or worse this week?

Every week below is a **closed loop**: a real feature ships, a real person can use it, and you can point to evidence of whether it worked. Weeks are additive — Week 2 doesn't replace Week 1, it sits on top of it.

---

## 1. Vision

Theosis is a knowledge graph of Scripture where StorySlots, Beings, and their relationships are first-class, evidence-backed data — not prose generated on demand. AI's job in this system is narrow and specific: **propose structure, retrieve context, and compose language** — never to originate a scriptural claim without a human-reviewed citation behind it.

## 2. Product Principles (engineering constraints, not slogans)

| Principle | What it forces you to build |
|---|---|
| Evidence first | Every node/edge field that makes a claim needs a `scripture_refs` row before it can leave `draft` |
| AI proposes, humans approve | A `review_status` state machine that no AI-authored write can skip |
| Scripture is immutable | Text is never stored — only `(book, chapter, verse, translation)` tuples, resolved at read time |
| Relationships are explainable | Edges are rows with their own confidence and refs, not implicit foreign keys |
| Nothing is magic | Every AI-derived UI element shows its evidence, its confidence, and (on request) how it was produced |

## 3. Personas (who exercises which loop)

- **Explorer** — wants to wander the graph, low commitment. Primary user of Week 1 + Week 3 (Explore, Graph).
- **Seeker** — brings a real personal question or season of life. Primary user of Week 2 + Week 4 (Ask, Personal).
- **Student** — wants depth and citations they can check. Cross-cuts all weeks; the persona who will notice if you cut corners on grounding.
- **Reviewer (you, initially)** — the human in human-in-the-loop. Every week produces something a reviewer touches, even Week 1.

## 4. Product Scope — the four closed-loop features

1. **Explore StorySlots at multiple granularities** and see relationships between them, evidence-first.
2. **Ask Scripture** — free-text personal or theological questions, answered with graph-grounded, citation-verified responses.
3. **Find yourself in God's story** — Being Journey matching: given a user's stated season/circumstance, surface Beings whose scriptural journey structurally parallels it.
4. **AI Knowledge Curator** — the pipeline that keeps feeding StorySlots/Beings/edges into the graph via AI draft → human review → publish, now visible to the user as a "how this was verified" layer, plus production hardening (eval, observability, cost).

Deferred, not designed out: Place, Theme, Covenant, Kingdom, Prophecy node types; multi-user review; scholarly-position confidence UI; Hebrew/Greek source integration.

---

## 5. Knowledge Graph Model — the one decision that must land before Week 1 migrations

**Granularity for StorySlots.** To support "explore at different granularities," StorySlot needs an explicit hierarchy, not just a flat table of events.

Decision: add a self-referential edge type rather than a parent-column, so containment is queryable the same way every other relationship is, and so a StorySlot can (later) belong to more than one containing arc without a schema change.

- New `relationship_type` value: `part_of` (child StorySlot → parent StorySlot)
- New field in `data JSONB` for StorySlot nodes: `"granularity": "event" | "episode" | "arc" | "book"`
- Query pattern for "zoom out": traverse `part_of` edges upward; "zoom in": traverse downward.

This is a one-line addition to your existing `edges` table and `NodeType` — no architecture change, exactly the property you designed the schema for.

**Being Journey similarity** (needed Week 3): Beings need an embedding derived from their ordered sequence of StorySlot participations (via `present_at` / `leads` edges), not just from a text blurb. This reuses `embeddings_openai` / `embeddings_gemini` with `entity_type = NODE` — no new table.

---

## 6. AI Architecture (the spine every week hangs off)

```
User → Frontend → API → Context Builder → Prompt Builder → Retriever → LLM → Validator → Reviewer (if write) → Postgres → Frontend
```

Every box is independently testable and independently swappable. Week 1 builds the pipe with almost nothing flowing through the LLM box. Weeks 2–4 progressively load more of it up.

---

## Week 1 — Explore Scripture Graph

**AI engineering focus:** knowledge graph modeling, graph traversal APIs, FastAPI architecture, deterministic-over-AI judgment.

**Feature shipped:** users browse StorySlots and Beings at multiple granularities, see relationship edges with their scripture references, zoom in/out via `part_of` traversal.

**Where AI is (and isn't):** Nowhere in the read path. This week's discipline is knowing when *not* to reach for AI — graph traversal is a deterministic query, and using an LLM to "summarize the graph" here would be an unearned risk for zero benefit. AI's only role this week is offline: seeding the initial graph (Genesis–Exodus) via `/ai/draft`, reviewed by you before publish.

**Context engineering:** N/A for the read path — the "context" is just the graph itself. For the seeding drafts: topic string → retrieved scripture text for the target passage range → prompt → structured JSON matching `NodeType`/`Edge` schema.

**Data touched:** `nodes`, `edges`, `scripture_refs`, `reviews` (all four tables exist and are populated for the first time).

**Evaluation (what you check before calling it shipped):**
- Every published edge has ≥1 validated `scripture_refs` row — a query, not a vibe check.
- Traversal query for `part_of` returns correct ancestor/descendant sets on a hand-built test fixture (Moses → Exodus → Pentateuch).

**Definition of shipped:** you can hand someone a link, they can click from Moses → The Exodus → an ancestor StorySlot, and every edge they hover shows a real chapter:verse.

---

## Week 2 — Ask Scripture

**AI engineering focus:** RAG, semantic + graph-hybrid retrieval, context engineering, citation validation.

**Feature shipped:** free-text question box. Answer is composed from retrieved graph nodes + scripture text, every claim citation-checked before display.

**Where AI is:** two calls, matching the two-LLM-call grounding pattern already in your memory — (1) given the question + retrieved graph context, suggest candidate scripture references; (2) given verified references only, compose the answer. Unverified references are dropped silently, never surfaced.

**Context engineering — the explicit contract:**
- **Inputs:** user question (raw text)
- **Retrieval:** semantic search over node embeddings (top-k StorySlots/Beings) + 1-hop graph neighbors of the top hit, so the model gets relational context, not just a bag of similar nodes
- **Memory:** none yet (single-turn this week — multi-turn is a Week 4+ stretch, not required for the loop to close)
- **Prompt:** question + retrieved node summaries + their scripture refs, explicit instruction to cite only from what's provided
- **Output:** structured JSON — answer text + list of `(book, chapter, verse)` used
- **Validation:** every cited ref re-checked against `BibleProvider`; refs that fail are stripped before the second LLM call composes final prose

**Data touched:** reuses `embeddings_openai`/`embeddings_gemini`, `scripture_refs`. No new tables.

**Evaluation:** build a 20–30 question benchmark set by hand now (you'll grow it in Week 4) with expected-citation ranges. Track: citation accuracy (cited ref is real and relevant), % of drafted refs that survive validation, latency, cost per question.

**Definition of shipped:** a Student persona can ask a real theological question and get back an answer where every citation, clicked, actually says what the answer claims it says.

---

## Week 3 — AI Knowledge Curator + Being Journey

**AI engineering focus:** tool calling, structured output validation with retry-repair, human-in-the-loop workflow, similarity-based retrieval.

**Feature shipped (two tightly linked pieces, ship together):**
1. **Review dashboard** — reviewer sees AI-drafted nodes/edges with evidence, confidence, and reasoning summary; can approve / reject / edit; every action logged to `reviews`.
2. **"Find yourself"** — user describes a season/circumstance in free text; system surfaces Beings whose journey (sequence of StorySlots) structurally parallels it, each with the specific scripture that makes the parallel legible — not a vibe match, a graph-grounded one.

**Where AI is:** the curator side already exists in your architecture (`AIDraftService`, `generate_structured` with `MAX_STRUCTURED_ATTEMPTS = 2` retry-repair) — this week is exposing it as a *visible workflow* rather than a backend job, plus adding the Being-Journey embedding + retrieval path.

**Context engineering for Being Journey:**
- **Inputs:** user's free-text description of their season
- **Retrieval:** embed the input, cosine-search against Being journey embeddings (built from each Being's ordered StorySlot sequence)
- **Prompt:** top matches + their actual edges/refs → LLM asked only to *narrate the parallel in the user's terms*, not to invent new correspondences
- **Validation:** the parallel must resolve to real edges the Being actually has — the LLM cannot introduce a StorySlot the Being wasn't `present_at`

**Data touched:** `embeddings_*` (new embedding source: journey sequences, not blurbs), `reviews` (now user-visible), no schema change beyond what Week 1 already added.

**Evaluation:** approval rate (% of AI drafts approved without edit) as a leading indicator of prompt quality; time-to-review; for Being Journey, a small hand-labeled set of "does this parallel actually hold" judgments.

**Definition of shipped:** you can review and publish a new node from the dashboard without touching a database client, and a Seeker persona can type "I feel like I'm in exile" and get back a real Being with real citations, not a generic devotional paragraph.

---

## Week 4 — Production-grade Theosis

**AI engineering focus:** evaluation pipelines, observability, cost engineering, security, deployment.

**Feature shipped:** everything from Weeks 1–3, now with visible trust signals and the operational floor under it — this is the week the *product*, not just a feature, ships.

**Where AI is:** no new AI capability required to satisfy the loop — the discipline this week is entirely about making the existing three AI features measurable, debuggable, and safe to leave running unattended. If time allows, this is where a lightweight conversation memory for Ask Scripture is a reasonable stretch, but it is explicitly optional against the loop.

**What "closes the loop" this week:**
- **Evaluation:** grow the Week 2 benchmark to ~100 questions; add a Week 3 curator benchmark (expected node/edge/citation output per topic); every prompt change from now on is measured against both before merge.
- **Observability:** every LLM call logs prompt version, model, tokens, latency, cost, retrieved context, and validation pass/fail — queryable, not just console output.
- **Cost engineering:** per-request cost tracked for Ask Scripture and Curator drafts; a visible monthly-projection number, not a surprise.
- **Security:** prompt-injection resistance check on Ask Scripture (a retrieved node summary shouldn't be able to make the model ignore its instructions), rate limits, reviewer-only permissions on approve/publish endpoints.
- **User-facing trust layer:** confidence and "verified" badges surfaced wherever AI touched an answer — this is Product Principle 3 ("nothing is magic") finally made visible end to end.

**Data touched:** a lightweight `ai_call_logs` table (prompt version, model, tokens, cost, latency, validation result) — the one new table this whole build needs.

**Evaluation:** the eval *is* the deliverable this week — a runnable script against both benchmark sets that outputs a scorecard.

**Definition of shipped:** you can run one command, get a scorecard for both AI features, look at a log for any given answer and see exactly what it retrieved and what it cost, and the public beta is live behind rate limits.

---

## 7. Cross-cutting build order (why weeks are sequenced this way)

Retrieval (Week 2) depends on nodes existing (Week 1). Curation UI (Week 3) depends on the draft pipeline already existing in your backend, so it's mostly surfacing, not building from scratch. Evaluation (Week 4) depends on having two live AI features worth benchmarking — you cannot meaningfully evaluate what doesn't exist yet. Each week's feature is real and closed-loop on its own; nothing here is a throwaway scaffold you rebuild later.

## 8. What you will have practiced, end to end

Knowledge graph modeling · deterministic-vs-AI judgment · RAG and hybrid retrieval · context engineering as an explicit contract · structured output + retry-repair validation · citation/groundedness checking · human-in-the-loop review workflow · embedding-based similarity beyond text · evaluation benchmark design · observability logging · cost tracking · prompt-injection-aware security · production deployment under rate limits.