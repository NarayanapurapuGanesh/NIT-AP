'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { User, Mail, Building, ShieldCheck, Lock, CheckCircle2 } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    department: 'Computer Science & Engineering',
    academicRole: 'Assistant Professor',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [registered, setRegistered] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.fullName || !formData.email || !formData.password) {
      setError('Please fill in all required fields.');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match. Please re-enter matching passwords.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const nameParts = formData.fullName.trim().split(' ');
      const firstName = nameParts[0] || 'Faculty';
      const lastName = nameParts.slice(1).join(' ') || 'Member';

      const result = await register({
        email: formData.email,
        password: formData.password,
        firstName,
        lastName,
        department: formData.department,
        academicRole: formData.academicRole,
      });

      if (!result.success) {
        setError(result.error || 'Registration failed.');
        setLoading(false);
        return;
      }

      setRegistered(true);
      setTimeout(() => {
        router.push('/dashboard');
      }, 1000);
    } catch {
      setError('An unexpected error occurred during account creation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md border border-slate-800 bg-slate-900/90 shadow-2xl backdrop-blur-xl">
      <CardHeader className="text-center space-y-2 pb-6">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-600/20 text-sky-400 border border-sky-500/30">
          <ShieldCheck className="h-6 w-6" />
        </div>
        <CardTitle className="text-2xl font-bold text-white tracking-tight">Create Institutional Account</CardTitle>
        <CardDescription className="text-slate-400 text-xs">
          Register to evaluate faculty dossiers & manage AI recruitment workflows
        </CardDescription>
      </CardHeader>

      <CardContent>
        {registered ? (
          <div className="py-8 text-center space-y-3">
            <CheckCircle2 className="h-12 w-12 text-emerald-400 mx-auto animate-bounce" />
            <h3 className="text-lg font-semibold text-white">Account Created Successfully!</h3>
            <p className="text-xs text-slate-400">Redirecting to your institutional dashboard...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 text-xs rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 font-medium leading-relaxed">
                {error}
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Full Name *</label>
              <div className="relative">
                <User className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <input
                  type="text"
                  name="fullName"
                  placeholder="Dr. Rajesh Kumar"
                  value={formData.fullName}
                  onChange={handleChange}
                  required
                  className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Institutional Email *</label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <input
                  type="email"
                  name="email"
                  placeholder="r.kumar@nitap.ac.in"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Department</label>
                <div className="relative">
                  <Building className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                  <select
                    name="department"
                    value={formData.department}
                    onChange={handleChange}
                    className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-2 py-2 text-xs text-white focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                  >
                    <option value="Computer Science & Engineering">CSE</option>
                    <option value="Electrical Engineering">EE</option>
                    <option value="Mechanical Engineering">ME</option>
                    <option value="Basic Sciences & Humanities">BSH</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Role / Rank</label>
                <select
                  name="academicRole"
                  value={formData.academicRole}
                  onChange={handleChange}
                  className="w-full rounded-lg bg-slate-950/80 border border-slate-800 px-3 py-2 text-xs text-white focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                >
                  <option value="Assistant Professor">Assistant Prof</option>
                  <option value="Associate Professor">Associate Prof</option>
                  <option value="Full Professor">Full Professor</option>
                  <option value="Selection Committee">Committee</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Password *</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <input
                  type="password"
                  name="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Confirm Password *</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <input
                  type="password"
                  name="confirmPassword"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                />
              </div>
            </div>

            <Button type="submit" isLoading={loading} className="w-full mt-2 bg-sky-600 hover:bg-sky-500 text-white font-medium py-2.5">
              {loading ? 'Creating Account...' : 'Complete Registration'}
            </Button>
          </form>
        )}
      </CardContent>

      <CardFooter className="flex flex-col space-y-3 pt-2 text-center">
        <div className="text-xs text-slate-400">
          Already have an institutional account?{' '}
          <Link href="/login" className="text-sky-400 font-semibold hover:underline">
            Sign In
          </Link>
        </div>
      </CardFooter>
    </Card>
  );
}
