import { PropsWithChildren } from 'react';
import { cn } from '@/shared/utils/cn';

type BadgeProps = PropsWithChildren<{
  tone?: 'neutral' | 'brand' | 'warning' | 'success';
  className?: string;
}>;

export function Badge({ tone = 'neutral', className, children }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-3 py-1 text-xs font-medium',
        tone === 'neutral' && 'bg-slate-100 text-slate-600',
        tone === 'brand' && 'bg-brand-50 text-brand-700',
        tone === 'warning' && 'bg-amber-50 text-amber-700',
        tone === 'success' && 'bg-emerald-50 text-emerald-700',
        className,
      )}
    >
      {children}
    </span>
  );
}
