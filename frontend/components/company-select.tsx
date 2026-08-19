"use client";

import { useEffect, useRef, useState } from "react";

export function CompanySelect({
  companies,
  value,
  onChange,
  disabled,
}: {
  companies: string[];
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [highlight, setHighlight] = useState(0);
  const boxRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const filtered = companies
    .filter((c) => c.toLowerCase().includes(query.trim().toLowerCase()))
    .slice(0, 50);

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  useEffect(() => {
    setHighlight(0);
  }, [query, open]);

  function pick(name: string) {
    onChange(name);
    setQuery(name);
    setOpen(false);
    inputRef.current?.focus();
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(h + 1, filtered.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (filtered[highlight]) pick(filtered[highlight]);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  }

  return (
    <div ref={boxRef} className="relative">
      <input
        ref={inputRef}
        className="search-input w-full"
        placeholder="Search company…"
        value={open ? query : value}
        disabled={disabled}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={onKeyDown}
      />
      {open && (
        <div className="absolute z-20 mt-1 max-h-60 w-full overflow-y-auto rounded border border-border bg-surface shadow-lg">
          {value !== "" && (
            <button
              type="button"
              onMouseDown={(e) => {
                e.preventDefault();
                pick("");
              }}
              className="flex w-full items-center px-3 py-2 text-left text-sm text-text-muted hover:bg-elevated"
            >
              Clear filter (show all companies)
            </button>
          )}
          {filtered.length === 0 ? (
            <div className="px-3 py-2 text-sm text-text-muted">No companies match.</div>
          ) : (
            filtered.map((c, i) => (
              <button
                key={c}
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault();
                  pick(c);
                }}
                onMouseEnter={() => setHighlight(i)}
                className={`flex w-full items-center justify-between px-3 py-2 text-left text-sm ${
                  i === highlight ? "bg-elevated text-text" : "text-text-secondary"
                }`}
              >
                <span>{c}</span>
                {c === value && <span className="text-xs text-primary">✓</span>}
              </button>
            ))
          )}
          <div className="border-t border-border px-3 py-1.5 text-[11px] text-text-muted">
            {companies.length} companies tracked
          </div>
        </div>
      )}
    </div>
  );
}