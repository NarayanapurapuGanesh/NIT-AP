import React from "react";
import { CheckCircle2, XCircle, Clock, Code2, Brain, AlertTriangle, ArrowRight, Zap, Award, Target, Beaker, FileCode2, Layers } from "lucide-react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

interface AssessmentReportProps {
  report: any;
  onClose?: () => void;
}

export default function AssessmentReport({ report, onClose }: AssessmentReportProps) {
  const router = useRouter();

  if (!report) return null;

  const { overall_assessment, session, submissions } = report;

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case "A": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "B": return "text-sky-400 bg-sky-500/10 border-sky-500/20";
      case "C": return "text-amber-400 bg-amber-500/10 border-amber-500/20";
      case "D": return "text-orange-400 bg-orange-500/10 border-orange-500/20";
      default: return "text-red-400 bg-red-500/10 border-red-500/20";
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#141415] text-slate-200 overflow-y-auto p-6 md:p-10 space-y-8">
      {/* Header Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-8 rounded-2xl bg-gradient-to-r from-[#1C1C1E] to-[#252528] border border-[#2C2C2E] shadow-xl"
      >
        <div className="space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-wider">
            <CheckCircle2 className="h-4 w-4" />
            <span>Assessment Complete</span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Final Coding Dossier</h1>
          <p className="text-sm text-gray-400">
            Session ID: <span className="font-mono text-xs">{session?.id}</span> • Completed on {new Date(report.generated_at).toLocaleDateString()}
          </p>
        </div>
        
        <div className="flex items-center gap-6 text-center">
          <div>
            <p className="text-[11px] text-gray-400 uppercase font-semibold mb-1">Total Score</p>
            <div className="text-4xl font-black font-mono text-white">
              {overall_assessment?.total_score}<span className="text-xl text-gray-500">/100</span>
            </div>
          </div>
          <div className={`flex flex-col items-center justify-center w-20 h-20 rounded-2xl border ${getGradeColor(overall_assessment?.grade)}`}>
            <span className="text-[10px] uppercase font-bold opacity-80 mb-1">Grade</span>
            <span className="text-4xl font-black">{overall_assessment?.grade}</span>
          </div>
        </div>
      </motion.div>

      {/* Summary Stats */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <div className="p-6 rounded-xl bg-[#1C1C1E] border border-[#2C2C2E] flex flex-col justify-between">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2.5 rounded-lg bg-sky-500/10 text-sky-400"><Target className="h-5 w-5" /></div>
            <h3 className="font-semibold text-white">Recommendation</h3>
          </div>
          <p className="text-lg font-bold text-sky-400">{overall_assessment?.recommendation || "Needs Review"}</p>
        </div>
        
        <div className="p-6 rounded-xl bg-[#1C1C1E] border border-[#2C2C2E] flex flex-col justify-between">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400"><Code2 className="h-5 w-5" /></div>
            <h3 className="font-semibold text-white">Questions Attempted</h3>
          </div>
          <p className="text-3xl font-bold font-mono text-white">{overall_assessment?.questions_attempted}</p>
        </div>

        <div className="p-6 rounded-xl bg-[#1C1C1E] border border-[#2C2C2E] flex flex-col justify-between">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400"><Clock className="h-5 w-5" /></div>
            <h3 className="font-semibold text-white">Language</h3>
          </div>
          <p className="text-xl font-bold text-white capitalize">{session?.programming_language}</p>
        </div>
      </motion.div>

      {/* Submissions Breakdown */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center mb-4">
          <Layers className="h-5 w-5 mr-2 text-sky-400" />
          Submission Details
        </h2>
        
        {submissions && submissions.map((sub: any, idx: number) => (
          <motion.div 
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 + (idx * 0.1) }}
            className="p-6 rounded-xl bg-[#1C1C1E] border border-[#2C2C2E] space-y-4 hover:border-gray-600 transition-colors"
          >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-[#2C2C2E] pb-4">
              <div>
                <div className="flex items-center space-x-3 mb-1">
                  <span className="text-sm font-bold text-gray-400">Q{idx + 1}</span>
                  <h3 className="text-lg font-bold text-white">{sub.question.title}</h3>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    sub.question.difficulty === 'easy' ? 'bg-emerald-500/20 text-emerald-400' :
                    sub.question.difficulty === 'medium' ? 'bg-amber-500/20 text-amber-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {sub.question.difficulty}
                  </span>
                </div>
                <p className="text-xs text-gray-500 capitalize">{sub.question.category} • {sub.question.bloom_level}</p>
              </div>
              <div className="text-right">
                <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Score</p>
                <div className="text-2xl font-black font-mono text-white">
                  {sub.scores?.overall || 0}<span className="text-sm text-gray-500">/100</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
              <div className="bg-[#141415] rounded-lg p-3 text-center border border-[#252528]">
                <div className="text-xs text-gray-500 font-semibold mb-1 flex items-center justify-center">
                  <Beaker className="h-3 w-3 mr-1" /> Tests
                </div>
                <div className="font-mono font-bold text-sky-400">{sub.scores?.correctness || 0}/100</div>
              </div>
              <div className="bg-[#141415] rounded-lg p-3 text-center border border-[#252528]">
                <div className="text-xs text-gray-500 font-semibold mb-1 flex items-center justify-center">
                  <Zap className="h-3 w-3 mr-1" /> Complexity
                </div>
                <div className="font-mono font-bold text-indigo-400">{sub.scores?.complexity || 0}/100</div>
                <div className="text-[9px] text-gray-600 mt-1">{sub.complexity?.estimated_time_complexity || "Unknown"}</div>
              </div>
              <div className="bg-[#141415] rounded-lg p-3 text-center border border-[#252528]">
                <div className="text-xs text-gray-500 font-semibold mb-1 flex items-center justify-center">
                  <Award className="h-3 w-3 mr-1" /> Quality
                </div>
                <div className="font-mono font-bold text-amber-400">{sub.scores?.quality || 0}/100</div>
                <div className="text-[9px] text-gray-600 mt-1">{sub.static_analysis?.issues_found || 0} Issues</div>
              </div>
              <div className="bg-[#141415] rounded-lg p-3 text-center border border-[#252528]">
                <div className="text-xs text-gray-500 font-semibold mb-1 flex items-center justify-center">
                  <Brain className="h-3 w-3 mr-1" /> Approach
                </div>
                <div className="font-mono font-bold text-pink-400">{sub.scores?.explanation || sub.scores?.overall || 0}/100</div>
              </div>
            </div>
            
            {/* Code Snippet Preview */}
            <div className="mt-4 p-4 rounded-lg bg-[#0D0D0D] border border-[#252528] overflow-x-auto relative group">
              <FileCode2 className="h-4 w-4 text-gray-600 absolute top-3 right-3 opacity-50" />
              <pre className="text-[11px] font-mono text-gray-400 leading-relaxed max-h-32 overflow-y-hidden group-hover:max-h-64 transition-all">
                {sub.submission.source_code}
              </pre>
            </div>
          </motion.div>
        ))}
        {(!submissions || submissions.length === 0) && (
          <div className="p-8 text-center bg-[#1C1C1E] rounded-xl border border-[#2C2C2E]">
            <p className="text-gray-500 text-sm">No submissions recorded for this session.</p>
          </div>
        )}
      </div>

      <div className="pt-6 flex justify-center pb-12">
        <button
          onClick={() => {
            if (onClose) onClose();
            router.push("/dashboard/coding-agent");
          }}
          className="flex items-center space-x-2 px-8 py-3 bg-white text-black rounded-lg font-bold hover:bg-gray-200 transition-colors shadow-[0_0_20px_rgba(255,255,255,0.15)]"
        >
          <span>Return to Dashboard</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}


