import { NextResponse } from "next/server";

const REPO_OWNER = "amd";
const REPO_NAME = "halo_playbooks";
const GITHUB_API = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`;

interface GHRunner {
  id: number;
  name: string;
  os: string;
  status: string;
  busy: boolean;
  labels: { name: string }[];
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
    const data = await ghFetch("/actions/runners?per_page=100", token);
    const ghRunners: GHRunner[] = data.runners ?? [];

    const runners = ghRunners.map((r) => ({
      runner_id: r.id,
      runner_name: r.name,
      os: r.os,
      status: r.status,
      busy: r.busy,
      labels: r.labels.map((l) => l.name),
    }));

    return NextResponse.json({ runners });
  } catch (e) {
    console.error("Failed to fetch runner data:", e);
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "Failed to fetch runner data" },
      { status: 500 }
    );
  }
}
