interface Model {
  name: string;
  description: string;
  size?: string;
  tags?: string[];
}

const models: Model[] = [
  {
    name: "GPT-OSS-120B",
    description: "Powerful 120B parameter open-source model for complex reasoning and generation tasks",
    size: "120B",
    tags: ["Flagship", "Reasoning"],
  },
  {
    name: "GPT-OSS-20B",
    description: "Efficient 20B parameter model balancing performance with resource efficiency",
    size: "20B",
    tags: ["Efficient"],
  },
  {
    name: "Qwen3-Coder-30B",
    description: "High-performance 30B coding model with strong instruction following and code generation",
    size: "30B",
    tags: ["Coding"],
  },
  {
    name: "Z Image Turbo",
    description: "Fast diffusion-based image pipeline for high-quality text-to-image generation",
    tags: ["Diffusion", "Fast"],
  },
];

export default function BuiltInModelsSection() {
  return (
    <section className="py-10 px-6 bg-gradient-to-b from-[#0d0d0d] to-[#111111]" id="models">
      <div className="max-w-[1400px] mx-auto">
        <div className="flex items-center gap-2.5 mb-6">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 flex items-center justify-center">
            <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">
              Explore Built-in Models
            </h2>
            <p className="text-xs text-[#a0a0a0]">
              Ready-to-use AI models optimized for your AMD device
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {models.map((model) => (
            <div
              key={model.name}
              className="group bg-[#1e1e1e] border border-[#333333] rounded-lg px-4 py-3 hover:border-emerald-500/40 hover:bg-[#242424] transition-all cursor-pointer"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 group-hover:border-emerald-500/40 transition-colors shrink-0">
                  <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="font-semibold text-sm text-white group-hover:text-emerald-300 transition-colors">
                      {model.name}
                    </h4>
                    {model.size && (
                      <span className="text-[10px] text-[#6b6b6b]">{model.size}</span>
                    )}
                  </div>
                  <p className="text-xs text-[#a0a0a0] line-clamp-1">{model.description}</p>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  {model.tags?.map((tag) => (
                    <span key={tag} className="px-1.5 py-0.5 bg-[#333333] text-[#a0a0a0] text-[10px] rounded">
                      {tag}
                    </span>
                  ))}
                  <svg className="w-3.5 h-3.5 text-[#888888] ml-1" viewBox="0 0 24 24" fill="currentColor" aria-label="Windows">
                    <path d="M3 12V6.75l6-1.32v6.48L3 12zm17-9v8.75l-10 .15V5.21L20 3zM3 13l6 .09v6.81l-6-1.15V13zm7 .25l10 .15V21l-10-1.91V13.25z"/>
                  </svg>
                  <svg className="w-3.5 h-3.5 text-[#888888]" viewBox="0 0 24 24" fill="currentColor" aria-label="Linux">
                    <path d="M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.132 1.884 1.071.771-.06 1.592-.536 2.257-1.306.631-.765 1.683-1.084 2.378-1.503.348-.199.629-.469.649-.853.023-.4-.2-.811-.714-1.376v-.097l-.003-.003c-.17-.2-.25-.535-.338-.926-.085-.401-.182-.786-.492-1.046h-.003c-.059-.054-.123-.067-.188-.135a.357.357 0 00-.19-.064c.431-1.278.264-2.55-.173-3.694-.533-1.41-1.465-2.638-2.175-3.483-.796-1.005-1.576-1.957-1.56-3.368.026-2.152.236-6.133-3.544-6.139z"/>
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
