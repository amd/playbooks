"use client";

import { useState } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import HeroSection from "@/components/HeroSection";
import DeveloperProgramSection from "@/components/BuiltInAppsSection";
import PlaybooksSection from "@/components/PlaybooksSection";
import BuiltInModelsSection from "@/components/BuiltInModelsSection";
import RocmSoftwareSection from "@/components/RocmSoftwareSection";
import SupportBanner from "@/components/SupportBanner";

export default function Home() {
  const [activeDevice, setActiveDevice] = useState("stx-halo");

  return (
    <main className="min-h-screen bg-[#0d0d0d] grid-pattern">
      <Header />
      <HeroSection activeDevice={activeDevice} onDeviceChange={setActiveDevice} />
      <PlaybooksSection activeDevice={activeDevice} />
      <DeveloperProgramSection />
      <BuiltInModelsSection />
      <RocmSoftwareSection />
      <SupportBanner />
      <Footer />
    </main>
  );
}
