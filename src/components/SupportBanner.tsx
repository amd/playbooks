import Link from "next/link";

export default function SupportBanner() {
  return (
    <section className="py-8 px-6">
      <div className="max-w-[1400px] mx-auto">
        <div className="bg-gradient-to-r from-[#2a1f1a] via-[#1e1e1e] to-[#1e1e1e] border border-[#333333] rounded-xl p-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-white mb-2">
              STX Halo™ Support
            </h2>
            <p className="text-[#a0a0a0]">
              Access documentation, software, and expert assistance for your STX
              Halo™.
            </p>
          </div>
          <Link
            href="#"
            className="px-6 py-3 bg-[#242424] hover:bg-[#333333] text-white font-medium rounded-lg border border-[#333333] transition-colors whitespace-nowrap"
          >
            Get Support
          </Link>
        </div>
      </div>
    </section>
  );
}
