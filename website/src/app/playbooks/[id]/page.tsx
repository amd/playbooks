"use client";

import { useState, useEffect, use, useRef } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import type { Playbook, Platform } from "@/types/playbook";
import { formatTime } from "@/types/playbook";

/**
 * Collapsible dropdown component for pre-installed software on AMD Halo
 */
function HaloPreinstalledDropdown({ content }: { content: string }) {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className="halo-preinstalled-container">
      <button 
        className="halo-preinstalled-trigger"
        onClick={() => setIsOpen(!isOpen)}
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
              p: ({ children }) => <p className="md-p">{children}</p>,
              ul: ({ children }) => <ul className="md-ul">{children}</ul>,
              ol: ({ children }) => <ol className="md-ol">{children}</ol>,
              li: ({ children }) => <li className="md-li">{children}</li>,
              a: ({ href, children }) => (
                <a href={href} className="md-link" target="_blank" rel="noopener noreferrer">
                  {children}
                </a>
              ),
              code: ({ className, children }) => {
                const isInline = !className;
                if (isInline) {
                  return <code className="inline-code">{children}</code>;
                }
                return <code className={className}>{children}</code>;
              },
              pre: ({ children }) => <pre className="code-block">{children}</pre>,
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      )}
    </div>
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

export default function PlaybookPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [playbook, setPlaybook] = useState<Playbook | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>("windows");
  const [activeHeading, setActiveHeading] = useState<string>("");
  const contentRef = useRef<HTMLDivElement>(null);
  const isClickScrolling = useRef(false);

  useEffect(() => {
    async function fetchPlaybook() {
      try {
        const res = await fetch(`/api/playbooks/${id}`);
        if (!res.ok) {
          if (res.status === 404) {
            setError("Playbook not found");
          } else {
            setError("Failed to load playbook");
          }
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
    }
    fetchPlaybook();
  }, [id]);

  // Transform relative image paths to API routes, filter by OS, and transform preinstalled blocks
  const filteredContent = playbook?.content 
    ? transformPreinstalledBlocks(
        filterContentByOS(playbook.content, selectedPlatform)
      )
        // Transform relative image paths in HTML img tags to use the API route
        .replace(/src=["'](?!https?:\/\/|\/)(.*?)["']/g, `src="/api/playbooks/${id}/$1"`)
    : "";

  // Extract table of contents from filtered content
  const tocItems = extractToc(filteredContent);

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

  // Track active heading on scroll
  useEffect(() => {
    if (!contentRef.current || tocItems.length === 0) return;

    const handleScroll = () => {
      // Skip scroll tracking while programmatic scroll is in progress
      if (isClickScrolling.current) return;
      
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
      
      if (currentActive && currentActive !== activeHeading) {
        setActiveHeading(currentActive);
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    // Initial check
    handleScroll();
    
    return () => window.removeEventListener("scroll", handleScroll);
  }, [tocItems, activeHeading]);

  return (
    <main className="min-h-screen bg-[#0d0d0d]">
      <Header />
      
      <div className="pt-24 pb-16 px-6">
        <div className="max-w-6xl mx-auto">
          {/* Back Link */}
          <Link 
            href="/#playbooks" 
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
                href="/#playbooks"
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

              {/* Main content area with TOC sidebar */}
              <div className="relative flex gap-8">
                {/* Table of Contents - Desktop only */}
                {tocItems.length > 0 && (
                  <aside className="hidden xl:block w-56 flex-shrink-0">
                    <div className="sticky top-24">
                      <TableOfContents 
                        items={tocItems} 
                        activeId={activeHeading}
                        onLinkClick={handleTocClick}
                      />
                    </div>
                  </aside>
                )}

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="bg-[#1a1a1a] border border-[#333] rounded-xl p-6 md:p-8">
                    {filteredContent ? (
                      <article ref={contentRef} className="playbook-content prose prose-invert max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeRaw]}
                          components={{
                            h1: ({ children }) => {
                              const text = String(children);
                              const headingId = slugify(text);
                              return <h1 id={headingId} className="md-h1 scroll-mt-28">{children}</h1>;
                            },
                            h2: ({ children }) => {
                              const text = String(children);
                              const headingId = slugify(text);
                              return <h2 id={headingId} className="md-h2 scroll-mt-28">{children}</h2>;
                            },
                            h3: ({ children }) => {
                              const text = String(children);
                              const headingId = slugify(text);
                              return <h3 id={headingId} className="md-h3 scroll-mt-28">{children}</h3>;
                            },
                            h4: ({ children }) => {
                              const text = String(children);
                              const headingId = slugify(text);
                              return <h4 id={headingId} className="md-h4 scroll-mt-28">{children}</h4>;
                            },
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
                            img: ({ src, alt }) => {
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
                                />
                              );
                            },
                            code: ({ className, children }) => {
                              const isInline = !className;
                              if (isInline) {
                                return <code className="inline-code">{children}</code>;
                              }
                              return (
                                <code className={className}>
                                  {children}
                                </code>
                              );
                            },
                            pre: ({ children }) => (
                              <pre className="code-block">{children}</pre>
                            ),
                            hr: () => <hr className="md-hr" />,
                            table: ({ children }) => <table className="md-table">{children}</table>,
                            thead: ({ children }) => <thead className="md-thead">{children}</thead>,
                            tbody: ({ children }) => <tbody className="md-tbody">{children}</tbody>,
                            tr: ({ children }) => <tr className="md-tr">{children}</tr>,
                            th: ({ children }) => <th className="md-th">{children}</th>,
                            td: ({ children }) => <td className="md-td">{children}</td>,
                            div: ({ className, ...props }) => {
                              // Handle the halo-preinstalled-dropdown custom element
                              if (className === 'halo-preinstalled-dropdown') {
                                const dataContent = (props as { 'data-content'?: string })['data-content'];
                                if (dataContent) {
                                  const decodedContent = decodeURIComponent(dataContent);
                                  return <HaloPreinstalledDropdown content={decodedContent} />;
                                }
                              }
                              return <div className={className} {...props} />;
                            },
                          }}
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
              </div>
            </>
          )}
        </div>
      </div>

      <Footer />
    </main>
  );
}
