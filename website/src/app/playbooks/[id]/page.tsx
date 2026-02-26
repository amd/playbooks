"use client";

import { useState, useEffect, use, useRef, useCallback, useMemo } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ImageLightbox from "@/components/ImageLightbox";
import CodeLightbox from "@/components/CodeLightbox";
import type { Playbook, Platform, TestCoverageInfo, TestResultInfo, PlaybookCoverageSummary } from "@/types/playbook";
import { formatTime } from "@/types/playbook";

// Global store for dropdown states - persists across re-renders without causing them
const dropdownStateStore: Record<string, boolean> = {};

// Languages that support syntax highlighting
const HIGHLIGHTED_LANGUAGES = new Set(["python", "py", "bash", "sh", "shell", "c", "cpp", "c++"]);

// Map language aliases to their canonical names for the highlighter
function normalizeLanguage(lang: string): string {
  const langMap: Record<string, string> = {
    "py": "python",
    "sh": "bash",
    "shell": "bash",
    "c++": "cpp",
  };
  return langMap[lang] || lang;
}

/**
 * Code block component with copy-to-clipboard functionality and syntax highlighting
 */
function CodeBlock({ children, language }: { children?: React.ReactNode; language?: string }) {
  const [copied, setCopied] = useState(false);
  const preRef = useRef<HTMLPreElement>(null);

  // Extract the code string from children
  const codeString = useMemo(() => {
    if (typeof children === "string") return children;
    // If children is a React element (code tag), extract its children
    if (children && typeof children === "object" && "props" in children) {
      const childElement = children as React.ReactElement<{ children?: React.ReactNode }>;
      const codeChildren = childElement.props?.children;
      if (typeof codeChildren === "string") return codeChildren;
    }
    return "";
  }, [children]);

  const handleCopy = useCallback(async () => {
    const code = codeString || preRef.current?.textContent || "";
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy code:", err);
    }
  }, [codeString]);

  // Check if we should use syntax highlighting
  const normalizedLang = language ? normalizeLanguage(language.toLowerCase()) : "";
  const shouldHighlight = normalizedLang && HIGHLIGHTED_LANGUAGES.has(language?.toLowerCase() || "");

  return (
    <div className="code-block-wrapper">
      <button
        className="code-copy-button"
        onClick={handleCopy}
        aria-label={copied ? "Copied!" : "Copy code"}
        title={copied ? "Copied!" : "Copy code"}
      >
        {copied ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        )}
      </button>
      {shouldHighlight && codeString ? (
        <SyntaxHighlighter
          language={normalizedLang}
          style={oneDark}
          customStyle={{
            margin: 0,
            padding: "1rem",
            borderRadius: "0.5rem",
            fontSize: "0.875rem",
            background: "#0a0a0a",
          }}
          codeTagProps={{
            style: {
              fontFamily: "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace",
            }
          }}
        >
          {codeString.replace(/\n$/, "")}
        </SyntaxHighlighter>
      ) : (
        <pre ref={preRef} className="code-block">{children}</pre>
      )}
    </div>
  );
}

/**
 * Collapsible dropdown component for pre-installed software on AMD Halo
 * Uses a global store to persist state without triggering parent re-renders
 */
function HaloPreinstalledDropdown({ 
  content, 
  dropdownId,
  playbookId,
  onImageClick,
  testCoverage,
}: { 
  content: string;
  dropdownId: string;
  playbookId: string;
  onImageClick: (image: { src: string; alt: string }) => void;
  testCoverage?: TestCoverageInfo;
}) {
  // Initialize from global store, use local state for rendering
  const [isOpen, setIsOpen] = useState(() => dropdownStateStore[dropdownId] ?? false);
  
  const handleToggle = useCallback(() => {
    setIsOpen(prev => {
      const newValue = !prev;
      dropdownStateStore[dropdownId] = newValue;
      return newValue;
    });
  }, [dropdownId]);
  
  return (
    <div className="halo-preinstalled-container">
      <button 
        className="halo-preinstalled-trigger"
        onClick={handleToggle}
        aria-expanded={isOpen}
      >
        <span className="halo-preinstalled-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </span>
        <span className="halo-preinstalled-text">Already pre-installed on your AMD Halo Developer Platform!</span>
        <span className={`halo-preinstalled-chevron ${isOpen ? 'open' : ''}`}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 9l-7 7-7-7" />
          </svg>
        </span>
      </button>
      {isOpen && (
        <div className="halo-preinstalled-content">
          <div className="halo-preinstalled-notice">
            This software comes pre-installed and configured on your AMD Halo Developer Platform. 
            If you need to reinstall or configure it manually, follow the instructions below:
          </div>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw]}
            components={{
              h1: ({ children }) => <h1 className="md-h1">{children}</h1>,
              h2: ({ children }) => <h2 className="md-h2">{children}</h2>,
              h3: ({ children }) => <h3 className="md-h3">{children}</h3>,
              h4: ({ children }) => <h4 className="md-h4">{children}</h4>,
              p: ({ children }) => <p className="md-p">{children}</p>,
              ul: ({ children }) => <ul className="md-ul">{children}</ul>,
              ol: ({ children }) => <ol className="md-ol">{children}</ol>,
              li: ({ children }) => <li className="md-li">{children}</li>,
              blockquote: ({ children }) => <blockquote className="md-blockquote">{children}</blockquote>,
              a: ({ href, children }) => (
                <a href={href} className="md-link" target="_blank" rel="noopener noreferrer">
                  {children}
                </a>
              ),
              img: (props: React.ImgHTMLAttributes<HTMLImageElement>) => {
                const { src, alt } = props;
                // Transform relative paths to use the API route
                let imageSrc = typeof src === "string" ? src : "";
                if (imageSrc && !imageSrc.startsWith("http") && !imageSrc.startsWith("/")) {
                  imageSrc = `/api/playbooks/${playbookId}/${imageSrc}`;
                }
                return (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img 
                    src={imageSrc} 
                    alt={alt || ""} 
                    className="rounded-lg max-w-full h-auto mx-auto my-6"
                    onClick={() => onImageClick({ src: imageSrc, alt: alt || "" })}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        onImageClick({ src: imageSrc, alt: alt || "" });
                      }
                    }}
                  />
                );
              },
              code: ({ className, children }: { className?: string; children?: React.ReactNode }) => {
                // Inline code (no className)
                if (!className) {
                  return <code className="inline-code">{children}</code>;
                }
                // Block code - just return the code element, let pre handle the wrapper
                return <code className={className}>{children}</code>;
              },
              pre: ({ children }: { children?: React.ReactNode }) => {
                // Extract language from the code child's className
                let language: string | undefined;
                let codeContent: React.ReactNode = children;
                
                if (children && typeof children === "object" && "props" in children) {
                  const codeElement = children as React.ReactElement<{ className?: string; children?: React.ReactNode }>;
                  const className = codeElement.props?.className;
                  if (className) {
                    const match = /language-(\w+)/.exec(className);
                    language = match ? match[1] : undefined;
                  }
                  codeContent = codeElement.props?.children;
                }
                
                // Use CodeBlock with language for syntax highlighting
                if (language && HIGHLIGHTED_LANGUAGES.has(language.toLowerCase())) {
                  return (
                    <CodeBlock language={language}>
                      {String(codeContent).replace(/\n$/, "")}
                    </CodeBlock>
                  );
                }
                
                return <CodeBlock>{children}</CodeBlock>;
              },
              hr: () => <hr className="md-hr" />,
              table: ({ children }) => <table className="md-table">{children}</table>,
              thead: ({ children }) => <thead className="md-thead">{children}</thead>,
              tbody: ({ children }) => <tbody className="md-tbody">{children}</tbody>,
              tr: ({ children }) => <tr className="md-tr">{children}</tr>,
              th: ({ children }) => <th className="md-th">{children}</th>,
              td: ({ children }) => <td className="md-td">{children}</td>,
              // Handle test-coverage-block markers inside dependency content
              div: (divProps: React.HTMLAttributes<HTMLDivElement> & { 'data-test-id'?: string; 'data-timeout'?: string; 'data-hidden'?: string; 'data-setup'?: string; 'data-code'?: string }) => {
                const { className: divClassName, ...divRest } = divProps;
                if (divClassName === 'test-coverage-block') {
                  const testId = divProps['data-test-id'] || '';
                  const testInfo = testCoverage?.tests.find(t => t.id === testId);
                  return (
                    <TestCoverageBlock
                      testId={testId}
                      timeout={divProps['data-timeout'] || '300'}
                      isHidden={divProps['data-hidden'] === 'true'}
                      setup={divProps['data-setup'] || ''}
                      code={decodeURIComponent(divProps['data-code'] || '')}
                      testResult={testInfo?.result}
                      playbookId={playbookId}
                    />
                  );
                }
                return <div className={divClassName} {...divRest} />;
              },
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}

/**
 * Setup content component for system configuration steps
 * Displays setup instructions directly (not collapsible) since these are required steps
 */
function HaloSetupContent({ 
  content,
  playbookId,
  onImageClick
}: { 
  content: string;
  playbookId: string;
  onImageClick: (image: { src: string; alt: string }) => void;
}) {
  return (
    <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={{
          h1: ({ children }) => <h1 className="md-h1">{children}</h1>,
          h2: ({ children }) => <h2 className="md-h2">{children}</h2>,
          h3: ({ children }) => <h3 className="md-h3">{children}</h3>,
          h4: ({ children }) => <h4 className="md-h4">{children}</h4>,
          p: ({ children }) => <p className="md-p">{children}</p>,
          ul: ({ children }) => <ul className="md-ul">{children}</ul>,
          ol: ({ children }) => <ol className="md-ol">{children}</ol>,
          li: ({ children }) => <li className="md-li">{children}</li>,
          blockquote: ({ children }) => <blockquote className="md-blockquote">{children}</blockquote>,
          a: ({ href, children }) => (
            <a href={href} className="md-link" target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
          img: (props: React.ImgHTMLAttributes<HTMLImageElement>) => {
            const { src, alt } = props;
            // Transform relative paths to use the API route
            let imageSrc = typeof src === "string" ? src : "";
            if (imageSrc && !imageSrc.startsWith("http") && !imageSrc.startsWith("/")) {
              imageSrc = `/api/playbooks/${playbookId}/${imageSrc}`;
            }
            return (
              // eslint-disable-next-line @next/next/no-img-element
              <img 
                src={imageSrc} 
                alt={alt || ""} 
                className="rounded-lg max-w-full h-auto mx-auto my-6"
                onClick={() => onImageClick({ src: imageSrc, alt: alt || "" })}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onImageClick({ src: imageSrc, alt: alt || "" });
                  }
                }}
              />
            );
          },
          code: ({ className, children }: { className?: string; children?: React.ReactNode }) => {
            // Inline code (no className)
            if (!className) {
              return <code className="inline-code">{children}</code>;
            }
            // Block code - just return the code element, let pre handle the wrapper
            return <code className={className}>{children}</code>;
          },
          pre: ({ children }: { children?: React.ReactNode }) => {
            // Extract language from the code child's className
            let language: string | undefined;
            let codeContent: React.ReactNode = children;
            
            if (children && typeof children === "object" && "props" in children) {
              const codeElement = children as React.ReactElement<{ className?: string; children?: React.ReactNode }>;
              const className = codeElement.props?.className;
              if (className) {
                const match = /language-(\w+)/.exec(className);
                language = match ? match[1] : undefined;
              }
              codeContent = codeElement.props?.children;
            }
            
            // Use CodeBlock with language for syntax highlighting
            if (language && HIGHLIGHTED_LANGUAGES.has(language.toLowerCase())) {
              return (
                <CodeBlock language={language}>
                  {String(codeContent).replace(/\n$/, "")}
                </CodeBlock>
              );
            }
            
            return <CodeBlock>{children}</CodeBlock>;
          },
          hr: () => <hr className="md-hr" />,
          table: ({ children }) => <table className="md-table">{children}</table>,
          thead: ({ children }) => <thead className="md-thead">{children}</thead>,
          tbody: ({ children }) => <tbody className="md-tbody">{children}</tbody>,
          tr: ({ children }) => <tr className="md-tr">{children}</tr>,
          th: ({ children }) => <th className="md-th">{children}</th>,
          td: ({ children }) => <td className="md-td">{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
  );
}

interface TocItem {
  id: string;
  text: string;
}

/**
 * Extracts table of contents from markdown content (main sections only - h2)
 */
function extractToc(content: string): TocItem[] {
  if (!content) return [];
  
  const headingRegex = /^##\s+(.+)$/gm;
  const toc: TocItem[] = [];
  let match;
  
  while ((match = headingRegex.exec(content)) !== null) {
    const text = match[1].trim();
    const id = slugify(text);
    toc.push({ id, text });
  }
  
  return toc;
}

/**
 * Generates a URL-safe slug from heading text
 */
function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .trim();
}

/**
 * Table of Contents Sidebar Component
 */
function TableOfContents({ 
  items, 
  activeId,
  onLinkClick
}: { 
  items: TocItem[]; 
  activeId: string;
  onLinkClick: (id: string) => void;
}) {
  if (items.length === 0) return null;

  return (
    <nav className="toc-sidebar">
      <div className="text-xs font-semibold text-[#6b6b6b] uppercase tracking-wider mb-3">
        On this page
      </div>
      <ul className="space-y-1">
        {items.map((item) => (
          <li key={item.id}>
            <a
              href={`#${item.id}`}
              onClick={(e) => {
                e.preventDefault();
                onLinkClick(item.id);
              }}
              className={`
                block text-sm py-1 pl-3 transition-colors duration-150 border-l-2
                ${activeId === item.id 
                  ? "text-[#D4915D] border-[#D4915D] font-medium" 
                  : "text-[#888] border-transparent hover:text-[#ccc] hover:border-[#555]"
                }
              `}
            >
              {item.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}

/**
 * Coverage Sidebar — lists ALL playbooks with their test counts,
 * grouped by category, matching the Python _test_preview.py layout.
 * Replaces the "On this page" TOC when running in coverage mode.
 */
function CoverageSidebar({
  currentPlaybookId,
  allPlaybooks,
  onToggleView,
}: {
  currentPlaybookId: string;
  allPlaybooks: PlaybookCoverageSummary[];
  onToggleView: () => void;
}) {
  // Group by category
  const grouped = useMemo(() => {
    const map: Record<string, PlaybookCoverageSummary[]> = {};
    for (const p of allPlaybooks) {
      if (!map[p.category]) map[p.category] = [];
      map[p.category].push(p);
    }
    return map;
  }, [allPlaybooks]);

  // Global stats
  const totalTests = allPlaybooks.reduce((s, p) => s + p.testCount, 0);
  const withTests = allPlaybooks.filter(p => p.testCount > 0).length;
  const total = allPlaybooks.length;

  return (
    <nav className="cov-sidebar">
      {/* Header */}
      <div className="cov-sidebar-header">
        <svg className="cov-sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
        <span>Test Coverage</span>
      </div>

      {/* Global stats badges */}
      <div className="cov-global-stats">
        <span className="cov-global-badge cov-global-badge-green">{totalTests} total tests</span>
        <span className={`cov-global-badge ${withTests < total ? "cov-global-badge-warn" : "cov-global-badge-green"}`}>
          {withTests}/{total} playbooks tested
        </span>
      </div>

      {/* Playbook list grouped by category */}
      <div className="cov-pb-list">
        {Object.entries(grouped).map(([category, playbooks]) => (
          <div key={category}>
            <div className="cov-pb-section">{category}</div>
            {playbooks.map(p => (
              <Link
                key={p.id}
                href={`/playbooks/${p.id}`}
                className={`cov-pb-item ${p.id === currentPlaybookId ? "cov-pb-active" : ""}`}
              >
                <span className={`cov-pb-dot ${p.testCount > 0 ? "cov-pb-dot-tested" : "cov-pb-dot-untested"}`} />
                <span className="cov-pb-title" title={p.title}>{p.title}</span>
                <span className={`cov-pb-count ${p.testCount > 0 ? "cov-pb-count-has" : "cov-pb-count-none"}`}>
                  {p.testCount}
                </span>
              </Link>
            ))}
          </div>
        ))}
      </div>

      {/* Toggle to user view */}
      <button className="cov-toggle-btn" onClick={onToggleView}>
        <svg className="cov-toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        Switch to User View
      </button>
    </nav>
  );
}

/**
 * Small floating toggle shown in the TOC sidebar position when in user-view mode
 * to allow switching back to coverage mode.
 */
function CoverageReturnToggle({ onToggle }: { onToggle: () => void }) {
  return (
    <button className="cov-return-toggle" onClick={onToggle}>
      <svg className="cov-return-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      Show Coverage
    </button>
  );
}

/**
 * Parses markdown content and filters OS-specific sections
 * 
 * Tags supported:
 * <!-- @os:windows --> ... <!-- @os:end -->
 * <!-- @os:linux --> ... <!-- @os:end -->
 * <!-- @os:all --> ... <!-- @os:end -->
 */
function filterContentByOS(content: string, platform: Platform): string {
  if (!content) return "";
  
  // Pattern to match OS-specific blocks
  const osBlockPattern = /<!-- @os:(windows|linux|all) -->([\s\S]*?)<!-- @os:end -->/g;
  
  let result = content;
  const matches = [...content.matchAll(osBlockPattern)];
  
  // Process matches in reverse order to preserve indices
  for (let i = matches.length - 1; i >= 0; i--) {
    const match = matches[i];
    const blockOS = match[1];
    const blockContent = match[2];
    const fullMatch = match[0];
    const startIndex = match.index!;
    
    let replacement = "";
    
    // Show only content for the selected platform
    if (blockOS === "all" || blockOS === platform) {
      replacement = blockContent;
    }
    // Otherwise, replacement is empty (content hidden)
    
    result = result.slice(0, startIndex) + replacement + result.slice(startIndex + fullMatch.length);
  }
  
  return result;
}

/**
 * Transforms @preinstalled tags into collapsible dropdown HTML
 * 
 * Tags supported:
 * <!-- @preinstalled --> ... <!-- @preinstalled:end -->
 * 
 * The content inside becomes a collapsible section with a special header
 * indicating the software is pre-installed on AMD Halo Developer Platform
 */
function transformPreinstalledBlocks(content: string): string {
  if (!content) return "";
  
  const preinstalledPattern = /<!-- @preinstalled -->([\s\S]*?)<!-- @preinstalled:end -->/g;
  
  return content.replace(preinstalledPattern, (_match, innerContent) => {
    // Escape any HTML in the content for the data attribute
    const escapedContent = innerContent.trim();
    return `<div class="halo-preinstalled-dropdown" data-content="${encodeURIComponent(escapedContent)}"></div>`;
  });
}

/**
 * Transforms @setup-content tags into setup instruction blocks
 * 
 * Tags supported:
 * <!-- @setup-content --> ... <!-- @setup-content:end -->
 * 
 * Unlike @preinstalled (which is collapsible since it's optional info),
 * setup content is displayed directly as required configuration steps.
 */
function transformSetupBlocks(content: string): string {
  if (!content) return "";
  
  const setupPattern = /<!-- @setup-content -->([\s\S]*?)<!-- @setup-content:end -->/g;
  
  return content.replace(setupPattern, (_match, innerContent) => {
    const escapedContent = innerContent.trim();
    return `<div class="halo-setup-content" data-content="${encodeURIComponent(escapedContent)}"></div>`;
  });
}

/**
 * Test coverage badge block — renders a badge header on top of a code block.
 * Only shown when running in dev:coverage mode.
 * When a test fails, shows a "View Logs" button to inspect stdout/stderr.
 */
function TestCoverageBlock({
  testId, timeout, isHidden, setup, code, testResult, playbookId, runId,
}: {
  testId: string;
  timeout: string;
  isHidden: boolean;
  setup: string;
  code: string;
  testResult?: TestResultInfo;
  playbookId?: string;
  runId?: number | null;
}) {
  const [logsOpen, setLogsOpen] = useState(false);
  const [logs, setLogs] = useState<{ stdout: string; stderr: string } | null>(null);
  const [logsLoading, setLogsLoading] = useState(false);
  const [logsError, setLogsError] = useState<string | null>(null);

  // Parse the fenced code block: ```lang\ncontent\n```
  const langMatch = code.match(/```(\w+)?\s*\n/);
  const language = langMatch?.[1] || "";
  const codeContent = code.replace(/```\w*\s*\n/, "").replace(/\n?```\s*$/, "");

  // Detect lines marked with #hide (hidden from user view, visible in coverage)
  const hasHideLines = codeContent.split('\n').some(line => line.trimEnd().endsWith('#hide'));

  let resultStatus = "";
  let resultLabel = "";
  if (testResult) {
    if (testResult.skipped) { resultStatus = "skip"; resultLabel = "Skipped"; }
    else if (testResult.success) { resultStatus = "pass"; resultLabel = "Passed"; }
    else { resultStatus = "fail"; resultLabel = "Failed"; }
  }

  // Show logs button for all tests that have results
  const showLogsButton = !!testResult;

  const handleViewLogs = useCallback(async () => {
    if (logsOpen) {
      setLogsOpen(false);
      return;
    }

    // If logs already fetched, just toggle open
    if (logs) {
      setLogsOpen(true);
      return;
    }

    // Fetch logs from API
    if (!playbookId) return;
    setLogsLoading(true);
    setLogsError(null);

    try {
      const logsUrl = runId
        ? `/api/playbooks/${playbookId}/logs/${testId}?run_id=${runId}`
        : `/api/playbooks/${playbookId}/logs/${testId}`;
      const res = await fetch(logsUrl);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setLogsError(data.error || "Failed to load logs");
        setLogsOpen(true);
        return;
      }
      const data = await res.json();
      setLogs(data);
      setLogsOpen(true);
    } catch {
      setLogsError("Failed to fetch logs");
      setLogsOpen(true);
    } finally {
      setLogsLoading(false);
    }
  }, [logsOpen, logs, playbookId, testId, runId]);

  return (
    <div className={`tc-block ${isHidden ? "tc-hidden" : ""} ${resultStatus ? `tc-result-${resultStatus}` : ""}`}>
      <div className={`tc-badge-header ${isHidden ? "tc-badge-hidden" : ""} ${resultStatus === "fail" ? "tc-badge-fail" : ""} ${resultStatus === "skip" ? "tc-badge-skip" : ""}`}>
        <span className={`tc-pill tc-pill-label ${isHidden ? "tc-pill-label-hidden" : ""}`}>
          {isHidden ? "👁 Hidden Test" : "✓ Tested"}
        </span>
        <span className="tc-pill tc-pill-id">{testId}</span>
        <span className="tc-pill tc-pill-timeout">⏱ {timeout}s</span>
        {setup && (
          <span className="tc-pill tc-pill-setup">⚙ {setup}</span>
        )}
        {showLogsButton && (
          <button
            className={`tc-logs-btn ${logsOpen ? "tc-logs-btn-active" : ""}`}
            onClick={handleViewLogs}
            disabled={logsLoading}
            title={logsOpen ? "Hide logs" : "View test logs"}
          >
            {logsLoading ? (
              <span className="tc-logs-spinner" />
            ) : (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
            )}
            {logsOpen ? "Hide Logs" : "View Logs"}
          </button>
        )}
        {testResult && (
          <span className={`tc-pill tc-pill-result tc-pill-result-${resultStatus}`}>
            {resultLabel}{testResult.duration ? ` (${testResult.duration.toFixed(1)}s)` : ""}
          </span>
        )}
      </div>
      {/* Collapsible log viewer */}
      {logsOpen && (
        <div className="tc-logs-panel">
          {logsError && !logs ? (
            <div className="tc-logs-error">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {logsError}
            </div>
          ) : (
            <>
              {testResult?.error && (
                <div className="tc-logs-error-message">
                  <span className="tc-logs-section-label">Error</span>
                  <pre className="tc-logs-pre">{testResult.error}</pre>
                </div>
              )}
              {logs?.stderr && (
                <div className="tc-logs-section tc-logs-stderr">
                  <span className="tc-logs-section-label">stderr</span>
                  <pre className="tc-logs-pre">{logs.stderr}</pre>
                </div>
              )}
              {logs?.stdout && (
                <div className="tc-logs-section tc-logs-stdout">
                  <span className="tc-logs-section-label">stdout</span>
                  <pre className="tc-logs-pre">{logs.stdout}</pre>
                </div>
              )}
              {logs && !logs.stdout && !logs.stderr && !testResult?.error && (
                <div className="tc-logs-empty">No log output available for this test.</div>
              )}
            </>
          )}
        </div>
      )}
      {hasHideLines ? (
        <div className="code-block-wrapper">
          <pre className="code-block tc-code-with-hide">
            <code>{codeContent.split('\n').map((line, i) => {
              const isHideLine = line.trimEnd().endsWith('#hide');
              const cleanLine = isHideLine ? line.replace(/\s*#hide\s*$/, '') : line;
              return (
                <div key={i} className={`tc-line ${isHideLine ? 'tc-line-hidden' : ''}`}>
                  {isHideLine && <span className="tc-hide-label">hidden</span>}
                  {cleanLine}
                </div>
              );
            })}</code>
          </pre>
        </div>
      ) : (
        <CodeBlock language={language}>{codeContent}</CodeBlock>
      )}
    </div>
  );
}

/**
 * Setup definition block — renders a visible badge for @setup:id=... definitions.
 * Only shown in coverage view; hidden in user view (like hidden test blocks).
 * Shows the setup step name and the command it expands to.
 */
function SetupDefinitionBlock({
  setupId,
  command,
}: {
  setupId: string;
  command: string;
}) {
  return (
    <div className="tc-block tc-setup-def">
      <div className="tc-badge-header tc-badge-setup">
        <span className="tc-pill tc-pill-label tc-pill-label-setup">⚙ Hidden Setup Definition</span>
        <span className="tc-pill tc-pill-id">{setupId}</span>
      </div>
      {command && (
        <div className="tc-setup-commands">
          <div className="tc-setup-cmd">
            <code className="tc-setup-code">{command}</code>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Stats bar showing test coverage summary for the playbook.
 * Only shown when GitHub test results are available.
 */
function TestCoverageStatsBar({
  coverage,
  availableRuns,
  selectedRunId,
  onRunChange,
}: {
  coverage: TestCoverageInfo;
  availableRuns: PlaybookRunOption[];
  selectedRunId: number | null;
  onRunChange: (id: number | null) => void;
}) {
  const covPct = coverage.totalCodeBlocks > 0
    ? Math.round((coverage.visibleTestCount / coverage.totalCodeBlocks) * 100)
    : 0;
  const covClass = covPct >= 60 ? "" : covPct >= 30 ? "tc-cov-mid" : "tc-cov-low";

  return (
    <div className="tc-stats-container">
      {/* Stats row */}
      <div className="tc-stats-bar">
        <span className="tc-stat tc-stat-green"><strong>{coverage.visibleTestCount}</strong> visible tests</span>
        <span className="tc-stat tc-stat-purple"><strong>{coverage.hiddenTestCount}</strong> hidden tests</span>
        <span className="tc-stat"><strong>{coverage.totalCodeBlocks}</strong> code blocks</span>
        <span className="tc-stat-divider" />
        <span className={`tc-stat-coverage ${covClass}`}>{covPct}% coverage</span>
        {availableRuns.length > 0 && (
          <span className="ml-auto">
            <PlaybookRunSelector
              runs={availableRuns}
              selectedId={selectedRunId}
              onChange={onRunChange}
            />
          </span>
        )}
      </div>
      {/* Results row */}
      {coverage.resultsSummary && (
        <div className="tc-results-bar">
          <span className="tc-results-label">Results:</span>
          <span className="tc-results-pill tc-results-pass">{coverage.resultsSummary.passed} passed</span>
          <span className="tc-results-pill tc-results-fail">{coverage.resultsSummary.failed} failed</span>
          <span className="tc-results-pill tc-results-skip">{coverage.resultsSummary.skipped} skipped</span>
        </div>
      )}
      {/* Legend */}
      <div className="tc-legend">
        <span className="tc-legend-title">Legend:</span>
        <span className="tc-legend-item"><span className="tc-legend-swatch tc-swatch-tested" /> Tested (visible)</span>
        <span className="tc-legend-item"><span className="tc-legend-swatch tc-swatch-hidden" /> Hidden test</span>
        <span className="tc-legend-item"><span className="tc-legend-swatch tc-swatch-untested" /> Not tested</span>
        {coverage.resultsSummary && (
          <>
            <span className="tc-legend-sep">|</span>
            <span className="tc-legend-item"><span className="tc-legend-swatch tc-swatch-pass" /> Passed</span>
            <span className="tc-legend-item"><span className="tc-legend-swatch tc-swatch-fail" /> Failed</span>
            <span className="tc-legend-item"><span className="tc-legend-swatch tc-swatch-skip" /> Skipped</span>
          </>
        )}
      </div>
    </div>
  );
}

function PlatformToggle({ 
  platforms, 
  selected, 
  onChange 
}: { 
  platforms: Platform[]; 
  selected: Platform; 
  onChange: (p: Platform) => void;
}) {
  const hasWindows = platforms.includes("windows");
  const hasLinux = platforms.includes("linux");

  return (
    <div className="flex items-center gap-2 p-1 bg-[#1a1a1a] rounded-lg border border-[#333]">
      {hasWindows && (
        <button
          onClick={() => onChange("windows")}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
            selected === "windows"
              ? "bg-[#D4915D] text-black"
              : "text-[#a0a0a0] hover:text-white hover:bg-[#333]"
          }`}
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801"/>
          </svg>
          Windows
        </button>
      )}
      {hasLinux && (
        <button
          onClick={() => onChange("linux")}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
            selected === "linux"
              ? "bg-[#D4915D] text-black"
              : "text-[#a0a0a0] hover:text-white hover:bg-[#333]"
          }`}
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.132 1.884 1.071.771-.06 1.592-.536 2.257-1.306.631-.765 1.683-1.084 2.378-1.503.348-.199.629-.469.649-.853.023-.4-.2-.811-.714-1.376v-.097l-.003-.003c-.17-.2-.25-.535-.338-.926-.085-.401-.182-.786-.492-1.046h-.003c-.059-.054-.123-.067-.188-.135a.357.357 0 00-.19-.064c.431-1.278.264-2.55-.173-3.694-.533-1.41-1.465-2.638-2.175-3.483-.796-1.005-1.576-1.957-1.56-3.368.026-2.152.236-6.133-3.544-6.139z"/>
          </svg>
          Linux
        </button>
      )}
    </div>
  );
}

interface PlaybookRunOption {
  id: number;
  htmlUrl: string;
  createdAt: string;
  event: string;
  headBranch: string;
  conclusion: string | null;
}

function PlaybookRunSelector({
  runs,
  selectedId,
  onChange,
}: {
  runs: PlaybookRunOption[];
  selectedId: number | null;
  onChange: (id: number | null) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useCallback((node: HTMLDivElement | null) => {
    if (!node) return;
    const handler = (e: MouseEvent) => {
      if (!node.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const selected = selectedId != null ? runs.find((r) => r.id === selectedId) : null;
  const label = selected ? new Date(selected.createdAt).toLocaleString() : "Latest nightly";

  const eventColors: Record<string, string> = {
    schedule: "bg-blue-900/30 text-blue-400 border-blue-800/30",
    workflow_dispatch: "bg-purple-900/30 text-purple-400 border-purple-800/30",
  };
  const eventLabels: Record<string, string> = { schedule: "Nightly", workflow_dispatch: "Manual" };

  return (
    <div ref={ref} className="relative inline-block">
      <button
        onClick={() => setOpen((o) => !o)}
        title="Select a workflow run to view its test results"
        className="flex items-center gap-1.5 px-2.5 py-1 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-xs text-[#6b6b6b] hover:border-[#555] hover:text-[#a0a0a0] transition-colors"
      >
        <svg className="w-3 h-3 text-[#D4915D] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span>Run: <span className="text-[#a0a0a0]">{label}</span></span>
        <svg className={`w-3 h-3 transition-transform ${open ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute left-0 top-full mt-1 z-50 w-72 bg-[#1a1a1a] border border-[#333] rounded-xl shadow-2xl overflow-hidden">
          <div className="max-h-64 overflow-y-auto">
            <button
              onClick={() => { onChange(null); setOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-2.5 text-xs hover:bg-[#242424] transition-colors ${selectedId == null ? "bg-[#242424]" : ""}`}
            >
              <span className="flex-1 text-left text-white font-medium">Latest nightly</span>
              {selectedId == null && <svg className="w-3 h-3 text-[#D4915D]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>}
            </button>
            <div className="border-t border-[#2a2a2a]" />
            {runs.map((run) => {
              const badgeCls = eventColors[run.event] ?? "bg-[#242424] text-[#6b6b6b] border-[#333]";
              const badgeLabel = eventLabels[run.event] ?? run.event;
              const isSelected = selectedId === run.id;
              return (
                <button
                  key={run.id}
                  onClick={() => { onChange(run.id); setOpen(false); }}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-xs hover:bg-[#242424] transition-colors ${isSelected ? "bg-[#242424]" : ""}`}
                >
                  <div className="flex-1 min-w-0 text-left">
                    <div className="text-[#a0a0a0]">{new Date(run.createdAt).toLocaleString()}</div>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span className={`px-1.5 py-0.5 text-[10px] font-semibold rounded border ${badgeCls}`}>{badgeLabel}</span>
                      <span className="text-[10px] text-[#555] truncate">{run.headBranch}</span>
                    </div>
                  </div>
                  {isSelected && <svg className="w-3 h-3 text-[#D4915D] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default function PlaybookPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ device?: string }> }) {
  const { id } = use(params);
  const { device: deviceHash } = use(searchParams);
  const backHref = deviceHash ? `/#${deviceHash}` : "/#playbooks";

  const [playbook, setPlaybook] = useState<Playbook | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>("windows");
  const [activeHeading, setActiveHeading] = useState<string>("");
  const [lightboxImage, setLightboxImage] = useState<{ src: string; alt: string } | null>(null);
  const [codeLightbox, setCodeLightbox] = useState<{ filename: string; code: string } | null>(null);
  // Coverage view toggle — true = show coverage badges & sidebar; false = normal user view
  const [coverageViewActive, setCoverageViewActive] = useState<boolean>(true);
  // All-playbooks coverage data for the sidebar (fetched once when in coverage mode)
  const [coveragePlaybooks, setCoveragePlaybooks] = useState<PlaybookCoverageSummary[]>([]);
  // Run selector state — null means "use latest"
  const [availableRuns, setAvailableRuns] = useState<PlaybookRunOption[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const activeHeadingRef = useRef<string>("");
  const contentRef = useRef<HTMLDivElement>(null);
  const isClickScrolling = useRef(false);

  const fetchPlaybook = useCallback(async (runId: number | null) => {
    setLoading(true);
    setError(null);
    try {
      const url = runId ? `/api/playbooks/${id}?run_id=${runId}` : `/api/playbooks/${id}`;
      const res = await fetch(url);
      if (!res.ok) {
        setError(res.status === 404 ? "Playbook not found" : "Failed to load playbook");
        return;
      }
      const data = await res.json();
      setPlaybook(data);

      // Auto-select platform: prefer windows, otherwise use the first available
      if (data.platforms.includes("windows")) {
        setSelectedPlatform("windows");
      } else if (data.platforms.length > 0) {
        setSelectedPlatform(data.platforms[0]);
      }
    } catch (err) {
      setError("Failed to load playbook");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchPlaybook(selectedRunId);
  }, [fetchPlaybook, selectedRunId]);

  // Fetch all-playbooks coverage summary when we detect coverage mode
  useEffect(() => {
    if (!playbook?.testCoverage) return;
    const url = selectedRunId
      ? `/api/playbooks/coverage?run_id=${selectedRunId}`
      : "/api/playbooks/coverage";
    fetch(url)
      .then(r => r.json())
      .then((data: PlaybookCoverageSummary[]) => setCoveragePlaybooks(data))
      .catch(() => {/* ignore */});
  }, [playbook?.testCoverage, selectedRunId]);

  // Fetch available runs once coverage data is detected (token is configured)
  useEffect(() => {
    if (!playbook?.testCoverage) return;
    if (availableRuns.length > 0) return;
    fetch("/api/dashboard/playbook-runs?per_page=20")
      .then(r => r.json())
      .then(d => { if (d.runs) setAvailableRuns(d.runs); })
      .catch(() => {/* non-critical */});
  }, [playbook?.testCoverage, availableRuns.length]);

  // Transform relative image paths to API routes, filter by OS, and transform preinstalled/setup blocks
  const filteredContent = playbook?.content 
    ? transformSetupBlocks(
        transformPreinstalledBlocks(
          filterContentByOS(playbook.content, selectedPlatform)
        )
      )
        // Transform relative image paths in HTML img tags to use the API route
        .replace(/src=["'](?!https?:\/\/|\/)(.*?)["']/g, `src="/api/playbooks/${id}/$1"`)
    : "";

  // Extract table of contents from filtered content
  const tocItems = extractToc(filteredContent);

  // Memoize the markdown components to prevent re-renders on scroll
  const markdownComponents = useMemo(() => ({
    h1: ({ children }: { children?: React.ReactNode }) => {
      const text = String(children);
      const headingId = slugify(text);
      return <h1 id={headingId} className="md-h1 scroll-mt-28">{children}</h1>;
    },
    h2: ({ children }: { children?: React.ReactNode }) => {
      const text = String(children);
      const headingId = slugify(text);
      return <h2 id={headingId} className="md-h2 scroll-mt-28">{children}</h2>;
    },
    h3: ({ children }: { children?: React.ReactNode }) => {
      const text = String(children);
      const headingId = slugify(text);
      return <h3 id={headingId} className="md-h3 scroll-mt-28">{children}</h3>;
    },
    h4: ({ children }: { children?: React.ReactNode }) => {
      const text = String(children);
      const headingId = slugify(text);
      return <h4 id={headingId} className="md-h4 scroll-mt-28">{children}</h4>;
    },
    p: ({ children }: { children?: React.ReactNode }) => <p className="md-p">{children}</p>,
    ul: ({ children }: { children?: React.ReactNode }) => <ul className="md-ul">{children}</ul>,
    ol: ({ children }: { children?: React.ReactNode }) => <ol className="md-ol">{children}</ol>,
    li: ({ children }: { children?: React.ReactNode }) => <li className="md-li">{children}</li>,
    blockquote: ({ children }: { children?: React.ReactNode }) => <blockquote className="md-blockquote">{children}</blockquote>,
    a: ({ href, children }: { href?: string; children?: React.ReactNode }) => {
      // Check if this is a link to a code file in the assets folder
      const isAssetCodeFile = href && 
        href.startsWith("assets/") && 
        /\.(py|js|ts|tsx|jsx|json|yaml|yml|sh|bash|css|html|xml|sql|rs|go|java|cpp|c|h|hpp|txt)$/i.test(href);
      
      if (isAssetCodeFile) {
        const filename = href.split("/").pop() || href;
        return (
          <button
            onClick={async (e) => {
              e.preventDefault();
              try {
                // Fetch the code file from the API
                const response = await fetch(`/api/playbooks/${id}/${href}`);
                if (response.ok) {
                  const code = await response.text();
                  setCodeLightbox({ filename, code });
                } else {
                  console.error("Failed to fetch code file:", response.status);
                }
              } catch (err) {
                console.error("Failed to fetch code file:", err);
              }
            }}
            className="md-link inline-flex items-center gap-1 cursor-pointer hover:underline"
            title={`Preview ${filename}`}
          >
            <svg className="w-4 h-4 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            {children}
          </button>
        );
      }
      
      return (
        <a href={href} className="md-link" target="_blank" rel="noopener noreferrer">
          {children}
        </a>
      );
    },
    img: (props: React.ImgHTMLAttributes<HTMLImageElement>) => {
      const { src, alt } = props;
      // Transform relative paths to use the API route
      let imageSrc = typeof src === "string" ? src : "";
      if (imageSrc && !imageSrc.startsWith("http") && !imageSrc.startsWith("/")) {
        imageSrc = `/api/playbooks/${id}/${imageSrc}`;
      }
      return (
        // eslint-disable-next-line @next/next/no-img-element
        <img 
          src={imageSrc} 
          alt={alt || ""} 
          className="rounded-lg max-w-full h-auto mx-auto my-6"
          onClick={() => setLightboxImage({ src: imageSrc, alt: alt || "" })}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              setLightboxImage({ src: imageSrc, alt: alt || "" });
            }
          }}
        />
      );
    },
    code: ({ className, children }: { className?: string; children?: React.ReactNode }) => {
      // Inline code (no className)
      if (!className) {
        return <code className="inline-code">{children}</code>;
      }
      // Block code - just return the code element, let pre handle the wrapper
      return <code className={className}>{children}</code>;
    },
    pre: ({ children }: { children?: React.ReactNode }) => {
      // Extract language from the code child's className
      let language: string | undefined;
      let codeContent: React.ReactNode = children;
      
      if (children && typeof children === "object" && "props" in children) {
        const codeElement = children as React.ReactElement<{ className?: string; children?: React.ReactNode }>;
        const className = codeElement.props?.className;
        if (className) {
          const match = /language-(\w+)/.exec(className);
          language = match ? match[1] : undefined;
        }
        codeContent = codeElement.props?.children;
      }
      
      // Use CodeBlock with language for syntax highlighting
      if (language && HIGHLIGHTED_LANGUAGES.has(language.toLowerCase())) {
        return (
          <CodeBlock language={language}>
            {String(codeContent).replace(/\n$/, "")}
          </CodeBlock>
        );
      }
      
      return <CodeBlock>{children}</CodeBlock>;
    },
    hr: () => <hr className="md-hr" />,
    table: ({ children }: { children?: React.ReactNode }) => <table className="md-table">{children}</table>,
    thead: ({ children }: { children?: React.ReactNode }) => <thead className="md-thead">{children}</thead>,
    tbody: ({ children }: { children?: React.ReactNode }) => <tbody className="md-tbody">{children}</tbody>,
    tr: ({ children }: { children?: React.ReactNode }) => <tr className="md-tr">{children}</tr>,
    th: ({ children }: { children?: React.ReactNode }) => <th className="md-th">{children}</th>,
    td: ({ children }: { children?: React.ReactNode }) => <td className="md-td">{children}</td>,
    div: (props: React.HTMLAttributes<HTMLDivElement> & { 'data-content'?: string; 'data-test-id'?: string; 'data-timeout'?: string; 'data-hidden'?: string; 'data-setup'?: string; 'data-code'?: string; 'data-setup-id'?: string; 'data-command'?: string }) => {
      const { className, ...rest } = props;
      // Handle setup-def-block (coverage mode — inline @setup:id=... definitions)
      if (className === 'setup-def-block') {
        return (
          <SetupDefinitionBlock
            setupId={props['data-setup-id'] || ''}
            command={decodeURIComponent(props['data-command'] || '')}
          />
        );
      }
      // Handle the halo-preinstalled-dropdown custom element
      if (className === 'halo-preinstalled-dropdown') {
        const dataContent = props['data-content'];
        if (dataContent) {
          const decodedContent = decodeURIComponent(dataContent);
          // Use content hash as stable ID for this dropdown
          const dropdownId = `dropdown-${dataContent.substring(0, 50)}`;
          return (
            <HaloPreinstalledDropdown 
              content={decodedContent} 
              dropdownId={dropdownId}
              playbookId={id}
              onImageClick={setLightboxImage}
              testCoverage={playbook?.testCoverage}
            />
          );
        }
      }
      // Handle the halo-setup-content custom element
      if (className === 'halo-setup-content') {
        const dataContent = props['data-content'];
        if (dataContent) {
          const decodedContent = decodeURIComponent(dataContent);
          return (
            <HaloSetupContent 
              content={decodedContent}
              playbookId={id}
              onImageClick={setLightboxImage}
            />
          );
        }
      }
      // Handle test-coverage-block (dev:coverage mode only)
      if (className === 'test-coverage-block') {
        const testId = props['data-test-id'] || '';
        const testInfo = playbook?.testCoverage?.tests.find(t => t.id === testId);
        return (
          <TestCoverageBlock
            testId={testId}
            timeout={props['data-timeout'] || '300'}
            isHidden={props['data-hidden'] === 'true'}
            setup={props['data-setup'] || ''}
            code={decodeURIComponent(props['data-code'] || '')}
            testResult={testInfo?.result}
            playbookId={id}
            runId={selectedRunId}
          />
        );
      }
      return <div className={className} {...rest} />;
    },
  }), [id, setLightboxImage, playbook?.testCoverage, selectedRunId]);

  // Handle clicking a TOC link - scroll and immediately set active
  const handleTocClick = (targetId: string) => {
    const element = document.getElementById(targetId);
    if (element) {
      // Set active immediately on click
      setActiveHeading(targetId);
      isClickScrolling.current = true;
      
      const offset = 100;
      const top = element.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: "smooth" });
      history.pushState(null, "", `#${targetId}`);
      
      // Re-enable scroll tracking after scroll animation completes
      setTimeout(() => {
        isClickScrolling.current = false;
      }, 1000);
    }
  };

  // Track active heading on scroll - use ref to avoid re-renders, only update state for TOC
  useEffect(() => {
    if (!contentRef.current || tocItems.length === 0) return;

    let rafId: number | null = null;
    
    const handleScroll = () => {
      // Skip scroll tracking while programmatic scroll is in progress
      if (isClickScrolling.current) return;
      
      // Use requestAnimationFrame to batch updates
      if (rafId) return;
      
      rafId = requestAnimationFrame(() => {
        rafId = null;
        
        const headings = contentRef.current?.querySelectorAll("h2[id]");
        if (!headings || headings.length === 0) return;
        
        // Find the heading that's currently at or near the top of the viewport
        // We look for the last heading that has scrolled past the threshold
        const threshold = 150; // How far from top of viewport to consider "active"
        let currentActive = "";
        
        for (const heading of headings) {
          const rect = heading.getBoundingClientRect();
          // If this heading is at or above the threshold, it's the current section
          if (rect.top <= threshold) {
            currentActive = heading.id;
          } else {
            // Once we find a heading below the threshold, stop
            break;
          }
        }
        
        // If no heading is above threshold, use the first one if we're near the top
        if (!currentActive && headings.length > 0) {
          const firstHeading = headings[0] as HTMLElement;
          const rect = firstHeading.getBoundingClientRect();
          if (rect.top < window.innerHeight / 2) {
            currentActive = firstHeading.id;
          }
        }
        
        // Only update state if the active heading actually changed
        if (currentActive && currentActive !== activeHeadingRef.current) {
          activeHeadingRef.current = currentActive;
          setActiveHeading(currentActive);
        }
      });
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    // Initial check
    handleScroll();
    
    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (rafId) cancelAnimationFrame(rafId);
    };
  }, [tocItems]);

  return (
    <main className="min-h-screen bg-[#0d0d0d]">
      <Header />
      
      <div className="pt-24 pb-16 px-6">
        <div className="max-w-5xl mx-auto">
          {/* Back Link */}
          <Link 
            href={backHref} 
            className="inline-flex items-center gap-2 text-[#a0a0a0] hover:text-[#D4915D] text-sm mb-6 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Playbooks
          </Link>

          {loading ? (
            <div className="flex items-center justify-center py-24">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[#D4915D]"></div>
            </div>
          ) : error ? (
            <div className="text-center py-24">
              <div className="text-red-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">{error}</h1>
              <p className="text-[#a0a0a0] mb-6">The playbook you&apos;re looking for doesn&apos;t exist or has been moved.</p>
              <Link 
                href={backHref}
                className="inline-flex items-center gap-2 px-4 py-2 bg-[#D4915D] text-black font-medium rounded-lg hover:bg-[#e5a26e] transition-colors"
              >
                View All Playbooks
              </Link>
            </div>
          ) : playbook && (
            <>
              {/* Header */}
              <div className="mb-8">
                <div className="flex items-center gap-2 mb-4 flex-wrap">
                  <span className={`px-2 py-0.5 text-[10px] font-medium rounded ${
                    playbook.category === "core" 
                      ? "bg-[#D4915D]/20 text-[#D4915D] border border-[#D4915D]/30"
                      : "bg-[#333] text-[#a0a0a0]"
                  }`}>
                    {playbook.category.toUpperCase()}
                  </span>
                  {playbook.isNew && (
                    <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-semibold rounded border border-emerald-500/30">
                      New
                    </span>
                  )}
{playbook.difficulty && (
                     <span className="px-2 py-0.5 text-[10px] font-medium rounded bg-[#2a2a2a] text-[#888] border border-[#3a3a3a]">
                       {playbook.difficulty}
                     </span>
                   )}
                  <span className="text-[#6b6b6b] text-xs flex items-center gap-1">
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {formatTime(playbook.time)}
                  </span>
                </div>

                <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">
                  {playbook.title}
                </h1>
                
                <p className="text-lg text-[#a0a0a0] mb-6">
                  {playbook.description}
                </p>

                {/* Cover Image */}
                {playbook.coverImage && (
                  <div className="mb-6">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={`/api/playbooks/${id}/${playbook.coverImage}`}
                      alt={playbook.title}
                      className="w-full rounded-xl border border-[#333] shadow-lg"
                    />
                  </div>
                )}

                {/* Platform Toggle */}
                {playbook.platforms.length > 0 && (
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                    <span className="text-sm text-[#6b6b6b]">View instructions for:</span>
                    <PlatformToggle 
                      platforms={playbook.platforms}
                      selected={selectedPlatform}
                      onChange={setSelectedPlatform}
                    />
                  </div>
                )}

                {/* Tags */}
                {playbook.tags && playbook.tags.length > 0 && (
                  <div className="flex items-center gap-2 mt-4 flex-wrap">
                    {playbook.tags.map((tag) => (
                      <span 
                        key={tag}
                        className="px-2 py-0.5 text-[10px] bg-[#242424] text-[#6b6b6b] rounded border border-[#333]"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Main content area with TOC / Coverage sidebar */}
              <div className={`relative flex gap-8 ${playbook.testCoverage && !coverageViewActive ? "tc-user-view" : ""}`}>
                {/* Sidebar - Desktop only */}
                <aside className={`hidden xl:block flex-shrink-0 ${playbook.testCoverage && coverageViewActive ? "w-64" : "w-56"}`}>
                  <div className="sticky top-24">
                    {playbook.testCoverage && coverageViewActive ? (
                      <CoverageSidebar
                        currentPlaybookId={id}
                        allPlaybooks={coveragePlaybooks}
                        onToggleView={() => setCoverageViewActive(false)}
                      />
                    ) : (
                      <>
                        {tocItems.length > 0 && (
                          <TableOfContents 
                            items={tocItems} 
                            activeId={activeHeading}
                            onLinkClick={handleTocClick}
                          />
                        )}
                        {/* Show return toggle when coverage data exists but user switched to user view */}
                        {playbook.testCoverage && !coverageViewActive && (
                          <CoverageReturnToggle onToggle={() => setCoverageViewActive(true)} />
                        )}
                      </>
                    )}
                  </div>
                </aside>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* Test Coverage Stats (only in coverage view) */}
                  {playbook.testCoverage && coverageViewActive && (
                    <TestCoverageStatsBar
                      coverage={playbook.testCoverage}
                      availableRuns={availableRuns}
                      selectedRunId={selectedRunId}
                      onRunChange={setSelectedRunId}
                    />
                  )}

                  <div className="bg-[#1a1a1a] border border-[#333] rounded-xl p-6 md:p-8">
                    {filteredContent ? (
                      <article ref={contentRef} className="playbook-content prose prose-invert max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeRaw]}
                          components={markdownComponents}
                        >
                          {filteredContent}
                        </ReactMarkdown>
                      </article>
                    ) : (
                      <div className="text-center py-12">
                        <div className="text-[#6b6b6b] mb-4">
                          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-2">Content Coming Soon</h3>
                        <p className="text-[#a0a0a0] text-sm">
                          This playbook is being prepared. Check back soon for detailed instructions.
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Mobile-only coverage toggle */}
                {playbook.testCoverage && (
                  <button
                    className="cov-mobile-toggle xl:hidden"
                    onClick={() => setCoverageViewActive(prev => !prev)}
                  >
                    {coverageViewActive ? (
                      <>
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        User View
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Coverage
                      </>
                    )}
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <Footer />

      {/* Image Lightbox */}
      <ImageLightbox
        src={lightboxImage?.src || ""}
        alt={lightboxImage?.alt || ""}
        isOpen={lightboxImage !== null}
        onClose={() => setLightboxImage(null)}
      />

      {/* Code Lightbox */}
      <CodeLightbox
        filename={codeLightbox?.filename || ""}
        code={codeLightbox?.code || ""}
        isOpen={codeLightbox !== null}
        onClose={() => setCodeLightbox(null)}
      />
    </main>
  );
}
