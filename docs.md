# Theosis — Engineering Docs (MVP, 2-Week Build)

Stack locked in: **Python (FastAPI) + Postgres/pgvector + Next.js/React**. Dev on Vercel + Railway/Render, prod later on GCP or AWS. This doc translates the PRD into a buildable system and a day-by-day plan.

---

## 1. What We're Actually Building in 2 Weeks

The PRD describes a huge ontology (StorySlot, Being, Place, Theme, Event, Covenant, Kingdom, Prophecy, Relationships, multiple reading modes, AI review pipeline, chronology models...). None of that is buildable in 2 weeks as a polished product. The move is: **build the graph engine generically enough that every future entity type is just data, not new architecture** — then seed it with a thin vertical slice.

### MVP Scope (in)
- Two entity types: **StorySlot** and **Being** (covers "Exodus," "Noah's Flood," "Moses," "God," etc.)
- **Relationships** as first-class edges (e.g. `Moses --leads--> Exodus`, `David --father_of--> Solomon`)
- Scripture references pulled from a Bible API, never stored as text
- One reading mode: **Being Journey** (follow a person through Scripture) — it's the most demo-able and viral-on-LinkedIn feature
- One visualization: interactive **Knowledge Graph** view (React Flow) + a simple **Timeline** strip
- AI draft → human review → publish pipeline, but with **you as the only reviewer** (no multi-user review UI yet)
- Basic keyword + semantic search over StorySlots/Beings

### Explicitly Out (v2+)
- Place, Theme, Covenant, Kingdom, Prophecy entities (schema supports them day 1, UI doesn't expose them yet)
- Multiple chronology models, confidence scholarly-position UI
- Multi-user review workflows, public contributions
- Hebrew/Greek integration, archaeological context

This is the difference between "comprehensive Scripture Knowledge Graph" (the vision) and "provable, postable, extensible core" (the 2-week deliverable).

---

## 2. Architecture

```
┌─────────────────┐      ┌──────────────────────┐      ┌─────────────────┐
│   Next.js App    │◄────►│   FastAPI Backend     │◄────►│   Postgres +     │
│  (Vercel)         │      │  (Railway/Render)      │      │   pgvector        │
│  - Graph viz       │      │  - REST/GraphQL-ish API │      │   (nodes, edges,  │
│  - Being Journey    │      │  - AI pipeline routes   │      │    scripture refs)│
│  - Search UI         │      │  - Review workflow       │      └─────────────────┘
└─────────────────┘      └──────────┬───────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │ External Bible API │
                                │ (API.Bible / ESV /   │
                                │  bible-api.com)        │
                                └──────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │  Claude API (drafts, │
                                │  embeddings, tagging) │
                                └──────────────────┘
```

Key principle carried from the PRD: **Scripture text is never stored in your DB.** You store `(book, chapter, verse_start, verse_end, translation, provider_ref)` tuples and resolve display text at read time via the Bible API (with a thin cache layer — Redis or just a Postgres cache table — so you're not hammering the external API).

---

## 3. Data Model (Postgres, graph-ish, pgvector-ready)

The generic node/edge pattern is what makes "every future feature = new projection, not new architecture" actually true.

```sql
-- Generic node table. `type` discriminates entity kind; `data` holds
-- type-specific fields so you don't need a new table per entity type.
CREATE TABLE nodes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type            TEXT NOT NULL CHECK (type IN
                        ('story_slot','being','place','theme','event',
                         'covenant','kingdom','prophecy')),
    title           TEXT NOT NULL,
    slug            TEXT UNIQUE NOT NULL,
    description     TEXT,
    data            JSONB NOT NULL DEFAULT '{}',   -- type-specific properties
    parent_id       UUID REFERENCES nodes(id),      -- for StorySlot hierarchy
    granularity_lvl INT,
    confidence      TEXT DEFAULT 'unknown' CHECK (confidence IN
                        ('confirmed','strong','moderate','weak',
                         'approximate','multiple_positions','unknown','under_review')),
    review_status   TEXT DEFAULT 'draft' CHECK (review_status IN
                        ('draft','in_review','approved','published')),
    embedding       VECTOR(1536),                   -- pgvector, for semantic search
    version         INT NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Relationships as first-class, richly-annotated edges — not FKs.
CREATE TABLE edges (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id           UUID NOT NULL REFERENCES nodes(id),
    target_id           UUID NOT NULL REFERENCES nodes(id),
    relationship_type   TEXT NOT NULL,   -- 'before','father_of','fulfills', etc.
    notes               TEXT,
    confidence          TEXT DEFAULT 'unknown',
    review_status       TEXT DEFAULT 'draft',
    version             INT NOT NULL DEFAULT 1,
    created_at          TIMESTAMPTZ DEFAULT now()
);

-- Every claim (node or edge) must point back to Scripture. This table
-- is the enforcement mechanism for "where is this supported in Scripture?"
CREATE TABLE scripture_refs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type     TEXT NOT NULL CHECK (entity_type IN ('node','edge')),
    entity_id       UUID NOT NULL,
    book            TEXT NOT NULL,
    chapter_start   INT NOT NULL,
    verse_start     INT,
    chapter_end     INT,
    verse_end       INT,
    translation     TEXT DEFAULT 'ESV',
    provider_ref    TEXT   -- opaque ref/URI from the Bible API provider
);

-- Review/audit trail for the AI -> Draft -> Reviewer -> Approved -> Published flow.
CREATE TABLE reviews (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type     TEXT NOT NULL CHECK (entity_type IN ('node','edge')),
    entity_id       UUID NOT NULL,
    status          TEXT NOT NULL,   -- mirrors review_status transitions
    reviewer        TEXT,            -- you, for now
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_nodes_type ON nodes(type);
CREATE INDEX idx_nodes_embedding ON nodes USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_edges_source ON edges(source_id);
CREATE INDEX idx_edges_target ON edges(target_id);
CREATE INDEX idx_scripture_entity ON scripture_refs(entity_type, entity_id);
```

**Why this shape:**
- Single `nodes` table with a `type` discriminator + `data JSONB` means adding Place, Theme, Covenant etc. later is a migration-free product decision, not a schema rewrite.
- `edges` as its own table (not FKs on `nodes`) is what makes relationships queryable, annotatable, and reviewable — matches the PRD's "relationships are first-class entities."
- `scripture_refs` is polymorphic over `(entity_type, entity_id)` so both nodes and edges are always traceable to text.
- pgvector lives directly on `nodes.embedding` — no separate vector DB needed at this scale. If graph traversal (multi-hop queries like "every king warned by a prophet") gets slow on recursive CTEs, that's your Neo4j migration trigger — not before.

---

## 4. Backend (FastAPI)

```
/app
  /models          # SQLAlchemy models (Node, Edge, ScriptureRef, Review)
  /schemas          # Pydantic request/response models
  /routers
    nodes.py         # CRUD + list/filter by type
    edges.py          # CRUD, traversal queries
    scripture.py        # Bible API proxy + cache
    search.py             # keyword + pgvector semantic search
    ai.py                   # draft generation, review workflow
  /services
    bible_provider.py     # abstraction over API.Bible/ESV/bible-api.com
    embeddings.py           # Claude/OpenAI embedding calls
    ai_drafts.py              # AI Story Slot / relationship generation
  /tasks
    scheduler.py        # cron/interval registration
    scan_gaps.py          # queries DB for underdeveloped areas of the graph
    generate.py              # calls ai_drafts service to fill identified gaps
    run_log.py                 # tracks what a task run touched, to avoid dup work  
  /db.py              # SQLAlchemy engine/session
  main.py
```

Minimum viable endpoints:
- `GET /nodes?type=being&search=moses`
- `GET /nodes/{id}` (includes edges + scripture_refs, expanded)
- `POST /nodes` (draft creation, review_status=draft)
- `GET /nodes/{id}/journey` — traversal for "Being Journey" mode, ordered by linked StorySlot chronology
- `POST /ai/draft` — given a topic, Claude proposes a StorySlot/Being + relationships + scripture refs, saved as draft
- `POST /reviews/{entity_id}/approve` — draft → published

Use **SQLAlchemy 2.0 (async) + asyncpg + Alembic** for migrations. Keep the Bible API behind a cache table (`scripture_cache(provider_ref, translation, text, fetched_at)`) so you're not rate-limited during demos.

---

## 5. Frontend (Next.js)

- **App Router**, Tailwind, TanStack Query for data fetching
- **React Flow** for the Knowledge Graph visualization (fastest path to an interactive node-graph; Cytoscape.js is the fallback if you need more graph-algorithm power)
- Pages: `/` (search/landing), `/being/[slug]` (Being Journey), `/story/[slug]` (StorySlot detail w/ scripture text pulled live), `/graph` (full graph explorer)
- Auth: skip for MVP unless you want a private admin/review view — if so, simplest is Clerk or just a hardcoded admin token for your own review actions

---

## 6. AI Workflow (matches PRD's Draft → Reviewer → Approved → Published)

1. You (or a script) call `POST /ai/draft` with a seed ("Moses," "The Exodus").
2. Claude generates a structured JSON draft: node fields + candidate scripture refs + candidate relationships, using tool-forced JSON output.
3. Draft is inserted with `review_status='draft'`.
4. You review in a simple admin list (`/admin/review`) — approve, edit, or reject.
5. Approve flips `review_status='published'` and logs a `reviews` row.

Keep the AI prompt strict: force it to cite `(book, chapter, verse)` for every claim, since that's the non-negotiable PRD principle ("every claim must answer: where is this supported in Scripture").

---

## 7. Two-Week Plan

**Week 1 — Core graph engine + data**
- Day 1: Repo scaffold (FastAPI + Next.js monorepo or two repos), Postgres on Railway/Render w/ pgvector enabled, Alembic migration for schema above
- Day 2: Node/Edge/ScriptureRef CRUD endpoints + Pydantic schemas
- Day 3: Bible API integration + cache table (pick API.Bible or bible-api.com — API.Bible has more translations, bible-api.com is zero-friction to start)
- Day 4: AI draft pipeline (`/ai/draft`) — seed 10-15 Beings and StorySlots (Genesis–Exodus range is a good demo slice)
- Day 5: Review endpoints + minimal admin UI to approve drafts
- Weekend: seed ~30-50 nodes + edges by running the AI pipeline across a curated list, review/approve them yourself

**Week 2 — Frontend + polish + launch**
- Day 6-7: Next.js scaffold, `/being/[slug]` Being Journey page, live scripture text rendering
- Day 8-9: React Flow graph explorer (`/graph`) — clickable nodes, filter by type
- Day 10: Search (keyword first, pgvector semantic search second)
- Day 11: Timeline strip view for a StorySlot's chronology
- Day 12: Deploy — Vercel (frontend), Railway/Render (backend+db)
- Day 13-14: Bug bash, seed a compelling demo path (e.g. full "Moses" Being Journey from birth to death, fully linked), record a demo video, prep launch posts

---

## 8. Build-in-Public Content Plan (LinkedIn/Twitter)

Post the *decisions*, not just the progress — engineering audiences engage more with reasoning than screenshots.

| Day | Post angle |
|---|---|
| 1 | "Why I'm not storing the Bible in my database" — the immutable-source-of-truth architecture decision |
| 3 | Nodes/edges as a generic graph in Postgres vs. reaching for Neo4j on day 1 — the pgvector + Postgres bet |
| 4-5 | AI-generated content that isn't allowed to be canonical — the Draft → Review → Publish pipeline and why every claim needs a citation |
| 7 | First working Being Journey demo (Moses) — screen recording |
| 9 | Graph explorer demo — React Flow screenshots |
| 11 | "Representing uncertainty" — showing confidence levels in the UI, why approximation beats false certainty |
| 14 | Launch post: what Theosis is, what it isn't, link to live demo |

Bonus thread ideas: "the ontology I chose NOT to build in week 1 and why," "what building a knowledge graph on top of an immutable, 2000-year-old text teaches you about schema design."

---

## 9. Open Decisions to Make Before Day 1

- **Bible API provider**: API.Bible (more translations, needs API key + usage limits) vs. bible-api.com (free, WEB translation only, zero setup). Recommend bible-api.com for week 1 speed, swap later.
- **Embeddings provider**: Claude doesn't currently expose a standalone embeddings endpoint — you'll likely want OpenAI's `text-embedding-3-small` or Voyage AI (Anthropic's recommended embeddings partner) for the `nodes.embedding` column.
- **Admin auth**: hardcoded token vs. real auth — hardcoded is fine for a 2-week solo build.