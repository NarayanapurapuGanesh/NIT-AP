"use client";

import { CheckCircle2, XCircle, Clock, AlertCircle } from "lucide-react";

interface TestResultsPanelProps {
  isRunning: boolean;
  isSubmitting: boolean;
  runResult: any;
  submitResult: any;
  activeTab: "run" | "submit";
  onTabChange: (tab: "run" | "submit") => void;
}

export default function TestResultsPanel({
  isRunning,
  isSubmitting,
  runResult,
  submitResult,
  activeTab,
  onTabChange,
}: TestResultsPanelProps) {
  
  const renderRunResult = () => {
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

  const renderSubmitResult = () => {
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
        <div className="flex items-center justify-center h-full text-gray-500">
          Submit your code to see test results and AI analysis.
        </div>
      );
    }

    const { test_results, complexity_analysis, static_analysis, overall_score } = submitResult;

    return (
      <div className="space-y-6">
        {/* Score Overview */}
        <div className="flex items-center space-x-6 bg-[#2C2C2E] p-4 rounded-xl border border-gray-700">
          <div className="flex flex-col items-center justify-center px-4 border-r border-gray-700">
            <span className="text-3xl font-bold text-white">{overall_score.toFixed(0)}</span>
            <span className="text-xs text-gray-400 uppercase tracking-wider mt-1">Overall</span>
          </div>
          <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm flex-1">
            <div className="flex justify-between">
              <span className="text-gray-400">Tests Passed</span>
              <span className={test_results.pass_rate === 100 ? "text-emerald-400" : "text-orange-400"}>
                {test_results.passed} / {test_results.total}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Time Complexity</span>
              <span className="text-blue-400 font-mono">{complexity_analysis.estimated_time_complexity}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Code Quality</span>
              <span className="text-purple-400">{static_analysis.maintainability_score}/100</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Space Complexity</span>
              <span className="text-blue-400 font-mono">{complexity_analysis.estimated_space_complexity}</span>
            </div>
          </div>
        </div>

        {/* Test Cases */}
        <div>
          <h3 className="text-white font-medium mb-3">Test Cases</h3>
          <div className="space-y-2">
            {test_results.results.map((tc: any, idx: number) => (
              <div 
                key={idx} 
                className={`flex items-center justify-between p-3 rounded-lg border ${
                  tc.verdict === 'accepted' 
                    ? 'bg-emerald-500/5 border-emerald-500/20' 
                    : 'bg-red-500/5 border-red-500/20'
                }`}
              >
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
                  <span className={`font-mono ${tc.verdict === 'accepted' ? 'text-emerald-400' : 'text-red-400'}`}>
                    {tc.verdict.replace(/_/g, ' ').toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Static Analysis Warnings */}
        {static_analysis.issues && static_analysis.issues.length > 0 && (
          <div>
            <h3 className="text-white font-medium mb-3">Code Quality Suggestions</h3>
            <div className="space-y-2">
              {static_analysis.issues.map((issue: any, idx: number) => (
                <div key={idx} className="flex items-start space-x-3 p-3 bg-[#2C2C2E] border border-gray-700 rounded-lg text-sm">
                  <AlertCircle className={`w-5 h-5 shrink-0 mt-0.5 ${
                    issue.severity === 'error' ? 'text-red-400' : 
                    issue.severity === 'warning' ? 'text-orange-400' : 'text-blue-400'
                  }`} />
                  <div>
                    <div className="text-gray-300">{issue.message}</div>
                    {issue.line > 0 && (
                      <div className="text-gray-500 text-xs mt-1">Line {issue.line}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-[#1C1C1E]">
      {/* Tabs */}
      <div className="flex border-b border-[#2C2C2E]">
        <button
          onClick={() => onTabChange("run")}
          className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "run" 
              ? "text-blue-400 border-blue-400 bg-blue-400/5" 
              : "text-gray-400 border-transparent hover:text-gray-300 hover:bg-white/5"
          }`}
        >
          Console Output
        </button>
        <button
          onClick={() => onTabChange("submit")}
          className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "submit" 
              ? "text-purple-400 border-purple-400 bg-purple-400/5" 
              : "text-gray-400 border-transparent hover:text-gray-300 hover:bg-white/5"
          }`}
        >
          Test Results & Analysis
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === "run" ? renderRunResult() : renderSubmitResult()}
      </div>
    </div>
  );
}
