import Link from "next/link";

const footerLinks = [
  { name: "Terms of Use", href: "#" },
  { name: "Privacy Policy", href: "#" },
  { name: "Your Privacy Choices", href: "#" },
  { name: "Contact", href: "#" },
];

export default function Footer() {
  return (
    <footer className="bg-[#0d0d0d] border-t border-[#333333] py-6">
      <div className="max-w-[1400px] mx-auto px-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2 text-sm text-[#6b6b6b]">
            {footerLinks.map((link, index) => (
              <span key={link.name} className="flex items-center gap-2">
                <Link
                  href={link.href}
                  className="hover:text-white transition-colors"
                >
                  {link.name}
                </Link>
                {index < footerLinks.length - 1 && (
                  <span className="text-[#444444]">|</span>
                )}
              </span>
            ))}
          </div>
          <p className="text-sm text-[#6b6b6b]">
            Copyright © 2025 AMD Corporation
          </p>
        </div>
      </div>
    </footer>
  );
}
