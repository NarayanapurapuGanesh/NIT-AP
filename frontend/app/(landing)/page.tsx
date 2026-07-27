'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Cpu, Shield, Database, Server, Sparkles, UserPlus, LogIn } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function LandingPage() {
  return (
    <div className="relative overflow-hidden pt-12 pb-24">
      <div className="absolute top-0 left-1/2 -z-10 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-gradient-to-tr from-sky-600/20 to-indigo-600/10 blur-[120px]" />

      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center max-w-3xl mx-auto space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 rounded-full border border-sky-500/30 bg-sky-500/10 px-4 py-1.5 text-xs font-medium text-sky-300"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Autonomous Multi-Agent Faculty Recruitment Suite</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl font-extrabold tracking-tight text-white sm:text-6xl"
          >
            Enterprise AI-Powered <br />
            <span className="bg-gradient-to-r from-sky-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
              Faculty Recruitment Platform
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-lg text-slate-400 leading-relaxed"
          >
            Streamlining faculty dossier parsing, video analysis, technical evaluation, and candidate reports. Register your account to get started.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex items-center justify-center space-x-4 pt-4"
          >
            <Link href="/register">
              <Button size="lg" className="bg-sky-600 hover:bg-sky-500 text-white shadow-xl shadow-sky-500/25 px-6 py-3 font-semibold flex items-center space-x-2">
                <UserPlus className="h-4 w-4" />
                <span>Get Started & Create Account</span>
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="outline" size="lg" className="border-slate-700 text-slate-300 hover:bg-slate-800 flex items-center space-x-2">
                <LogIn className="h-4 w-4" />
                <span>Sign In to Portal</span>
              </Button>
            </Link>
          </motion.div>
        </div>

        {/* Feature Grid */}
        <div id="features" className="mt-24 grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            {
              icon: <Cpu className="h-6 w-6 text-sky-400" />,
              title: 'Resume & Dossier Agent',
              desc: 'Automated CV parsing, qualification verification, teaching experience extraction, and rubric match scoring.',
            },
            {
              icon: <Server className="h-6 w-6 text-indigo-400" />,
              title: 'Video Analysis Agent',
              desc: 'Multimodal interview transcript analysis, soft-skill radar scoring, pedagogical clarity, and confidence metrics.',
            },
            {
              icon: <Database className="h-6 w-6 text-emerald-400" />,
              title: 'Technical & Coding Agent',
              desc: 'Technical coding evaluation, algorithm efficiency scoring, test suite validation, and code maintainability analysis.',
            },
            {
              icon: <Shield className="h-6 w-6 text-purple-400" />,
              title: 'Interactive Q&A Session',
              desc: 'Interactive candidate interview simulation, live panel question evaluation, and overall synthesis report generation.',
            },
          ].map((item, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * idx }}
              className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 backdrop-blur-md"
            >
              <div className="mb-4 inline-block rounded-lg bg-slate-800/80 p-3">{item.icon}</div>
              <h3 className="text-base font-semibold text-white">{item.title}</h3>
              <p className="mt-2 text-sm text-slate-400 leading-normal">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
