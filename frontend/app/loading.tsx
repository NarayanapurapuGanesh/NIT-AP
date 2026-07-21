import { Loader } from '@/components/ui/Loader';

export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <Loader size="lg" label="Initializing FacultyIQ Workspace..." />
    </div>
  );
}
