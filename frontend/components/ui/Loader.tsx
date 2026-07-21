'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

export const Loader: React.FC<LoaderProps> = ({ size = 'md', className, label }) => {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 space-y-3">
      <Loader2 className={cn('animate-spin text-sky-500', sizes[size], className)} />
      {label && <p className="text-sm text-slate-400">{label}</p>}
    </div>
  );
};
