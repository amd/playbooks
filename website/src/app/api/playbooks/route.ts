import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import type { Playbook, PlaybookMeta, Category } from "@/types/playbook";

const PLAYBOOKS_ROOT = path.join(process.cwd(), "..", "playbooks");

function getCategory(categoryFolder: string): Category {
  if (categoryFolder === "core") return "core";
  if (categoryFolder === "supplemental") return "supplemental";
  return "backup";
}

function scanPlaybooks(): Playbook[] {
  const playbooks: Playbook[] = [];
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
      
      if (!fs.existsSync(jsonPath)) {
        continue;
      }

      try {
        const jsonContent = fs.readFileSync(jsonPath, "utf-8");
        const meta: PlaybookMeta = JSON.parse(jsonContent);
        
        const playbook: Playbook = {
          ...meta,
          category: getCategory(category),
          path: `${category}/${folder.name}`,
        };
        
        playbooks.push(playbook);
      } catch (error) {
        console.error(`Error reading playbook at ${jsonPath}:`, error);
      }
    }
  }

  return playbooks;
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const publishedOnly = searchParams.get("published") !== "false";
  const category = searchParams.get("category");
  const platform = searchParams.get("platform");

  let playbooks = scanPlaybooks();

  // Filter by published status
  if (publishedOnly) {
    playbooks = playbooks.filter((p) => p.published);
  }

  // Filter by category
  if (category) {
    playbooks = playbooks.filter((p) => p.category === category);
  }

  // Filter by platform
  if (platform) {
    playbooks = playbooks.filter((p) => 
      p.platforms.includes(platform as "windows" | "linux")
    );
  }

  // Sort: featured first, then by category (core first), then by title
  playbooks.sort((a, b) => {
    if (a.isFeatured && !b.isFeatured) return -1;
    if (!a.isFeatured && b.isFeatured) return 1;
    
    const categoryOrder = { core: 0, supplemental: 1, backup: 2 };
    if (categoryOrder[a.category] !== categoryOrder[b.category]) {
      return categoryOrder[a.category] - categoryOrder[b.category];
    }
    
    return a.title.localeCompare(b.title);
  });

  return NextResponse.json(playbooks);
}

