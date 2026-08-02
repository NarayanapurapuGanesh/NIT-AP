"use client";

import { Play, Send, RotateCcw, AlignLeft, Settings } from "lucide-react";

interface EditorToolbarProps {
  language: string;
  theme: string;
  setTheme: (theme: string) => void;
  fontSize: number;
  setFontSize: (size: number) => void;
  onReset: () => void;
  onFormat: () => void;
  onRun: () => void;
  onSubmit: () => void;
  isExecuting: boolean;
}

export default function EditorToolbar({
  language,
  theme,
  setTheme,
  fontSize,
  setFontSize,
  onReset,
  onFormat,
  onRun,
  onSubmit,
  isExecuting
}: EditorToolbarProps) {
  
  return (
    <div className="flex items-center justify-between px-4 py-2 bg-[#1C1C1E] border-b border-[#2C2C2E]">
      <div className="flex items-center space-x-3">
        {/* Language Display (Readonly for now as backend sets it per session) */}
        <div className="text-xs font-semibold text-gray-300 bg-gray-800/50 px-3 py-1.5 rounded-md flex items-center">
          {language.toUpperCase()}
          <span className="ml-2 text-gray-500">▼</span>
        </div>

        {/* Theme */}
        <select
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          className="bg-transparent text-gray-400 text-xs font-medium focus:outline-none hover:text-gray-200 cursor-pointer"
        >
          <option value="vs-dark">Dark Theme</option>
          <option value="light">Light Theme</option>
        </select>

        {/* Font Size */}
        <div className="flex items-center text-xs text-gray-400">
          <Settings className="w-3 h-3 mr-1" />
          <select
            value={fontSize}
            onChange={(e) => setFontSize(Number(e.target.value))}
            className="bg-transparent font-medium focus:outline-none hover:text-gray-200 cursor-pointer"
          >
            <option value="12">12px</option>
            <option value="14">14px</option>
            <option value="16">16px</option>
            <option value="18">18px</option>
          </select>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={onFormat}
          title="Format Code (Alt+Shift+F)"
          className="p-1.5 text-gray-400 hover:text-gray-200 hover:bg-gray-800 rounded transition-colors"
        >
          <AlignLeft className="w-4 h-4" />
        </button>
        <button
          onClick={onReset}
          title="Reset to Starter Code"
          className="p-1.5 text-gray-400 hover:text-gray-200 hover:bg-gray-800 rounded transition-colors mr-2"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        <button
          onClick={onRun}
          disabled={isExecuting}
          className="flex items-center space-x-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded text-xs font-medium transition-colors disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5 text-blue-400" />
          <span>Run</span>
        </button>

        <button
          onClick={onSubmit}
          disabled={isExecuting}
          className="flex items-center space-x-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-500 border border-emerald-500/30 px-3 py-1.5 rounded text-xs font-medium transition-colors disabled:opacity-50"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Submit</span>
        </button>
      </div>
    </div>
  );
}
