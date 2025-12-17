import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

export async function GET() {
  try {
    // Read the cached data file
    const cacheFilePath = path.join(process.cwd(), "github_issues_cache.json");
    const fileContent = await readFile(cacheFilePath, "utf-8");
    const data = JSON.parse(fileContent);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error reading GitHub issues cache:", error);
    
    return NextResponse.json(
      { 
        error: "Failed to read GitHub issues cache. Run 'python fetch_github_issues.py' first.",
        issues: [] 
      },
      { status: 500 }
    );
  }
}
