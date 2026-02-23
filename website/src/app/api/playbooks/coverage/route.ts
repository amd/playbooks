import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import type { PlaybookMeta, Category, PlaybookCoverageSummary } from "@/types/playbook";

const PLAYBOOKS_ROOT = path.join(process.cwd(), "..", "playbooks");
const DEPENDENCIES_ROOT = path.join(PLAYBOOKS_ROOT, "dependencies");
const TEST_RESULTS_ROOT = path.join(process.cwd(), "..", "test-results");

interface DependencyRegistryEntry {
  name: string;
  file: string;
  [key: string]: unknown;
}

/**
 * Loads the dependency registry for resolving @require tags.
 */
function loadDependencyRegistry(): Record<string, DependencyRegistryEntry> | null {
  const registryPath = path.join(DEPENDENCIES_ROOT, "registry.json");
  if (!fs.existsSync(registryPath)) return null;
  try {
    const raw = JSON.parse(fs.readFileSync(registryPath, "utf-8"));
    return raw.dependencies || null;
  } catch {
    return null;
  }
}

/**
 * Counts @test tags (and hidden tests / code blocks) found inside dependency
 * content referenced by @require tags in the given README content.
 */
function countDependencyTests(readmeContent: string): { testCount: number; hiddenCount: number; codeBlockCount: number } {
  const registry = loadDependencyRegistry();
  if (!registry) return { testCount: 0, hiddenCount: 0, codeBlockCount: 0 };

  let testCount = 0;
  let hiddenCount = 0;
  let codeBlockCount = 0;

  const requirePattern = /<!-- @require:([a-z0-9-,]+) -->/g;
  let reqMatch;
  while ((reqMatch = requirePattern.exec(readmeContent)) !== null) {
    const depIds = reqMatch[1].split(',').map((id: string) => id.trim()).filter(Boolean);
    for (const depId of depIds) {
      const dep = registry[depId];
      if (!dep) continue;
      const depFilePath = path.join(DEPENDENCIES_ROOT, dep.file);
      if (!fs.existsSync(depFilePath)) continue;
      try {
        const depContent = fs.readFileSync(depFilePath, "utf-8");
        // Count @test tags in the dependency content
        const testTagPattern = /<!-- @test:([^>]+) -->/g;
        let testMatch;
        while ((testMatch = testTagPattern.exec(depContent)) !== null) {
          testCount++;
          if (/hidden\s*=\s*(?:"true"|true)/i.test(testMatch[1])) {
            hiddenCount++;
          }
        }
        // Count code blocks
        codeBlockCount += (depContent.match(/```\w*\s*\n/g) || []).length;
      } catch {
        // ignore read errors
      }
    }
  }

  return { testCount, hiddenCount, codeBlockCount };
}

function getCategory(categoryFolder: string): Category {
  if (categoryFolder === "core") return "core";
  if (categoryFolder === "supplemental") return "supplemental";
  return "backup";
}

/**
 * Scans all playbooks and returns per-playbook test coverage summaries.
 * Mirrors the scan_playbooks() function from _test_preview.py.
 */
function scanCoverage(): PlaybookCoverageSummary[] {
  const summaries: PlaybookCoverageSummary[] = [];
  const categories = ["core", "supplemental"];

  for (const category of categories) {
    const categoryPath = path.join(PLAYBOOKS_ROOT, category);
    if (!fs.existsSync(categoryPath)) continue;

    const folders = fs.readdirSync(categoryPath, { withFileTypes: true });

    for (const folder of folders) {
      if (!folder.isDirectory()) continue;

      const jsonPath = path.join(categoryPath, folder.name, "playbook.json");
      const readmePath = path.join(categoryPath, folder.name, "README.md");
      if (!fs.existsSync(jsonPath)) continue;

      let meta: PlaybookMeta;
      try {
        meta = JSON.parse(fs.readFileSync(jsonPath, "utf-8"));
      } catch {
        continue;
      }

      let testCount = 0;
      let hiddenCount = 0;
      let totalCodeBlocks = 0;

      if (fs.existsSync(readmePath)) {
        const content = fs.readFileSync(readmePath, "utf-8");

        // Count @test tags in the README itself
        const testTagPattern = /<!-- @test:([^>]+) -->/g;
        let match;
        while ((match = testTagPattern.exec(content)) !== null) {
          testCount++;
          if (/hidden\s*=\s*(?:"true"|true)/i.test(match[1])) {
            hiddenCount++;
          }
        }

        // Count code blocks in the README
        totalCodeBlocks = (content.match(/```\w*\s*\n/g) || []).length;

        // Also count tests and code blocks from @require dependencies
        const depCounts = countDependencyTests(content);
        testCount += depCounts.testCount;
        hiddenCount += depCounts.hiddenCount;
        totalCodeBlocks += depCounts.codeBlockCount;
      }

      // Check for test results
      let hasResults = false;
      let resultsSummary: { passed: number; failed: number; skipped: number } | undefined;
      const resultsPath = path.join(TEST_RESULTS_ROOT, meta.id, "summary.json");
      if (fs.existsSync(resultsPath)) {
        try {
          const raw = JSON.parse(fs.readFileSync(resultsPath, "utf-8"));
          hasResults = true;
          resultsSummary = {
            passed: raw.passed ?? 0,
            failed: raw.failed ?? 0,
            skipped: raw.skipped ?? 0,
          };
        } catch {
          // ignore
        }
      }

      summaries.push({
        id: meta.id,
        title: meta.title || meta.id,
        category: getCategory(category),
        platforms: meta.platforms || [],
        testCount,
        hiddenCount,
        visibleTestCount: testCount - hiddenCount,
        totalCodeBlocks,
        hasResults,
        resultsSummary,
      });
    }
  }

  return summaries;
}

export async function GET() {
  return NextResponse.json(scanCoverage());
}
