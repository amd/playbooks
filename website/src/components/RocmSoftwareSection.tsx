interface Software {
  name: string;
  description: string;
  url: string;
  tags?: string[];
}

const software: Software[] = [
  {
    name: "ComfyUI",
    description:
      "Node-based UI for Stable Diffusion with powerful, modular image generation workflows",
    url: "https://github.com/comfyanonymous/ComfyUI",
    tags: ["Image Gen", "Workflows"],
  },
  {
    name: "LM Studio",
    description:
      "Desktop app for discovering, downloading, and running local LLMs with an intuitive interface",
    url: "https://lmstudio.ai",
    tags: ["LLM", "Desktop"],
  },
  {
    name: "n8n",
    description:
      "Open-source workflow automation platform with AI-native capabilities and 400+ integrations",
    url: "https://n8n.io",
    tags: ["Automation", "AI Agents"],
  },
  {
    name: "PyTorch",
    description:
      "Industry-standard deep learning framework with ROCm-accelerated GPU compute support",
    url: "https://pytorch.org",
    tags: ["Framework", "Training"],
  },
  {
    name: "Lemonade",
    description:
      "Serve optimized LLMs, images, and speech locally from your own GPUs and NPUs",
    url: "https://github.com/lemonade-sdk/lemonade",
    tags: ["LLM", "Multi-modal"],
  },
];

export default function RocmSoftwareSection() {
  return (
    <section
      className="py-10 px-6 bg-gradient-to-b from-[#111111] to-[#0d0d0d]"
      id="rocm-software"
    >
      <div className="max-w-[1400px] mx-auto">
        <div className="flex items-center gap-2.5 mb-6">
          <div className="w-8 h-8 rounded-lg bg-[#D4915D]/15 border border-[#D4915D]/30 flex items-center justify-center">
            <svg
              className="w-4 h-4 text-[#D4915D]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25z"
              />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">
              Pre-Installed Apps
            </h2>
            <p className="text-xs text-[#a0a0a0]">
              GPU-accelerated apps ready to run out of the box on your Radeon
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {software.map((sw) => (
            <a
              key={sw.name}
              href={sw.url}
              target="_blank"
              rel="noopener noreferrer"
              className="group bg-[#1e1e1e] border border-[#333333] rounded-lg px-4 py-3 hover:border-[#D4915D]/50 hover:bg-[#242424] transition-all cursor-pointer block"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-[#D4915D]/10 border border-[#D4915D]/20 group-hover:border-[#D4915D]/40 transition-colors shrink-0">
                  <svg
                    className="w-5 h-5 text-[#D4915D]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z"
                    />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="font-semibold text-sm text-white group-hover:text-[#E8B896] transition-colors">
                      {sw.name}
                    </h4>
                  </div>
                  <p className="text-xs text-[#a0a0a0] line-clamp-1">
                    {sw.description}
                  </p>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  {sw.tags?.map((tag) => (
                    <span
                      key={tag}
                      className="px-1.5 py-0.5 bg-[#333333] text-[#a0a0a0] text-[10px] rounded"
                    >
                      {tag}
                    </span>
                  ))}
                  <svg
                    className="w-3.5 h-3.5 text-[#888888] ml-1 group-hover:text-[#D4915D] transition-colors"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"
                    />
                  </svg>
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
