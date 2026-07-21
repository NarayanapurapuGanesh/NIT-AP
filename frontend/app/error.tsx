'use client';

import React from 'react';
import { ErrorState } from '@/components/ui/ErrorState';

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 p-6">
      <ErrorState
        title="Application Error"
        description={error.message || 'An unexpected client-side error occurred.'}
        onRetry={reset}
      />
    </div>
  );
}
