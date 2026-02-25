import { NextResponse } from "next/server";

const REPO_OWNER = "amd";
const REPO_NAME = "halo_playbooks";
const GITHUB_API = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`;

interface GHJob {
  id: number;
  run_id: number;
  name: string;
  status: string;
  conclusion: string | null;
  started_at: string | null;
  completed_at: string | null;
  labels: string[];
  runner_id: number;
  runner_name: string;
  html_url: string;
}

interface GHRun {
  id: number;
  name: string;
  status: string;
  conclusion: string | null;
  created_at: string;
  html_url: string;
}

async function ghFetch(path: string, token: string) {
  const res = await fetch(`${GITHUB_API}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    next: { revalidate: 0 },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`GitHub ${res.status}: ${body}`);
  }
  return res.json();
}

export async function GET() {
  const token = process.env.DASHBOARD_GITHUB_TOKEN?.trim();
  if (!token) {
    return NextResponse.json(
      { error: "DASHBOARD_GITHUB_TOKEN environment variable is not set. Add it to website/.env.local" },
      { status: 500 }
    );
  }

  try {
    const runsData = await ghFetch(
      "/actions/workflows/test-playbooks.yml/runs?per_page=10",
      token
    );
    const runs: GHRun[] = runsData.workflow_runs ?? [];

    const jobResults = await Promise.all(
      runs.map((run) =>
        ghFetch(`/actions/runs/${run.id}/jobs?per_page=100`, token)
          .then((d) => d.jobs as GHJob[])
          .catch(() => [] as GHJob[])
      )
    );

    const allJobs = jobResults.flat();

    const selfHostedJobs = allJobs.filter(
      (j) => j.labels.includes("self-hosted") && j.runner_name
    );

    const runnerMap = new Map<
      string,
      {
        runner_id: number;
        runner_name: string;
        labels: string[];
        jobs: {
          id: number;
          run_id: number;
          name: string;
          status: string;
          conclusion: string | null;
          started_at: string | null;
          completed_at: string | null;
          html_url: string;
        }[];
      }
    >();

    for (const job of selfHostedJobs) {
      const key = job.runner_name;
      if (!runnerMap.has(key)) {
        runnerMap.set(key, {
          runner_id: job.runner_id,
          runner_name: job.runner_name,
          labels: job.labels,
          jobs: [],
        });
      }
      runnerMap.get(key)!.jobs.push({
        id: job.id,
        run_id: job.run_id,
        name: job.name,
        status: job.status,
        conclusion: job.conclusion,
        started_at: job.started_at,
        completed_at: job.completed_at,
        html_url: job.html_url,
      });
    }

    for (const runner of runnerMap.values()) {
      runner.jobs.sort(
        (a, b) =>
          new Date(b.started_at ?? 0).getTime() -
          new Date(a.started_at ?? 0).getTime()
      );
    }

    return NextResponse.json({
      runners: Array.from(runnerMap.values()),
      runs_checked: runs.length,
    });
  } catch (e) {
    console.error("Failed to fetch runner data:", e);
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "Failed to fetch runner data" },
      { status: 500 }
    );
  }
}
