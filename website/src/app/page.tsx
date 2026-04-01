"use client";

import { useState, useCallback } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import HeroSection from "@/components/HeroSection";
import DeveloperProgramSection from "@/components/BuiltInAppsSection";
import PlaybooksSection from "@/components/PlaybooksSection";
import BuiltInModelsSection from "@/components/BuiltInModelsSection";
import RocmSoftwareSection from "@/components/RocmSoftwareSection";
import SupportBanner from "@/components/SupportBanner";
import type { Device } from "@/types/playbook";
import { DEVICE_CATEGORY_MAP } from "@/types/playbook";

export default function Home() {
  const [activeDevice, setActiveDevice] = useState("reference");
  const [selectedDevice, setSelectedDevice] = useState<Device | null>("halo");

  const handleCategoryChange = useCallback((category: string) => {
    setActiveDevice(category);
    if (category === "all") {
      setSelectedDevice(null);
    } else {
      const info = DEVICE_CATEGORY_MAP[category as keyof typeof DEVICE_CATEGORY_MAP];
      setSelectedDevice(info?.devices[0] ?? null);
    }
  }, []);

  return (
    <main className="min-h-screen bg-[#0d0d0d] grid-pattern">
      <Header />
      <HeroSection activeDevice={activeDevice} onDeviceChange={handleCategoryChange} />
      <PlaybooksSection activeDevice={activeDevice} selectedDevice={selectedDevice} onSelectedDeviceChange={setSelectedDevice} />
      <DeveloperProgramSection />
      <BuiltInModelsSection />
      <RocmSoftwareSection />
      <SupportBanner />
      <Footer />
    </main>
  );
}
