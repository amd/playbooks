import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import type { PlaybookMeta, Category, PlaybookCoverageSummary } from "@/types/playbook";

const PLAYBOOKS_ROOT = path.join(process.cwd(), "..", "playbooks");
const TEST_RESULTS_ROOT = path.join(process.cwd(), "..", "test-results");

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

        // Count @test tags
        const testTagPattern = /<!-- @test:([^>]+) -->/g;
        let match;
        while ((match = testTagPattern.exec(content)) !== null) {
          testCount++;
          if (/hidden\s*=\s*(?:"true"|true)/i.test(match[1])) {
            hiddenCount++;
          }
        }

        // Count code blocks
        totalCodeBlocks = (content.match(/```\w*\s*\n/g) || []).length;
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
