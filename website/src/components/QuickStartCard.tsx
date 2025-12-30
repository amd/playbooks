import Link from "next/link";
import type { ReactNode } from "react";

interface QuickStartCardProps {
  title: string;
  description: string;
  time: string;
  href: string;
  icon: string;
}

const iconMap: Record<string, ReactNode> = {
  vscode: (
    <svg viewBox="0 0 24 24" className="w-8 h-8" fill="#0078d4">
      <path d="M17.583 3.271l-4.5 4.5L17.583 3.271zm0 0l4.125 4.125v9.208l-4.125 4.125-10.5-7.875L3.958 16.5.833 14.292V9.708L3.958 7.5l3.125 3.646L17.583 3.271zM17.583 20.729l-10.5-7.875-3.125 3.646L.833 14.292V9.708L3.958 7.5l3.125 3.646 10.5-7.875 4.125 4.125v9.208l-4.125 4.125z" />
    </svg>
  ),
  dashboard: (
    <svg viewBox="0 0 24 24" className="w-8 h-8" fill="#D4915D">
      <path d="M4 5h16v2H4zm0 6h10v2H4zm0 6h16v2H4zm14-6h2v8h-2z" />
    </svg>
  ),
  webui: (
    <svg viewBox="0 0 24 24" className="w-8 h-8" fill="#C47D52">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
    </svg>
  ),
  comfy: (
    <svg viewBox="0 0 24 24" className="w-8 h-8" fill="#5BA4A4">
      <path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14zM5 15h14v3H5zm0-4h14v3H5zm0-4h14v3H5z" />
    </svg>
  ),
};

export default function QuickStartCard({
  title,
  description,
  time,
  href,
  icon,
}: QuickStartCardProps) {
  const getTimeColor = (timeStr: string) => {
    if (timeStr.includes("5")) return "time-badge-ember";
    if (timeStr.includes("15")) return "time-badge-copper";
    if (timeStr.includes("30")) return "time-badge-teal";
    if (timeStr.includes("45")) return "time-badge-warm";
    return "time-badge-ember";
  };

  return (
    <Link href={href} className="block">
      <div className="bg-[#1e1e1e] border border-[#333333] rounded-xl p-5 card-hover h-full">
        <div className="flex items-start gap-4">
          <div className="p-2 bg-[#242424] rounded-lg shrink-0">
            {iconMap[icon] || iconMap.vscode}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="font-semibold text-white truncate">{title}</h3>
              <span
                className={`px-2 py-0.5 rounded-full text-xs font-medium shrink-0 ${getTimeColor(
                  time
                )}`}
              >
                {time}
              </span>
            </div>
            <p className="text-sm text-[#a0a0a0] line-clamp-2">{description}</p>
          </div>
        </div>
      </div>
    </Link>
  );
}
