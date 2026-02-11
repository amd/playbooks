"use client";

import { useEffect, useCallback } from "react";

interface ImageLightboxProps {
  src: string;
  alt: string;
  isOpen: boolean;
  onClose: () => void;
}

/**
 * A clean, minimal lightbox component for expanding images
 * Features:
 * - Click outside to close
 * - ESC key to close
 * - Smooth fade animation
 * - Zoom effect on the image
 */
export default function ImageLightbox({ src, alt, isOpen, onClose }: ImageLightboxProps) {
  // Handle ESC key to close
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") {
      onClose();
    }
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      // Prevent body scroll when lightbox is open
      document.body.style.overflow = "hidden";
    }
    
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center animate-lightbox-fade-in"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/90 backdrop-blur-sm" />
      
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 z-10 p-2 text-white/70 hover:text-white transition-colors rounded-full hover:bg-white/10"
        aria-label="Close image"
      >
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      
      {/* Hint text */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/50 text-sm">
        Press <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-xs">ESC</kbd> or click anywhere to close
      </div>
      
      {/* Image container */}
      <div 
        className="relative max-w-[90vw] max-h-[90vh] animate-lightbox-zoom-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={src}
          alt={alt}
          className="max-w-full max-h-[90vh] object-contain rounded-lg shadow-2xl"
        />
        
        {/* Alt text caption if available */}
        {alt && (
          <div className="absolute -bottom-10 left-0 right-0 text-center text-white/60 text-sm truncate px-4">
            {alt}
          </div>
        )}
      </div>
    </div>
  );
}
