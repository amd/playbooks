// Copyright Advanced Micro Devices, Inc.
//
// SPDX-License-Identifier: MIT

/**
 * Reads playbook results of the OrchestrAI CI workflow (test-playbooks-orchestrai.yml).
 *
 * Each batch job of that workflow uploads a `batch-results-<n>-[<locale>-]<platform>-<arch>`
 * artifact holding `batch.json` (one row per playbook, with the OrchestrAI run,
 * ReportPortal launch and GitHub job links) and `<playbook>/summary.json` (test counts).
 *
 * A batch can test English and localized playbooks on the same machine. Its rows are then
 * keyed `<locale>/<id>` (`playbook`), with the bare id in `playbook_id` and the locale in
 * `locale`, and their counts are in `<locale>/<id>/summary.json`. A localized entry whose
 * tests are the same as its English version's is not run again: it carries `covered_by`
 * (the English key) and reports the English result.
 */
import JSZip from "jszip";

const GITHUB_API = "https://api.github.com/repos/amd/playbooks";
export const ORCHESTRAI_WORKFLOW_FILE = "test-playbooks-orchestrai.yml";
const ARTIFACT_PREFIX = "batch-results-";
const DOWNLOAD_CONCURRENCY = 8;

export interface OrchestraiRun {
  id: number;
  html_url: string;
  created_at: string;
  event: string;
  status: string;
}

interface Artifact {
  id: number;
  name: string;
  expired: boolean;
  archive_download_url: string;
}

/** One playbook on one system (device + OS + locale) in an OrchestrAI CI run. */
export interface OrchestraiResult {
  playbookId: string;
  platform: string;
  arch: string;
  locale: string;
  /** Set when the entry was not run because its English version runs the same tests. */
  coveredBy: string;
  /** PASSED, FAILED, ERROR, NOT_RUN or INTERRUPTED */
  outcome: string;
  required: boolean;
  batchLabel: string;
  runUrl: string;
  rpUrl: string;
  jobUrl: string;
  reason: string;
  attempt: number;
  firstOutcome: string;
  passed: number;
  failed: number;
  skipped: number;
  totalTests: number;
}

interface BatchRow {
  /** The batch key: `<id>` for English, `<locale>/<id>` in a batch shared by several languages. */
  playbook: string;
  playbook_id?: string;
  platform: string;
  arch: string;
  locale?: string;
  covered_by?: string;
  outcome?: string;
  required?: boolean;
  label?: string;
  batch_id?: string;
  run_url?: string;
  rp_url?: string;
  job_url?: string;
  reason?: string;
  attempt?: number;
  first_outcome?: string;
}

interface PlaybookSummary {
  total_tests?: number;
  passed?: number;
  failed?: number;
  skipped?: number;
  reportportal_url?: string | null;
}

// A completed run's artifacts never change: keep its parsed results.
const completedRunCache = new Map<number, OrchestraiResult[]>();

function ghFetch(pathname: string, token: string): Promise<Response> {
  return fetch(`${GITHUB_API}${pathname}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    next: { revalidate: 300 },
  });
}

async function listBatchArtifacts(runId: number, token: string): Promise<Artifact[]> {
  const collected: Artifact[] = [];
  for (let page = 1; ; page++) {
    const res = await ghFetch(`/actions/runs/${runId}/artifacts?per_page=100&page=${page}`, token);
    if (!res.ok) throw new Error(`Failed to list artifacts of run ${runId} (${res.status})`);
    const body = (await res.json()) as { artifacts: Artifact[] };
    collected.push(...body.artifacts);
    if (body.artifacts.length < 100) break;
  }
  return collected.filter((a) => !a.expired && a.name.startsWith(ARTIFACT_PREFIX));
}

async function getRun(runId: number, token: string): Promise<OrchestraiRun | null> {
  const res = await ghFetch(`/actions/runs/${runId}`, token);
  if (!res.ok) return null;
  return (await res.json()) as OrchestraiRun;
}

/** The newest completed scheduled run that uploaded batch results. */
async function getLatestNightly(token: string): Promise<{ run: OrchestraiRun; artifacts: Artifact[] } | null> {
  for (let page = 1; page <= 3; page++) {
    const res = await ghFetch(
      `/actions/workflows/${ORCHESTRAI_WORKFLOW_FILE}/runs?event=schedule&status=completed&per_page=20&page=${page}`,
      token
    );
    if (!res.ok) throw new Error(`Failed to list OrchestrAI workflow runs (${res.status})`);
    const { workflow_runs: runs } = (await res.json()) as { workflow_runs: OrchestraiRun[] };
    if (runs.length === 0) break;
    for (const run of runs) {
      const artifacts = await listBatchArtifacts(run.id, token);
      if (artifacts.length > 0) return { run, artifacts };
    }
  }
  return null;
}

async function readBatchArtifact(artifact: Artifact, token: string): Promise<OrchestraiResult[]> {
  const res = await fetch(artifact.archive_download_url, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    redirect: "follow",
    cache: "no-store",
  });
  if (!res.ok) return [];
  const zip = await JSZip.loadAsync(await res.arrayBuffer());
  const batchFile = Object.values(zip.files).find(
    (f) => !f.dir && (f.name === "batch.json" || f.name.endsWith("/batch.json"))
  );
  if (!batchFile) return [];
  let rows: BatchRow[];
  try {
    rows = JSON.parse(await batchFile.async("text")) as BatchRow[];
  } catch {
    return [];
  }

  const root = batchFile.name.slice(0, batchFile.name.length - "batch.json".length);
  const readSummary = async (key: string): Promise<PlaybookSummary | null> => {
    const file = key ? zip.file(`${root}${key}/summary.json`) : null;
    if (!file) return null;
    try {
      return JSON.parse(await file.async("text")) as PlaybookSummary;
    } catch {
      return null; // counts stay at zero; the outcome still comes from batch.json
    }
  };
  return Promise.all(
    rows.map(async (row) => {
      const key = row.playbook || "";
      const slash = key.lastIndexOf("/");
      const coveredBy = row.covered_by || "";
      // A covered entry did not run: its counts are those of the English run it reports.
      const summary: PlaybookSummary =
        (await readSummary(key)) ?? (coveredBy ? await readSummary(coveredBy) : null) ?? {};
      return {
        playbookId: row.playbook_id || key.slice(slash + 1),
        platform: (row.platform || "").toLowerCase() === "windows" ? "windows" : "linux",
        arch: (row.arch || "").toLowerCase(),
        locale: row.locale ?? (slash > 0 ? key.slice(0, slash) : ""),
        coveredBy,
        outcome: (row.outcome || "FAILED").toUpperCase(),
        required: row.required === true,
        batchLabel: row.label || row.batch_id || "",
        runUrl: row.run_url || "",
        rpUrl: row.rp_url || summary.reportportal_url || "",
        jobUrl: row.job_url || "",
        reason: row.reason || "",
        attempt: row.attempt ?? 1,
        firstOutcome: row.first_outcome || "",
        passed: summary.passed ?? 0,
        failed: summary.failed ?? 0,
        skipped: summary.skipped ?? 0,
        totalTests: summary.total_tests ?? 0,
      };
    })
  );
}

async function mapLimit<T, R>(items: T[], limit: number, fn: (item: T) => Promise<R>): Promise<R[]> {
  const out: R[] = new Array(items.length);
  let next = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (next < items.length) {
      const i = next++;
      out[i] = await fn(items[i]);
    }
  });
  await Promise.all(workers);
  return out;
}

/**
 * Results of one OrchestrAI CI run (runId), or of the latest nightly when omitted.
 * Returns null when no run with batch results exists.
 */
export async function loadOrchestraiResults(
  token: string,
  runId?: number
): Promise<{ run: OrchestraiRun; results: OrchestraiResult[] } | null> {
  let run: OrchestraiRun | null;
  let artifacts: Artifact[] | null = null;
  if (runId) {
    run = await getRun(runId, token);
  } else {
    const latest = await getLatestNightly(token);
    run = latest?.run ?? null;
    artifacts = latest?.artifacts ?? null;
  }
  if (!run) return null;

  const cached = completedRunCache.get(run.id);
  if (cached) return { run, results: cached };

  artifacts ??= await listBatchArtifacts(run.id, token);
  const results = (await mapLimit(artifacts, DOWNLOAD_CONCURRENCY, (a) => readBatchArtifact(a, token))).flat();
  if (run.status === "completed") completedRunCache.set(run.id, results);
  return { run, results };
}
