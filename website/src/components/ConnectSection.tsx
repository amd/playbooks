import Image from "next/image";
import Link from "next/link";

export default function ConnectSection() {
  return (
    <section className="py-8 px-6">
      <div className="max-w-[1400px] mx-auto">
        <div className="animate-fade-in-delay-1">
          <h2 className="text-xl font-semibold text-white mb-2">
            Connect from Another Computer
          </h2>
          <p className="text-[#a0a0a0] mb-6">Get started with AMD Link</p>

          {/* Featured Card */}
          <div className="bg-[#1e1e1e] border border-[#333333] rounded-xl overflow-hidden card-hover glow-effect">
            <div className="flex flex-col md:flex-row">
              {/* Image Section */}
              <div className="md:w-1/2 p-6 flex items-center justify-center bg-gradient-to-br from-[#2a1f1a] to-[#1a1410]">
                <div className="relative w-full aspect-video max-w-md">
                  {/* Terminal mockup */}
                  <div className="absolute inset-0 bg-[#0d0d0d] rounded-lg border border-[#333333] overflow-hidden">
                    <div className="h-8 bg-[#1a1a1a] border-b border-[#333333] flex items-center px-3 gap-2">
                      <div className="w-3 h-3 rounded-full bg-[#ff5f57]"></div>
                      <div className="w-3 h-3 rounded-full bg-[#febc2e]"></div>
                      <div className="w-3 h-3 rounded-full bg-[#28c840]"></div>
                    </div>
                    <div className="p-4 font-mono text-xs text-[#D4915D]">
                      <p className="mb-1">
                        <span className="text-[#a0a0a0]">$</span> amd-link --configure
                      </p>
                      <p className="text-[#a0a0a0] mb-1">Configuring SSH access...</p>
                      <p className="text-[#D4915D]">✓ Connection established</p>
                      <p className="text-[#a0a0a0] mt-2 mb-1">
                        <span className="text-[#a0a0a0]">$</span> ssh user@amd-device
                      </p>
                      <p className="text-[#D4915D]">Welcome to AMD Developer Platform</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Content Section */}
              <div className="md:w-1/2 p-8 flex flex-col justify-center">
                <h3 className="text-2xl font-semibold text-white mb-3">
                  Set Up Local Network Access
                </h3>
                <p className="text-[#a0a0a0] mb-4">
                  AMD Link helps set up and configure SSH access
                </p>
                <div className="flex items-center gap-2 text-sm text-[#a0a0a0] mb-6">
                  <svg
                    className="w-4 h-4 text-[#D4915D]"
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
                  <span>5 min</span>
                </div>
                <Link
                  href="/halo/connect-to-your-halo"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-[#D4915D] hover:bg-[#B8784A] text-black font-medium rounded-lg transition-colors w-fit"
                >
                  Configure Now
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M14 5l7 7m0 0l-7 7m7-7H3"
                    />
                  </svg>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
