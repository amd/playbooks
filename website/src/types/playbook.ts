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
export type Category = "core" | "supplemental" | "backup";
export type Difficulty = "beginner" | "intermediate" | "advanced";

export interface PlaybookMeta {
  /** Unique identifier matching the folder name */
  id: string;
  
  /** Display title */
  title: string;
  
  /** Short description (shown in cards) */
  description: string;
  
  /** Estimated time in minutes */
  time: number;
  
  /** Supported platforms */
  platforms: Platform[];
  
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
  platform: string;
  timeout: number;
  hidden: boolean;
  dependsOn: string[];
  result?: TestResultInfo;
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

