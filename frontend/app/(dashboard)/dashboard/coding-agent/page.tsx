"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Play, Code2, Cpu, Brain, Layers } from "lucide-react";
import { startSession } from "@/lib/api/coding";
import { motion } from "framer-motion";

export default function CodingAgentLanding() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    candidate_name: "John Doe",
    candidate_email: "john@example.com",
    department: "Software Engineering",
    programming_language: "python",
    difficulty: "medium",
    max_questions: 5,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
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
          <h2 className="text-xl font-semibold text-white mb-6">Session Configuration</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">
                Candidate Name
              </label>
              <input
                type="text"
                name="candidate_name"
                value={formData.candidate_name}
                onChange={handleChange}
                className="w-full bg-[#2C2C2E] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">
                Candidate Email
              </label>
              <input
                type="email"
                name="candidate_email"
                value={formData.candidate_email}
                onChange={handleChange}
                className="w-full bg-[#2C2C2E] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Language
                </label>
                <select
                  name="programming_language"
                  value={formData.programming_language}
                  onChange={handleChange}
                  className="w-full bg-[#2C2C2E] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="python">Python</option>
                  <option value="cpp">C++</option>
                  <option value="java">Java</option>
                  <option value="javascript">JavaScript</option>
                  <option value="csharp">C#</option>
                  <option value="c">C</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Starting Difficulty
                </label>
                <select
                  name="difficulty"
                  value={formData.difficulty}
                  onChange={handleChange}
                  className="w-full bg-[#2C2C2E] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">
                Number of Questions
              </label>
              <input
                type="number"
                name="max_questions"
                value={formData.max_questions}
                onChange={handleChange}
                min="1"
                max="20"
                className="w-full bg-[#2C2C2E] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-6 flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition-colors disabled:opacity-50"
            >
              {isLoading ? (
                <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Start Assessment Session</span>
                </>
              )}
            </button>
          </form>
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
