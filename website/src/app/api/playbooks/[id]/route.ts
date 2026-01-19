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
 * Transforms @require tags into @preinstalled blocks with dependency content
 * 
 * Syntax: <!-- @require:dependency-id -->
 * 
 * This allows playbooks to reference shared dependency installation instructions
 * from the central dependencies folder.
 */
function processRequireTags(content: string): string {
  const requirePattern = /<!-- @require:([a-z0-9-]+) -->/g;
  
  return content.replace(requirePattern, (_match, dependencyId) => {
    const depContent = loadDependencyContent(dependencyId);
    
    if (!depContent) {
      console.warn(`Dependency not found: ${dependencyId}`);
      return `<!-- Dependency "${dependencyId}" not found -->`;
    }
    
    // Wrap the dependency content in @preinstalled tags
    // The content already has @os tags, so they'll be processed correctly
    return `<!-- @preinstalled -->\n${depContent}\n<!-- @preinstalled:end -->`;
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

