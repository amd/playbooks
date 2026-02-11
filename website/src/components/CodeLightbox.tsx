"use client";

import { useEffect, useCallback, useState } from "react";

interface CodeLightboxProps {
  filename: string;
  code: string;
  isOpen: boolean;
  onClose: () => void;
}

/**
 * A lightbox component for previewing code files from playbook assets
 * Features:
 * - Syntax highlighting based on file extension
 * - Copy to clipboard functionality
 * - Click outside to close
 * - ESC key to close
 * - Smooth fade animation
 */
export default function CodeLightbox({ filename, code, isOpen, onClose }: CodeLightboxProps) {
  const [copied, setCopied] = useState(false);

  // Handle ESC key to close
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") {
      onClose();
    }
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      // Prevent body scroll when lightbox is open
      document.body.style.overflow = "hidden";
    }
    
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
      // Reset copied state when lightbox closes (cleanup is safe for setState)
      setCopied(false);
    };
  }, [isOpen, handleKeyDown]);


  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy code:", err);
    }
  }, [code]);

  // Get language from file extension for syntax highlighting class
  const getLanguageFromFilename = (name: string): string => {
    const ext = name.split(".").pop()?.toLowerCase() || "";
    const languageMap: Record<string, string> = {
      py: "python",
      js: "javascript",
      ts: "typescript",
      tsx: "typescript",
      jsx: "javascript",
      json: "json",
      yaml: "yaml",
      yml: "yaml",
      md: "markdown",
      sh: "bash",
      bash: "bash",
      zsh: "bash",
      txt: "text",
      css: "css",
      html: "html",
      xml: "xml",
      sql: "sql",
      rs: "rust",
      go: "go",
      java: "java",
      cpp: "cpp",
      c: "c",
      h: "c",
      hpp: "cpp",
    };
    return languageMap[ext] || "text";
  };

  const language = getLanguageFromFilename(filename);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center animate-lightbox-fade-in"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/90 backdrop-blur-sm" />
      
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 z-10 p-2 text-white/70 hover:text-white transition-colors rounded-full hover:bg-white/10"
        aria-label="Close code preview"
      >
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      
      {/* Hint text */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/50 text-sm">
        Press <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-xs">ESC</kbd> or click anywhere to close
      </div>
      
      {/* Code container */}
      <div 
        className="relative w-[90vw] max-w-4xl max-h-[85vh] animate-lightbox-zoom-in flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header with filename and copy button */}
        <div className="flex items-center justify-between px-4 py-3 bg-[#1e1e1e] border-b border-[#333] rounded-t-lg">
          <div className="flex items-center gap-3">
            {/* File icon */}
            <svg className="w-5 h-5 text-[#D4915D]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            <span className="text-white font-medium">{filename}</span>
            <span className="text-xs text-[#6b6b6b] px-2 py-0.5 bg-[#2a2a2a] rounded">
              {language}
            </span>
          </div>
          
          {/* Copy button */}
          <button
            onClick={handleCopy}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md transition-all ${
              copied 
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" 
                : "bg-[#2a2a2a] text-[#a0a0a0] hover:text-white hover:bg-[#333] border border-[#444]"
            }`}
            aria-label={copied ? "Copied!" : "Copy code"}
          >
            {copied ? (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-sm font-medium">Copied!</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span className="text-sm font-medium">Copy</span>
              </>
            )}
          </button>
        </div>
        
        {/* Code content */}
        <div className="flex-1 overflow-auto bg-[#0d0d0d] rounded-b-lg">
          <pre className="p-4 text-sm leading-relaxed">
            <code className={`language-${language} text-[#e0e0e0]`}>
              {code}
            </code>
          </pre>
        </div>
      </div>
    </div>
  );
}
