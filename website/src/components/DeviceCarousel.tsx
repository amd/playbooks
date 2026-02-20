"use client";

import { useState, useEffect, useCallback } from "react";
import raiImg from "@/app/assets/rai.png";
import haloImg from "@/app/assets/halo.png";
import radeonImg from "@/app/assets/radeon.png";

const devices = [
  { id: "stx-halo", name: "STX Halo™", img: haloImg },
  { id: "Krackan", name: "Krackan Point™", img: raiImg },
  { id: "amd-radeon", name: "Radeon™ GPUs", img: radeonImg },
];

const ACCENT = "#D4915D";

export default function DeviceCarousel() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  const goToDevice = useCallback(
    (index: number) => {
      setActiveIndex(index);
      setIsAutoPlaying(false);
    },
    []
  );

  const goNext = useCallback(() => {
    setActiveIndex((prev) => (prev + 1) % devices.length);
  }, []);

  // Auto-play
  useEffect(() => {
    if (!isAutoPlaying) return;
    const interval = setInterval(goNext, 5000);
    return () => clearInterval(interval);
  }, [isAutoPlaying, goNext]);

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Device Selector Tabs */}
      <div className="flex justify-center mb-8">
        <div className="inline-flex items-center bg-[#1a1a1a] border border-[#333333] rounded-xl p-1.5 gap-1">
          {devices.map((device, index) => (
            <button
              key={device.id}
              onClick={() => goToDevice(index)}
              className={`relative px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ${
                index === activeIndex
                  ? "text-black shadow-lg"
                  : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
              }`}
              style={
                index === activeIndex
                  ? { backgroundColor: ACCENT }
                  : undefined
              }
            >
              {device.name}
            </button>
          ))}
        </div>
      </div>

      {/* Image with crossfade */}
      <div className="relative flex justify-center" style={{ minHeight: "200px" }}>
        {devices.map((device, index) => (
          <img
            key={device.id}
            src={device.img.src}
            alt={device.name}
            className="max-h-48 md:max-h-50 w-auto object-contain absolute transition-all duration-500 ease-in-out"
            style={{
              opacity: index === activeIndex ? 1 : 0,
              transform: index === activeIndex ? "scale(1)" : "scale(0.95)",
              pointerEvents: index === activeIndex ? "auto" : "none",
            }}
          />
        ))}
      </div>

    </div>
  );
}
