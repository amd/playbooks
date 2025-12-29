import Image from "next/image";
import courseBanner from "@/app/assets/course_banner_02.png";

interface AppItem {
  name: string;
  description: string;
  category: "image_gen" | "chat";
  icon: React.ReactNode;
}

const apps: AppItem[] = [
  {
    name: "Comfy UI",
    description: "Node-based AI image generation workflow",
    category: "image_gen",
    icon: (
      <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.5}>
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
        <path d="M10 6.5h4M6.5 10v4M17.5 10v4M10 17.5h4" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    name: "Amuse",
    description: "Intuitive AI image creation app",
    category: "image_gen",
    icon: (
      <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.5}>
        <circle cx="12" cy="12" r="9" />
        <path d="M8 14s1.5 2 4 2 4-2 4-2" strokeLinecap="round" />
        <circle cx="9" cy="10" r="1" fill="currentColor" />
        <circle cx="15" cy="10" r="1" fill="currentColor" />
      </svg>
    ),
  },
  {
    name: "LM Studio",
    description: "Run local LLMs with a sleek interface",
    category: "chat",
    icon: (
      <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.5}>
        <path d="M12 3L3 8v8l9 5 9-5V8l-9-5z" />
        <path d="M12 12L3 8M12 12l9-4M12 12v9" />
      </svg>
    ),
  },
  {
    name: "Open WebUI",
    description: "Feature-rich web UI for local LLMs",
    category: "chat",
    icon: (
      <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.5}>
        <rect x="3" y="4" width="18" height="16" rx="2" />
        <path d="M7 8h10M7 12h6M7 16h8" strokeLinecap="round" />
      </svg>
    ),
  },
];

export default function BuiltInAppsSection() {
  return (
    <section className="py-4 px-6" id="apps">
      <div className="max-w-[1400px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Left Side - Hugging Face Course CTA - Horizontal Layout */}
          <div className="relative group overflow-hidden rounded-xl bg-gradient-to-br from-[#2a1f1a] via-[#1a1a1a] to-[#1e1815] border border-[#D4915D]/30 hover:border-[#D4915D]/50 transition-all duration-500">
            <div className="absolute inset-0 bg-gradient-to-br from-[#D4915D]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
            <div className="relative p-4 flex gap-4 items-center">
              {/* Course Image - Left side, smaller */}
              <div className="relative rounded-lg overflow-hidden shrink-0 w-[180px] hidden sm:block">
                <Image
                  src={courseBanner}
                  alt="Hugging Face AMD Course"
                  className="w-full h-auto object-contain group-hover:scale-105 transition-transform duration-700"
                />
              </div>

              {/* Content - Right side */}
              <div className="flex-1 flex flex-col min-w-0">
                {/* Badge */}
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-0.5 rounded-full bg-[#D4915D]/20 text-[#D4915D] text-[10px] font-semibold tracking-wide uppercase">
                    Free Course
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-white/5 text-[#a0a0a0] text-[10px]">
                    🤗 Hugging Face
                  </span>
                </div>

                {/* Course Title */}
                <h2 className="text-xl font-bold text-white mb-1 leading-tight">
                  Master AI on <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#D4915D] to-[#E8B896]">STX Halo™</span>
                </h2>
                
                <p className="text-[#a0a0a0] text-sm mb-3 leading-relaxed line-clamp-2">
                  Learn to deploy and optimize LLMs, image generators, and more on AMD Radeon™ hardware.
                </p>

                {/* CTA Button */}
                <a
                  href="https://huggingface.co/learn/amd-gpus-with-hugging-face-course/unit0/introduction"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-[#D4915D] to-[#C47D52] text-black font-semibold text-xs hover:from-[#E8B896] hover:to-[#D4915D] transition-all duration-300 group/btn shadow-lg shadow-[#D4915D]/20 w-fit"
                >
                  Enroll Now
                  <svg className="w-3.5 h-3.5 group-hover/btn:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </a>
              </div>
            </div>
          </div>

          {/* Right Side - Pre-installed Apps - Compact */}
          <div className="bg-gradient-to-br from-[#1a1815] via-[#161616] to-[#161616] border border-[#D4915D]/20 rounded-xl p-4">
            {/* Section Header - Inline with View All */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#D4915D]/20 to-[#C47D52]/10 border border-[#D4915D]/30 flex items-center justify-center shrink-0">
                  <svg className="w-3.5 h-3.5 text-[#D4915D]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 6h4v4H6zM14 6h4v4h-4zM6 14h4v4H6zM14 14h4v4h-4z" />
                  </svg>
                </div>
                <h2 className="text-base font-bold text-white">
                  Pre-installed Apps
                </h2>
              </div>
              <button className="text-xs text-[#D4915D] hover:text-[#E8B896] transition-colors flex items-center gap-1 group/link">
                View all
                <svg className="w-3 h-3 group-hover/link:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            {/* Apps List - 2x2 Grid, Compact */}
            <div className="grid grid-cols-2 gap-2">
              {apps.map((app) => (
                <div
                  key={app.name}
                  className="group/app bg-[#1e1e1e] border border-[#333333] rounded-lg p-2.5 hover:border-[#D4915D]/40 hover:bg-[#222222] transition-all cursor-pointer"
                >
                  <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded-md border transition-colors shrink-0 ${
                      app.category === "image_gen" 
                        ? "bg-gradient-to-br from-[#D4915D]/15 to-[#E8A87C]/10 border-[#D4915D]/25 text-[#E8A87C] group-hover/app:border-[#D4915D]/50"
                        : "bg-gradient-to-br from-[#5BA4A4]/15 to-[#5BA4A4]/10 border-[#5BA4A4]/25 text-[#5BA4A4] group-hover/app:border-[#5BA4A4]/50"
                    }`}>
                      {app.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <h4 className="font-medium text-white group-hover/app:text-[#E8B896] transition-colors text-xs truncate">
                          {app.name}
                        </h4>
                        <span className={`text-[9px] px-1.5 py-0.5 rounded shrink-0 ${
                          app.category === "image_gen"
                            ? "bg-[#D4915D]/15 text-[#D4915D]"
                            : "bg-[#5BA4A4]/15 text-[#5BA4A4]"
                        }`}>
                          {app.category === "image_gen" ? "Image" : "Chat"}
                        </span>
                      </div>
                      <p className="text-[10px] text-[#888888] leading-tight mt-0.5 line-clamp-1">{app.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
