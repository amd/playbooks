import Link from "next/link";

interface PlaybookCardProps {
  title: string;
  description: string;
  time: string;
  href: string;
  featured?: boolean;
}

export default function PlaybookCard({
  title,
  description,
  time,
  href,
  featured = false,
}: PlaybookCardProps) {
  const getTimeColor = (timeStr: string) => {
    const lowerTime = timeStr.toLowerCase();
    if (lowerTime.includes("hr") || lowerTime.includes("hour")) {
      return "time-badge-warm";
    }
    if (lowerTime.includes("30") || lowerTime.includes("45")) {
      return "time-badge-teal";
    }
    return "time-badge-ember";
  };

  return (
    <Link href={href} className="block group">
      <div
        className={`bg-[#1e1e1e] border border-[#333333] rounded-xl overflow-hidden card-hover h-full ${
          featured ? "md:flex" : ""
        }`}
      >
        {/* Icon/Thumbnail Area */}
        <div
          className={`bg-gradient-to-br from-[#242424] to-[#1a1a1a] p-6 flex items-center justify-center ${
            featured ? "md:w-1/3" : "h-32"
          }`}
        >
          <div className="w-16 h-16 rounded-lg bg-[#333333] flex items-center justify-center">
            <svg
              className="w-8 h-8 text-[#D4915D]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
              />
            </svg>
          </div>
        </div>

        {/* Content */}
        <div className={`p-5 ${featured ? "md:w-2/3 md:flex md:flex-col md:justify-center" : ""}`}>
          <h3 className="font-semibold text-white mb-2 group-hover:text-[#D4915D] transition-colors">
            {title}
          </h3>
          <p className="text-sm text-[#a0a0a0] mb-4 line-clamp-2">{description}</p>
          <div className="flex items-center gap-2">
            <svg
              className="w-4 h-4 text-[#6b6b6b]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getTimeColor(time)}`}>
              {time}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}
