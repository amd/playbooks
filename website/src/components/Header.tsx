"use client";

import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import AMDLogo from "@/app/assets/AMD_Logo.png";

const navLinks = [
  { name: "Playbooks", href: "#playbooks" },
  { name: "Models", href: "#models" },
  { name: "Docs", href: "/docs", external: true },
];

export default function Header() {
  const [searchFocused, setSearchFocused] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-[#0d0d0d]/95 backdrop-blur-md border-b border-[#333333]">
      <div className="max-w-[1400px] mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3">
          <Image
            src={AMDLogo}
            alt="AMD"
            width={80}
            height={32}
            className="h-8 w-auto brightness-0 invert"
          />
          <span className="text-[#D4915D] font-semibold text-lg">Playbooks</span>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              className={`px-4 py-2 text-sm transition-colors flex items-center gap-1 ${
                link.name === "Playbooks"
                  ? "text-[#D4915D] font-medium hover:text-[#E8A87C]"
                  : "text-[#a0a0a0] hover:text-white"
              }`}
            >
              {link.name}
              {link.external && (
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 12 12"
                  fill="currentColor"
                  className="opacity-50"
                >
                  <path d="M3.5 1.5v1h4.793L1.5 9.293l.707.707L9 3.207V8h1V1.5H3.5z" />
                </svg>
              )}
            </Link>
          ))}
        </nav>

        {/* Search and Actions */}
        <div className="flex items-center gap-3">
          <div
            className={`relative hidden sm:flex items-center transition-all ${
              searchFocused ? "w-72" : "w-56"
            }`}
          >
            <svg
              className="absolute left-3 w-4 h-4 text-[#6b6b6b]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              placeholder="Search"
              className="w-full pl-10 pr-4 py-2 bg-[#1a1a1a] border border-[#333333] rounded-md text-sm text-white placeholder-[#6b6b6b] focus:outline-none focus:border-[#D4915D] transition-colors"
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setSearchFocused(false)}
            />
          </div>

          <button className="w-8 h-8 flex items-center justify-center text-[#a0a0a0] hover:text-white border border-[#333333] rounded-full text-sm font-medium transition-colors">
            ?
          </button>

          <button className="px-4 py-2 text-sm font-medium text-white bg-transparent border border-[#333333] rounded-md hover:bg-[#1a1a1a] transition-colors">
            Login
          </button>
        </div>
      </div>
    </header>
  );
}
