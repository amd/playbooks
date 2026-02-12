import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const TEST_RESULTS_ROOT = path.join(process.cwd(), "..", "test-results");

/**
 * Serves test log files (stdout/stderr) for a given playbook and test ID.
 * 
 * GET /api/playbooks/{id}/logs/{testId}
 * 
 * Returns JSON with stdout and stderr contents:
 * { stdout: string, stderr: string }
 */
export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string; testId: string }> }
) {
  const { id: playbookId, testId } = await params;

  // Validate testId to prevent path traversal
  if (!/^[a-zA-Z0-9_-]+$/.test(testId)) {
    return NextResponse.json(
      { error: "Invalid test ID" },
      { status: 400 }
    );
  }

  const resultsDir = path.join(TEST_RESULTS_ROOT, playbookId);

  // Security check: ensure the resolved path is within the test-results directory
  const resolvedDir = path.resolve(resultsDir);
  const resolvedRoot = path.resolve(TEST_RESULTS_ROOT);
  if (!resolvedDir.startsWith(resolvedRoot)) {
    return NextResponse.json(
      { error: "Invalid path" },
      { status: 403 }
    );
  }

  if (!fs.existsSync(resolvedDir)) {
    return NextResponse.json(
      { error: "No test results found for this playbook" },
      { status: 404 }
    );
  }

  // Read stdout and stderr log files
  const stdoutPath = path.join(resolvedDir, `${testId}_stdout.txt`);
  const stderrPath = path.join(resolvedDir, `${testId}_stderr.txt`);

  let stdout = "";
  let stderr = "";

  try {
    if (fs.existsSync(stdoutPath)) {
      stdout = fs.readFileSync(stdoutPath, "utf-8");
    }
  } catch (error) {
    console.error(`Error reading stdout for ${testId}:`, error);
  }

  try {
    if (fs.existsSync(stderrPath)) {
      stderr = fs.readFileSync(stderrPath, "utf-8");
    }
  } catch (error) {
    console.error(`Error reading stderr for ${testId}:`, error);
  }

  // Return 404 if no logs exist at all
  if (!stdout && !stderr) {
    return NextResponse.json(
      { error: "No logs found for this test" },
      { status: 404 }
    );
  }

  return NextResponse.json({ stdout, stderr });
}
