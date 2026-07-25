import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Badge } from "../Badge";

describe("Badge", () => {
  it("renders children", () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("applies neutral tone by default", () => {
    render(<Badge>Default</Badge>);
    const badge = screen.getByText("Default");
    expect(badge.className).toContain("bg-slate-100");
    expect(badge.className).toContain("text-slate-600");
  });

  it("applies brand tone", () => {
    render(<Badge tone="brand">Brand</Badge>);
    const badge = screen.getByText("Brand");
    expect(badge.className).toContain("bg-brand-50");
  });

  it("applies warning tone", () => {
    render(<Badge tone="warning">Warning</Badge>);
    const badge = screen.getByText("Warning");
    expect(badge.className).toContain("bg-amber-50");
  });

  it("merges custom className", () => {
    render(<Badge className="extra">Custom</Badge>);
    const badge = screen.getByText("Custom");
    expect(badge.className).toContain("extra");
  });
});
