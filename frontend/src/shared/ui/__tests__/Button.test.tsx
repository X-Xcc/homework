import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "../Button";

describe("Button", () => {
  it("renders children", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText("Click me")).toBeInTheDocument();
  });

  it("fires onClick handler", () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    fireEvent.click(screen.getByText("Click"));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("shows loading text when loading", () => {
    render(<Button loading>Save</Button>);
    expect(screen.getByText("处理中...")).toBeInTheDocument();
  });

  it("disables button when loading", () => {
    render(<Button loading>Save</Button>);
    expect(screen.getByText("处理中...").closest("button")).toBeDisabled();
  });

  it("disables button when disabled prop is set", () => {
    render(<Button disabled>Save</Button>);
    expect(screen.getByText("Save").closest("button")).toBeDisabled();
  });

  it("applies primary variant by default", () => {
    render(<Button>Primary</Button>);
    const btn = screen.getByText("Primary");
    expect(btn.className).toContain("bg-brand-600");
  });

  it("applies secondary variant", () => {
    render(<Button variant="secondary">Secondary</Button>);
    const btn = screen.getByText("Secondary");
    expect(btn.className).toContain("border");
  });
});
