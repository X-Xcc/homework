import { PropsWithChildren, ReactNode } from 'react';

type WorkspaceShellProps = PropsWithChildren<{
  left?: ReactNode;
  right?: ReactNode;
}>;

export function WorkspaceShell({ left, right, children }: WorkspaceShellProps) {
  return (
    <div className="grid gap-6 xl:grid-cols-[260px_minmax(0,1fr)_320px]">
      <aside className="space-y-4">{left}</aside>
      <section className="min-w-0">{children}</section>
      <aside className="space-y-4">{right}</aside>
    </div>
  );
}
