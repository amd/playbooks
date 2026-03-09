import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import JSZip from "jszip";

const REPO_OWNER = "amd";
const REPO_NAME = "halo_playbooks";
const GITHUB_API = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`;
const WORKFLOW_FILE = "test-playbooks.yml";
const PLAYBOOKS_ROOT = path.join(process.cwd(), "..", "playbooks");
const CATEGORY_ORDER: Record<string, number> = { core: 0, supplemental: 1, backup: 2 };
const HARDWARE_LABELS: Record<string, string> = {
  halo: "STX Halo",
  stx: "STX Point",
  krk: "Krackan Point",
  rx7900xt: "Radeon RX 7900 XT",
  rx9070xt: "Radeon RX 9070 XT",
};

interface WorkflowRun {
  id: number;
  html_url: string;
  created_at: string;
  event: string;
}

interface WorkflowRunsResponse {
  workflow_runs: WorkflowRun[];
}

interface Artifact {
  id: number;
  name: string;
  expired: boolean;
  archive_download_url: string;
}

interface ArtifactsResponse {
  artifacts: Artifact[];
}

interface PlaybookMeta {
  id: string;
  title?: string;
  platforms?: string[];
  tested_platforms?: Record<string, string[] | undefined>;
  developed?: boolean;
  published?: boolean;
}

interface PlaybookEntry {
  id: string;
  title: string;
  category: string;
  combinations: string[];
  developed: boolean;
}

interface SummaryRaw {
  playbook_id?: string;
  platform?: string;
  total_tests?: number;
  passed?: number;
  failed?: number;
  skipped?: number;
}

interface CellSummary {
  playbookId: string;
  platform: string;
  arch: string;
  passed: number;
  failed: number;
  skipped: number;
  totalTests: number;
  status: "pass" | "fail" | "partial" | "no-tests";
}

function normalizePlatform(platform: string): string {
  return platform.toLowerCase() === "windows" ? "windows" : "linux";
}

function combinationId(arch: string, platform: string): string {
  return `${arch.toLowerCase()}|${normalizePlatform(platform)}`;
}

function combinationLabel(arch: string): string {
  const normalizedArch = arch.toLowerCase();
  return HARDWARE_LABELS[normalizedArch] ?? arch;
}

function parseArtifactName(name: string): { playbookId: string; platform: string; arch: string | null } | null {
  if (!name.startsWith("test-results-")) return null;
  const suffix = name.slice("test-results-".length);

  // Format with arch: {playbook}-{platform}-{arch}
  const matchWithArch = suffix.match(/^(.+)-(windows|linux)-([a-z0-9._-]+)$/i);
  if (matchWithArch) {
    return {
      playbookId: matchWithArch[1],
      platform: matchWithArch[2].toLowerCase(),
      arch: matchWithArch[3].toLowerCase(),
    };
  }

  // Format without arch (current nightly format): {playbook}-{platform}
  const matchNoArch = suffix.match(/^(.+)-(windows|linux)$/i);
  if (matchNoArch) {
    return {
      playbookId: matchNoArch[1],
      platform: matchNoArch[2].toLowerCase(),
      arch: null,
    };
  }

  return null;
}

function classifyCell(summary: SummaryRaw): CellSummary["status"] {
  const totalTests = summary.total_tests ?? 0;
  const failed = summary.failed ?? 0;
  const passed = summary.passed ?? 0;
  if (totalTests === 0) return "no-tests";
  if (failed > 0) return "fail";
  if (passed === totalTests) return "pass";
  return "partial";
}

function loadPlaybooks(): PlaybookEntry[] {
  const categories = ["core", "supplemental", "backup"];
  const rows: PlaybookEntry[] = [];

  for (const category of categories) {
    const categoryPath = path.join(PLAYBOOKS_ROOT, category);
    if (!fs.existsSync(categoryPath)) continue;
    const folders = fs.readdirSync(categoryPath, { withFileTypes: true });

    for (const folder of folders) {
      if (!folder.isDirectory()) continue;
      const jsonPath = path.join(categoryPath, folder.name, "playbook.json");
      if (!fs.existsSync(jsonPath)) continue;

      try {
        const meta = JSON.parse(fs.readFileSync(jsonPath, "utf-8")) as PlaybookMeta;
        if (meta.published === false) continue;

        let combos: string[] = [];
        const tested = meta.tested_platforms ?? {};
        const testedKeys = Object.keys(tested);

        if (testedKeys.length === 0) {
          const platforms = meta.platforms ?? [];
          combos = platforms.map((platform) => combinationId("halo", platform));
        } else {
          for (const [platform, archList] of Object.entries(tested)) {
            for (const arch of archList ?? []) {
              combos.push(combinationId(arch, platform));
            }
          }
        }

        combos = Array.from(new Set(combos));

        const developed = meta.developed === true;

        rows.push({
          id: meta.id,
          title: meta.title || meta.id,
          category,
          combinations: combos,
          developed,
        });
      } catch {
        // Ignore unreadable playbooks
      }
    }
  }

  rows.sort((a, b) => {
    const categoryDiff = (CATEGORY_ORDER[a.category] ?? 99) - (CATEGORY_ORDER[b.category] ?? 99);
    if (categoryDiff !== 0) return categoryDiff;
    return a.title.localeCompare(b.title);
  });

  return rows;
}

async function ghFetch(pathname: string, token: string): Promise<Response> {
  return fetch(`${GITHUB_API}${pathname}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    next: { revalidate: 900 },
  });
}

async function listRunArtifacts(runId: number, token: string): Promise<Artifact[]> {
  const collected: Artifact[] = [];
  let page = 1;

  while (true) {
    const res = await ghFetch(`/actions/runs/${runId}/artifacts?per_page=100&page=${page}`, token);
    if (!res.ok) {
      throw new Error(`Failed to list artifacts (${res.status})`);
    }

    const body = (await res.json()) as ArtifactsResponse;
    collected.push(...body.artifacts);

    if (body.artifacts.length < 100) break;
    page += 1;
  }

  return collected;
}

async function getRunByIdLocal(
  token: string,
  runId: number
): Promise<{ run: WorkflowRun; artifacts: Artifact[] } | null> {
  const runRes = await ghFetch(`/actions/runs/${runId}`, token);
  if (!runRes.ok) return null;
  const run = (await runRes.json()) as WorkflowRun;
  const artifacts = await listRunArtifacts(runId, token);
  return { run, artifacts };
}

async function getLatestNightlyRunWithArtifacts(
  token: string
): Promise<{ run: WorkflowRun; artifacts: Artifact[] } | null> {
  // Scheduled-only, as requested. We scan recent pages and pick the newest run
  // that actually produced test-results artifacts.
  for (let page = 1; page <= 5; page += 1) {
    const scheduledRes = await ghFetch(
      `/actions/workflows/${WORKFLOW_FILE}/runs?event=schedule&status=completed&per_page=20&page=${page}`,
      token
    );
    if (!scheduledRes.ok) {
      throw new Error(`Failed to list scheduled workflow runs (${scheduledRes.status})`);
    }

    const scheduled = (await scheduledRes.json()) as WorkflowRunsResponse;
    if (scheduled.workflow_runs.length === 0) break;

    for (const run of scheduled.workflow_runs) {
      const artifacts = await listRunArtifacts(run.id, token);
      const hasTestArtifacts = artifacts.some(
        (artifact) => !artifact.expired && artifact.name.startsWith("test-results-")
      );
      if (hasTestArtifacts) {
        return { run, artifacts };
      }
    }
  }

  return null;
}

async function extractSummary(artifact: Artifact, token: string): Promise<SummaryRaw | null> {
  // GitHub redirects /artifacts/{id}/zip to a signed S3 URL.
  // Must use the standard GitHub Accept header (not octet-stream) or the API returns 415.
  const downloadRes = await fetch(artifact.archive_download_url, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    redirect: "follow",
  });

  if (!downloadRes.ok) return null;
  const zipBuffer = await downloadRes.arrayBuffer();
  const zip = await JSZip.loadAsync(zipBuffer);
  const summaryFile = Object.values(zip.files).find(
    (file) => !file.dir && (file.name === "summary.json" || file.name.endsWith("/summary.json"))
  );

  if (!summaryFile) {
    const noTestsFile = Object.values(zip.files).find(
      (file) => !file.dir && (file.name === "no_tests.txt" || file.name.endsWith("/no_tests.txt"))
    );
    if (noTestsFile) {
      return { total_tests: 0, passed: 0, failed: 0, skipped: 0 };
    }
    return null;
  }

  try {
    return JSON.parse(await summaryFile.async("text")) as SummaryRaw;
  } catch {
    return null;
  }
}

export async function GET(request: Request) {
  const token = process.env.DASHBOARD_GITHUB_TOKEN?.trim();
  if (!token) {
    return NextResponse.json(
      {
        error:
          "DASHBOARD_GITHUB_TOKEN is not set. Add it in website/.env.local with repo Actions read access.",
      },
      { status: 500 }
    );
  }

  const { searchParams } = new URL(request.url);
  const runIdParam = searchParams.get("run_id");
  const runId = runIdParam ? parseInt(runIdParam, 10) : undefined;

  try {
    const playbooks = loadPlaybooks();
    const nightly = runId
      ? await getRunByIdLocal(token, runId)
      : await getLatestNightlyRunWithArtifacts(token);
    if (!nightly) {
      const allColumns = Object.keys(HARDWARE_LABELS)
        .flatMap((archKey) =>
          ["windows", "linux"].map((platform) => ({
            id: combinationId(archKey, platform),
            arch: archKey,
            platform,
            hardware: combinationLabel(archKey),
            os: platform === "windows" ? "Windows" : "Linux",
          }))
        )
        .sort((a, b) => {
          const hwA = Object.values(HARDWARE_LABELS).indexOf(a.hardware);
          const hwB = Object.values(HARDWARE_LABELS).indexOf(b.hardware);
          if (hwA !== hwB) return hwA - hwB;
          return a.os.localeCompare(b.os);
        });

      return NextResponse.json({
        run: null,
        columns: allColumns,
        rows: playbooks.map((pb) => ({
          playbookId: pb.id,
          title: pb.title,
          category: pb.category,
          developed: pb.developed,
          cells: {},
        })),
      });
    }

    const testArtifacts = nightly.artifacts.filter(
      (artifact) => !artifact.expired && artifact.name.startsWith("test-results-")
    );

    const summaryEntriesNested = await Promise.all(
      testArtifacts.map(async (artifact) => {
        const parsed = parseArtifactName(artifact.name);
        if (!parsed) return [];

        const summary = await extractSummary(artifact, token);
        if (!summary) return [];

        const playbookId = summary.playbook_id || parsed.playbookId;
        const platform = normalizePlatform(summary.platform || parsed.platform);

        // Determine which archs to attribute this artifact to.
        // Nightly artifacts omit the arch from the name, so we infer from
        // the playbook's tested_platforms declarations.
        let archs: string[];
        if (parsed.arch !== null) {
          archs = [parsed.arch];
        } else {
          const pb = playbooks.find((p) => p.id === playbookId);
          archs = pb
            ? pb.combinations
                .filter((c) => c.endsWith(`|${platform}`))
                .map((c) => c.split("|")[0])
            : [];
          if (archs.length === 0) archs = ["halo"];
        }

        return archs.map((arch) => ({
          comboId: combinationId(arch, platform),
          cell: {
            playbookId,
            platform,
            arch,
            passed: summary.passed ?? 0,
            failed: summary.failed ?? 0,
            skipped: summary.skipped ?? 0,
            totalTests: summary.total_tests ?? 0,
            status: classifyCell(summary),
          } satisfies CellSummary,
        }));
      })
    );

    const summaryEntries = summaryEntriesNested.flat();

    const byPlaybookAndCombo = new Map<string, CellSummary>();
    const comboIds = new Set<string>();

    // Always include the full CI matrix (all hardware × OS combos)
    for (const archKey of Object.keys(HARDWARE_LABELS)) {
      for (const platform of ["windows", "linux"]) {
        comboIds.add(combinationId(archKey, platform));
      }
    }

    for (const pb of playbooks) {
      for (const combo of pb.combinations) comboIds.add(combo);
    }

    for (const entry of summaryEntries) {
      if (!entry) continue;
      comboIds.add(entry.comboId);
      byPlaybookAndCombo.set(`${entry.cell.playbookId}::${entry.comboId}`, entry.cell);
    }

    const columns = Array.from(comboIds)
      .map((comboId) => {
        const [arch, platform] = comboId.split("|");
        return {
          id: comboId,
          arch,
          platform,
          hardware: combinationLabel(arch),
          os: platform === "windows" ? "Windows" : "Linux",
        };
      })
      .sort((a, b) => {
        const hwA = Object.values(HARDWARE_LABELS).indexOf(a.hardware);
        const hwB = Object.values(HARDWARE_LABELS).indexOf(b.hardware);
        const hwOrderA = hwA === -1 ? 999 : hwA;
        const hwOrderB = hwB === -1 ? 999 : hwB;
        if (hwOrderA !== hwOrderB) return hwOrderA - hwOrderB;
        if (a.hardware !== b.hardware) return a.hardware.localeCompare(b.hardware);
        return a.os.localeCompare(b.os);
      });

    const rows = playbooks.map((pb) => {
      const cells: Record<string, CellSummary> = {};
      for (const col of columns) {
        const key = `${pb.id}::${col.id}`;
        const existing = byPlaybookAndCombo.get(key);
        if (existing) cells[col.id] = existing;
      }
      return {
        playbookId: pb.id,
        title: pb.title,
        category: pb.category,
        developed: pb.developed,
        cells,
      };
    });

    return NextResponse.json({
      run: {
        id: nightly.run.id,
        htmlUrl: nightly.run.html_url,
        createdAt: nightly.run.created_at,
        event: nightly.run.event,
      },
      columns,
      rows,
    });
  } catch (error) {
    console.error("Failed to build playbook matrix:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to build playbook matrix" },
      { status: 500 }
    );
  }
}
