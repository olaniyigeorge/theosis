"use client";

import { useEffect, useRef, useState } from "react";
import styles from "./advice.module.css";
import {
  QUERY_MAX_LENGTH,
  QUERY_MIN_LENGTH,
  requestScriptureAdvice,
} from "@/lib/theosis/api";
import {
  ScriptureAdviceError,
  type AdviceExchange,
  type ScriptureCitation,
} from "@/lib/theosis/types";
import Link from "next/link";

// Visual pace-setter matching the backend's grounding pipeline
const STAGES = [
  "Searching Scripture for relevant passages",
  "Verifying references against canonical text",
  "Composing grounded counsel",
] as const;

const STAGE_DURATION_MS = 1400;

const SUGGESTIONS = [
  "How do I forgive someone who hasn't asked for it?",
  "What does Scripture say about burnout and rest?",
  "How should I respond to unexpected betrayal?",
  "Where do I find peace when anxiety takes over?",
] as const;

type Status = "idle" | "loading" | "error";

export default function AdviceExperience() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeStage, setActiveStage] = useState(0);
  const [exchanges, setExchanges] = useState<AdviceExchange[]>([]);

  const stageTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => {
      if (stageTimer.current) clearInterval(stageTimer.current);
      abortRef.current?.abort();
    };
  }, []);

  const trimmedLength = query.trim().length;
  const overLimit = trimmedLength > QUERY_MAX_LENGTH;
  const canSubmit =
    status !== "loading" &&
    trimmedLength >= QUERY_MIN_LENGTH &&
    trimmedLength <= QUERY_MAX_LENGTH;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    const askedQuery = query.trim();
    setStatus("loading");
    setErrorMessage(null);
    setActiveStage(0);

    if (stageTimer.current) clearInterval(stageTimer.current);
    stageTimer.current = setInterval(() => {
      setActiveStage((s) => (s < STAGES.length - 1 ? s + 1 : s));
    }, STAGE_DURATION_MS);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await requestScriptureAdvice(askedQuery, controller.signal);
      const exchange: AdviceExchange = {
        id: `${Date.now()}`,
        query: askedQuery,
        response,
        askedAt: Date.now(),
      };
      setExchanges((prev) => [exchange, ...prev]);
      setQuery("");
      setStatus("idle");
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      const message =
        err instanceof ScriptureAdviceError
          ? err.message
          : "Something went wrong. Try again.";
      setErrorMessage(message);
      setStatus("error");
    } finally {
      if (stageTimer.current) clearInterval(stageTimer.current);
    }
  }

  function handleRetry() {
    setStatus("idle");
    setErrorMessage(null);
  }

  function handleSelectSuggestion(text: string) {
    if (status === "loading") return;
    setQuery(text);
  }

  return (
    <div className={styles.page}>
      <div className={styles.wrap}>
        <nav className="flex items-center gap-1.5 text-xs tracking-tight">
          <Link 
            href="/" 
            className={`${styles.eyebrow} hover:text-foreground transition-colors duration-150`}
          >
            Theosis
          </Link>
          <span className="text-muted-foreground/40 select-none"> | </span>
          <span className={styles.eyebrow}>Scripture Counsel</span>
        </nav>

        
        <h1 className={styles.title}>Bring it to the text.</h1>
        <p className={styles.subtitle}>
          Ask a real question. What comes back is composed strictly from
          Scripture verified against live canonical sources — unverified references are discarded.
        </p>

        <form className={styles.form} onSubmit={handleSubmit}>
          <label className={styles.formLabel} htmlFor="advice-query">
            What are you carrying?
          </label>
          <textarea
            id="advice-query"
            className={styles.textarea}
            placeholder="How do I navigate uncertainty without losing hope?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={status === "loading"}
          />

          <div className={styles.suggestionsGroup}>
            {SUGGESTIONS.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                className={styles.suggestionPill}
                onClick={() => handleSelectSuggestion(suggestion)}
                disabled={status === "loading"}
              >
                {suggestion}
              </button>
            ))}
          </div>

          <div className={styles.formFooter}>
            <span
              className={`${styles.counter} ${overLimit ? styles.overLimit : ""}`}
            >
              {trimmedLength}/{QUERY_MAX_LENGTH}
            </span>
            <button type="submit" className={styles.submit} disabled={!canSubmit}>
              {status === "loading" ? "Seeking…" : "Seek counsel"}
            </button>
          </div>

          {status === "loading" && (
            <div className={styles.stages} aria-live="polite">
              {STAGES.map((label, i) => (
                <div
                  key={label}
                  className={`${styles.stage} ${
                    i === activeStage ? styles.active : ""
                  } ${i < activeStage ? styles.done : ""}`}
                >
                  <span className={styles.stageDot} />
                  {label}
                </div>
              ))}
            </div>
          )}
        </form>

        {status === "error" && errorMessage && (
          <div className={styles.error} role="alert">
            <p className={styles.errorTitle}>No grounded response available</p>
            <p className={styles.errorBody}>{errorMessage}</p>
            <button className={styles.retry} onClick={handleRetry}>
              Try again
            </button>
          </div>
        )}

        {exchanges.length > 0 && (
          <div className={styles.exchanges}>
            {exchanges.map((exchange) => (
              <ExchangeView key={exchange.id} exchange={exchange} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ExchangeView({ exchange }: { exchange: AdviceExchange }) {
  return (
    <div className={styles.exchange}>
      <p className={styles.question}>{exchange.query}</p>
      <div className={styles.adviceCard}>
        <p className={styles.adviceText}>{exchange.response.advice}</p>
      </div>

      <p className={styles.citationsHeading}>
        Grounded in {exchange.response.citations.length}{" "}
        {exchange.response.citations.length === 1 ? "reference" : "references"}
      </p>

      {exchange.response.citations.length === 0 ? (
        <p className={styles.citationsEmpty}>
          No reference cleared verification for this specific answer.
        </p>
      ) : (
        <div className={styles.citationList}>
          {exchange.response.citations.map((citation, i) => (
            <CitationRow key={i} citation={citation} />
          ))}
        </div>
      )}
    </div>
  );
}

function CitationRow({ citation }: { citation: ScriptureCitation }) {
  const ref = citation.verse_end
    ? `${citation.book} ${citation.chapter}:${citation.verse_start}-${citation.verse_end}`
    : `${citation.book} ${citation.chapter}:${citation.verse_start}`;

  return (
    <details className={styles.citation}>
      <summary className={styles.citationSummary}>
        <span className={styles.citationRef}>{ref}</span>
        <span className={styles.citationTranslation}>{citation.translation}</span>
        <span className={styles.verifiedTag}>Verified</span>
      </summary>
      <p className={styles.citationText}>{citation.text}</p>
    </details>
  );
}