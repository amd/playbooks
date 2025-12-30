import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const PLAYBOOKS_ROOT = path.join(process.cwd(), "..", "playbooks");

function findPlaybookPath(id: string): string | null {
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
        const meta = JSON.parse(jsonContent);
        
        if (meta.id === id) {
          return playbookPath;
        }
      } catch (error) {
        console.error(`Error reading playbook at ${jsonPath}:`, error);
      }
    }
  }

  return null;
}

// Map file extensions to MIME types
function getMimeType(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const mimeTypes: Record<string, string> = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
  };
  return mimeTypes[ext] || "application/octet-stream";
}

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string; path: string[] }> }
) {
  const { id, path: assetPath } = await params;
  
  // Find the playbook directory
  const playbookPath = findPlaybookPath(id);
  
  if (!playbookPath) {
    return NextResponse.json(
      { error: "Playbook not found" },
      { status: 404 }
    );
  }

  // Construct the full asset path (assets folder is part of the URL route, so we add it here)
  const assetFilePath = path.join(playbookPath, "assets", ...assetPath);
  
  // Security check: ensure the resolved path is within the playbook directory
  const resolvedPath = path.resolve(assetFilePath);
  const resolvedPlaybookPath = path.resolve(playbookPath);
  
  if (!resolvedPath.startsWith(resolvedPlaybookPath)) {
    return NextResponse.json(
      { error: "Invalid path" },
      { status: 403 }
    );
  }

  // Check if file exists
  if (!fs.existsSync(resolvedPath)) {
    return NextResponse.json(
      { error: "Asset not found" },
      { status: 404 }
    );
  }

  // Read and return the file
  try {
    const fileBuffer = fs.readFileSync(resolvedPath);
    const mimeType = getMimeType(resolvedPath);
    
    return new NextResponse(fileBuffer, {
      headers: {
        "Content-Type": mimeType,
        "Cache-Control": "public, max-age=31536000, immutable",
      },
    });
  } catch (error) {
    console.error(`Error reading asset at ${resolvedPath}:`, error);
    return NextResponse.json(
      { error: "Failed to read asset" },
      { status: 500 }
    );
  }
}

