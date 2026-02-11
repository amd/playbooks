import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import type { Playbook, PlaybookMeta, Category } from "@/types/playbook";

const PLAYBOOKS_ROOT = path.join(process.cwd(), "..", "playbooks");
const DEPENDENCIES_ROOT = path.join(PLAYBOOKS_ROOT, "dependencies");

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
          if (fs.existsSync(readmePath)) {
            content = fs.readFileSync(readmePath, "utf-8");
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

