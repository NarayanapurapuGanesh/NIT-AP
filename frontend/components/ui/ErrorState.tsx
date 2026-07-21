'use client';

import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from './Button';

export interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'An Error Occurred',
  description = 'Failed to load requested resources. Please try again.',
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-rose-900/50 bg-rose-950/20 p-12 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-900/40 text-rose-400 mb-4">
        <AlertTriangle className="h-6 w-6" />
      </div>
      <h3 className="text-lg font-semibold text-rose-200">{title}</h3>
      <p className="mt-1 text-sm text-rose-300/70 max-w-sm">{description}</p>
      {onRetry && (
        <Button variant="danger" onClick={onRetry} className="mt-6">
          Retry Action
        </Button>
      )}
    </div>
  );
};
