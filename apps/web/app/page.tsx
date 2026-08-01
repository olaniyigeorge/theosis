import Link from "next/link";

const navigation = [
  { label: "Explore", href: "/explore" },
  { label: "Search", href: "/search" },
  { label: "Journeys", href: "/journeys" },
  { label: "API", href: "/docs" },
];

const entryPoints = [
  {
    tag: "Scripture Advice",
    title: "Bring your life to Scripture",
    description:
      "Ask questions about your current season, struggles, or calling. Receive biblical wisdom anchored directly to graph evidence.",
    href: "/ask", // Powered by POST /advice
    badge: "Personal Insights",
  },
  {
    tag: "Being Journey",
    title: "Follow a life trajectory",
    description:
      "Trace turning points, covenant moments, and character arcs across Scripture—and discover where your own story intersects.",
    href: "/journeys", // Powered by POST /draft
    badge: "Character & Self",
  },
  {
    tag: "Graph Explorer",
    title: "Explore the eternal story",
    description:
      "Navigate non-linear connections between people, places, covenants, and divine promises across generations.",
    href: "/explore",
    badge: "Interactive Graph",
  },
];

const previewNodes = [
  { label: "Being", name: "Moses", ref: "Exodus 3:1" },
  { label: "Story Event", name: "The Burning Bush", ref: "Exodus 3:2-4" },
  { label: "Covenant Node", name: "Sinai Covenant", ref: "Exodus 19:5" },
];

const principles = [
  {
    title: "Scripture is the source of truth",
    description:
      "Every entity and relationship exists because it can be directly traced back to a specific passage.",
  },
  {
    title: "Connections have evidence",
    description:
      "Relationships are never assumptions. Every edge in the graph carries its exact supporting scripture reference.",
  },
  {
    title: "AI assists, humans verify",
    description:
      "AI models assist in discovering and indexing connections, but no data is committed without human review.",
  },
];

export default function Home() {
  return (
    <>
      <header className="top">
        <div className="wrap topbar">
          <Link className="mark" href="/">
            Theos<em>is</em>
          </Link>
          <nav aria-label="Main Navigation">
            {navigation.map((item) => (
              <Link key={item.href} href={item.href}>
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      <main className="wrap" id="top">
        {/* HERO SECTION */}
        <section className="hero">
          <div className="hero-content">
            <div className="eyebrow">
              <span className="status-dot"></span> A Knowledge Graph of Scripture
            </div>
            <h1 className="title">
              Every story connected. Every claim anchored <em>to Scripture.</em>
            </h1>
            <p className="tagline">
              Theosis transforms Scripture into a navigable knowledge graph—connecting
              people, places, events, themes, and covenants while{" "}
              <strong>preserving the original biblical source behind every connection.</strong>
            </p>

            <div className="hero-actions">
              <Link className="btn primary" href="/explore">
                Explore the graph &rarr;
              </Link>
              <Link className="btn ghost" href="/search">
                Search Scripture
              </Link>
            </div>

            <div className="status-line">
              <span>backend online</span> &middot; <span>schema v1</span> &middot;{" "}
              <span>review pipeline active</span>
            </div>
          </div>

          {/* GRAPH PREVIEW COMPONENT */}
          <div className="graph-card">
            <div className="preview-head">
              <div>
                <span className="eyebrow" style={{ marginBottom: 4 }}>
                  Live Connection Preview
                </span>
                <h2 className="preview-title">Moses &rarr; Exodus &rarr; Covenant</h2>
              </div>
              <span className="verified-badge">Peer Verified</span>
            </div>

            <div className="graph-visualization">
              {previewNodes.map((node) => (
                <div className="node-card" key={node.name}>
                  <span className="node-label">{node.label}</span>
                  <p className="node-name">{node.name}</p>
                  <span className="mono" style={{ fontSize: "0.75rem", color: "var(--ink-soft)", marginTop: "8px", display: "block" }}>
                    {node.ref}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* SECTION I: ENTRY POINTS */}
        <section className="chapter" id="entry">
          <div className="chapter-head">
            <span className="numeral">I</span>
            <h2>Three ways to enter Scripture</h2>
          </div>

          <div className="card-grid">
            {entryPoints.map((entry) => (
              <Link className="entry-card" href={entry.href} key={entry.title}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span className="tag">{entry.tag}</span>
                    <span className="mono" style={{ fontSize: "0.65rem", color: "var(--verdigris)", border: "1px solid var(--verdigris-dim)", padding: "2px 6px", borderRadius: "2px" }}>
                      {entry.badge}
                    </span>
                  </div>
                  <h3>{entry.title}</h3>
                  <p>{entry.description}</p>
                </div>
                <span className="entry-link">Begin &rarr;</span>
              </Link>
            ))}
</div>
        </section>

        {/* SECTION II: PRINCIPLES */}
        <section className="chapter" id="trust">
          <div className="chapter-head">
            <span className="numeral">II</span>
            <h2>Built around biblical evidence</h2>
          </div>
          <div className="principle-grid">
            {principles.map((item) => (
              <div className="principle" key={item.title}>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CALL TO ACTION */}
        <section className="chapter">
          <div className="close-card">
            <h2>Start with a name you already know.</h2>
            <p>
              Search Moses, Abraham, David, the Exodus, or any thread in Scripture
              and discover where the connections lead.
            </p>
            <Link className="btn primary" href="/search">
              Begin exploring &rarr;
            </Link>
          </div>
        </section>
      </main>

      <footer className="wrap">
        <span>Theosis &middot; Scripture Knowledge Graph</span>
        <Link href="/docs">API Reference &rarr;</Link>
      </footer>
    </>
  );
}