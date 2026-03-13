export default function DeveloperProgramSection() {
  return (
    <section className="py-4 px-6" id="developer-program">
      <div className="max-w-[1400px] mx-auto">
        <div className="relative group overflow-hidden rounded-xl bg-gradient-to-br from-[#2a1f1a] via-[#1a1a1a] to-[#1e1815] border border-[#D4915D]/30 hover:border-[#D4915D]/50 transition-all duration-500">
          <div className="absolute inset-0 bg-gradient-to-br from-[#D4915D]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

          <div className="relative p-4 md:p-5 flex flex-col md:flex-row gap-4 items-center">
            {/* Image - Left side */}
            <div className="relative rounded-lg overflow-hidden shrink-0 w-full md:w-[240px]">
              <img
                src="https://th.bing.com/th/id/OIP.QEVdu0o4dWP9Nbxl9OFuXgHaEK?w=287&h=180&c=7&r=0&o=7&pid=1.7&rm=3"
                alt="AMD Developer Program"
                className="w-full h-auto object-cover rounded-lg group-hover:scale-105 transition-transform duration-700"
              />
            </div>

            {/* Content - Right side */}
            <div className="flex-1 flex flex-col min-w-0">
              {/* Title */}
              <h2 className="text-lg md:text-xl font-bold text-white mb-2 leading-tight">
                Join the{" "}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#D4915D] to-[#E8B896]">
                  AMD Developer Program
                </span>
              </h2>

              <p className="text-[#a0a0a0] text-sm mb-3 leading-relaxed max-w-xl">
                Get early access to tools, SDKs, and resources to build, optimize, and deploy AI workloads on AMD hardware.
              </p>

              {/* CTA Button */}
              <a
                href="https://www.amd.com/en/developer.html"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-[#D4915D] to-[#C47D52] text-black font-semibold text-sm hover:from-[#E8B896] hover:to-[#D4915D] transition-all duration-300 group/btn shadow-lg shadow-[#D4915D]/20 w-fit"
              >
                Join Now
                <svg
                  className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
