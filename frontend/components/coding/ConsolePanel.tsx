"use client";

import { CheckCircle2, XCircle, Clock, AlertCircle, Terminal, Info, ChevronRight, Zap, Code2, BrainCircuit } from "lucide-react";
import { QuestionResponse } from "@/lib/api/coding";
import { motion } from "framer-motion";

interface ConsolePanelProps {
  question: QuestionResponse | null;
  isRunning: boolean;
  isSubmitting: boolean;
  runResult: any;
  submitResult: any;
  activeTab: "testcase" | "console" | "result" | "complexity" | "ai_feedback";
  onTabChange: (tab: "testcase" | "console" | "result" | "complexity" | "ai_feedback") => void;
  onNextQuestion: () => void;
}

export default function ConsolePanel({
  question,
  isRunning,
  isSubmitting,
  runResult,
  submitResult,
  activeTab,
  onTabChange,
  onNextQuestion,
}: ConsolePanelProps) {
  
  const renderTestcases = () => {
    if (!question || !question.public_test_cases) return null;
    return (
      <div className="space-y-4">
        {question.public_test_cases.map((tc, idx) => (
          <div key={idx} className="bg-[#2C2C2E] border border-gray-700 rounded-lg p-4 font-mono text-sm">
            <div className="text-gray-400 mb-2 font-semibold">Testcase {idx + 1}</div>
            <div className="mb-2">
              <span className="text-gray-500 block mb-1">Input:</span>
              <div className="bg-[#1C1C1E] p-2 rounded text-blue-300 whitespace-pre-wrap font-mono text-sm">{typeof tc.input === 'object' ? JSON.stringify(tc.input) : String(tc.input)}</div>
            </div>
            <div>
              <span className="text-gray-500 block mb-1">Expected Output:</span>
              <div className="bg-[#1C1C1E] p-2 rounded text-emerald-300 whitespace-pre-wrap font-mono text-sm">{typeof tc.expected_output === 'object' ? JSON.stringify(tc.expected_output) : String(tc.expected_output)}</div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderConsole = () => {
    if (isRunning) {
      return (
        <div className="flex items-center justify-center h-full space-x-3 text-blue-400">
          <div className="w-5 h-5 border-2 border-blue-400/20 border-t-blue-400 rounded-full animate-spin" />
          <span>Executing code...</span>
        </div>
      );
    }

    if (!runResult) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          <Terminal className="w-8 h-8 mr-3 opacity-50" />
          Run your code to see console output here.
        </div>
      );
    }

    const isError = runResult.exit_code !== 0;

    return (
      <div className="space-y-4 font-mono text-sm">
        <div className={`flex items-center space-x-2 ${isError ? 'text-red-400' : 'text-emerald-400'}`}>
          {isError ? <AlertCircle className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
          <span className="font-semibold">
            {isError ? "Execution Error" : "Execution Finished"}
          </span>
          <span className="text-gray-500 text-xs ml-4">
            ({runResult.execution_time_ms.toFixed(0)} ms)
          </span>
        </div>
        
        {runResult.stdout && (
          <div>
            <div className="text-gray-500 text-xs mb-1 uppercase tracking-wider">Standard Output</div>
            <div className="bg-[#1C1C1E] border border-[#2C2C2E] p-3 rounded-lg text-gray-300 whitespace-pre-wrap">
              {runResult.stdout}
            </div>
          </div>
        )}

        {runResult.stderr && (
          <div>
            <div className="text-gray-500 text-xs mb-1 uppercase tracking-wider">Standard Error</div>
            <div className="bg-red-500/10 border border-red-500/20 p-3 rounded-lg text-red-400 whitespace-pre-wrap">
              {runResult.stderr}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderResult = () => {
    if (isSubmitting) {
      return (
        <div className="flex items-center justify-center h-full space-x-3 text-purple-400">
          <div className="w-5 h-5 border-2 border-purple-400/20 border-t-purple-400 rounded-full animate-spin" />
          <span>Running full test suite & AI analysis...</span>
        </div>
      );
    }

    if (!submitResult) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-4">
          <Info className="w-8 h-8 opacity-50" />
          <div className="text-center">
            <div className="font-medium">Status: Not Evaluated</div>
            <div className="text-sm">Submit your code to see results and analysis.</div>
          </div>
        </div>
      );
    }

    const { test_results, overall_score, correctness_score, complexity_score, quality_score } = submitResult;
    const isSuccess = test_results.pass_rate === 100;

    return (
      <div className="space-y-6">
        {/* Score Breakdown (Replaced old UI) */}
        <div className={`p-4 rounded-xl border ${isSuccess ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              {isSuccess ? <CheckCircle2 className="w-6 h-6 text-emerald-500" /> : <XCircle className="w-6 h-6 text-red-500" />}
              <span className={`text-xl font-bold ${isSuccess ? 'text-emerald-500' : 'text-red-500'}`}>
                {isSuccess ? 'Submission Successful' : 'Submission Failed'}
              </span>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400 uppercase tracking-wider">Overall Score</div>
              <div className="text-2xl font-bold text-white">{overall_score.toFixed(0)}/100</div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm pt-4 border-t border-gray-700/50">
            <div>
              <div className="text-gray-400 mb-1">Correctness</div>
              <div className="font-semibold text-white">{correctness_score.toFixed(0)} / 100</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Complexity</div>
              <div className="font-semibold text-white">{complexity_score.toFixed(0)} / 100</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Code Quality</div>
              <div className="font-semibold text-white">{quality_score.toFixed(0)} / 100</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Explanation</div>
              <div className="font-semibold text-gray-500">Pending</div>
            </div>
          </div>
          
          <div className="mt-6">
             <button
                onClick={onNextQuestion}
                className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-colors"
              >
                <span>Continue Assessment</span>
                <ChevronRight className="w-4 h-4" />
             </button>
          </div>
        </div>

        {/* Test Cases (Hidden Inputs masked) */}
        <div>
          <h3 className="text-white font-medium mb-3">Test Cases</h3>
          <div className="space-y-2">
            {test_results.results.map((tc: any, idx: number) => (
              <div 
                key={idx} 
                className={`flex flex-col p-3 rounded-lg border ${
                  tc.verdict === 'accepted' 
                    ? 'bg-emerald-500/5 border-emerald-500/20' 
                    : 'bg-red-500/5 border-red-500/20'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {tc.verdict === 'accepted' 
                      ? <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                      : <XCircle className="w-5 h-5 text-red-500" />
                    }
                    <span className="text-gray-300 font-medium">
                      Test Case {idx + 1} {tc.is_hidden && <span className="text-xs text-gray-500 ml-2">(Hidden)</span>}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-gray-400 flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      {tc.execution_time_ms.toFixed(0)} ms
                    </span>
                  </div>
                </div>

                {tc.verdict !== 'accepted' && (
                  <div className="mt-3 bg-[#1C1C1E] p-3 rounded-md font-mono text-sm space-y-2 border border-gray-700/50">
                    <div className="text-red-400 font-bold mb-2">{tc.verdict.replace(/_/g, ' ').toUpperCase()}</div>
                    
                    {!tc.is_hidden ? (
                      <>
                        <div>
                          <span className="text-gray-500">Expected:</span>
                          <div className="text-emerald-300 whitespace-pre-wrap">{typeof tc.expected_output === 'object' ? JSON.stringify(tc.expected_output) : String(tc.expected_output)}</div>
                        </div>
                        <div>
                          <span className="text-gray-500">Received:</span>
                          <div className="text-red-300 whitespace-pre-wrap">
                            {tc.actual_output ? (typeof tc.actual_output === 'object' ? JSON.stringify(tc.actual_output) : String(tc.actual_output)) : (tc.error ? "No output" : "")}
                          </div>
                        </div>
                        {tc.error && (
                          <div className="mt-2 pt-2 border-t border-red-500/20">
                            <span className="text-red-400 font-semibold mb-1 block">Error:</span>
                            <div className="text-red-300 whitespace-pre-wrap text-xs">{String(tc.error)}</div>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-gray-400 italic">
                        Hidden test case failed. Details are kept hidden.
                        {tc.error && <div className="text-red-400 mt-2 not-italic">Error: {tc.error}</div>}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderComplexity = () => {
    if (!submitResult) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-4">
          <Zap className="w-8 h-8 opacity-50" />
          <div className="text-center">
            <div className="font-medium">Status: Not Evaluated</div>
            <div className="text-sm">Submit your code to see complexity analysis.</div>
          </div>
        </div>
      );
    }
    
    const { complexity_analysis } = submitResult;
    
    return (
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-[#2C2C2E] border border-gray-700 p-5 rounded-xl">
          <div className="flex items-center space-x-2 text-gray-400 mb-4 font-semibold uppercase tracking-wider text-xs">
            <Clock className="w-4 h-4" />
            <span>Time Complexity</span>
          </div>
          <div className="text-3xl font-mono text-blue-400 mb-4">{complexity_analysis.estimated_time_complexity}</div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Expected</span>
              <span className="text-gray-300 font-mono">{question?.expected_time_complexity || 'O(n)'}</span>
            </div>
            <div className="flex justify-between border-t border-gray-700/50 pt-2">
              <span className="text-gray-500">Status</span>
              <span className={complexity_analysis.matches_expected ? "text-emerald-400 font-medium" : "text-orange-400 font-medium"}>
                {complexity_analysis.matches_expected ? "Optimal ✓" : "Suboptimal"}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-[#2C2C2E] border border-gray-700 p-5 rounded-xl">
          <div className="flex items-center space-x-2 text-gray-400 mb-4 font-semibold uppercase tracking-wider text-xs">
            <Zap className="w-4 h-4" />
            <span>Space Complexity</span>
          </div>
          <div className="text-3xl font-mono text-blue-400 mb-4">{complexity_analysis.estimated_space_complexity}</div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Expected</span>
              <span className="text-gray-300 font-mono">{question?.expected_space_complexity || 'O(1)'}</span>
            </div>
            <div className="flex justify-between border-t border-gray-700/50 pt-2">
              <span className="text-gray-500">Status</span>
              <span className="text-emerald-400 font-medium">Analyzed ✓</span>
            </div>
          </div>
        </div>
        
        <div className="col-span-1 md:col-span-2 bg-[#2C2C2E] border border-gray-700 p-5 rounded-xl mt-2 text-sm text-gray-300">
          <span className="font-semibold text-gray-400">Analysis Details: </span>
          {complexity_analysis.analysis_details}
        </div>
      </div>
    );
  };

  const renderAIFeedback = () => {
    if (!submitResult) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-4">
          <BrainCircuit className="w-8 h-8 opacity-50" />
          <div className="text-center">
            <div className="font-medium">Status: Not Evaluated</div>
            <div className="text-sm">Submit your code to see AI feedback and static analysis.</div>
          </div>
        </div>
      );
    }
    
    const { static_analysis } = submitResult;
    
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between p-4 bg-[#2C2C2E] border border-gray-700 rounded-xl">
          <div>
            <h3 className="text-white font-medium">AI Code Review</h3>
            <p className="text-sm text-gray-400 mt-1">Static code analysis and maintainability heuristics.</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-purple-400">{static_analysis.maintainability_score}</div>
            <div className="text-xs text-gray-500 uppercase tracking-wider">Maintainability</div>
          </div>
        </div>

        <div className="space-y-3">
          {static_analysis.issues && static_analysis.issues.length > 0 ? (
            static_analysis.issues.map((issue: any, idx: number) => (
              <div key={idx} className="flex items-start space-x-3 p-4 bg-[#2C2C2E] border border-gray-700 rounded-xl text-sm">
                <AlertCircle className={`w-5 h-5 shrink-0 mt-0.5 ${
                  issue.severity === 'error' ? 'text-red-400' : 
                  issue.severity === 'warning' ? 'text-orange-400' : 'text-blue-400'
                }`} />
                <div>
                  <div className="text-gray-200 font-medium mb-1 capitalize">{issue.category.replace(/_/g, ' ')}</div>
                  <div className="text-gray-400">{issue.message}</div>
                  {issue.line > 0 && (
                    <div className="text-gray-500 text-xs mt-2 font-mono">Found at line {issue.line}</div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="flex items-start space-x-3 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-sm">
               <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
               <div>
                  <div className="text-emerald-400 font-medium mb-1">Excellent Code Quality</div>
                  <div className="text-gray-400">No major code smells, security flaws, or high cyclomatic complexity found!</div>
               </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const tabs = [
    { id: "testcase", label: "Testcase" },
    { id: "console", label: "Console" },
    { id: "result", label: "Result" },
    { id: "complexity", label: "Complexity" },
    { id: "ai_feedback", label: "AI Feedback" },
  ] as const;

  return (
    <div className="flex flex-col h-full bg-[#1C1C1E] rounded-b-xl">
      {/* Tabs */}
      <div className="flex bg-[#2C2C2E]/50 px-2 pt-2 border-b border-[#2C2C2E] shrink-0 overflow-x-auto scrollbar-hide">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors border-t border-l border-r rounded-t-lg mx-0.5 ${
              activeTab === tab.id 
                ? "text-gray-200 bg-[#1C1C1E] border-[#2C2C2E]" 
                : "text-gray-500 border-transparent hover:text-gray-300 hover:bg-[#2C2C2E]"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        {activeTab === "testcase" && renderTestcases()}
        {activeTab === "console" && renderConsole()}
        {activeTab === "result" && renderResult()}
        {activeTab === "complexity" && renderComplexity()}
        {activeTab === "ai_feedback" && renderAIFeedback()}
      </div>
    </div>
  );
}
