import { PropsWithChildren } from 'react';
import { cn } from '@/shared/utils/cn';

type PageContainerProps = PropsWithChildren<{
  className?: string;
}>;

export function PageContainer({ className, children }: PageContainerProps) {
  return <div className={cn('mx-auto w-full max-w-[1200px]', className)}>{children}</div>;
}
