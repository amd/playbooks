"use client";

import { useState } from "react";
import Link from "next/link";

interface Playbook {
  title: string;
  description: string;
  href: string;
  isNew?: boolean;
  isFeatured?: boolean;
}

interface Course {
  title: string;
  description: string;
  partner: string;
  href: string;
}

const playbooks: Playbook[] = [
  {
    title: "Fine-tuning on vLLM",
    description: "Learn how to fine-tune models using vLLM on your STX Halo™ for optimized inference",
    href: "/halo/vllm-finetuning",
    isNew: true,
    isFeatured: true,
  },
  {
    title: "Clustering with Two Halo™ Devices",
    description: "Set up a multi-node cluster using two STX Halo™ devices for distributed workloads",
    href: "/halo/clustering",
  },
  {
    title: "LLM Debate Arena with 8 LLMs",
    description: "Create an interactive debate arena where multiple LLMs discuss and debate topics",
    href: "/halo/llm-debate",
  },
  {
    title: "Local LLM Coding with GitHub Copilot and Qwen3-Next-80B",
    description: "Use GitHub Copilot with locally-running Qwen3-Next-80B for private code assistance",
    href: "/halo/copilot-qwen",
  },
  {
    title: "Automating Workflows with n8n and GPT-OSS-120b",
    description: "Build powerful automation workflows combining n8n with local GPT-OSS-120b inference",
    href: "/halo/n8n-automation",
  },
  {
    title: "Quantize and Export Models to GGUF",
    description: "Learn to quantize and export models to GGUF format for efficient local inference",
    href: "/halo/gguf-export",
  },
  {
    title: "FLUX.2-dev Fine-tuning",
    description: "Fine-tune FLUX.2-dev for custom image generation with your own datasets",
    href: "/halo/flux2-finetuning",
  },
  {
    title: "Creating Multi-agent Chatbots",
    description: "Build sophisticated multi-agent chatbot systems with coordinated AI responses",
    href: "/halo/multi-agent",
  },
];

const courses: Course[] = [
  {
    title: "The Halo™ Path: Supercharging Hugging Face LLMs",
    description: "Master LLM optimization and deployment on STX Halo™ with official Hugging Face certification",
    partner: "Hugging Face Partnership",
    href: "/halo/huggingface-course",
  },
];


export default function PlaybooksSection() {
  const [showAll, setShowAll] = useState(false);

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
          <p className="text-[#a0a0a0] text-sm max-w-2xl mx-auto">
            Step-by-step guides to help you master AI development on STX Halo™. From fine-tuning to deployment, we&apos;ve got you covered.
          </p>
        </div>

        {/* Featured Playbook - Hero Style */}
        {featuredPlaybook && (
          <Link href={featuredPlaybook.href} className="block mb-6">
            <div className="group relative bg-gradient-to-r from-[#1e1e1e] to-[#242424] border border-[#D4915D]/30 rounded-xl overflow-hidden hover:border-[#D4915D]/60 transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-r from-[#D4915D]/5 to-transparent" />
              <div className="absolute top-0 right-0 w-48 h-48 bg-[#D4915D]/5 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2" />
              
              <div className="relative p-5 md:p-6 flex flex-col md:flex-row items-start md:items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-0.5 bg-[#D4915D] text-black text-[10px] font-bold rounded-full uppercase tracking-wide">
                      Featured
                    </span>
                    {featuredPlaybook.isNew && (
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-semibold rounded-full border border-emerald-500/30">
                        New
                      </span>
                    )}
                  </div>
                  <h3 className="text-base md:text-lg font-bold text-white mb-2 group-hover:text-[#D4915D] transition-colors">
                    {featuredPlaybook.title}
                  </h3>
                  <p className="text-[#a0a0a0] text-sm mb-4 max-w-xl">
                    {featuredPlaybook.description}
                  </p>
                  <div className="flex items-center gap-4">
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
            <Link key={playbook.title} href={playbook.href} className="block group">
              <div className="h-full bg-[#1e1e1e] border border-[#333333] rounded-lg p-4 hover:border-[#D4915D]/50 hover:bg-[#242424] transition-all duration-300">
                <div className="flex items-start justify-between mb-3">
                  <div className="p-1.5 rounded-md bg-[#D4915D]/10 border border-[#D4915D]/20">
                    <svg className="w-4 h-4 text-[#D4915D]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                    </svg>
                  </div>
                </div>
                <h3 className="text-sm font-semibold text-white mb-1 group-hover:text-[#D4915D] transition-colors line-clamp-2">
                  {playbook.title}
                </h3>
                <p className="text-xs text-[#a0a0a0] line-clamp-2 mb-3">
                  {playbook.description}
                </p>
                <div className="flex items-center text-xs text-[#D4915D] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                  <span>View Playbook</span>
                  <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
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

