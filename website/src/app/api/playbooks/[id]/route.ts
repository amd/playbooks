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
 * Transforms @require tags into @preinstalled blocks with dependency content
 * 
 * Syntax: 
 *   <!-- @require:dependency-id -->           (single dependency)
 *   <!-- @require:dep1,dep2,dep3 -->          (multiple dependencies, single dropdown)
 * 
 * This allows playbooks to reference shared dependency installation instructions
 * from the central dependencies folder. Multiple dependencies are combined into
 * a single "Already pre-installed" dropdown.
 */
function processRequireTags(content: string): string {
  // Match @require with one or more comma-separated dependency IDs
  const requirePattern = /<!-- @require:([a-z0-9-,]+) -->/g;
  
  return content.replace(requirePattern, (_match, dependencyIds: string) => {
    // Split by comma and trim whitespace
    const ids = dependencyIds.split(',').map((id: string) => id.trim()).filter(Boolean);
    
    const contents: string[] = [];
    const notFound: string[] = [];
    
    for (const depId of ids) {
      const depContent = loadDependencyContent(depId);
      if (depContent) {
        contents.push(depContent);
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
    
    // Combine all dependency contents with a separator and wrap in @preinstalled tags
    const combinedContent = contents.join('\n\n---\n\n');
    return `<!-- @preinstalled -->\n${combinedContent}\n<!-- @preinstalled:end -->`;
  });
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

    const testInfo: TestInfo = { id: testId, platform, timeout, hidden, dependsOn };
    const result = resultsMap[testId];
    if (result) testInfo.result = result;
    tests.push(testInfo);

    const deps = dependsOn.join(",");
    const encodedCode = encodeURIComponent(codeBlock);
    const marker = `<div class="test-coverage-block" data-test-id="${testId}" data-platform="${platform}" data-timeout="${timeout}" data-hidden="${hidden}" data-depends="${deps}" data-code="${encodedCode}"></div>`;
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
            // Process @require tags to inject shared dependency content
            content = processRequireTags(content);
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

