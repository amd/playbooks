import { NextResponse } from "next/server";
import { listRecentRuns } from "@/lib/github-test-results";

/**
 * GET /api/dashboard/playbook-runs
 *
 * Returns a list of recent completed runs of the test workflow so clients
 * can populate a run-selector UI.
 *
 * Query params:
 *   per_page  – number of runs to return (default 20, max 50)
 */
export async function GET(request: Request) {
  const token = process.env.DASHBOARD_GITHUB_TOKEN?.trim();
  if (!token) {
    return NextResponse.json(
      { error: "DASHBOARD_GITHUB_TOKEN is not configured" },
      { status: 503 }
    );
  }

  const { searchParams } = new URL(request.url);
  const perPage = Math.min(50, Math.max(1, parseInt(searchParams.get("per_page") ?? "20", 10)));

  try {
    const runs = await listRecentRuns(token, perPage);
    return NextResponse.json({ runs });
  } catch (err) {
    console.error("Failed to list playbook runs:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to list workflow runs" },
      { status: 500 }
    );
  }
}
