interface Model {
  name: string;
  description: string;
  category: "text_gen" | "text_to_image";
  size?: string;
  tags?: string[];
}

const models: Model[] = [
  {
    name: "GPT-OSS-120b",
    description: "Powerful 120B parameter open-source model for complex reasoning and generation tasks",
    category: "text_gen",
    size: "120B",
    tags: ["Flagship", "Reasoning"],
  },
  {
    name: "GPT-OSS-20b",
    description: "Efficient 20B parameter model balancing performance with resource efficiency",
    category: "text_gen",
    size: "20B",
    tags: ["Efficient"],
  },
  {
    name: "GLM 4.5 Air",
    description: "Lightweight yet capable model for everyday language tasks and conversations",
    category: "text_gen",
    tags: ["Fast", "Conversational"],
  },
  {
    name: "Qwen3-Next-80B",
    description: "State-of-the-art 80B model with exceptional multilingual and coding capabilities",
    category: "text_gen",
    size: "80B",
    tags: ["Multilingual", "Coding"],
  },
  {
    name: "Stable Diffusion 3.5 Large",
    description: "Latest Stable Diffusion model with enhanced photorealism and prompt adherence",
    category: "text_to_image",
    tags: ["Photorealistic", "High Quality"],
  },
  {
    name: "FLUX.2-dev",
    description: "Advanced image generation with exceptional detail and artistic versatility",
    category: "text_to_image",
    tags: ["Creative", "Detailed"],
  },
];

export default function BuiltInModelsSection() {
  const textGenModels = models.filter((m) => m.category === "text_gen");
  const imageModels = models.filter((m) => m.category === "text_to_image");

  return (
    <section className="py-16 px-6 bg-gradient-to-b from-[#0d0d0d] to-[#111111]" id="models">
      <div className="max-w-[1400px] mx-auto">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-10">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 flex items-center justify-center">
                <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
                </svg>
              </div>
              <span className="text-emerald-400 text-sm font-medium uppercase tracking-wider">Built-in Models</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">
              Explore Built-in Models
            </h2>
            <p className="text-[#a0a0a0] text-lg max-w-2xl">
              Ready-to-use AI models optimized for your AMD device
            </p>
          </div>
        </div>

        {/* Text Generation Models */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500/20 to-indigo-500/20 flex items-center justify-center">
              <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white">Text Generation</h3>
            <span className="px-2 py-0.5 bg-[#333333] text-[#a0a0a0] text-xs rounded-full">
              {textGenModels.length} models
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {textGenModels.map((model) => (
              <div
                key={model.name}
                className="group bg-[#1e1e1e] border border-[#333333] rounded-xl p-5 hover:border-emerald-500/40 hover:bg-[#242424] transition-all cursor-pointer"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border border-blue-500/20 group-hover:border-blue-500/40 transition-colors">
                    <svg className="w-7 h-7 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <h4 className="font-semibold text-white group-hover:text-emerald-300 transition-colors">
                          {model.name}
                        </h4>
                        {model.size && (
                          <span className="text-xs text-[#6b6b6b]">{model.size} Parameters</span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-xs shrink-0">
                        <svg className="w-4 h-4 text-[#888888]" viewBox="0 0 24 24" fill="currentColor" aria-label="Windows">
                          <path d="M3 12V6.75l6-1.32v6.48L3 12zm17-9v8.75l-10 .15V5.21L20 3zM3 13l6 .09v6.81l-6-1.15V13zm7 .25l10 .15V21l-10-1.91V13.25z"/>
                        </svg>
                        <svg className="w-4 h-4 text-[#888888]" viewBox="0 0 24 24" fill="currentColor" aria-label="Linux">
                          <path d="M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.132 1.884 1.071.771-.06 1.592-.536 2.257-1.306.631-.765 1.683-1.084 2.378-1.503.348-.199.629-.469.649-.853.023-.4-.2-.811-.714-1.376v-.097l-.003-.003c-.17-.2-.25-.535-.338-.926-.085-.401-.182-.786-.492-1.046h-.003c-.059-.054-.123-.067-.188-.135a.357.357 0 00-.19-.064c.431-1.278.264-2.55-.173-3.694-.533-1.41-1.465-2.638-2.175-3.483-.796-1.005-1.576-1.957-1.56-3.368.026-2.152.236-6.133-3.544-6.139z"/>
                        </svg>
                      </div>
                    </div>
                    <p className="text-sm text-[#a0a0a0] mb-3 line-clamp-2">{model.description}</p>
                    {model.tags && (
                      <div className="flex flex-wrap gap-1.5">
                        {model.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 bg-[#333333] text-[#a0a0a0] text-xs rounded-md"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Text-to-Image Models */}
        <div>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
              <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white">Text-to-Image</h3>
            <span className="px-2 py-0.5 bg-[#333333] text-[#a0a0a0] text-xs rounded-full">
              {imageModels.length} models
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {imageModels.map((model) => (
              <div
                key={model.name}
                className="group bg-[#1e1e1e] border border-[#333333] rounded-xl p-5 hover:border-emerald-500/40 hover:bg-[#242424] transition-all cursor-pointer"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 group-hover:border-purple-500/40 transition-colors">
                    <svg className="w-7 h-7 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h4 className="font-semibold text-white group-hover:text-emerald-300 transition-colors">
                        {model.name}
                      </h4>
                      <div className="flex items-center gap-2 text-xs shrink-0">
                        <svg className="w-4 h-4 text-[#888888]" viewBox="0 0 24 24" fill="currentColor" aria-label="Windows">
                          <path d="M3 12V6.75l6-1.32v6.48L3 12zm17-9v8.75l-10 .15V5.21L20 3zM3 13l6 .09v6.81l-6-1.15V13zm7 .25l10 .15V21l-10-1.91V13.25z"/>
                        </svg>
                        <svg className="w-4 h-4 text-[#888888]" viewBox="0 0 24 24" fill="currentColor" aria-label="Linux">
                          <path d="M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.132 1.884 1.071.771-.06 1.592-.536 2.257-1.306.631-.765 1.683-1.084 2.378-1.503.348-.199.629-.469.649-.853.023-.4-.2-.811-.714-1.376v-.097l-.003-.003c-.17-.2-.25-.535-.338-.926-.085-.401-.182-.786-.492-1.046h-.003c-.059-.054-.123-.067-.188-.135a.357.357 0 00-.19-.064c.431-1.278.264-2.55-.173-3.694-.533-1.41-1.465-2.638-2.175-3.483-.796-1.005-1.576-1.957-1.56-3.368.026-2.152.236-6.133-3.544-6.139z"/>
                        </svg>
                      </div>
                    </div>
                    <p className="text-sm text-[#a0a0a0] mb-3 line-clamp-2">{model.description}</p>
                    {model.tags && (
                      <div className="flex flex-wrap gap-1.5">
                        {model.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 bg-[#333333] text-[#a0a0a0] text-xs rounded-md"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
}

