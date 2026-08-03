"use client";

import Editor, { useMonaco } from "@monaco-editor/react";
import { useEffect, useRef } from "react";

interface CodeEditorProps {
  language: string;
  value: string;
  onChange: (value: string | undefined) => void;
  readOnly?: boolean;
  theme?: string;
  fontSize?: number;
  onMount?: (editor: any, monaco: any) => void;
}

export default function CodeEditor({ 
  language, 
  value, 
  onChange, 
  readOnly = false,
  theme = "vs-dark",
  fontSize = 14,
  onMount
}: CodeEditorProps) {
  const monaco = useMonaco();
  const editorRef = useRef<any>(null);

  useEffect(() => {
    if (monaco) {
      monaco.editor.defineTheme("premium-dark", {
        base: "vs-dark",
        inherit: true,
        rules: [],
        colors: {
          "editor.background": "#1C1C1E",
          "editor.lineHighlightBackground": "#2C2C2E",
          "editorLineNumber.foreground": "#5C5C5E",
          "editorIndentGuide.background": "#2C2C2E",
        },
      });
    }
  }, [monaco]);

  const mapLanguage = (lang: string) => {
    switch (lang.toLowerCase()) {
      case "python": return "python";
      case "cpp": return "cpp";
      case "c": return "c";
      case "java": return "java";
      case "javascript": return "javascript";
      case "csharp": return "csharp";
      default: return "python";
    }
  };

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    if (onMount) {
      onMount(editor, monaco);
    }
  };

  return (
    <div className={`w-full h-full ${theme === "vs-light" ? "bg-[#fffffe]" : "bg-[#1C1C1E]"}`}>
      <Editor
        height="100%"
        language={mapLanguage(language)}
        value={value}
        onChange={onChange}
        theme={theme === "vs-dark" ? "premium-dark" : "vs-light"}
        onMount={handleEditorDidMount}
        options={{
          minimap: { enabled: false },
          fontSize: fontSize,
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          fontLigatures: true,
          scrollBeyondLastLine: false,
          smoothScrolling: true,
          cursorBlinking: "smooth",
          cursorSmoothCaretAnimation: "on",
          formatOnPaste: true,
          padding: { top: 16, bottom: 16 },
          readOnly: readOnly,
          renderLineHighlight: "all",
          scrollbar: {
            verticalScrollbarSize: 8,
            horizontalScrollbarSize: 8,
          },
        }}
        loading={
          <div className="flex h-full items-center justify-center text-gray-500 text-sm">
            Loading Editor...
          </div>
        }
      />
    </div>
  );
}
