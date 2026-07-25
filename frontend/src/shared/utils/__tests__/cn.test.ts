import { describe, it, expect } from "vitest";
import { cn } from "../cn";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("filters falsy values", () => {
    expect(cn("foo", false && "bar", undefined, "baz")).toBe("foo baz");
  });

  it("handles conditional classes", () => {
    const isActive = true;
    expect(cn("base", isActive && "active")).toBe("base active");
  });

  it("resolves Tailwind conflicts via twMerge", () => {
    expect(cn("px-4", "px-6")).toBe("px-6");
  });

  it("returns empty string for no inputs", () => {
    expect(cn()).toBe("");
  });
});
