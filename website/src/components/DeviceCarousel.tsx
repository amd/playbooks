"use client";

import { useState, useEffect, useCallback } from "react";

const devices = [
  { id: "stx-halo", name: "STX Halo™" },
  { id: "stx-point", name: "STX Point" },
  { id: "kraken", name: "Kraken" },
  { id: "amd-radeon", name: "Radeon™ GPUs" },
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

      {/* Image */}
      <div className="flex justify-center">
        <img
          src="/rai.png"
          alt="AMD Ryzen AI"
          className="max-h-64 md:max-h-80 w-auto object-contain"
        />
      </div>

    </div>
  );
}
