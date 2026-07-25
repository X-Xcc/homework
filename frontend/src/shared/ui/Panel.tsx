import { PropsWithChildren } from 'react';
import { cn } from '@/shared/utils/cn';

type PanelProps = PropsWithChildren<{
  className?: string;
  title?: string;
  description?: string;
}>;

export function Panel({ className, title, description, children }: PanelProps) {
  return (
    <div className={cn('rounded-3xl border border-slate-200 bg-white p-5 shadow-soft', className)}>
      {(title || description) && (
        <div className="mb-4">
          {title ? <div className="text-sm font-semibold text-slate-900">{title}</div> : null}
          {description ? <p className="mt-1 text-sm text-slate-500">{description}</p> : null}
        </div>
      )}
      {children}
    </div>
  );
}
