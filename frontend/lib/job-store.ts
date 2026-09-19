/** Client-side Save / Hide for public job rows (hiringcafe-style actions).
 *
 *  No backend needed: ids persist in localStorage. Pure array helpers are
 *  exported for unit tests; the load/save wrappers touch localStorage.
 */

export const SAVED_KEY = "jobquest:saved-jobs:v1";
export const HIDDEN_KEY = "jobquest:hidden-jobs:v1";
export const APPLIED_KEY = "jobquest:applied-jobs:v1";
const MAX_IDS = 500;

export function toggleInList(list: string[], id: string): string[] {
  if (list.includes(id)) return list.filter((x) => x !== id);
  return [id, ...list].slice(0, MAX_IDS);
}

export function removeFromList(list: string[], id: string): string[] {
  return list.filter((x) => x !== id);
}

export function filterHidden<T extends { id: string }>(jobs: T[], hidden: string[]): T[] {
  if (hidden.length === 0) return jobs;
  const set = new Set(hidden);
  return jobs.filter((j) => !set.has(j.id));
}

function readKey(key: string): string[] {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter((x) => typeof x === "string") : [];
  } catch {
    return [];
  }
}

function writeKey(key: string, ids: string[]): void {
  try {
    localStorage.setItem(key, JSON.stringify(ids.slice(0, MAX_IDS)));
  } catch {}
}

export function loadSaved(): string[] {
  return readKey(SAVED_KEY);
}

export function loadHidden(): string[] {
  return readKey(HIDDEN_KEY);
}

export function toggleSaved(current: string[], id: string): string[] {
  const next = toggleInList(current, id);
  writeKey(SAVED_KEY, next);
  return next;
}

export function hideJob(current: string[], id: string): string[] {
  if (current.includes(id)) return current;
  const next = [id, ...current].slice(0, MAX_IDS);
  writeKey(HIDDEN_KEY, next);
  return next;
}

export function unhideAll(): string[] {
  writeKey(HIDDEN_KEY, []);
  return [];
}

export function loadApplied(): string[] {
  return readKey(APPLIED_KEY);
}

/** Join multi-select filter values into a csv query param (undefined = unset). */
export function splitCsvParam(values: string[]): string | undefined {
  const cleaned = values.map((v) => v.trim()).filter(Boolean);
  return cleaned.length ? cleaned.join(",") : undefined;
}

export function markApplied(current: string[], id: string): string[] {
  if (current.includes(id)) return current;
  const next = [id, ...current].slice(0, MAX_IDS);
  writeKey(APPLIED_KEY, next);
  return next;
}
