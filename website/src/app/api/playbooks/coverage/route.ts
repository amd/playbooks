import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import type { PlaybookMeta, Platform, Device, Category, PlaybookCoverageSummary } from "@/types/playbook";
import {
  getLatestNightlyRun,
  extractFullSummary,
  findAllPlaybookArtifacts,
} from "@/lib/github-test-results";

const PLAYBOOKS_ROOT = path.join(process.cwd(), "..", "playbooks");
const DEPENDENCIES_ROOT = path.join(PLAYBOOKS_ROOT, "dependencies");

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
        const testTagPattern = /<!-- @test:([^>]+) -->/g;
        let testMatch;
        while ((testMatch = testTagPattern.exec(depContent)) !== null) {
          testCount++;
          if (/hidden\s*=\s*(?:"true"|true)/i.test(testMatch[1])) {
            hiddenCount++;
          }
        }
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

interface PlaybookScanResult {
  id: string;
  title: string;
  category: Category;
  shown_platforms: Partial<Record<Device, Platform[]>>;
  testCount: number;
  hiddenCount: number;
  visibleTestCount: number;
  totalCodeBlocks: number;
}

/**
 * Scans all playbook READMEs and counts @test tags per playbook.
 * Does not read any local test-results files — results come from GitHub.
 */
function scanPlaybooks(): PlaybookScanResult[] {
  const results: PlaybookScanResult[] = [];
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

        const testTagPattern = /<!-- @test:([^>]+) -->/g;
        let match;
        while ((match = testTagPattern.exec(content)) !== null) {
          testCount++;
          if (/hidden\s*=\s*(?:"true"|true)/i.test(match[1])) {
            hiddenCount++;
          }
        }

        totalCodeBlocks = (content.match(/```\w*\s*\n/g) || []).length;

        const depCounts = countDependencyTests(content);
        testCount += depCounts.testCount;
        hiddenCount += depCounts.hiddenCount;
        totalCodeBlocks += depCounts.codeBlockCount;
      }

      results.push({
        id: meta.id,
        title: meta.title || meta.id,
        category: getCategory(category),
        shown_platforms: (meta.shown_platforms || {}) as Partial<Record<Device, Platform[]>>,
        testCount,
        hiddenCount,
        visibleTestCount: testCount - hiddenCount,
        totalCodeBlocks,
      });
    }
  }

  return results;
}

export async function GET() {
  const scanned = scanPlaybooks();

  // Try to enrich results with GitHub Actions artifacts
  const token = process.env.DASHBOARD_GITHUB_TOKEN?.trim();
  const resultsByPlaybook = new Map<string, { passed: number; failed: number; skipped: number }>();

  if (token) {
    try {
      const nightly = await getLatestNightlyRun(token);
      if (nightly) {
        await Promise.all(
          scanned.map(async (pb) => {
            const allArtifacts = findAllPlaybookArtifacts(nightly.artifacts, pb.id);
            if (allArtifacts.length === 0) return;

            let totalPassed = 0, totalFailed = 0, totalSkipped = 0;
            await Promise.all(allArtifacts.map(async ({ artifact }) => {
              const summary = await extractFullSummary(artifact, token);
              if (!summary) return;
              totalPassed += summary.passed ?? 0;
              totalFailed += summary.failed ?? 0;
              totalSkipped += summary.skipped ?? 0;
            }));

            if (totalPassed + totalFailed + totalSkipped > 0) {
              resultsByPlaybook.set(pb.id, {
                passed: totalPassed,
                failed: totalFailed,
                skipped: totalSkipped,
              });
            }
          })
        );
      }
    } catch (err) {
      // GitHub fetch failed — return coverage without results
      console.error("Failed to fetch GitHub test results for coverage:", err);
    }
  }

  const summaries: PlaybookCoverageSummary[] = scanned.map((pb) => {
    const ghResults = resultsByPlaybook.get(pb.id);
    return {
      ...pb,
      hasResults: !!ghResults,
      resultsSummary: ghResults,
    };
  });

  return NextResponse.json(summaries);
}
