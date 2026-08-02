"use client";

import { useState } from "react";
import { QuestionResponse } from "@/lib/api/coding";
import { Building2, CheckCircle2, ChevronRight, Hash, Network, ScrollText, AlertCircle, Lightbulb } from "lucide-react";

interface ProblemDescriptionProps {
  question: QuestionResponse;
}

type TabType = "description" | "hints" | "submissions";

export default function ProblemDescription({ question }: ProblemDescriptionProps) {
  const [activeTab, setActiveTab] = useState<TabType>("description");

  const getDifficultyColor = (diff: string) => {
    switch (diff.toLowerCase()) {
      case "easy": return "text-emerald-500";
      case "medium": return "text-orange-500";
      case "hard": return "text-red-500";
      default: return "text-gray-500";
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#1C1C1E] text-gray-300">
      {/* Tabs */}
      <div className="flex border-b border-[#2C2C2E] px-2 shrink-0">
        <button
          onClick={() => setActiveTab("description")}
          className={`flex items-center px-4 py-2.5 text-sm font-medium transition-colors border-b-2 ${
            activeTab === "description" ? "border-blue-500 text-blue-500" : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          <ScrollText className="w-4 h-4 mr-2" />
          Description
        </button>
        <button
          onClick={() => setActiveTab("hints")}
          className={`flex items-center px-4 py-2.5 text-sm font-medium transition-colors border-b-2 ${
            activeTab === "hints" ? "border-blue-500 text-blue-500" : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          <Lightbulb className="w-4 h-4 mr-2" />
          Hints
        </button>
        <button
          onClick={() => setActiveTab("submissions")}
          className={`flex items-center px-4 py-2.5 text-sm font-medium transition-colors border-b-2 ${
            activeTab === "submissions" ? "border-blue-500 text-blue-500" : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          <CheckCircle2 className="w-4 h-4 mr-2" />
          Submissions
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {activeTab === "description" && (
          <>
            {/* Header / Title */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-3">
                {question.title}
              </h2>
              
              {/* DSA Metadata */}
              <div className="flex flex-wrap items-center gap-3 text-xs mb-6">
                <span className={`font-semibold ${getDifficultyColor(question.difficulty)}`}>
                  {question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)}
                </span>
                
                <span className="text-gray-600">|</span>
                
                <span className="flex items-center text-gray-400 bg-gray-800/50 px-2 py-0.5 rounded">
                  <Hash className="w-3 h-3 mr-1 text-gray-500" />
                  {question.category.replace(/_/g, " ")}
                </span>
                
                <span className="flex items-center text-gray-400 bg-gray-800/50 px-2 py-0.5 rounded">
                  <Network className="w-3 h-3 mr-1 text-gray-500" />
                  Expected: {question.expected_time_complexity || "O(n)"}
                </span>

                <span className="flex items-center text-emerald-400/80 bg-emerald-900/20 px-2 py-0.5 rounded">
                  <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-500/80" />
                  Acceptance: 68%
                </span>
              </div>
            </div>

            {/* Main Description */}
            <div className="prose prose-invert max-w-none text-sm text-gray-300 leading-relaxed">
              <div dangerouslySetInnerHTML={{ __html: question.description.replace(/\n/g, '<br/>') }} />
            </div>

            {/* Examples */}
            {question.public_test_cases && question.public_test_cases.length > 0 && (
              <div className="mt-8 space-y-4">
                <h3 className="text-base font-semibold text-white">Examples</h3>
                {question.public_test_cases.map((tc, idx) => (
                  <div key={idx} className="bg-gray-800/40 border border-gray-700/50 rounded-lg p-4 font-mono text-sm space-y-2">
                    <div>
                      <span className="text-gray-400 font-semibold select-none">Input: </span>
                      <span className="text-blue-300 whitespace-pre-wrap">{typeof tc.input === 'object' ? JSON.stringify(tc.input) : String(tc.input)}</span>
                    </div>
                    <div>
                      <span className="text-gray-400 font-semibold select-none">Output: </span>
                      <span className="text-emerald-300 whitespace-pre-wrap">{typeof tc.expected_output === 'object' ? JSON.stringify(tc.expected_output) : String(tc.expected_output)}</span>
                    </div>
                    {tc.description && (
                      <div className="text-gray-400 mt-2 text-xs font-sans border-t border-gray-700/50 pt-2">
                        <span className="font-semibold">Explanation: </span>
                        {tc.description}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Constraints */}
            {question.constraints && (
              <div className="mt-8">
                <h3 className="text-base font-semibold text-white mb-3">Constraints</h3>
                <div className="bg-gray-800/40 border border-gray-700/50 rounded-lg p-4 font-mono text-sm text-gray-400">
                  <div dangerouslySetInnerHTML={{ __html: question.constraints.replace(/\n/g, '<br/>') }} />
                </div>
              </div>
            )}
          </>
        )}

        {activeTab === "hints" && (
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-white mb-4 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-yellow-500" />
              Problem Hints
            </h3>
            {question.hints && question.hints.length > 0 ? (
              question.hints.map((hint, idx) => (
                <div key={idx} className="bg-gray-800/40 border border-gray-700/50 p-4 rounded-lg text-sm text-gray-300">
                  <div className="font-semibold text-gray-400 mb-1 text-xs">Hint {idx + 1}</div>
                  {hint}
                </div>
              ))
            ) : (
              <div className="text-sm text-gray-500 italic">No hints available for this problem.</div>
            )}
          </div>
        )}

        {activeTab === "submissions" && (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <AlertCircle className="w-12 h-12 mb-4 text-gray-600" />
            <p>Your previous submissions will appear here.</p>
          </div>
        )}
      </div>
    </div>
  );
}
