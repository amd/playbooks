/**
 * Playbook Contract
 * 
 * This file defines the schema for playbooks that is shared between
 * the playbook.json files and the website.
 * 
 * ## OS-Specific Content Tags
 * 
 * In README.md files, use the following tags for OS-specific instructions:
 * 
 * ```markdown
 * <!-- @os:windows -->
 * Windows-specific instructions here
 * <!-- @os:end -->
 * 
 * <!-- @os:linux -->
 * Linux-specific instructions here
 * <!-- @os:end -->
 * 
 * <!-- @os:all -->
 * Instructions for all platforms
 * <!-- @os:end -->
 * ```
 * 
 * Content outside of these tags is shown on all platforms.
 * 
 * ## Device-Specific Content Tags
 * 
 * Use `@device` tags for device-specific instructions. Supports comma-separated
 * values to target multiple devices:
 * 
 * ```markdown
 * <!-- @device:halo -->
 * STX Halo-only instructions
 * <!-- @device:end -->
 * 
 * <!-- @device:halo,stx -->
 * Instructions for both Halo and STX Point
 * <!-- @device:end -->
 * 
 * <!-- @device:rx7900xt,rx9070xt -->
 * Instructions for discrete Radeon GPUs
 * <!-- @device:end -->
 * 
 * <!-- @device:all -->
 * Instructions for all devices
 * <!-- @device:end -->
 * ```
 * 
 * Valid device IDs: halo, stx, krk, rx7900xt, rx9070xt.
 * Content outside of `@device` tags is shown on all devices.
 * 
 * ## Pre-installed Software Dropdowns
 * 
 * For software pre-installed on AMD Halo Developer Platform, use the `@require` tag
 * to reference installation instructions from the central `dependencies/` folder:
 * 
 * ```markdown
 * <!-- @require:comfyui -->
 * ```
 * 
 * For multiple dependencies, use comma-separated IDs for a single dropdown:
 * 
 * ```markdown
 * <!-- @require:comfyui,pytorch -->
 * ```
 * 
 * Available dependencies are defined in `playbooks/dependencies/registry.json`.
 * This renders as a collapsible dropdown with a green checkmark indicating
 * the software is already available on the Halo platform.
 */

export type Platform = "windows" | "linux";
export type Architecture = "halo" | "krk";
export type Device = "halo" | "stx" | "krk" | "rx7900xt" | "rx9070xt";
export type Category = "core" | "supplemental" | "backup";
export type Difficulty = "beginner" | "intermediate" | "advanced";

export const DEVICE_IDS: Device[] = ["halo", "stx", "krk", "rx7900xt", "rx9070xt"];

export const deviceNames: Record<Device, string> = {
  halo: "STX Halo",
  stx: "STX Point",
  krk: "Krackan Point",
  rx7900xt: "RX 7900 XT",
  rx9070xt: "RX 9070 XT",
};

export interface PlaybookMeta {
  /** Unique identifier matching the folder name */
  id: string;
  
  /** Display title */
  title: string;
  
  /** Short description (shown in cards) */
  description: string;
  
  /** Estimated time in minutes */
  time: number;
  
  /** Shown platforms per device — controls which OS/device combos appear in the UI */
  supported_platforms: Partial<Record<Device, Platform[]>>;

  /** Tested platforms per device (used by CI to select runners) */
  tested_platforms?: Partial<Record<Device, Platform[]>>;

  /** Required platforms per device (CI marks these as must-pass) */
  required_platforms?: Partial<Record<Device, Platform[]>>;
  
  /** Whether this is a new playbook */
  isNew?: boolean;
  
  /** Whether this playbook should be featured */
  isFeatured?: boolean;
  
  /** Whether this playbook is ready to be published */
  published: boolean;
  
  /** Difficulty level */
  difficulty?: Difficulty;
  
  /** Tags for filtering/searching */
  tags?: string[];
  
  /** Icon name or emoji for the playbook */
  icon?: string;
  
  /** Prerequisites (IDs of other playbooks) */
  prerequisites?: string[];
  
  /** Cover image path relative to the playbook folder (e.g., "assets/cover.png") */
  coverImage?: string;
}

export interface TestResultInfo {
  success: boolean;
  skipped: boolean;
  duration: number;
  error: string;
}

export interface TestInfo {
  id: string;
  timeout: number;
  hidden: boolean;
  result?: TestResultInfo;
  /** Per-device test results keyed by device/arch ID (e.g. "halo", "stx") */
  deviceResults?: Record<string, TestResultInfo>;
}

export interface TestCoverageInfo {
  tests: TestInfo[];
  totalCodeBlocks: number;
  visibleTestCount: number;
  hiddenTestCount: number;
  resultsSummary?: {
    passed: number;
    failed: number;
    skipped: number;
  };
  /** Per-device summaries keyed by device/arch ID */
  deviceSummaries?: Record<string, { passed: number; failed: number; skipped: number }>;
  /** Ordered list of tested device/arch IDs */
  testedDevices?: string[];
}

/** Per-playbook coverage summary used by the sidebar overview */
export interface PlaybookCoverageSummary {
  id: string;
  title: string;
  category: Category;
  supported_platforms: Partial<Record<Device, Platform[]>>;
  testCount: number;
  hiddenCount: number;
  visibleTestCount: number;
  totalCodeBlocks: number;
  hasResults: boolean;
  resultsSummary?: {
    passed: number;
    failed: number;
    skipped: number;
  };
}

export interface Playbook extends PlaybookMeta {
  /** Category derived from folder structure */
  category: Category;
  
  /** Path to the playbook folder */
  path: string;
  
  /** Raw markdown content from README.md */
  content?: string;

  /** Test coverage data — only present when running in coverage mode */
  testCoverage?: TestCoverageInfo;
}

/**
 * Formats time in minutes to a human-readable string
 */
export function formatTime(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} MIN`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (mins === 0) {
    return hours === 1 ? "1 HR" : `${hours} HRS`;
  }
  return `${hours}h ${mins}m`;
}

/**
 * Extracts a deduplicated list of platforms (OS) from a supported_platforms map.
 */
export function extractPlatforms(shownPlatforms: Partial<Record<Device, Platform[]>>): Platform[] {
  const set = new Set<Platform>();
  for (const platforms of Object.values(shownPlatforms)) {
    if (platforms) for (const p of platforms) set.add(p);
  }
  return Array.from(set);
}

/**
 * Extracts devices from a supported_platforms map that support the given platform.
 * If no platform is provided, returns all devices.
 */
export function extractDevices(
  shownPlatforms: Partial<Record<Device, Platform[]>>,
  platform?: Platform,
): Device[] {
  return (Object.entries(shownPlatforms) as [Device, Platform[]][])
    .filter(([, platforms]) => !platform || platforms.includes(platform))
    .map(([device]) => device);
}

/**
 * Platform display names
 */
export const platformNames: Record<Platform, string> = {
  windows: "Windows",
  linux: "Linux",
};

/**
 * Platform icons (as simple characters for now)
 */
export const platformIcons: Record<Platform, string> = {
  windows: "⊞",
  linux: "🐧",
};

