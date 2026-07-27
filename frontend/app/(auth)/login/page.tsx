'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Mail, Lock, LogIn, ArrowRight } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await login({ email, password });
      if (!result.success) {
        setError(result.error || 'Invalid email or password.');
        setLoading(false);
        return;
      }

      router.push('/dashboard');
    } catch {
      setError('An unexpected login error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md border border-slate-800 bg-slate-900/90 shadow-2xl backdrop-blur-xl">
      <CardHeader className="text-center space-y-2 pb-6">
        <CardTitle className="text-2xl font-bold text-white tracking-tight">Institutional Portal</CardTitle>
        <CardDescription className="text-slate-400 text-xs">
          Sign in to access FacultyIQ Multi-Agent Recruitment Platform
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleLogin} className="space-y-4">
          {error && (
            <div className="p-3 text-xs rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 font-medium leading-relaxed">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-xs font-medium text-slate-300 mb-1">
              Institutional Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                id="email"
                name="email"
                type="email"
                required
                autoComplete="email"
                placeholder="faculty@nitap.ac.in"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError('');
                }}
                className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
              />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-xs font-medium text-slate-300 mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (error) setError('');
                }}
                className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
              />
            </div>
          </div>

          <Button
            type="submit"
            isLoading={loading}
            className="w-full mt-2 bg-sky-600 hover:bg-sky-500 text-white font-medium py-2.5 flex items-center justify-center space-x-2"
          >
            <LogIn className="h-4 w-4 mr-1" />
            <span>{loading ? 'Authenticating...' : 'Sign In to Dashboard'}</span>
          </Button>
        </form>
      </CardContent>

      <CardFooter className="flex flex-col space-y-3 pt-2 text-center">
        <div className="text-xs text-slate-400">
          Don&apos;t have an institutional account?{' '}
          <Link href="/register" className="text-sky-400 font-semibold hover:underline">
            Register / Sign Up
          </Link>
        </div>
      </CardFooter>
    </Card>
  );
}
