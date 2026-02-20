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

export default function DeviceCarousel({ activeId, onActiveIdChange }: DeviceCarouselProps) {
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  const selectDevice = useCallback((id: string) => {
    onActiveIdChange(id);
    setIsAutoPlaying(false);
  }, [onActiveIdChange]);

  const goNext = useCallback(() => {
    onActiveIdChange((() => {
      const allIds = [ALL_ID, ...devices.map((d) => d.id)];
      const idx = allIds.indexOf(activeId);
      return allIds[(idx + 1) % allIds.length];
    })());
  }, [activeId, onActiveIdChange]);

  useEffect(() => {
    if (!isAutoPlaying) return;
    const interval = setInterval(goNext, 5000);
    return () => clearInterval(interval);
  }, [isAutoPlaying, goNext]);

  const isAll = activeId === ALL_ID;

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Device Selector Tabs */}
      <div className="flex justify-center mb-8">
        <div className="inline-flex items-center bg-[#1a1a1a] border border-[#333333] rounded-xl p-1.5 gap-1">
          {devices.map((device) => (
            <button
              key={device.id}
              onClick={() => selectDevice(device.id)}
              className={`relative px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ${
                activeId === device.id
                  ? "text-black shadow-lg"
                  : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
              }`}
              style={
                activeId === device.id
                  ? { backgroundColor: ACCENT }
                  : undefined
              }
            >
              {device.name}
            </button>
          ))}
          <button
            onClick={() => selectDevice(ALL_ID)}
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
          {devices.map((device, i) => (
            <img
              key={device.id}
              src={device.img.src}
              alt={device.name}
              className="max-h-40 md:max-h-44 w-auto object-contain absolute drop-shadow-xl"
              style={{
                transform: `translateX(${overlapStyles[i].translateX}) translateY(${overlapStyles[i].translateY}) rotate(${overlapStyles[i].rotate})`,
                zIndex: overlapStyles[i].zIndex,
                transition: "transform 0.5s ease",
              }}
            />
          ))}
        </div>

        {/* Individual device views */}
        {devices.map((device) => (
          <img
            key={device.id}
            src={device.img.src}
            alt={device.name}
            className="max-h-48 md:max-h-50 w-auto object-contain absolute transition-all duration-500 ease-in-out"
            style={{
              opacity: activeId === device.id ? 1 : 0,
              transform: activeId === device.id ? "scale(1)" : "scale(0.95)",
              pointerEvents: activeId === device.id ? "auto" : "none",
            }}
          />
        ))}
      </div>
    </div>
  );
}
