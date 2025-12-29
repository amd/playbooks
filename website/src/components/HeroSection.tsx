import Image from "next/image";
import haloPng from "@/app/assets/halo.png";

export default function HeroSection() {
  return (
    <section className="pt-28 pb-12 px-6 gradient-hero relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#D4915D]/5 rounded-full blur-3xl" />
      
      <div className="max-w-[1400px] mx-auto relative z-10">
        <div className="text-center max-w-3xl mx-auto animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-5 leading-tight">
            Start your journey on {" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#D4915D] to-[#E8B896]">
              STX Halo™
            </span>
          </h1>
          
          <div className="my-6 flex justify-center">
            <Image
              src={haloPng}
              alt="STX Halo™"
              className="max-w-[400px] h-auto"
              priority
            />
          </div>
          
          <p className="text-lg md:text-xl text-[#a0a0a0] mb-8 max-w-2xl mx-auto">
            Pre-installed apps, step-by-step playbooks, and powerful AI models ready to run on AMD hardware
          </p>
          
          {/* Quick nav buttons */}
          <div className="flex flex-wrap items-center justify-center gap-3">
            <a
              href="#playbooks"
              className="px-5 py-2.5 bg-[#D4915D] hover:bg-[#B8784A] rounded-lg text-sm font-medium text-black transition-all flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
              </svg>
              View Playbooks
            </a>
            <a
              href="#apps"
              className="px-5 py-2.5 bg-[#1e1e1e] hover:bg-[#2a2a2a] border border-[#333333] hover:border-[#444444] rounded-lg text-sm font-medium text-white transition-all flex items-center gap-2"
            >
              <svg className="w-4 h-4 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 6h4v4H6zM14 6h4v4h-4zM6 14h4v4H6zM14 14h4v4h-4z" />
              </svg>
              Explore Apps
            </a>
            <a
              href="#models"
              className="px-5 py-2.5 bg-[#1e1e1e] hover:bg-[#2a2a2a] border border-[#333333] hover:border-[#444444] rounded-lg text-sm font-medium text-white transition-all flex items-center gap-2"
            >
              <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
              </svg>
              Browse Models
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
