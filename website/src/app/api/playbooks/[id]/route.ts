import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import type { Playbook, PlaybookMeta, Category, TestInfo, TestCoverageInfo } from "@/types/playbook";

const PLAYBOOKS_ROOT = path.join(process.cwd(), "..", "playbooks");
const DEPENDENCIES_ROOT = path.join(PLAYBOOKS_ROOT, "dependencies");
const TEST_RESULTS_ROOT = path.join(process.cwd(), "..", "test-results");
const SHOW_COVERAGE = process.env.SHOW_TEST_COVERAGE === "true";

interface DependencyRegistry {
  dependencies: Record<string, {
    name: string;
    description: string;
    category: string;
    platforms: string[];
    file: string;
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
 * Unlike processTestTags (which may hide code blocks for hidden tests),
 * this always keeps code blocks visible since they are the dependency's
 * installation instructions shown in the pre-installed dropdown.
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
  playbookId: string,
): { processedContent: string; tests: TestInfo[]; codeBlockCount: number } {
  const testBlockPattern = /<!-- @test:([^>]+) -->\s*(```\w*\s*\n[\s\S]*?```)\s*<!-- @test:end -->/g;
  const tests: TestInfo[] = [];
  const { resultsMap } = SHOW_COVERAGE ? loadTestResults(playbookId) : { resultsMap: {} };

  // Count code blocks before processing (on the original content)
  const codeBlockCount = (depContent.match(/```\w*\s*\n/g) || []).length;

  const processedContent = depContent.replace(testBlockPattern, (_match, attrStr: string, codeBlock: string) => {
    const attrs = parseTestAttributes(attrStr);
    const testId = (attrs.id as string) || "unknown";
    const platform = (attrs.platform as string) || "all";
    const timeout = (attrs.timeout as number) || 300;
    const hidden = (attrs.hidden as boolean) || false;
    const dependsOn = (attrs.depends_on as string[]) || [];
    const setup = (attrs.setup as string) || "";

    const testInfo: TestInfo = { id: testId, platform, timeout, hidden, dependsOn };
    const result = resultsMap[testId];
    if (result) testInfo.result = result;
    tests.push(testInfo);

    if (SHOW_COVERAGE) {
      // In coverage mode: replace the test block with a coverage marker div
      // inline in the dependency content. The dropdown component renders these
      // as TestCoverageBlock badges, just like the main content does.
      const deps = dependsOn.join(",");
      const encodedCode = encodeURIComponent(codeBlock);
      return `<div class="test-coverage-block" data-test-id="${testId}" data-platform="${platform}" data-timeout="${timeout}" data-hidden="${hidden}" data-depends="${deps}" data-setup="${setup}" data-code="${encodedCode}"></div>`;
    }

    // Normal mode: strip test tags but keep the code block visible
    // (it's the installation instruction). Strip #hide lines for clean display.
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
 * This allows playbooks to reference shared dependency installation instructions
 * from the central dependencies folder. Multiple dependencies are combined into
 * a single "Already pre-installed" dropdown.
 * 
 * Returns the modified content plus any test info extracted from dependencies,
 * so they can be merged into the playbook's overall test coverage.
 */
function processRequireTags(content: string, playbookId: string): {
  content: string;
  dependencyTests: TestInfo[];
  dependencyCodeBlocks: number;
} {
  // Match @require with one or more comma-separated dependency IDs
  const requirePattern = /<!-- @require:([a-z0-9-,]+) -->/g;
  const allDependencyTests: TestInfo[] = [];
  let totalDependencyCodeBlocks = 0;
  
  const processed = content.replace(requirePattern, (_match, dependencyIds: string) => {
    // Split by comma and trim whitespace
    const ids = dependencyIds.split(',').map((id: string) => id.trim()).filter(Boolean);
    
    const contents: string[] = [];
    const notFound: string[] = [];
    
    for (const depId of ids) {
      const depContent = loadDependencyContent(depId);
      if (depContent) {
        // Process test tags inside the dependency content
        const { processedContent: processed, tests, codeBlockCount } =
          processDependencyTestTags(depContent, playbookId);
        contents.push(processed);
        allDependencyTests.push(...tests);
        totalDependencyCodeBlocks += codeBlockCount;
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
    
    // Combine all dependency contents with a separator and wrap in @preinstalled tags.
    // In coverage mode the dependency content already contains inline coverage
    // marker divs that the frontend dropdown will render as test badges.
    const combinedContent = contents.join('\n\n---\n\n');
    return `<!-- @preinstalled -->\n${combinedContent}\n<!-- @preinstalled:end -->`;
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
    else if (key === "depends_on") attrs[key] = value.split(",").map((s: string) => s.trim()).filter(Boolean);
    else attrs[key] = value;
  }
  return attrs;
}

/**
 * Loads test results for a playbook from test-results/{id}/summary.json
 */
function loadTestResults(playbookId: string): { resultsMap: Record<string, { success: boolean; skipped: boolean; duration: number; error: string }>; summary?: { passed: number; failed: number; skipped: number } } {
  const resultsPath = path.join(TEST_RESULTS_ROOT, playbookId, "summary.json");
  if (!fs.existsSync(resultsPath)) return { resultsMap: {} };
  try {
    const raw = JSON.parse(fs.readFileSync(resultsPath, "utf-8"));
    const resultsMap: Record<string, { success: boolean; skipped: boolean; duration: number; error: string }> = {};
    for (const r of raw.results || []) {
      resultsMap[r.test_id] = {
        success: r.success,
        skipped: r.skipped ?? false,
        duration: r.duration ?? 0,
        error: r.error_message ?? "",
      };
    }
    return {
      resultsMap,
      summary: { passed: raw.passed ?? 0, failed: raw.failed ?? 0, skipped: raw.skipped ?? 0 },
    };
  } catch {
    return { resultsMap: {} };
  }
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
 * Normal mode (default):
 *   The @test tags are stripped but the code block remains visible.
 *   If hidden=true, both the tags AND the code block are removed.
 *   Lines ending with #hide are stripped from the code block.
 * 
 * Coverage mode (SHOW_TEST_COVERAGE=true):
 *   @test tags are replaced with visible marker divs that the frontend
 *   renders as test-coverage badges on top of code blocks.
 *   Hidden blocks are kept visible with a "hidden test" indicator.
 *   Lines with #hide are kept and visually annotated by the frontend.
 *   Returns test metadata for the stats bar.
 */
function processTestTags(content: string, playbookId: string): { content: string; testCoverage?: TestCoverageInfo } {
  const testBlockPattern = /<!-- @test:([^>]+) -->\s*(```\w*\s*\n[\s\S]*?```)\s*<!-- @test:end -->/g;

  if (!SHOW_COVERAGE) {
    // Normal/user view: strip tags, hide hidden blocks, strip #hide lines
    const processed = content.replace(testBlockPattern, (_match, attrs: string, codeBlock: string) => {
      const hiddenMatch = /hidden\s*=\s*(?:"true"|true)/i.exec(attrs);
      return hiddenMatch ? '' : stripHideLines(codeBlock);
    });
    return { content: processed };
  }

  // ── Coverage mode ──────────────────────────────────────────────
  const tests: TestInfo[] = [];
  const { resultsMap, summary: resultsSummary } = loadTestResults(playbookId);

  const processed = content.replace(testBlockPattern, (_match, attrStr: string, codeBlock: string) => {
    const attrs = parseTestAttributes(attrStr);
    const testId = (attrs.id as string) || "unknown";
    const platform = (attrs.platform as string) || "all";
    const timeout = (attrs.timeout as number) || 300;
    const hidden = (attrs.hidden as boolean) || false;
    const dependsOn = (attrs.depends_on as string[]) || [];

    const setup = (attrs.setup as string) || "";

    const testInfo: TestInfo = { id: testId, platform, timeout, hidden, dependsOn };
    const result = resultsMap[testId];
    if (result) testInfo.result = result;
    tests.push(testInfo);

    const deps = dependsOn.join(",");
    const encodedCode = encodeURIComponent(codeBlock);
    const marker = `<div class="test-coverage-block" data-test-id="${testId}" data-platform="${platform}" data-timeout="${timeout}" data-hidden="${hidden}" data-depends="${deps}" data-setup="${setup}" data-code="${encodedCode}"></div>`;
    return marker;
  });

  const totalCodeBlocks = (content.match(/```\w*\s*\n/g) || []).length;

  return {
    content: processed,
    testCoverage: {
      tests,
      totalCodeBlocks,
      visibleTestCount: tests.filter(t => !t.hidden).length,
      hiddenTestCount: tests.filter(t => t.hidden).length,
      resultsSummary,
    },
  };
}

/**
 * Processes inline @setup:id=... definitions (reusable setup steps defined
 * directly in the README).
 *
 * Normal mode: strips the HTML comments (they are invisible anyway, but be explicit).
 * Coverage mode: replaces them with visible marker divs so the frontend can
 *   render them as "Setup Definition" badges, similar to hidden test blocks.
 *
 * Supports the @os:-wrapped format where platform is inferred from context:
 *   <!-- @os:windows -->
 *   <!-- @setup:id=activate-venv command="llm-env\Scripts\activate.bat" -->
 *   <!-- @os:end -->
 *
 * Definitions outside @os: blocks apply to all platforms.
 *
 * These are distinct from the @setup:setup-id tags handled by processSetupTags,
 * which reference external setup files from the dependencies registry.
 */
function processSetupDefinitions(content: string): string {
  // Match @setup definitions that contain key=value pairs (e.g. id=..., command=...)
  // Distinguished from the old @setup:id format by the presence of '='
  const setupDefPattern = /<!-- @setup:([^>]*\bid=[^>]+?) -->/g;

  if (!SHOW_COVERAGE) {
    // Normal/user view: strip definition comments
    return content.replace(setupDefPattern, '');
  }

  // Coverage mode: determine OS context for each @setup and replace with visible marker divs
  // Pre-compute @os: block ranges to determine platform context
  const osBlockPattern = /<!-- @os:(windows|linux) -->([\s\S]*?)<!-- @os:end -->/g;
  const osRanges: { start: number; end: number; platform: string }[] = [];
  let osMatch;
  while ((osMatch = osBlockPattern.exec(content)) !== null) {
    osRanges.push({ start: osMatch.index, end: osMatch.index + osMatch[0].length, platform: osMatch[1] });
  }

  return content.replace(setupDefPattern, (_match, attrStr: string, offset: number) => {
    const attrs = parseTestAttributes(attrStr);
    const setupId = (attrs.id as string) || '';
    if (!setupId) return '';

    const command = (attrs.command as string) || '';

    // Determine the platform from surrounding @os: block context
    const enclosingOs = osRanges.find(r => offset >= r.start && offset < r.end);
    const platform = enclosingOs ? enclosingOs.platform : 'all';

    return `<div class="setup-def-block" data-setup-id="${setupId}" data-command="${encodeURIComponent(command)}" data-platform="${platform}"></div>`;
  });
}

/**
 * Transforms @setup tags into @setup-content blocks with setup step content
 * 
 * Syntax: 
 *   <!-- @setup:setup-id -->           (single setup step)
 *   <!-- @setup:setup1,setup2 -->      (multiple setup steps)
 * 
 * This allows playbooks to reference shared system setup/configuration instructions
 * from the central dependencies folder. Unlike @require (for pre-installed software),
 * @setup is for configuration steps users need to perform.
 */
function processSetupTags(content: string): string {
  // Match @setup with one or more comma-separated setup IDs (supports underscores and hyphens)
  const setupPattern = /<!-- @setup:([a-z0-9_-]+(?:,[a-z0-9_-]+)*) -->/g;
  
  return content.replace(setupPattern, (_match, setupIds: string) => {
    // Split by comma and trim whitespace
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
    
    // Combine all setup contents with a separator and wrap in @setup-content tags
    const combinedContent = contents.join('\n\n---\n\n');
    return `<!-- @setup-content -->\n${combinedContent}\n<!-- @setup-content:end -->`;
  });
}

function getCategory(categoryFolder: string): Category {
  if (categoryFolder === "core") return "core";
  if (categoryFolder === "supplemental") return "supplemental";
  return "backup";
}

function findPlaybook(id: string): Playbook | null {
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
            // Process @test tags (strip tags, or emit coverage markers)
            const testResult = processTestTags(content, meta.id);
            content = testResult.content;
            testCoverage = testResult.testCoverage;
            // Process inline @setup:id=... definitions (strip or emit coverage markers)
            content = processSetupDefinitions(content);
            // Process @require tags to inject shared dependency content
            // Also extracts tests from dependencies for coverage tracking
            const requireResult = processRequireTags(content, meta.id);
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
  const playbook = findPlaybook(id);

  if (!playbook) {
    return NextResponse.json(
      { error: "Playbook not found" },
      { status: 404 }
    );
  }

  return NextResponse.json(playbook);
}

