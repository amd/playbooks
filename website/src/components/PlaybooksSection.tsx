"use client";

import { useState, useEffect, type ReactNode } from "react";
import Link from "next/link";
import type { Playbook, Platform } from "@/types/playbook";
import { formatTime, platformNames } from "@/types/playbook";

interface Course {
  title: string;
  description: string;
  partner: string;
  href: string;
}

const courses: Course[] = [
  {
    title: "The Halo™ Path: Supercharging Hugging Face LLMs",
    description: "Master LLM optimization and deployment on STX Halo™ with official Hugging Face certification",
    partner: "Hugging Face Partnership",
    href: "/halo/huggingface-course",
  },
];

function PlatformBadge({ platform }: { platform: Platform }) {
  const icons: Record<Platform, ReactNode> = {
    windows: (
      <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
        <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801"/>
      </svg>
    ),
    linux: (
      <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.132 1.884 1.071.771-.06 1.592-.536 2.257-1.306.631-.765 1.683-1.084 2.378-1.503.348-.199.629-.469.649-.853.023-.4-.2-.811-.714-1.376v-.097l-.003-.003c-.17-.2-.25-.535-.338-.926-.085-.401-.182-.786-.492-1.046h-.003c-.059-.054-.123-.067-.188-.135a.357.357 0 00-.19-.064c.431-1.278.264-2.55-.173-3.694-.533-1.41-1.465-2.638-2.175-3.483-.796-1.005-1.576-1.957-1.56-3.368.026-2.152.236-6.133-3.544-6.139zm.529 3.405h.013c.213 0 .396.062.584.198.19.135.33.332.438.533.105.259.158.459.166.724 0-.02.006-.04.006-.06v.105a.086.086 0 01-.004-.021l-.004-.024a1.807 1.807 0 01-.15.706.953.953 0 01-.213.335.71.71 0 00-.088-.042c-.104-.045-.198-.064-.284-.133a1.312 1.312 0 00-.22-.066c.05-.06.146-.133.183-.198.053-.128.082-.262.082-.405 0-.108-.022-.21-.058-.305-.045-.09-.1-.172-.16-.238a.422.422 0 00-.189-.135.515.515 0 00-.18-.034c-.067 0-.137.003-.204.018a1.592 1.592 0 00-.373.147v.013c.053-.093.138-.233.18-.332.028-.067.033-.147.033-.15a.673.673 0 00-.013-.129.596.596 0 01.012-.134v-.013c.067-.13.2-.213.337-.213zm-2.287.073a.647.647 0 01.09.005c.29.046.431.303.464.606.009.06.017.117.017.177 0 .076-.01.15-.023.227l-.009.033-.013.043-.009.019a.537.537 0 01-.043.098c-.008.02-.017.04-.029.057-.04.068-.09.13-.146.184a.75.75 0 01-.16.114c-.073.038-.146.068-.227.082a.58.58 0 01-.09.008c-.117 0-.225-.035-.32-.099-.029-.026-.058-.058-.084-.088a.797.797 0 01-.148-.253c-.037-.1-.057-.201-.057-.31 0-.104.02-.208.056-.308a.82.82 0 01.368-.458c.105-.06.228-.091.356-.091zm.943 1.205c.054 0 .114.013.176.04.054.03.105.076.154.123.054.053.1.112.138.18.04.065.073.14.091.218.023.09.034.18.034.274v.018a.96.96 0 01-.034.225c-.018.076-.054.146-.092.213-.04.065-.088.126-.143.178-.053.052-.11.097-.166.133a.613.613 0 01-.173.066.466.466 0 01-.092.009.427.427 0 01-.255-.077.668.668 0 01-.183-.19c-.05-.076-.087-.16-.11-.249a.877.877 0 01-.036-.254c0-.087.012-.174.036-.257a.83.83 0 01.11-.245.689.689 0 01.18-.182.504.504 0 01.258-.083c.035 0 .07.003.107.01zm4.904 5.984c.6 0 1.149.39 1.535 1.004.336.533.557 1.212.558 1.945 0 .207-.018.4-.05.579a4.093 4.093 0 01-.25.946c-.056.134-.114.265-.178.387a3.89 3.89 0 01-.472.726 4.003 4.003 0 01-.543.537c-.198.15-.392.275-.585.37a2.185 2.185 0 01-.566.207 2.233 2.233 0 01-.478.052c-.234 0-.457-.04-.651-.116a1.872 1.872 0 01-.507-.287 2.09 2.09 0 01-.373-.406 2.87 2.87 0 01-.257-.46c-.15-.327-.237-.689-.237-1.06 0-.353.08-.677.215-.963a2.28 2.28 0 01.549-.735c.232-.203.497-.363.78-.465a2.55 2.55 0 01.893-.159zm-8.392.023c.252 0 .505.034.748.098.24.064.47.158.68.28.212.121.404.27.571.446.168.175.308.376.418.597.11.221.19.461.235.71.046.249.058.507.037.762a3.17 3.17 0 01-.127.651 3.083 3.083 0 01-.267.585 2.942 2.942 0 01-.38.51 2.798 2.798 0 01-.471.415 2.54 2.54 0 01-.532.29 2.234 2.234 0 01-.568.14 2.23 2.23 0 01-.565-.024 2.27 2.27 0 01-.529-.165 2.35 2.35 0 01-.459-.29 2.58 2.58 0 01-.374-.396 2.942 2.942 0 01-.282-.48 3.27 3.27 0 01-.186-.543 3.45 3.45 0 01-.089-.579 3.29 3.29 0 01.02-.584c.033-.195.087-.381.158-.557.072-.176.162-.343.269-.497.106-.154.229-.296.365-.42a2.52 2.52 0 01.44-.324 2.35 2.35 0 01.489-.206 2.22 2.22 0 01.52-.07z"/>
      </svg>
    ),
  };

  return (
    <span 
      className="inline-flex items-center gap-1 px-1.5 py-0.5 text-[10px] rounded bg-[#333] text-[#a0a0a0]"
      title={platformNames[platform]}
    >
      {icons[platform]}
    </span>
  );
}

function DifficultyBadge({ difficulty }: { difficulty?: string }) {
  if (!difficulty) return null;
  
  return (
    <span className="px-1.5 py-0.5 text-[10px] font-medium rounded bg-[#2a2a2a] text-[#888] border border-[#3a3a3a]">
      {difficulty}
    </span>
  );
}

export default function PlaybooksSection() {
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAll, setShowAll] = useState(false);
  const [platformFilter, setPlatformFilter] = useState<Platform | null>(null);

  useEffect(() => {
    async function fetchPlaybooks() {
      try {
        const url = platformFilter 
          ? `/api/playbooks?platform=${platformFilter}`
          : "/api/playbooks";
        const res = await fetch(url);
        const data = await res.json();
        setPlaybooks(data);
      } catch (error) {
        console.error("Error fetching playbooks:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchPlaybooks();
  }, [platformFilter]);

  const featuredPlaybook = playbooks.find((p) => p.isFeatured);
  const regularPlaybooks = playbooks.filter((p) => !p.isFeatured);
  const displayedPlaybooks = showAll ? regularPlaybooks : regularPlaybooks.slice(0, 6);

  return (
    <section className="py-12 px-6 relative overflow-hidden" id="playbooks">
      {/* Dramatic background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0d0d0d] via-[#1a0f0a] to-[#0d0d0d]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#D4915D]/10 via-transparent to-transparent" />
      
      {/* Decorative elements */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#D4915D]/50 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#D4915D]/50 to-transparent" />

      <div className="max-w-[1400px] mx-auto relative z-10">
        {/* Section Header - Prominent */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-3 px-3 py-1.5 rounded-full bg-[#D4915D]/10 border border-[#D4915D]/30">
            <svg className="w-4 h-4 text-[#D4915D]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
            </svg>
            <span className="text-[#D4915D] text-xs font-semibold uppercase tracking-wider">Playbooks</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-3">
            Learn. Build. <span className="text-[#D4915D]">Deploy.</span>
          </h2>
          <p className="text-[#a0a0a0] text-sm max-w-2xl mx-auto mb-4">
            Step-by-step guides to help you master AI development on STX Halo™. From fine-tuning to deployment, we&apos;ve got you covered.
          </p>
          
          {/* Platform Filter */}
          <div className="flex items-center justify-center gap-2">
            <span className="text-xs text-[#6b6b6b]">Filter by platform:</span>
            <button
              onClick={() => setPlatformFilter(null)}
              className={`px-2.5 py-1 text-xs rounded-md transition-colors ${
                !platformFilter 
                  ? "bg-[#D4915D] text-black font-medium" 
                  : "bg-[#242424] text-[#a0a0a0] hover:bg-[#333]"
              }`}
            >
              All
            </button>
            <button
              onClick={() => setPlatformFilter("windows")}
              className={`px-2.5 py-1 text-xs rounded-md transition-colors flex items-center gap-1.5 ${
                platformFilter === "windows" 
                  ? "bg-[#D4915D] text-black font-medium" 
                  : "bg-[#242424] text-[#a0a0a0] hover:bg-[#333]"
              }`}
            >
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801"/>
              </svg>
              Windows
            </button>
            <button
              onClick={() => setPlatformFilter("linux")}
              className={`px-2.5 py-1 text-xs rounded-md transition-colors flex items-center gap-1.5 ${
                platformFilter === "linux" 
                  ? "bg-[#D4915D] text-black font-medium" 
                  : "bg-[#242424] text-[#a0a0a0] hover:bg-[#333]"
              }`}
            >
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.132 1.884 1.071.771-.06 1.592-.536 2.257-1.306.631-.765 1.683-1.084 2.378-1.503.348-.199.629-.469.649-.853.023-.4-.2-.811-.714-1.376v-.097l-.003-.003c-.17-.2-.25-.535-.338-.926-.085-.401-.182-.786-.492-1.046h-.003c-.059-.054-.123-.067-.188-.135a.357.357 0 00-.19-.064c.431-1.278.264-2.55-.173-3.694-.533-1.41-1.465-2.638-2.175-3.483-.796-1.005-1.576-1.957-1.56-3.368.026-2.152.236-6.133-3.544-6.139z"/>
              </svg>
              Linux
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#D4915D]"></div>
          </div>
        ) : (
          <>
            {/* Featured Playbook - Hero Style */}
            {featuredPlaybook && (
              <Link href={`/playbooks/${featuredPlaybook.id}`} className="block mb-6">
                <div className="group relative bg-gradient-to-r from-[#1e1e1e] to-[#242424] border border-[#D4915D]/30 rounded-xl overflow-hidden hover:border-[#D4915D]/60 transition-all duration-300">
                  <div className="absolute inset-0 bg-gradient-to-r from-[#D4915D]/5 to-transparent" />
                  <div className="absolute top-0 right-0 w-48 h-48 bg-[#D4915D]/5 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2" />
                  
                  <div className="relative p-5 md:p-6 flex flex-col md:flex-row items-start md:items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <span className="px-2 py-0.5 bg-[#D4915D] text-black text-[10px] font-bold rounded-full uppercase tracking-wide">
                          Featured
                        </span>
                        {featuredPlaybook.isNew && (
                          <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-semibold rounded-full border border-emerald-500/30">
                            New
                          </span>
                        )}
                        <DifficultyBadge difficulty={featuredPlaybook.difficulty} />
                        <div className="flex gap-1">
                          {featuredPlaybook.platforms.map((p) => (
                            <PlatformBadge key={p} platform={p} />
                          ))}
                        </div>
                      </div>
                      <h3 className="text-base md:text-lg font-bold text-white mb-2 group-hover:text-[#D4915D] transition-colors">
                        {featuredPlaybook.title}
                      </h3>
                      <p className="text-[#a0a0a0] text-sm mb-4 max-w-xl">
                        {featuredPlaybook.description}
                      </p>
                      <div className="flex items-center gap-4">
                        <span className="text-[#6b6b6b] text-xs flex items-center gap-1.5">
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {formatTime(featuredPlaybook.time)}
                        </span>
                        <span className="text-[#D4915D] text-sm font-medium flex items-center gap-2 group-hover:gap-3 transition-all">
                          Start Learning
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                          </svg>
                        </span>
                      </div>
                    </div>
                    <div className="hidden md:flex items-center justify-center w-16 h-16 rounded-xl bg-[#D4915D]/10 border border-[#D4915D]/20 group-hover:border-[#D4915D]/40 transition-colors">
                      <svg className="w-8 h-8 text-[#D4915D]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L4.2 15.3m15.6 0l.3 1.524A3.002 3.002 0 0117.83 19.5H6.17a3.002 3.002 0 01-2.27-2.676l.3-1.524" />
                      </svg>
                    </div>
                  </div>
                </div>
              </Link>
            )}

            {/* Playbook Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-6">
              {displayedPlaybooks.map((playbook) => (
                <Link key={playbook.id} href={`/playbooks/${playbook.id}`} className="block group">
                  <div className="h-full bg-[#1e1e1e] border border-[#333333] rounded-lg p-4 hover:border-[#D4915D]/50 hover:bg-[#242424] transition-all duration-300">
                    <div className="flex items-start justify-between mb-3">
                      <div className="p-1.5 rounded-md bg-[#D4915D]/10 border border-[#D4915D]/20">
                        <svg className="w-4 h-4 text-[#D4915D]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                        </svg>
                      </div>
                      <div className="flex items-center gap-1.5">
                        {playbook.isNew && (
                          <span className="px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-semibold rounded border border-emerald-500/30">
                            New
                          </span>
                        )}
                        <div className="flex gap-1">
                          {playbook.platforms.map((p) => (
                            <PlatformBadge key={p} platform={p} />
                          ))}
                        </div>
                      </div>
                    </div>
                    <h3 className="text-sm font-semibold text-white mb-1 group-hover:text-[#D4915D] transition-colors line-clamp-2">
                      {playbook.title}
                    </h3>
                    <p className="text-xs text-[#a0a0a0] line-clamp-2 mb-3">
                      {playbook.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-[#6b6b6b] text-[10px] flex items-center gap-1">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {formatTime(playbook.time)}
                        </span>
                        <DifficultyBadge difficulty={playbook.difficulty} />
                      </div>
                      <div className="flex items-center text-xs text-[#D4915D] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                        <span>View</span>
                        <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Show More Button */}
            {regularPlaybooks.length > 6 && (
              <div className="text-center mb-10">
                <button
                  onClick={() => setShowAll(!showAll)}
                  className="px-5 py-2 bg-[#242424] hover:bg-[#333333] text-white text-sm font-medium rounded-lg border border-[#333333] hover:border-[#D4915D]/50 transition-all"
                >
                  {showAll ? "Show Less" : `Show All Playbooks (${regularPlaybooks.length})`}
                </button>
              </div>
            )}
          </>
        )}

        {/* Courses Section */}
        <div className="mt-10">
          <div className="flex items-center gap-2.5 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-500/20 to-amber-500/20 border border-yellow-500/30 flex items-center justify-center">
              <svg className="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
              </svg>
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">Courses & Certifications</h3>
              <p className="text-xs text-[#6b6b6b]">Official learning paths with industry partners</p>
            </div>
          </div>

          {courses.map((course) => (
            <Link key={course.title} href={course.href} className="block group">
              <div className="bg-gradient-to-r from-[#1e1e1e] to-[#242424] border border-yellow-500/20 rounded-lg p-4 hover:border-yellow-500/40 transition-all">
                <div className="flex flex-col md:flex-row md:items-center gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="px-2 py-0.5 bg-yellow-500/10 text-yellow-400 text-[10px] font-semibold rounded-full border border-yellow-500/20">
                        {course.partner}
                      </span>
                    </div>
                    <h4 className="text-sm font-semibold text-white mb-1 group-hover:text-yellow-400 transition-colors">
                      {course.title}
                    </h4>
                    <p className="text-xs text-[#a0a0a0]">{course.description}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="hidden md:flex items-center gap-2 text-yellow-400 text-sm font-medium group-hover:gap-3 transition-all">
                      <span>Enroll Now</span>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>

      </div>
    </section>
  );
}
