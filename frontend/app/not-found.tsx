'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { FileQuestion } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 p-6 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-900 border border-slate-800 text-sky-400 mb-6">
        <FileQuestion className="h-8 w-8" />
      </div>
      <h1 className="text-4xl font-extrabold text-white tracking-tight">404 - Page Not Found</h1>
      <p className="mt-2 text-sm text-slate-400 max-w-md">
        The requested resource or endpoint could not be found within the FacultyIQ portal.
      </p>
      <Link href="/" className="mt-8">
        <Button variant="primary">Return to Homepage</Button>
      </Link>
    </div>
  );
}
