"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Play, Code2, Cpu, Brain, Layers, AlertTriangle, CheckCircle2, Wifi, Video, Mic, MonitorOff } from "lucide-react";
import { startSession } from "@/lib/api/coding";
import { motion, AnimatePresence } from "framer-motion";

export default function CodingAgentLanding() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [showGuidelines, setShowGuidelines] = useState(false);
  const [formData, setFormData] = useState({
    candidate_name: "John Doe",
    candidate_email: "john@example.com",
    department: "Software Engineering",
    programming_language: "python",
    difficulty: "medium",
    max_questions: 5,
  });


  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      // Request full screen
      const elem = document.documentElement;
      if (elem.requestFullscreen) {
        elem.requestFullscreen().catch(e => console.log("Fullscreen error:", e));
      }
      
      const session = await startSession({
        ...formData,
        max_questions: Number(formData.max_questions),
      });
      router.push(`/dashboard/coding-agent/${session.session_id}`);
    } catch (error) {
      console.error("Failed to start session:", error);
      setIsLoading(false);
    }
  };

  if (showGuidelines) {
    return (
      <div className="max-w-3xl mx-auto space-y-8 p-6 mt-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-[#1C1C1E] border border-[#2C2C2E] rounded-xl p-8"
        >
          <div className="flex items-center space-x-4 mb-8 border-b border-[#2C2C2E] pb-6">
            <div className="p-3 bg-orange-500/10 rounded-xl shrink-0">
              <AlertTriangle className="w-8 h-8 text-orange-500" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Pre-Assessment Guidelines</h2>
              <p className="text-gray-400 mt-1">Please read carefully before starting your session.</p>
            </div>
          </div>

          <div className="space-y-6 mb-10">
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-[#2C2C2E] rounded-lg shrink-0 mt-1">
                <Wifi className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h4 className="text-white font-medium text-lg">Stable Internet Connection</h4>
                <p className="text-gray-400 text-sm mt-1">Ensure you have a continuous, stable Wi-Fi or wired connection. Disconnections may terminate your assessment.</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="p-2 bg-[#2C2C2E] rounded-lg shrink-0 mt-1">
                <Video className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h4 className="text-white font-medium text-lg">Camera & Microphone Required</h4>
                <p className="text-gray-400 text-sm mt-1">Your webcam and microphone must remain on throughout the entire duration of the assessment for proctoring purposes.</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="p-2 bg-[#2C2C2E] rounded-lg shrink-0 mt-1">
                <MonitorOff className="w-5 h-5 text-red-400" />
              </div>
              <div>
                <h4 className="text-white font-medium text-lg">No Tab Switching</h4>
                <p className="text-gray-400 text-sm mt-1">Navigating away from the assessment window, switching tabs, or opening other applications is strictly prohibited and will be flagged.</p>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-6 border-t border-[#2C2C2E]">
            <button
              onClick={() => setShowGuidelines(false)}
              className="px-6 py-2.5 text-gray-400 hover:text-white transition-colors"
            >
              Back
            </button>
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-medium px-8 py-2.5 rounded-lg transition-colors disabled:opacity-50"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <CheckCircle2 className="w-5 h-5" />
                  <span>I Agree, Start Session</span>
                </>
              )}
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 p-6">
      <div className="flex items-center space-x-4 mb-8">
        <div className="p-3 bg-blue-500/10 rounded-xl">
          <Code2 className="w-8 h-8 text-blue-500" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Coding Intelligence Agent
          </h1>
          <p className="text-gray-400 mt-1">
            Configure and launch an adaptive coding assessment session
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Form Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-[#1C1C1E] border border-[#2C2C2E] rounded-xl p-6"
        >
          <h2 className="text-xl font-semibold text-white mb-6">Start Coding Assessment</h2>
          <div className="space-y-4">
            <p className="text-gray-400 text-sm mb-4">
              Click the button below to instantly launch an adaptive coding assessment.
            </p>

            <button
              onClick={() => setShowGuidelines(true)}
              className="w-full mt-6 flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition-colors"
            >
              <>
                <Play className="w-5 h-5" />
                <span>Start Assessment Session</span>
              </>
            </button>
          </div>
        </motion.div>

        {/* Info Section */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-[#1C1C1E] border border-[#2C2C2E] rounded-xl p-6"
          >
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-emerald-500/10 rounded-lg shrink-0">
                <Brain className="w-6 h-6 text-emerald-500" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-white mb-2">Adaptive Evaluation</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  The agent dynamically selects questions from a bank of 120+ problems across 21 categories. 
                  Difficulty scales based on performance, using Bloom's Taxonomy progression.
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-[#1C1C1E] border border-[#2C2C2E] rounded-xl p-6"
          >
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-purple-500/10 rounded-lg shrink-0">
                <Cpu className="w-6 h-6 text-purple-500" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-white mb-2">Secure Sandbox</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Code is executed in isolated Docker containers with memory limits and network restrictions,
                  supporting Python, C++, Java, JS, and C#.
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-[#1C1C1E] border border-[#2C2C2E] rounded-xl p-6"
          >
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-orange-500/10 rounded-lg shrink-0">
                <Layers className="w-6 h-6 text-orange-500" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-white mb-2">Multi-Dimensional Analysis</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Goes beyond pass/fail by statically analyzing Big-O complexity, code smells, 
                  and using AI to evaluate textual explanations and conduct technical Viva follow-ups.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
