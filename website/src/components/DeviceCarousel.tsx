"use client";

import { useCallback } from "react";
import raiImg from "@/app/assets/rai.png";
import haloImg from "@/app/assets/halo.png";
import radeonImg from "@/app/assets/radeon.png";

const families = [
  { id: "reference", name: "AMD Ryzen\u2122 AI Halo", img: haloImg },
  { id: "apu", name: "Ryzen\u2122 AI APUs", img: raiImg },
  { id: "gpu", name: "Radeon\u2122 GPUs", img: radeonImg },
];

const ALL_ID = "all";
const ACCENT = "#D4915D";

const overlapStyles: { translateX: string; translateY: string; rotate: string; zIndex: number }[] = [
  { translateX: "-75%", translateY: "2%", rotate: "-4deg", zIndex: 1 },
  { translateX: "0%", translateY: "-3%", rotate: "0deg", zIndex: 3 },
  { translateX: "100%", translateY: "2%", rotate: "4deg", zIndex: 2 },
];

interface DeviceCarouselProps {
  activeId: string;
  onActiveIdChange: (id: string) => void;
}

export default function DeviceCarousel({
  activeId,
  onActiveIdChange,
}: DeviceCarouselProps) {
  const selectFamily = useCallback((id: string) => {
    onActiveIdChange(id);
  }, [onActiveIdChange]);

  const isAll = activeId === ALL_ID;

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Device Family Tabs */}
      <div className="flex justify-center mb-8">
        <div className="inline-flex items-center bg-[#1a1a1a] border border-[#333333] rounded-xl p-1.5 gap-1">
          {families.map((family) => (
            <button
              key={family.id}
              onClick={() => selectFamily(family.id)}
              className={`relative px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 flex items-center gap-1.5 ${
                activeId === family.id
                  ? "text-black shadow-lg"
                  : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
              }`}
              style={
                activeId === family.id
                  ? { backgroundColor: ACCENT }
                  : undefined
              }
            >
              {family.name}
            </button>
          ))}
          <button
            onClick={() => selectFamily(ALL_ID)}
            className={`relative px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ${
              isAll
                ? "text-black shadow-lg"
                : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
            }`}
            style={isAll ? { backgroundColor: ACCENT } : undefined}
          >
            All
          </button>
        </div>
      </div>

      {/* Image display */}
      <div className="relative flex justify-center items-center" style={{ minHeight: "200px" }}>
        {/* Overlapped "All" view */}
        <div
          className="absolute inset-0 flex justify-center items-center transition-all duration-500 ease-in-out"
          style={{
            opacity: isAll ? 1 : 0,
            transform: isAll ? "scale(1)" : "scale(0.92)",
            pointerEvents: isAll ? "auto" : "none",
          }}
        >
          {families.map((family, i) => (
            <img
              key={family.id}
              src={family.img.src}
              alt={family.name}
              className="max-h-40 md:max-h-44 w-auto object-contain absolute drop-shadow-xl"
              style={{
                transform: `translateX(${overlapStyles[i].translateX}) translateY(${overlapStyles[i].translateY}) rotate(${overlapStyles[i].rotate})`,
                zIndex: overlapStyles[i].zIndex,
                transition: "transform 0.5s ease",
              }}
            />
          ))}
        </div>

        {/* Individual family views */}
        {families.map((family) => (
          <img
            key={family.id}
            src={family.img.src}
            alt={family.name}
            className="max-h-48 md:max-h-50 w-auto object-contain absolute transition-all duration-500 ease-in-out"
            style={{
              opacity: activeId === family.id ? 1 : 0,
              transform: activeId === family.id ? "scale(1)" : "scale(0.95)",
              pointerEvents: activeId === family.id ? "auto" : "none",
            }}
          />
        ))}
      </div>
    </div>
  );
}
