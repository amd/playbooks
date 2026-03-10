import PlaybookCard from "./PlaybookCard";

const allPlaybooks = [
  {
    title: "FLUX.1 Dreambooth LoRA Fine-tuning",
    description:
      "Fine-tune FLUX.1-dev 12B model using Dreambooth LoRA for custom image generation",
    time: "1 HR",
    href: "/halo/flux-finetuning",
  },
  {
    title: "Optimized JAX",
    description: "Optimize JAX to run on Halo™",
    time: "2 HRS",
    href: "/halo/jax",
  },
  {
    title: "LLaMA Factory",
    description: "Install and fine-tune models with LLaMA Factory",
    time: "1 HR",
    href: "/halo/llama-factory",
  },
  {
    title: "Build and Deploy a Multi-Agent Chatbot",
    description:
      "Deploy a multi-agent chatbot system and chat with agents on your Halo™",
    time: "1 HR",
    href: "/halo/multi-agent-chatbot",
  },
  {
    title: "Multi-modal Inference",
    description: "Setup multi-modal inference with ROCm",
    time: "1 HR",
    href: "/halo/multi-modal-inference",
  },
  {
    title: "RCCL for Two Halo™ Devices",
    description: "Install and test RCCL on two Halo™ devices",
    time: "30 MIN",
    href: "/halo/rccl",
  },
  {
    title: "Fine-tune with ROCm",
    description: "Use AMD ROCm to fine-tune models locally",
    time: "1 HR",
    href: "/halo/rocm-fine-tune",
  },
  {
    title: "MIGraphX on Halo™",
    description: "Deploy optimized inference on Halo™ with MIGraphX",
    time: "30 MIN",
    href: "/halo/migraphx",
  },
  {
    title: "FP8 Quantization",
    description:
      "Quantize a model to FP8 to run on Halo™ using AMD optimization tools",
    time: "1 HR",
    href: "/halo/fp8-quantization",
  },
  {
    title: "Fine-tune with Pytorch",
    description: "Use Pytorch to fine-tune models locally",
    time: "1 HR",
    href: "/halo/pytorch-fine-tune",
  },
  {
    title: "RAG Application",
    description:
      "Clone and run a reproducible RAG application on your Halo™",
    time: "30 MIN",
    href: "/halo/rag-application",
  },
  {
    title: "Speculative Decoding",
    description:
      "Learn how to set up speculative decoding for fast inference on Halo™",
    time: "30 MIN",
    href: "/halo/speculative-decoding",
  },
  {
    title: "Connect Two Halo™ Devices",
    description:
      "Connect two Halo™ devices and setup them up for inference and fine-tuning",
    time: "1 HR",
    href: "/halo/connect-two-halos",
  },
  {
    title: "Set up Tailscale on Your Halo™",
    description:
      "Use Tailscale to connect to your Halo™ on your home network no matter where you are",
    time: "30 MIN",
    href: "/halo/tailscale",
  },
  {
    title: "vLLM for Inference",
    description:
      "Install and configure vLLM to run on a single Halo™ or on two Halo™ devices",
    time: "1 HR",
    href: "/halo/vllm",
  },
  {
    title: "Text to Knowledge Graph",
    description:
      "Transform unstructured text into interactive knowledge graphs with LLM inference and graph visualization",
    time: "30 MIN",
    href: "/halo/txt2kg",
  },
  {
    title: "Unsloth on STX Halo™",
    description: "Optimized fine-tuning with Unsloth",
    time: "1 HR",
    href: "/halo/unsloth",
  },
  {
    title: "Install and Use vLLM for Inference",
    description: "Use a container or build vLLM from source for Halo™",
    time: "30 MIN",
    href: "/halo/vllm-install",
  },
  {
    title: "Build a Video Search and Summarization Agent",
    description: "Run the VSS Blueprint on your Halo™",
    time: "1 HR",
    href: "/halo/vss",
  },
];

export default function AllPlaybooksSection() {
  return (
    <section className="py-12 px-6">
      <div className="max-w-[1400px] mx-auto">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-2">All Playbooks</h2>
          <p className="text-[#a0a0a0]">
            Detailed instructions to set up and run popular AI workflows on AMD
            hardware
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {allPlaybooks.map((playbook) => (
            <PlaybookCard key={playbook.title} {...playbook} />
          ))}
        </div>
      </div>
    </section>
  );
}
