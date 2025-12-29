import Header from "@/components/Header";
import Footer from "@/components/Footer";
import HeroSection from "@/components/HeroSection";
import BuiltInAppsSection from "@/components/BuiltInAppsSection";
import PlaybooksSection from "@/components/PlaybooksSection";
import BuiltInModelsSection from "@/components/BuiltInModelsSection";
import SupportBanner from "@/components/SupportBanner";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0d0d0d] grid-pattern">
      <Header />
      <HeroSection />
      <BuiltInAppsSection />
      <PlaybooksSection />
      <BuiltInModelsSection />
      <SupportBanner />
      <Footer />
    </main>
  );
}
