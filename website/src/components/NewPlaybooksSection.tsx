import PlaybookCard from "./PlaybookCard";

const newPlaybooks = [
  {
    title: "SGLang Inference Server",
    description: "Install and use SGLang on Ryzen™ AI Max",
    time: "30 MIN",
    href: "/halo/sglang",
  },
  {
    title: "ROCm Data Science",
    description:
      "Install and use AMD ROCm libraries to accelerate UMAP, HDBSCAN, pandas and more with zero code changes",
    time: "30 MIN",
    href: "/halo/rocm-data-science",
  },
  {
    title: "Vibe Coding in VS Code",
    description:
      "Use Ryzen™ AI Max as a local or remote Vibe Coding assistant with Ollama and Continue",
    time: "30 MIN",
    href: "/halo/vibe-coding",
  },
];

export default function NewPlaybooksSection() {
  return (
    <section className="py-12 px-6 bg-[#141414]">
      <div className="max-w-[1400px] mx-auto">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-2">New Playbooks</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {newPlaybooks.map((playbook) => (
            <PlaybookCard key={playbook.title} {...playbook} />
          ))}
        </div>
      </div>
    </section>
  );
}
