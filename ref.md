# Theosis

> **Discover your place in God's unfolding story.**

---

# Vision

Theosis is a Scripture Knowledge Graph that helps believers understand God's Word through multiple interconnected lenses while remaining grounded in a single, immutable source of truth: **the Bible**.

Rather than functioning as another Bible application, Theosis is a layer **built on top of Scripture** that organizes knowledge extracted from it into timelines, beings, themes, covenants, prophecies, relationships, and historical contexts.

The goal is not simply to help users know the Bible better, but to help them understand God's unfolding redemptive story, discern patterns throughout Scripture, discover their place within that story, and faithfully respond to God's calling.

---

# Mission

To build the world's most comprehensive Scripture Knowledge Graph that enables believers to explore, reason through, and discover Scripture while remaining completely grounded in the biblical text.

---

# Core Philosophy

## Scripture Alone is the Source of Truth

Everything in Theosis ultimately traces back to one source:

> **The Bible.**

Theosis does **not** replace Scripture.

It does **not** become another Bible translation.

Instead, Scripture is referenced from supported Bible providers/APIs while every other piece of information inside the platform is derived from, linked back to, and reviewable against Scripture.

Nothing exists independently from its Scriptural foundation.

---

# Fundamental Principle

The biblical text is immutable.

Everything else is metadata.

This includes:

- Story Slots
- Timelines
- Chronologies
- Themes
- Teachings
- Relationships
- Being Profiles
- Historical Dating
- Interpretations
- Prophecy Links
- Fulfillment Links
- Genealogies
- Reading Paths
- AI Generated Insights

These are all **derived knowledge layers** that must always reference the underlying biblical text.

---

# Product Goals

Enable believers to:

- Understand the Bible chronologically.
- Explore Scripture through multiple perspectives.
- Follow individual beings throughout Scripture.
- Understand historical context.
- Compare themes across Scripture.
- Study prophecy and fulfillment.
- Explore biblical relationships.
- Discover recurring biblical patterns.
- Build personal study journeys.
- Compare scholarly viewpoints.
- Discover God's redemptive narrative from Genesis to Revelation.

---

# Non-Goals

Theosis is **not**:

- A Bible translation.
- A Bible reader.
- A devotional platform.
- A commentary replacing Scripture.

Those experiences may exist around the platform, but the platform itself is fundamentally a **Scripture Knowledge Graph**.

---

# Single Source of Truth

Theosis intentionally does **not** model:

- Books
- Chapters
- Verses
- Biblical text

as primary database entities.

Instead, those are referenced through supported Bible APIs and providers.

Every derived object stores references back to Scripture.

Example:

```
Story Slot
    ↓

Genesis 6–9

Exodus 12

Matthew 26

Hebrews 11
```

Every claim inside the system should ultimately answer:

> **"Where is this supported in Scripture?"**

---

# Core Architecture

The system is built around a graph.

Every node and relationship ultimately points back to Scripture.

```
            Scripture
                │
                ▼
        Knowledge Graph
                │
 ┌──────────────┼──────────────┐
 ▼              ▼              ▼
Timeline     Study Views   Knowledge Graph
```

---

# First-Class Entities

Theosis intentionally keeps its ontology small.

These become the foundational graph nodes.

## StorySlot

Represents an identifiable portion of Scripture.

Examples:

- Creation
- Fall
- Noah's Flood
- Abraham's Call
- Ten Plagues
- The Exodus
- Sermon on the Mount
- Crucifixion
- Pentecost

Story Slots become one of the central entities in the graph.

---

## Being

Represents every intelligent being mentioned or inferred within Scripture.

Examples:

- God
- Father
- Son
- Holy Spirit
- Angels
- Cherubim
- Seraphim
- Satan
- Demons
- Humans

This intentionally replaces the earlier "Person" model.

Every Being can participate in Story Slots and relationships regardless of its nature.

Possible properties:

- Identity
- Names
- Aliases
- Nature
- Description
- Roles
- Timeline Participation
- Story Slots
- Relationships
- Commands Given
- Commands Received
- Speeches
- Themes
- Covenants
- Prophecies
- Fulfillments
- Supporting Scripture

---

## Place

Examples:

- Eden
- Egypt
- Jerusalem
- Babylon
- Sinai

Properties include:

- Name
- Alternate Names
- Geographic Metadata
- Story Slots
- Associated Beings
- Themes
- Supporting Scripture

---

## Theme

Examples:

- Faith
- Grace
- Kingdom
- Covenant
- Prayer
- Holiness
- Redemption
- Intercession

Themes connect Story Slots, Beings, Events, Prophecies, and Teachings.

---

## Event

Represents significant happenings that may span or exist within Story Slots.

Examples:

- Creation
- Fall
- Flood
- Resurrection
- Pentecost

---

## Covenant

Examples:

- Noahic Covenant
- Abrahamic Covenant
- Mosaic Covenant
- Davidic Covenant
- New Covenant

---

## Kingdom

Examples:

- Kingdom of Israel
- Kingdom of Judah
- Kingdom of God
- Babylon
- Persia

---

## Prophecy

Represents prophetic declarations and their associated metadata.

Properties include:

- Prophecy
- Fulfillments
- Related Story Slots
- Themes
- Supporting Scripture
- Confidence
- Scholarly Positions

---

# Story Slot

Story Slots are the heart of the system.

Every Story Slot represents a meaningful unit of Scripture.

A Story Slot may represent:

- an entire narrative
- a historical period
- a discourse
- a miracle
- a journey
- a teaching
- a battle
- a single event

Examples:

```
The Exodus

or

The Ten Plagues

or

Crossing the Red Sea
```

All are valid Story Slots.

---

# Story Slot Granularity

Story Slots intentionally support multiple levels of granularity.

For example:

```
Exodus

├── Ten Plagues
├── Passover
├── Red Sea Crossing
├── Song of Moses
├── Bitter Waters
├── Manna
├── Water from the Rock
└── Sinai Covenant
```

Likewise,

```
Life of Christ

├── Birth
├── Baptism
├── Temptation
├── Sermon on the Mount
├── Miracles
├── Passion Week
├── Crucifixion
└── Resurrection
```

Granularity is therefore hierarchical while remaining part of the same graph.

---

# Story Slot Properties

Every Story Slot may include:

- Identifier
- Title
- Description
- Parent Story Slot
- Child Story Slots
- Granularity Level
- Approximate Start
- Approximate End
- Approximate Duration
- Chronology Model
- Confidence
- Supporting Scripture
- Participating Beings
- Places
- Themes
- Events
- Covenants
- Kingdoms
- Prophecies
- Fulfillments
- Relationships
- Review Status
- Version History

---

# Relationships

Relationships are first-class entities.

Relationships should not merely exist as foreign keys.

Relationships themselves contain knowledge.

Example:

```
David

father_of

Solomon
```

This relationship itself contains:

- Supporting Scripture
- Confidence
- Reviewer
- Sources
- Notes
- Version History

Relationship types may include:

- before
- after
- during
- parallel
- fulfills
- prophesies
- references
- quotes
- teaches
- contrasts
- symbolizes
- ancestor_of
- descendant_of
- parent_of
- spouse_of
- disciple_of
- teacher_of
- king_of
- prophet_of
- priest_of
- member_of
- appears_with

The graph should make relationships explicit rather than implicit.

---

# Reading Modes

Because every visualization derives from the same graph, multiple reading experiences become possible.

Examples include:

## Canonical

Genesis → Revelation

---

## Chronological

Historical order.

---

## Historical Narrative

Only follow the unfolding biblical narrative.

---

## Literary

Grouped by literary genre.

---

## Story Slot Navigation

Navigate from story to story.

---

## Being Journey

Follow a Being throughout Scripture.

---

## Theme Journey

Follow themes throughout Scripture.

---

## Covenant Journey

Trace every covenant.

---

## Kingdom Journey

Trace kingdoms throughout Scripture.

---

## Prophecy Journey

Follow prophecy through fulfillment.

---

## Custom Reading Paths

User-created study journeys.

---

# Timeline Models

Chronology is intentionally pluggable.

Multiple chronology models should coexist.

Examples:

- Traditional
- Scholarly
- Academic
- Community-created

Each chronology model should include:

- Supporting Scripture
- Supporting Links
- Supporting Relationships
- Confidence
- Reviewer
- Revision History

The graph should naturally allow stronger chronology models to emerge over time through richer supporting evidence.

---

# Representing Uncertainty

Uncertainty is expected.

The system should never force false certainty.

Every derived object should communicate its confidence.

Possible statuses include:

- Confirmed
- Strong Evidence
- Moderate Evidence
- Weak Evidence
- Approximate
- Multiple Positions
- Unknown
- Under Review

Every uncertain claim should include:

- Supporting Scripture
- Supporting Relationships
- Supporting Reasoning
- Alternative Positions
- Review History

Approximation is the default where certainty is unavailable.

Every approximation remains open for future review.

---

# Facts vs Interpretations

Theosis distinguishes facts from interpretations.

## Facts

Facts are directly grounded in Scripture.

Every fact must reference supporting passages.

Facts may still require review if AI-generated.

---

## Interpretations

Interpretations are higher-level understandings built upon Scriptural facts.

Examples:

- Teachings
- Symbolism
- Typology
- Theological Insights
- Devotional Reflections

Interpretations exist in separate layers.

Multiple interpretations may coexist.

No interpretation replaces Scripture.

---

# AI Workflow

AI acts as an assistant, never as the final authority.

AI may:

- Generate Story Slots
- Suggest Relationships
- Infer Themes
- Infer Being Properties
- Suggest Chronologies
- Detect Patterns
- Recommend Cross References
- Build Graph Connections
- Identify Potential Prophecies
- Suggest Fulfillments

However,

**AI-generated content never becomes canonical automatically.**

Every generated node or relationship enters a review workflow.

```
AI

↓

Draft

↓

Reviewer

↓

Approved

↓

Published
```

Human review is mandatory before publication.

---

# Review System

Every mutable entity supports:

- Drafts
- Reviews
- Version History
- Change Requests
- Review Notes
- Approval Status

Nothing enters the graph without review.

---

# Search

The graph should support many search methods.

Examples:

- Being Search
- Theme Search
- Place Search
- Event Search
- Covenant Search
- Kingdom Search
- Prophecy Search
- Natural Language Search
- Semantic Search
- Graph Traversal
- Relationship Search
- Timeline Search

Future examples:

> Show every king warned by a prophet.

> Show every covenant involving sacrifice.

> Show every appearance of angels during periods of exile.

---

# Visualization Modes

Every visualization is simply another projection of the graph.

Examples include:

## Timeline

Gantt-style visualization.

---

## Knowledge Graph

Interactive graph exploration.

---

## Study Bible

Study mode enriched with graph metadata.

---

## Character / Being Explorer

Explore every Being.

---

## Theme Explorer

Visualize thematic development.

---

## Covenant Explorer

Trace covenant relationships.

---

## Prophecy Explorer

Visualize prophecy and fulfillment.

---

## Historical Maps

Geographic visualization.

---

## Genealogy Explorer

Interactive family trees.

---

## Parallel Passage Comparison

Compare related passages.

---

# Future Extensibility

The graph should be designed so that future capabilities require new projections rather than new architectures.

Potential future capabilities include:

- AI Study Companion
- Personal Discipleship Journeys
- Sermon Preparation
- Original Hebrew & Greek Integration
- Interactive Family Trees
- Archaeological Context
- Church History Extensions
- Community Review Workflows
- Public Knowledge Contributions
- Study Collections
- Personal Knowledge Graphs

---

# Architectural Principle

Every feature within Theosis should ultimately be a different way of exploring the same underlying graph.

The graph is the platform.

Story Slots, Beings, Themes, Places, Covenants, Prophecies, Timelines, Search, AI, Visualizations, and future capabilities are all different projections of one interconnected knowledge graph.

At every level of abstraction, the graph must remain grounded in its only immutable source of truth:

> **The Holy Scriptures.**