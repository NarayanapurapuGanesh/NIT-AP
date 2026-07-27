'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { User, Lock, Save, CheckCircle2, ShieldCheck, Mail, Building, KeyRound } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function ProfilePage() {
  const { user, updateProfile } = useAuth();

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (user) {
      setFirstName(user.firstName || '');
      setLastName(user.lastName || '');
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    if (!firstName.trim() || !lastName.trim()) {
      setMessage({ type: 'error', text: 'First name and last name cannot be empty.' });
      return;
    }

    if (newPassword) {
      if (!currentPassword) {
        setMessage({ type: 'error', text: 'Please enter your current password to change password.' });
        return;
      }
      if (newPassword !== confirmPassword) {
        setMessage({ type: 'error', text: 'New password and confirmation do not match.' });
        return;
      }
    }

    setSaving(true);

    try {
      const result = await updateProfile({
        firstName: firstName.trim(),
        lastName: lastName.trim(),
        currentPassword: currentPassword || undefined,
        newPassword: newPassword || undefined,
      });

      if (!result.success) {
        setMessage({ type: 'error', text: result.error || 'Failed to update profile.' });
        setSaving(false);
        return;
      }

      setMessage({ type: 'success', text: 'Account profile updated successfully!' });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch {
      setMessage({ type: 'error', text: 'An error occurred while updating profile.' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl">
      {/* Header Banner */}
      <div className="flex items-center justify-between p-6 rounded-2xl bg-gradient-to-r from-sky-950/80 via-slate-900 to-indigo-950/80 border border-sky-500/20 shadow-xl backdrop-blur-xl">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
            <User className="h-3.5 w-3.5" />
            <span>Account Management</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Edit Account Profile & Password</h1>
          <p className="text-xs text-slate-400">
            Update your personal name details and security password for FacultyIQ.
          </p>
        </div>
      </div>

      {message && (
        <div
          className={`p-4 rounded-xl text-xs font-medium border flex items-center space-x-2 ${
            message.type === 'success'
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
              : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
          ) : (
            <ShieldCheck className="h-4 w-4 text-rose-400 flex-shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Name & Account Details Card */}
        <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <CardHeader className="border-b border-slate-800/80 pb-4">
            <CardTitle className="text-base font-bold text-white flex items-center">
              <User className="h-4 w-4 text-sky-400 mr-2" />
              Personal Identity Information
            </CardTitle>
            <CardDescription className="text-xs text-slate-400">
              Your name as it appears across faculty recruitment evaluation reports
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">First Name *</label>
                <div className="relative">
                  <User className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                    className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Last Name *</label>
                <div className="relative">
                  <User className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                  <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    required
                    className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Institutional Email (Read Only)</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-600" />
                  <input
                    type="email"
                    disabled
                    value={user?.email || ''}
                    className="w-full rounded-lg bg-slate-950/40 border border-slate-800/60 pl-9 pr-3 py-2 text-sm text-slate-400 cursor-not-allowed"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Department / Role</label>
                <div className="relative">
                  <Building className="absolute left-3 top-2.5 h-4 w-4 text-slate-600" />
                  <input
                    type="text"
                    disabled
                    value={`${user?.department || 'CSE'} — ${user?.academicRole || 'Faculty Member'}`}
                    className="w-full rounded-lg bg-slate-950/40 border border-slate-800/60 pl-9 pr-3 py-2 text-sm text-slate-400 cursor-not-allowed"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Change Password Card */}
        <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <CardHeader className="border-b border-slate-800/80 pb-4">
            <CardTitle className="text-base font-bold text-white flex items-center">
              <KeyRound className="h-4 w-4 text-sky-400 mr-2" />
              Security & Password Settings
            </CardTitle>
            <CardDescription className="text-xs text-slate-400">
              Leave blank if you do not wish to update your password
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6 space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Current Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">New Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Confirm New Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full rounded-lg bg-slate-950/80 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Button */}
        <div className="flex justify-end">
          <Button
            type="submit"
            isLoading={saving}
            className="bg-sky-600 hover:bg-sky-500 text-white font-medium px-6 py-2.5 flex items-center space-x-2"
          >
            <Save className="h-4 w-4 mr-1.5" />
            <span>{saving ? 'Saving Changes...' : 'Save Profile Changes'}</span>
          </Button>
        </div>
      </form>
    </div>
  );
}
