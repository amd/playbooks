import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const DEPENDENCIES_ROOT = path.join(process.cwd(), "..", "playbooks", "dependencies");

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
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: assetPath } = await params;
  
  // Construct the full asset path
  const assetFilePath = path.join(DEPENDENCIES_ROOT, "assets", ...assetPath);
  
  // Security check: ensure the resolved path is within the dependencies directory
  const resolvedPath = path.resolve(assetFilePath);
  const resolvedDependenciesPath = path.resolve(DEPENDENCIES_ROOT);
  
  if (!resolvedPath.startsWith(resolvedDependenciesPath)) {
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
