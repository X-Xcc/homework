import { PropsWithChildren } from 'react';
import { cn } from '@/shared/utils/cn';

type CardProps = PropsWithChildren<{
  className?: string;
}>;

export function Card({ className, children }: CardProps) {
  return (
    <section className={cn('rounded-3xl border border-slate-200 bg-white p-5 shadow-soft', className)}>
      {children}
    </section>
  );
}
