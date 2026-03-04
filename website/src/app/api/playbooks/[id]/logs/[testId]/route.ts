import { NextResponse } from "next/server";
import {
  getLatestNightlyRun,
  getRunById,
  findAllPlaybookArtifacts,
  extractTestLogs,
} from "@/lib/github-test-results";

/**
 * Serves test log files (stdout/stderr) for a given playbook and test ID,
 * fetched from the latest GitHub Actions nightly run artifacts.
 *
 * GET /api/playbooks/{id}/logs/{testId}
 *
 * Returns JSON: { stdout: string, stderr: string }
 */
export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string; testId: string }> }
) {
  const { id: playbookId, testId } = await params;

  // Validate testId to prevent injection
  if (!/^[a-zA-Z0-9_-]+$/.test(testId)) {
    return NextResponse.json({ error: "Invalid test ID" }, { status: 400 });
  }

  const token = process.env.DASHBOARD_GITHUB_TOKEN?.trim();
  if (!token) {
    return NextResponse.json(
      { error: "DASHBOARD_GITHUB_TOKEN is not configured" },
      { status: 503 }
    );
  }

  // Optional specific run ID — if omitted the latest nightly run is used.
  const { searchParams } = new URL(request.url);
  const runIdParam = searchParams.get("run_id");
  const runId = runIdParam ? parseInt(runIdParam, 10) : undefined;

  let nightly;
  try {
    nightly = runId
      ? await getRunById(token, runId)
      : await getLatestNightlyRun(token);
  } catch (err) {
    console.error("Failed to fetch nightly run:", err);
    return NextResponse.json(
      { error: "Failed to fetch workflow run from GitHub" },
      { status: 502 }
    );
  }

  if (!nightly) {
    return NextResponse.json(
      { error: "No nightly test run found" },
      { status: 404 }
    );
  }

  const allArtifacts = findAllPlaybookArtifacts(nightly.artifacts, playbookId);

  for (const { artifact } of allArtifacts) {
    try {
      const logs = await extractTestLogs(artifact, token, testId);
      if (!logs) continue;
      if (!logs.stdout && !logs.stderr) continue;
      return NextResponse.json(logs);
    } catch {
      // Try next artifact
    }
  }

  return NextResponse.json(
    { error: "No logs found for this test in the latest nightly run" },
    { status: 404 }
  );
}
