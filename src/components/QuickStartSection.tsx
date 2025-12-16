import QuickStartCard from "./QuickStartCard";

const quickStarts = [
  {
    title: "VS Code",
    description: "Install and use VS Code locally or remotely",
    time: "5 MIN",
    href: "/halo/vscode",
    icon: "vscode",
  },
  {
    title: "Halo™ Dashboard",
    description: "Monitor your STX Halo™ system and launch JupyterLab",
    time: "30 MIN",
    href: "/halo/dashboard",
    icon: "dashboard",
  },
  {
    title: "Open WebUI with Ollama",
    description: "Install Open WebUI and use Ollama to chat with models on your Halo™",
    time: "15 MIN",
    href: "/halo/open-webui",
    icon: "webui",
  },
  {
    title: "Comfy UI",
    description: "Install and use Comfy UI to generate images",
    time: "45 MIN",
    href: "/halo/comfy-ui",
    icon: "comfy",
  },
];

export default function QuickStartSection() {
  return (
    <section className="py-8 px-6">
      <div className="max-w-[1400px] mx-auto">
        <div className="animate-fade-in-delay-2">
          <h2 className="text-xl font-semibold text-white mb-2">
            First Time Here?
          </h2>
          <p className="text-[#a0a0a0] mb-6">Try these developer quickstarts</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {quickStarts.map((item) => (
              <QuickStartCard key={item.title} {...item} />
            ))}
          </div>

          <p className="text-center text-[#a0a0a0] mt-6">
            See More Playbooks Below
          </p>
        </div>
      </div>
    </section>
  );
}
