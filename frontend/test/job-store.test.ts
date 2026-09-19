import { describe, expect, it } from "vitest";
import { filterHidden, removeFromList, toggleInList } from "../lib/job-store";
import { splitCsvParam } from "../lib/job-store";

describe("job-store pure helpers", () => {
  it("toggles an id in and out", () => {
    expect(toggleInList([], "a")).toEqual(["a"]);
    expect(toggleInList(["a"], "a")).toEqual([]);
    expect(toggleInList(["b"], "a")).toEqual(["a", "b"]);
  });

  it("removes an id", () => {
    expect(removeFromList(["a", "b"], "a")).toEqual(["b"]);
    expect(removeFromList(["b"], "a")).toEqual(["b"]);
  });

  it("filters hidden jobs out", () => {
    const jobs = [{ id: "1" }, { id: "2" }, { id: "3" }];
    expect(filterHidden(jobs, [])).toHaveLength(3);
    expect(filterHidden(jobs, ["2"]).map((j) => j.id)).toEqual(["1", "3"]);
  });

  it("builds csv params from multi-selects", () => {
    expect(splitCsvParam([])).toBeUndefined();
    expect(splitCsvParam(["", "  "])).toBeUndefined();
    expect(splitCsvParam(["a", " b "])).toBe("a,b");
  });
});
