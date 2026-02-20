"use client";

import { useState } from "react";
import DeviceCarousel from "./DeviceCarousel";

const titles: Record<string, { prefix: string; highlight: string }> = {
  all: { prefix: "Start your AI journey with", highlight: "AMD Developer Playbooks™" },
  "stx-halo": { prefix: "Start your journey on", highlight: "STX Halo™" },
  Krackan: { prefix: "Start your journey on", highlight: "Krackan Point™" },
  "amd-radeon": { prefix: "Start your journey on", highlight: "Radeon GPUs™" },
};

export default function HeroSection() {
  const [activeId, setActiveId] = useState("all");
  const { prefix, highlight } = titles[activeId] ?? titles.all;

  return (
    <section className="pt-28 pb-4 px-6 gradient-hero relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#D4915D]/5 rounded-full blur-3xl" />
      
      <div className="max-w-[1400px] mx-auto relative z-10">
        <div className="text-center max-w-4xl mx-auto animate-fade-in mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-3 leading-tight">
            {prefix}{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#D4915D] to-[#E8B896]">
              {highlight}
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-[#a0a0a0] max-w-2xl mx-auto">
            Step-by-step playbooks and powerful AI models ready to run. Choose your device to get started.
          </p>
        </div>

        {/* Device Carousel */}
        <DeviceCarousel activeId={activeId} onActiveIdChange={setActiveId} />
      </div>
    </section>
  );
}
