import Link from "next/link";

const navigation = [
  { label: "Explore", href: "/explore" },
  { label: "Search", href: "/search" },
  { label: "Journeys", href: "/journeys" },
  { label: "API", href: "/docs" },
];

const entryPoints = [
  {
    tag: "Being Journey",
    title: "Follow a person",
    description:
      "Trace a person's appearances, relationships, events, and turning points across Scripture.",
    href: "/journeys",
  },
  {
    tag: "Graph Explorer",
    title: "Explore the story graph",
    description:
      "Navigate connections between people, places, events, kingdoms, covenants, and prophecies.",
    href: "/explore",
  },
  {
    tag: "Search",
    title: "Search Scripture knowledge",
    description:
      "Find entities, themes, and stories with every answer connected back to its source.",
    href: "/search",
  },
];

const previewNodes = ["Being", "Story Slot", "Scripture Reference"];

const principles = [
  {
    title: "Scripture is the source of truth",
    description:
      "Every entity and relationship exists because it can be traced back to a specific passage.",
  },
  {
    title: "Connections have evidence",
    description:
      "Relationships are not assumptions. Each edge carries its supporting reference.",
  },
  {
    title: "AI assists, humans verify",
    description:
      "AI helps discover and organize knowledge, but nothing is published without review.",
  },
];

export default function Home() {
  return (
    <>
      <header className="top">
        <div className="topbar">
          <Link className="mark" href="/">
            Theos<em>is</em>
          </Link>
          <nav>
            {navigation.map((item) => (
              <Link key={item.href} href={item.href}>
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      <main className="wrap" id="top">
        <section className="hero">
          <p className="eyebrow">A Knowledge Graph of Scripture</p>
          <h1 className="title">
            Every story connected. Every claim anchored{" "}
            <em>to Scripture.</em>
          </h1>
          <p className="tagline">
            Theosis transforms Scripture into a navigable knowledge graph —
            connecting people, places, events, themes, and stories while{" "}
            <strong>
              preserving the original biblical source behind every
              connection.
            </strong>
          </p>

          <div className="hero-actions">
            <Link className="btn primary" href="/explore">
              Explore the graph →
            </Link>
            <Link className="btn ghost" href="/search">
              Search Scripture
            </Link>
          </div>
          <p className="status-line">
            <span className="status-dot"></span>
            backend online · schema v1 · review pipeline active
          </p>

          <div className="graph-card">
            <div className="preview-head">
              <div>
                <p className="cap">Live Knowledge Graph</p>
                <h2 className="preview-title">Moses → Exodus → Joshua</h2>
              </div>
              <span className="verified-badge">verified</span>
            </div>

            <div className="node-grid">
              {previewNodes.map((node) => (
                <div className="node-card" key={node}>
                  <span className="node-label">Node</span>
                  <p className="node-name">{node}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="chapter" id="entry">
          <div className="chapter-head">
            <span className="numeral">I</span>
            <h2>Three ways to enter Scripture</h2>
          </div>
          <div className="chapter-body">
            <div className="card-grid">
              {entryPoints.map((entry) => (
                <Link className="entry-card" href={entry.href} key={entry.title}>
                  <span className="tag">{entry.tag}</span>
                  <h3>{entry.title}</h3>
                  <p>{entry.description}</p>
                  <span className="entry-link">Open →</span>
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className="chapter" id="trust">
          <div className="chapter-head">
            <span className="numeral">II</span>
            <h2>Built around biblical evidence</h2>
          </div>
          <div className="chapter-body">
            <div className="principle-grid">
              {principles.map((item) => (
                <div className="principle" key={item.title}>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="chapter">
          <div className="close-card">
            <h2>Start with a name you already know.</h2>
            <p>
              Search Moses, Abraham, David, the Exodus, or any thread in
              Scripture and discover where it leads.
            </p>
            <Link className="btn primary" href="/search">
              Begin exploring →
            </Link>
          </div>
        </section>
      </main>

      <footer className="wrap">
        <span>Theosis · Scripture Knowledge Graph</span>
        <Link href="/docs">API Reference →</Link>
      </footer>
    </>
  );
}