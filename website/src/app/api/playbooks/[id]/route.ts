import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import type { Playbook, PlaybookMeta, Category, TestInfo, TestCoverageInfo } from "@/types/playbook";
import { loadAllGitHubTestResults } from "@/lib/github-test-results";
import type { DeviceTestResult } from "@/lib/github-test-results";

const PLAYBOOKS_ROOT = path.join(process.cwd(), "..", "playbooks");
const DEPENDENCIES_ROOT = path.join(PLAYBOOKS_ROOT, "dependencies");

type ResultsMap = Record<string, { success: boolean; skipped: boolean; duration: number; error: string }>;

interface DependencyRegistry {
  dependencies: Record<string, {
    name: string;
    description: string;
    category: string;
    platforms: string[];
    file: string;
    preinstalled?: Record<string, string[]>;
  }>;
  setup?: Record<string, {
    name: string;
    description: string;
    platforms: string[];
    file: string;
  }>;
}

/**
 * Loads the dependency registry
 */
function loadDependencyRegistry(): DependencyRegistry | null {
  const registryPath = path.join(DEPENDENCIES_ROOT, "registry.json");
  if (!fs.existsSync(registryPath)) {
    return null;
  }
  try {
    const content = fs.readFileSync(registryPath, "utf-8");
    return JSON.parse(content);
  } catch (error) {
    console.error("Error loading dependency registry:", error);
    return null;
  }
}

/**
 * Loads a dependency's markdown content
 */
function loadDependencyContent(dependencyId: string): string | null {
  const registry = loadDependencyRegistry();
  if (!registry || !registry.dependencies[dependencyId]) {
    return null;
  }
  
  const dep = registry.dependencies[dependencyId];
  const filePath = path.join(DEPENDENCIES_ROOT, dep.file);
  
  if (!fs.existsSync(filePath)) {
    return null;
  }
  
  try {
    return fs.readFileSync(filePath, "utf-8");
  } catch (error) {
    console.error(`Error loading dependency ${dependencyId}:`, error);
    return null;
  }
}

/**
 * Loads a setup step's markdown content
 */
function loadSetupContent(setupId: string): string | null {
  const registry = loadDependencyRegistry();
  if (!registry || !registry.setup || !registry.setup[setupId]) {
    return null;
  }
  
  const setup = registry.setup[setupId];
  const filePath = path.join(DEPENDENCIES_ROOT, setup.file);
  
  if (!fs.existsSync(filePath)) {
    return null;
  }
  
  try {
    return fs.readFileSync(filePath, "utf-8");
  } catch (error) {
    console.error(`Error loading setup ${setupId}:`, error);
    return null;
  }
}

/**
 * Processes @test tags found inside dependency content loaded via @require.
 *
 * Normal mode: strips @test tag comments, keeps code blocks, strips #hide lines.
 * Coverage mode: replaces test blocks with coverage marker divs inline so
 *   they render as badges inside the pre-installed dropdown itself.
 *
 * Returns the processed dependency content and extracted TestInfo for
 * merging into the playbook's overall test coverage stats.
 */
function processDependencyTestTags(
  depContent: string,
  showCoverage: boolean,
  resultsMap: ResultsMap,
  deviceResultsList?: DeviceTestResult[],
): { processedContent: string; tests: TestInfo[]; codeBlockCount: number } {
  const testBlockPattern = /<!-- @test:([^>]+) -->\s*(```\w*\s*\n[\s\S]*?```)\s*<!-- @test:end -->/g;
  const tests: TestInfo[] = [];

  const codeBlockCount = (depContent.match(/```\w*\s*\n/g) || []).length;

  const processedContent = depContent.replace(testBlockPattern, (_match, attrStr: string, codeBlock: string) => {
    const attrs = parseTestAttributes(attrStr);
    const testId = (attrs.id as string) || "unknown";
    const timeout = (attrs.timeout as number) || 300;
    const hidden = (attrs.hidden as boolean) || false;
    const setup = (attrs.setup as string) || "";

    const testInfo: TestInfo = { id: testId, timeout, hidden };
    const result = resultsMap[testId];
    if (result) testInfo.result = result;
    if (deviceResultsList) {
      const dr: Record<string, typeof result> = {};
      for (const d of deviceResultsList) {
        if (d.resultsMap[testId]) dr[`${d.device}-${d.platform}`] = d.resultsMap[testId];
      }
      if (Object.keys(dr).length > 0) testInfo.deviceResults = dr;
    }
    tests.push(testInfo);

    if (showCoverage) {
      const encodedCode = encodeURIComponent(codeBlock);
      return `<div class="test-coverage-block" data-test-id="${testId}" data-timeout="${timeout}" data-hidden="${hidden}" data-setup="${setup}" data-code="${encodedCode}"></div>`;
    }

    return stripHideLines(codeBlock);
  });

  return { processedContent, tests, codeBlockCount };
}

/**
 * Transforms @require tags into @preinstalled blocks with dependency content.
 * Also extracts and processes any @test tags found inside dependencies.
 *
 * Syntax:
 *   <!-- @require:dependency-id -->           (single dependency)
 *   <!-- @require:dep1,dep2,dep3 -->          (multiple dependencies, single dropdown)
 *
 * Returns the modified content plus any test info extracted from dependencies,
 * so they can be merged into the playbook's overall test coverage.
 */
/**
 * Computes the intersection of preinstalled device lists across multiple dependencies.
 * A device is only considered preinstalled if ALL deps in the group list it.
 */
function mergePreinstalledData(maps: Array<Record<string, string[]>>): Record<string, string[]> {
  if (maps.length === 0) return {};
  if (maps.length === 1) return maps[0];

  const allPlatforms = new Set<string>();
  for (const m of maps) {
    for (const p of Object.keys(m)) allPlatforms.add(p);
  }

  const result: Record<string, string[]> = {};
  for (const platform of allPlatforms) {
    const lists = maps.map(m => m[platform] || []);
    result[platform] = lists[0].filter(device =>
      lists.every(list => list.includes(device))
    );
  }
  return result;
}

function processRequireTags(
  content: string,
  showCoverage: boolean,
  resultsMap: ResultsMap,
  deviceResultsList?: DeviceTestResult[],
): {
  content: string;
  dependencyTests: TestInfo[];
  dependencyCodeBlocks: number;
} {
  const requirePattern = /<!-- @require:([a-z0-9-,]+) -->/g;
  const allDependencyTests: TestInfo[] = [];
  let totalDependencyCodeBlocks = 0;
  const registry = loadDependencyRegistry();
  
  const processed = content.replace(requirePattern, (_match, dependencyIds: string) => {
    const ids = dependencyIds.split(',').map((id: string) => id.trim()).filter(Boolean);
    
    const contents: string[] = [];
    const notFound: string[] = [];
    const preinstalledMaps: Array<Record<string, string[]>> = [];
    
    for (const depId of ids) {
      const depContent = loadDependencyContent(depId);
      if (depContent) {
        const { processedContent: proc, tests, codeBlockCount } =
          processDependencyTestTags(depContent, showCoverage, resultsMap, deviceResultsList);
        contents.push(proc);
        allDependencyTests.push(...tests);
        totalDependencyCodeBlocks += codeBlockCount;
        
        const depMeta = registry?.dependencies[depId];
        preinstalledMaps.push(depMeta?.preinstalled || {});
      } else {
        notFound.push(depId);
      }
    }
    
    if (notFound.length > 0) {
      console.warn(`Dependencies not found: ${notFound.join(', ')}`);
    }
    
    if (contents.length === 0) {
      return `<!-- Dependencies "${dependencyIds}" not found -->`;
    }
    
    const mergedPreinstalled = mergePreinstalledData(preinstalledMaps);
    const combinedContent = contents.join('\n\n---\n\n');
    return `<!-- @preinstalled:${JSON.stringify(mergedPreinstalled)} -->\n${combinedContent}\n<!-- @preinstalled:end -->`;
  });

  return {
    content: processed,
    dependencyTests: allDependencyTests,
    dependencyCodeBlocks: totalDependencyCodeBlocks,
  };
}

/**
 * Parses key=value attributes from a @test tag string.
 */
function parseTestAttributes(attrString: string): Record<string, unknown> {
  const attrs: Record<string, unknown> = {};
  const pattern = /(\w+)=(?:"([^"]+)"|(\S+))/g;
  let match;
  while ((match = pattern.exec(attrString)) !== null) {
    const key = match[1];
    const value = match[2] || match[3];
    if (key === "timeout") attrs[key] = parseInt(value, 10);
    else if (key === "hidden" || key === "continue_on_error") attrs[key] = value.toLowerCase() === "true";
    else attrs[key] = value;
  }
  return attrs;
}

/**
 * Strips <!-- @github-only --> ... <!-- @github-only:end --> blocks.
 * These blocks contain notices intended only for GitHub readers and
 * should never appear on the website.
 */
function stripGitHubOnlyBlocks(content: string): string {
  return content.replace(
    /<!-- @github-only -->[\s\S]*?<!-- @github-only:end -->\n?/g,
    ''
  );
}

/**
 * Strips lines ending with `#hide` from a fenced code block.
 * These lines are executed by the test runner but invisible to website readers.
 * Preserves the code fence delimiters (``` lines).
 */
function stripHideLines(codeBlock: string): string {
  return codeBlock
    .split('\n')
    .filter(line => !line.trimEnd().endsWith('#hide'))
    .join('\n');
}

/**
 * Processes @test tags used for CI testing.
 *
 * Normal mode (no GitHub results available):
 *   The @test tags are stripped but the code block remains visible.
 *   If hidden=true, both the tags AND the code block are removed.
 *   Lines ending with #hide are stripped from the code block.
 *
 * Coverage mode (GitHub results available):
 *   @test tags are replaced with visible marker divs that the frontend
 *   renders as test-coverage badges on top of code blocks.
 *   Hidden blocks are kept visible with a "hidden test" indicator.
 *   Lines with #hide are kept and visually annotated by the frontend.
 *   Returns test metadata for the stats bar.
 */
function processTestTags(
  content: string,
  showCoverage: boolean,
  resultsMap: ResultsMap,
  resultsSummary?: { passed: number; failed: number; skipped: number },
  deviceResultsList?: DeviceTestResult[],
  deviceSummaries?: Record<string, { passed: number; failed: number; skipped: number }>,
): { content: string; testCoverage?: TestCoverageInfo } {
  const testBlockPattern = /<!-- @test:([^>]+) -->\s*(```\w*\s*\n[\s\S]*?```)\s*<!-- @test:end -->/g;

  if (!showCoverage) {
    const processed = content.replace(testBlockPattern, (_match, attrs: string, codeBlock: string) => {
      const hiddenMatch = /hidden\s*=\s*(?:"true"|true)/i.exec(attrs);
      return hiddenMatch ? '' : stripHideLines(codeBlock);
    });
    return { content: processed };
  }

  // ── Coverage mode ──────────────────────────────────────────────
  const tests: TestInfo[] = [];

  const processed = content.replace(testBlockPattern, (_match, attrStr: string, codeBlock: string) => {
    const attrs = parseTestAttributes(attrStr);
    const testId = (attrs.id as string) || "unknown";
    const timeout = (attrs.timeout as number) || 300;
    const hidden = (attrs.hidden as boolean) || false;
    const setup = (attrs.setup as string) || "";

    const testInfo: TestInfo = { id: testId, timeout, hidden };
    const result = resultsMap[testId];
    if (result) testInfo.result = result;
    if (deviceResultsList) {
      const dr: Record<string, typeof result> = {};
      for (const d of deviceResultsList) {
        if (d.resultsMap[testId]) dr[`${d.device}-${d.platform}`] = d.resultsMap[testId];
      }
      if (Object.keys(dr).length > 0) testInfo.deviceResults = dr;
    }
    tests.push(testInfo);

    const encodedCode = encodeURIComponent(codeBlock);
    return `<div class="test-coverage-block" data-test-id="${testId}" data-timeout="${timeout}" data-hidden="${hidden}" data-setup="${setup}" data-code="${encodedCode}"></div>`;
  });

  const totalCodeBlocks = (content.match(/```\w*\s*\n/g) || []).length;
  const testedDevices = deviceResultsList?.map(d => `${d.device}-${d.platform}`) ?? [];

  return {
    content: processed,
    testCoverage: {
      tests,
      totalCodeBlocks,
      visibleTestCount: tests.filter(t => !t.hidden).length,
      hiddenTestCount: tests.filter(t => t.hidden).length,
      resultsSummary,
      deviceSummaries,
      testedDevices: testedDevices.length > 0 ? testedDevices : undefined,
    },
  };
}

/**
 * Processes inline @setup:id=... definitions (reusable setup steps defined
 * directly in the README).
 *
 * Normal mode: strips the HTML comments.
 * Coverage mode: replaces them with visible marker divs so the frontend can
 *   render them as "Setup Definition" badges.
 */
function processSetupDefinitions(content: string, showCoverage: boolean): string {
  const setupDefPattern = /<!-- @setup:([^>]*\bid=[^>]+?) -->/g;

  if (!showCoverage) {
    return content.replace(setupDefPattern, '');
  }

  return content.replace(setupDefPattern, (_match, attrStr: string) => {
    const attrs = parseTestAttributes(attrStr);
    const setupId = (attrs.id as string) || '';
    if (!setupId) return '';
    const command = (attrs.command as string) || '';
    return `<div class="setup-def-block" data-setup-id="${setupId}" data-command="${encodeURIComponent(command)}"></div>`;
  });
}

/**
 * Transforms @setup tags into @setup-content blocks with setup step content.
 */
function processSetupTags(content: string): string {
  const setupPattern = /<!-- @setup:([a-z0-9_-]+(?:,[a-z0-9_-]+)*) -->/g;
  
  return content.replace(setupPattern, (_match, setupIds: string) => {
    const ids = setupIds.split(',').map((id: string) => id.trim()).filter(Boolean);
    
    const contents: string[] = [];
    const notFound: string[] = [];
    
    for (const setupId of ids) {
      const setupContent = loadSetupContent(setupId);
      if (setupContent) {
        contents.push(setupContent);
      } else {
        notFound.push(setupId);
      }
    }
    
    if (notFound.length > 0) {
      console.warn(`Setup steps not found: ${notFound.join(', ')}`);
    }
    
    if (contents.length === 0) {
      return `<!-- Setup steps "${setupIds}" not found -->`;
    }
    
    const combinedContent = contents.join('\n\n---\n\n');
    return `<!-- @setup-content -->\n${combinedContent}\n<!-- @setup-content:end -->`;
  });
}

function getCategory(categoryFolder: string): Category {
  if (categoryFolder === "core") return "core";
  if (categoryFolder === "supplemental") return "supplemental";
  return "backup";
}

function findPlaybook(
  id: string,
  showCoverage: boolean,
  resultsMap: ResultsMap,
  resultsSummary?: { passed: number; failed: number; skipped: number },
  deviceResultsList?: DeviceTestResult[],
  deviceSummaries?: Record<string, { passed: number; failed: number; skipped: number }>,
): Playbook | null {
  const categories = ["core", "supplemental", "backup"];

  for (const category of categories) {
    const categoryPath = path.join(PLAYBOOKS_ROOT, category);
    
    if (!fs.existsSync(categoryPath)) {
      continue;
    }

    const folders = fs.readdirSync(categoryPath, { withFileTypes: true });
    
    for (const folder of folders) {
      if (!folder.isDirectory()) continue;
      
      const playbookPath = path.join(categoryPath, folder.name);
      const jsonPath = path.join(playbookPath, "playbook.json");
      const readmePath = path.join(playbookPath, "README.md");
      
      if (!fs.existsSync(jsonPath)) {
        continue;
      }

      try {
        const jsonContent = fs.readFileSync(jsonPath, "utf-8");
        const meta: PlaybookMeta = JSON.parse(jsonContent);
        
        if (meta.id === id) {
          let content = "";
          let testCoverage: TestCoverageInfo | undefined;
          if (fs.existsSync(readmePath)) {
            content = fs.readFileSync(readmePath, "utf-8");
            content = stripGitHubOnlyBlocks(content);
            const testResult = processTestTags(content, showCoverage, resultsMap, resultsSummary, deviceResultsList, deviceSummaries);
            content = testResult.content;
            testCoverage = testResult.testCoverage;
            content = processSetupDefinitions(content, showCoverage);
            const requireResult = processRequireTags(content, showCoverage, resultsMap, deviceResultsList);
            content = requireResult.content;
            // Merge dependency tests into the coverage data
            if (testCoverage && requireResult.dependencyTests.length > 0) {
              testCoverage.tests.push(...requireResult.dependencyTests);
              testCoverage.visibleTestCount += requireResult.dependencyTests.filter(t => !t.hidden).length;
              testCoverage.hiddenTestCount += requireResult.dependencyTests.filter(t => t.hidden).length;
              testCoverage.totalCodeBlocks += requireResult.dependencyCodeBlocks;
            }
            // Process @setup tags to inject shared setup/configuration content
            content = processSetupTags(content);
          }

          const playbook: Playbook = {
            ...meta,
            category: getCategory(category),
            path: `${category}/${folder.name}`,
            content,
            ...(testCoverage ? { testCoverage } : {}),
          };
          
          return playbook;
        }
      } catch (error) {
        console.error(`Error reading playbook at ${jsonPath}:`, error);
      }
    }
  }

  return null;
}

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  // Optional specific run ID — if omitted the latest nightly run is used.
  const { searchParams } = new URL(request.url);
  const runIdParam = searchParams.get("run_id");
  const runId = runIdParam ? parseInt(runIdParam, 10) : undefined;

  // Attempt to load test results from GitHub Actions artifacts.
  // Coverage mode is only enabled when both SHOW_TEST_COVERAGE=true (i.e. running
  // via `npm run dev:coverage`) AND a GitHub token is set and results are found.
  let showCoverage = false;
  let resultsMap: ResultsMap = {};
  let resultsSummary: { passed: number; failed: number; skipped: number } | undefined;
  let deviceResultsList: DeviceTestResult[] | undefined;
  let deviceSummaries: Record<string, { passed: number; failed: number; skipped: number }> | undefined;

  const coverageModeEnabled = process.env.SHOW_TEST_COVERAGE === "true";
  const token = process.env.DASHBOARD_GITHUB_TOKEN?.trim();
  if (coverageModeEnabled && token) {
    showCoverage = true;
    try {
      const loaded = await loadAllGitHubTestResults(id, token, runId);
      if (loaded) {
        resultsMap = loaded.resultsMap;
        resultsSummary = loaded.summary;
        deviceResultsList = loaded.deviceResults;
        deviceSummaries = {};
        for (const dr of loaded.deviceResults) {
          deviceSummaries[`${dr.device}-${dr.platform}`] = dr.summary;
        }
      }
    } catch (err) {
      console.error(`Failed to fetch GitHub test results for ${id}:`, err);
    }
  }

  const playbook = findPlaybook(id, showCoverage, resultsMap, resultsSummary, deviceResultsList, deviceSummaries);

  if (!playbook) {
    return NextResponse.json(
      { error: "Playbook not found" },
      { status: 404 }
    );
  }

  return NextResponse.json(playbook);
}
