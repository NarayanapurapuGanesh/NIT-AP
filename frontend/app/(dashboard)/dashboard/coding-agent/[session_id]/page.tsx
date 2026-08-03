"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Clock, ChevronRight } from "lucide-react";
import { Panel, Group as PanelGroup, Separator as PanelResizeHandle } from "react-resizable-panels";
import { getSession, getNextQuestion, runCode, submitCode, QuestionResponse, SessionResponse } from "@/lib/api/coding";
import CodeEditor from "@/components/coding/CodeEditor";
import ProblemDescription from "@/components/coding/ProblemDescription";
import ConsolePanel from "@/components/coding/ConsolePanel";
import EditorToolbar from "@/components/coding/EditorToolbar";
import { motion } from "framer-motion";

export default function CodingArena() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.session_id as string;

  const [session, setSession] = useState<SessionResponse | null>(null);
  const [question, setQuestion] = useState<QuestionResponse | null>(null);
  const [code, setCode] = useState<string>("");
  const [language, setLanguage] = useState<string>("python");
  const [codeCache, setCodeCache] = useState<Record<string, string>>({});
  const [timeLeft, setTimeLeft] = useState(45 * 60);
  
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(1);
  
  const [runResult, setRunResult] = useState<any>(null);
  const [submitResult, setSubmitResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<"testcase" | "console" | "result" | "complexity" | "ai_feedback">("testcase");

  const [theme, setTheme] = useState("vs-dark");
  const [fontSize, setFontSize] = useState(14);
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const sess = await getSession(sessionId);
        setSession(sess);

        if (sess.status === "completed") {
          alert("This session is already completed!");
          return;
        }

        const q = await getNextQuestion(sessionId);
        setQuestion(q);
        setCurrentQuestionIndex(sess.questions_answered + 1);
        
        if (q.starter_code && q.starter_code[sess.programming_language]) {
          setCode(q.starter_code[sess.programming_language]);
          setCodeCache({ [sess.programming_language]: q.starter_code[sess.programming_language] });
        }
        setLanguage(sess.programming_language);
      } catch (err) {
        console.error("Failed to load arena:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, [sessionId]);

  useEffect(() => {
    if (!session || !session.started_at || session.status === "completed") return;
    const startTime = new Date(session.started_at + "Z").getTime();
    const duration = 45 * 60 * 1000;
    
    const updateTimer = () => {
      const now = new Date().getTime();
      const diff = Math.max(0, Math.floor((duration - (now - startTime)) / 1000));
      setTimeLeft(diff);
      if (diff <= 0) {
        clearInterval(timerId);
        alert("Time is up! The session has ended.");
        router.push("/dashboard/coding-agent");
      }
    };
    
    updateTimer();
    const timerId = setInterval(updateTimer, 1000);
    return () => clearInterval(timerId);
  }, [session, router]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleRun = useCallback(async () => {
    if (!question || !session || isRunning || isSubmitting) return;
    if (!code.trim()) {
      alert("Please write some code before running.");
      return;
    }
    setIsRunning(true);
    setActiveTab("console");
    setRunResult(null);
    try {
      const stdin = question.public_test_cases?.[0]?.input || "";
      const result = await runCode({
        source_code: code,
        language: language,
        stdin,
      });
      setRunResult(result);
    } catch (err) {
      console.error(err);
    } finally {
      setIsRunning(false);
    }
  }, [question, session, code, isRunning, isSubmitting]);

  const handleSubmit = useCallback(async () => {
    if (!question || !session || isRunning || isSubmitting) return;
    if (!code.trim()) {
      alert("Please write some code before submitting.");
      return;
    }
    setIsSubmitting(true);
    setActiveTab("result");
    setSubmitResult(null);
    try {
      const result = await submitCode({
        session_id: sessionId,
        question_id: question.id,
        source_code: code,
        language: language,
      });
      setSubmitResult(result);
      
      if (session) {
        setSession({
          ...session,
          questions_answered: session.questions_answered + 1,
          total_score: result.overall_score,
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  }, [question, session, code, isRunning, isSubmitting, sessionId]);

  const handleNextQuestion = async () => {
    setIsLoading(true);
    setSubmitResult(null);
    setRunResult(null);
    setActiveTab("testcase");
    try {
      const sess = await getSession(sessionId);
      const q = await getNextQuestion(sessionId);
      setQuestion(q);
      setCurrentQuestionIndex(sess.questions_answered + 1);
      
      
      setCodeCache({});
      if (q.starter_code && q.starter_code[language]) {
        setCode(q.starter_code[language]);
        setCodeCache({ [language]: q.starter_code[language] });
      } else {
        const defaultCode = language === "python" ? "def solution():\n    pass" :
                            language === "cpp" ? "#include <iostream>\n#include <vector>\nusing namespace std;\n\n// Your code here" :
                            language === "java" ? "class Solution {\n    // Your code here\n}" : "// Your code here";
        setCode(defaultCode);
        setCodeCache({ [language]: defaultCode });
      }
    } catch (err) {
      const sess = await getSession(sessionId);
      if (sess.status === "completed") {
        router.push("/dashboard/coding-agent");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    if (confirm("Reset to starter code? Current changes will be lost.")) {
      if (question?.starter_code) {
        setCode(question.starter_code[language] || "");
      }
    }
  };

  const handleLanguageChange = (newLang: string) => {
    setCodeCache(prev => ({ ...prev, [language]: code }));
    setLanguage(newLang);
    
    if (codeCache[newLang]) {
      setCode(codeCache[newLang]);
    } else if (question?.starter_code && question.starter_code[newLang]) {
      setCode(question.starter_code[newLang]);
    } else {
      const defaultCode = newLang === "python" ? "def solution():\n    pass" :
                          newLang === "cpp" ? "#include <iostream>\n#include <vector>\nusing namespace std;\n\n// Your code here" :
                          newLang === "java" ? "class Solution {\n    // Your code here\n}" : "// Your code here";
      setCode(defaultCode);
    }
  };

  const handleFormat = () => {
    if (editorRef.current && monacoRef.current) {
      if (session?.programming_language === 'python') {
        alert("Native code formatting for Python is not supported in the browser. Please format your code manually.");
        return;
      }
      const action = editorRef.current.getAction('editor.action.formatDocument');
      if (action) {
        action.run();
      } else {
        alert("Code formatting is not supported for this language.");
      }
    }
  };

  const handleEditorMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Keyboard Shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      handleRun();
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter, () => {
      handleSubmit();
    });
  };

  if (isLoading || !question || !session) {
    return (
      <div className="flex items-center justify-center h-full min-h-screen bg-[#0C0C0E]">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-10 h-10 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
          <div className="text-gray-400 font-medium">Preparing Coding Arena...</div>
        </div>
      </div>
    );
  }

  const isCompleted = session.status === "completed";

  return (
    <div className="flex flex-col h-screen bg-[#0C0C0E] overflow-hidden font-sans">
      {/* LeetCode Style Professional Header */}
      <header className="h-14 bg-[#1C1C1E] border-b border-[#2C2C2E] flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center space-x-6">
          <div className="font-bold text-white text-lg tracking-tight">FacultyIQ</div>
          <div className="flex items-center space-x-3 text-sm">
            <span className="text-gray-400">Assessment:</span>
            <span className="text-gray-200 font-medium bg-[#2C2C2E] px-3 py-1 rounded-full">
              Question {currentQuestionIndex} / {session.max_questions}
            </span>
          </div>
        </div>
        
        <div className="flex items-center space-x-6">
          {/* Progress Breakdown */}
          <div className="flex items-center space-x-3 text-sm">
             <span className="flex items-center text-emerald-400"><span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5"/>2 Easy</span>
             <span className="flex items-center text-orange-400"><span className="w-2 h-2 rounded-full bg-orange-400 mr-1.5"/>2 Med</span>
             <span className="flex items-center text-red-400"><span className="w-2 h-2 rounded-full bg-red-400 mr-1.5"/>1 Hard</span>
          </div>
          
          <div className="w-px h-5 bg-gray-700" />
          
          <div className="flex items-center text-gray-300 font-mono bg-gray-800/50 px-3 py-1.5 rounded-md border border-gray-700/50">
             <Clock className="w-4 h-4 mr-2 text-gray-400" />
             {formatTime(timeLeft)}
          </div>

          <button
            onClick={handleNextQuestion}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-md font-medium text-sm transition-colors"
          >
            <span>Next Question</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main Split Layout using react-resizable-panels */}
      <div className="flex-1 flex overflow-hidden p-1">
        <PanelGroup orientation="horizontal" id="coding-arena-horizontal">
          
          {/* Left: Problem Description */}
          <Panel defaultSize={40} minSize={25} className="rounded-xl overflow-hidden border border-[#2C2C2E] m-1 bg-[#1C1C1E]">
            <ProblemDescription question={question} />
          </Panel>

          <PanelResizeHandle className="w-2 hover:bg-blue-500/50 transition-colors cursor-col-resize group flex items-center justify-center">
            <div className="h-8 w-1 bg-gray-700 group-hover:bg-blue-400 rounded-full transition-colors" />
          </PanelResizeHandle>

          {/* Right: Editor and Results */}
          <Panel defaultSize={60} minSize={30} className="m-1 flex flex-col min-h-0 bg-[#0C0C0E]">
            <PanelGroup orientation="vertical" id="coding-arena-vertical">
              
              {/* Top Right: Monaco Editor */}
              <Panel defaultSize={65} minSize={20} className="rounded-xl overflow-hidden border border-[#2C2C2E] flex flex-col bg-[#1C1C1E]">
                <EditorToolbar 
                  language={language}
                  setLanguage={handleLanguageChange}
                  theme={theme}
                  setTheme={setTheme}
                  fontSize={fontSize}
                  setFontSize={setFontSize}
                  onReset={handleReset}
                  onFormat={handleFormat}
                  onRun={handleRun}
                  onSubmit={handleSubmit}
                  isExecuting={isRunning || isSubmitting || isCompleted}
                />
                <div className="flex-1 min-h-0 relative">
                  <CodeEditor
                    language={language}
                    value={code}
                    onChange={(val) => setCode(val || "")}
                    readOnly={isSubmitting || isCompleted}
                    theme={theme}
                    fontSize={fontSize}
                    onMount={handleEditorMount}
                  />
                  {/* Keyboard Shortcuts Hint Overlay */}
                  <div className="absolute bottom-2 right-4 text-[10px] text-gray-600 font-mono select-none pointer-events-none">
                    Ctrl+Enter: Run | Ctrl+Shift+Enter: Submit
                  </div>
                </div>
              </Panel>

              <PanelResizeHandle className="h-2 hover:bg-blue-500/50 transition-colors cursor-row-resize group flex items-center justify-center">
                <div className="w-8 h-1 bg-gray-700 group-hover:bg-blue-400 rounded-full transition-colors" />
              </PanelResizeHandle>

              {/* Bottom Right: Console & Results */}
              <Panel defaultSize={35} minSize={20} className="rounded-xl overflow-hidden border border-[#2C2C2E] bg-[#1C1C1E]">
                <ConsolePanel
                  question={question}
                  isRunning={isRunning}
                  isSubmitting={isSubmitting}
                  runResult={runResult}
                  submitResult={submitResult}
                  activeTab={activeTab}
                  onTabChange={setActiveTab}
                  onNextQuestion={handleNextQuestion}
                />
              </Panel>

            </PanelGroup>
          </Panel>

        </PanelGroup>
      </div>
    </div>
  );
}
