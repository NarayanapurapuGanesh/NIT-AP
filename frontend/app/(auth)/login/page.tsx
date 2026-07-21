'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export default function LoginPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Sign In</CardTitle>
        <CardDescription>Enter your institutional credentials to access FacultyIQ</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input id="email" label="Institutional Email" type="email" placeholder="faculty@university.edu" />
        <Input id="password" label="Password" type="password" placeholder="••••••••" />
      </CardContent>
      <CardFooter className="flex flex-col space-y-4">
        <Link href="/dashboard" className="w-full">
          <Button className="w-full">Sign In to Dashboard</Button>
        </Link>
        <div className="text-center text-xs text-slate-500">
          FacultyIQ Enterprise Security • SSO & SAML ready
        </div>
      </CardFooter>
    </Card>
  );
}
