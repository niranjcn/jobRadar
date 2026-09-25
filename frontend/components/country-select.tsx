"use client";

import { useEffect, useRef, useState } from "react";
import type { GeoCountry } from "@/lib/types";

export function CountrySelect({
  countries,
  onSelect,
  disabled,
}: {
  countries: GeoCountry[];
  onSelect: (name: string) => void;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [highlight, setHighlight] = useState(0);
  const boxRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const filtered = countries
    .filter((c) =>
      `${c.name} ${c.code} ${(c.aliases || []).join(" ")}`
        .toLowerCase()
        .includes(query.trim().toLowerCase()),
    )
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
    onSelect(name);
    setOpen(false);
    setQuery("");
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
      if (filtered[highlight]) pick(filtered[highlight].name);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  }

  return (
    <div ref={boxRef} className="relative">
      <input
        ref={inputRef}
        className="search-input w-full"
        placeholder="Search countries (e.g. Pakistan, Germany, Canada)…"
        value={query}
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
          {filtered.length === 0 ? (
            <div className="px-3 py-2 text-sm text-text-muted">
              No country matches — press Enter to add anyway
            </div>
          ) : (
            filtered.map((c, i) => (
                <button
                  key={c.code}
                  type="button"
                  onMouseDown={(e) => {
                    e.preventDefault();
                    pick(c.name);
                  }}
                  onMouseEnter={() => setHighlight(i)}
                  className={`flex w-full items-center justify-between px-3 py-2 text-left text-sm ${
                    i === highlight ? "bg-elevated text-text" : "text-text-secondary"
                  }`}
                >
                  <span>{c.name}</span>
                  <span className="text-xs text-text-muted">{c.code}</span>
                </button>
              ))
          )}
          <div className="border-t border-border px-3 py-1.5 text-[11px] text-text-muted">
            {countries.length} countries supported
          </div>
        </div>
      )}
    </div>
  );
}
