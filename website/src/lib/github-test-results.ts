/**
 * Shared utilities for fetching GitHub Actions test results artifacts.
 *
 * Used by playbook API routes to replace local test-results/ file reads
 * with data pulled from the latest nightly workflow run.
 */
import JSZip from "jszip";

const REPO_OWNER = "amd";
const REPO_NAME = "halo_playbooks";
const GITHUB_API = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`;
const WORKFLOW_FILE = "test-playbooks.yml";

export interface WorkflowRun {
  id: number;
  html_url: string;
  created_at: string;
  event: string;
}

export interface Artifact {
  id: number;
  name: string;
  expired: boolean;
  archive_download_url: string;
}

export interface NightlyRun {
  run: WorkflowRun;
  artifacts: Artifact[];
}

/** Per-test result entry inside summary.json */
export interface TestResultEntry {
  test_id: string;
  success: boolean;
  skipped?: boolean;
  duration?: number;
  error_message?: string;
}

/** Full summary.json shape (aggregate + per-test results) */
export interface SummaryFull {
  playbook_id?: string;
  platform?: string;
  total_tests?: number;
  passed?: number;
  failed?: number;
  skipped?: number;
  results?: TestResultEntry[];
}

/** Parsed test results ready for use by coverage rendering */
export interface LoadedTestResults {
  resultsMap: Record<string, { success: boolean; skipped: boolean; duration: number; error: string }>;
  summary: { passed: number; failed: number; skipped: number };
}

/** Per-device test results from a single artifact */
export interface DeviceTestResult {
  device: string;
  platform: string;
  resultsMap: Record<string, { success: boolean; skipped: boolean; duration: number; error: string }>;
  summary: { passed: number; failed: number; skipped: number };
}

/** Combined test results across all devices/archs for a playbook */
export interface LoadedAllTestResults {
  resultsMap: Record<string, { success: boolean; skipped: boolean; duration: number; error: string }>;
  summary: { passed: number; failed: number; skipped: number };
  deviceResults: DeviceTestResult[];
}

function ghFetch(pathname: string, token: string): Promise<Response> {
  return fetch(`${GITHUB_API}${pathname}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    // Cache for 15 minutes at the Next.js fetch layer
    next: { revalidate: 900 },
  });
}

async function listRunArtifacts(runId: number, token: string): Promise<Artifact[]> {
  const collected: Artifact[] = [];
  let page = 1;

  while (true) {
    const res = await ghFetch(
      `/actions/runs/${runId}/artifacts?per_page=100&page=${page}`,
      token
    );
    if (!res.ok) throw new Error(`Failed to list artifacts (${res.status})`);
    const body = await res.json() as { artifacts: Artifact[] };
    collected.push(...body.artifacts);
    if (body.artifacts.length < 100) break;
    page++;
  }

  return collected;
}

/**
 * Finds the most recent completed nightly run that produced test-results artifacts.
 * Scans up to 5 pages of recent scheduled workflow runs.
 */
export async function getLatestNightlyRun(token: string): Promise<NightlyRun | null> {
  for (let page = 1; page <= 5; page++) {
    const res = await ghFetch(
      `/actions/workflows/${WORKFLOW_FILE}/runs?event=schedule&status=completed&per_page=20&page=${page}`,
      token
    );
    if (!res.ok) throw new Error(`Failed to list workflow runs (${res.status})`);
    const data = await res.json() as { workflow_runs: WorkflowRun[] };
    if (data.workflow_runs.length === 0) break;

    for (const run of data.workflow_runs) {
      const artifacts = await listRunArtifacts(run.id, token);
      const hasTestArtifacts = artifacts.some(
        (a) => !a.expired && a.name.startsWith("test-results-")
      );
      if (hasTestArtifacts) return { run, artifacts };
    }
  }

  return null;
}

/**
 * Parses a test-results artifact name into its components.
 *
 * Supported formats:
 *   test-results-{playbook}-{platform}-{arch}  (with arch)
 *   test-results-{playbook}-{platform}          (without arch)
 */
export function parseArtifactName(
  name: string
): { playbookId: string; platform: string; arch: string | null } | null {
  if (!name.startsWith("test-results-")) return null;
  const suffix = name.slice("test-results-".length);

  const matchWithArch = suffix.match(/^(.+)-(windows|linux)-([a-z0-9._-]+)$/i);
  if (matchWithArch) {
    return {
      playbookId: matchWithArch[1],
      platform: matchWithArch[2].toLowerCase(),
      arch: matchWithArch[3].toLowerCase(),
    };
  }

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

/** Downloads and unzips a GitHub Actions artifact. */
async function downloadArtifactZip(artifact: Artifact, token: string): Promise<JSZip | null> {
  const res = await fetch(artifact.archive_download_url, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    redirect: "follow",
  });
  if (!res.ok) return null;
  const buffer = await res.arrayBuffer();
  return JSZip.loadAsync(buffer);
}

/**
 * Extracts the full summary.json (including per-test results) from an artifact zip.
 * Returns null if the artifact cannot be downloaded or contains no summary.
 */
export async function extractFullSummary(
  artifact: Artifact,
  token: string
): Promise<SummaryFull | null> {
  const zip = await downloadArtifactZip(artifact, token);
  if (!zip) return null;

  const summaryFile = Object.values(zip.files).find(
    (f) => !f.dir && (f.name === "summary.json" || f.name.endsWith("/summary.json"))
  );

  if (!summaryFile) {
    const noTestsFile = Object.values(zip.files).find(
      (f) => !f.dir && (f.name === "no_tests.txt" || f.name.endsWith("/no_tests.txt"))
    );
    if (noTestsFile) return { total_tests: 0, passed: 0, failed: 0, skipped: 0, results: [] };
    return null;
  }

  try {
    return JSON.parse(await summaryFile.async("text")) as SummaryFull;
  } catch {
    return null;
  }
}

/**
 * Extracts stdout/stderr log files for a specific test from an artifact zip.
 * Returns null if the artifact cannot be downloaded.
 */
export async function extractTestLogs(
  artifact: Artifact,
  token: string,
  testId: string
): Promise<{ stdout: string; stderr: string } | null> {
  const zip = await downloadArtifactZip(artifact, token);
  if (!zip) return null;

  const findFile = (filename: string) =>
    Object.values(zip.files).find(
      (f) => !f.dir && (f.name === filename || f.name.endsWith(`/${filename}`))
    );

  const stdoutFile = findFile(`${testId}_stdout.txt`);
  const stderrFile = findFile(`${testId}_stderr.txt`);

  const stdout = stdoutFile ? await stdoutFile.async("text") : "";
  const stderr = stderrFile ? await stderrFile.async("text") : "";

  return { stdout, stderr };
}

/**
 * Finds all non-expired test-results artifacts for a given playbook from a nightly run.
 * Prefers Windows over Linux when both are present.
 */
export function findPlaybookArtifacts(
  artifacts: Artifact[],
  playbookId: string
): { windows?: Artifact; linux?: Artifact } {
  const result: { windows?: Artifact; linux?: Artifact } = {};

  for (const artifact of artifacts) {
    if (artifact.expired) continue;
    const parsed = parseArtifactName(artifact.name);
    if (!parsed || parsed.playbookId !== playbookId) continue;
    if (parsed.platform === "windows" && !result.windows) result.windows = artifact;
    if (parsed.platform === "linux" && !result.linux) result.linux = artifact;
  }

  return result;
}

/**
 * Finds ALL non-expired test-results artifacts for a given playbook,
 * returning each with its parsed platform and arch.
 */
export function findAllPlaybookArtifacts(
  artifacts: Artifact[],
  playbookId: string
): Array<{ artifact: Artifact; platform: string; arch: string }> {
  const result: Array<{ artifact: Artifact; platform: string; arch: string }> = [];

  for (const artifact of artifacts) {
    if (artifact.expired) continue;
    const parsed = parseArtifactName(artifact.name);
    if (!parsed || parsed.playbookId !== playbookId) continue;
    result.push({
      artifact,
      platform: parsed.platform,
      arch: parsed.arch || "halo",
    });
  }

  return result;
}

/** Summary of a single workflow run, used to populate run selectors. */
export interface RunSummary {
  id: number;
  htmlUrl: string;
  createdAt: string;
  event: string;
  headBranch: string;
  conclusion: string | null;
}

/**
 * Lists recent completed runs of the test workflow across all event types.
 * Used to populate run-selector UIs.
 */
export async function listRecentRuns(token: string, perPage = 20): Promise<RunSummary[]> {
  const res = await ghFetch(
    `/actions/workflows/${WORKFLOW_FILE}/runs?status=completed&per_page=${perPage}`,
    token
  );
  if (!res.ok) throw new Error(`Failed to list workflow runs (${res.status})`);
  const data = await res.json() as {
    workflow_runs: Array<{
      id: number;
      html_url: string;
      created_at: string;
      event: string;
      head_branch: string;
      conclusion: string | null;
    }>;
  };
  return data.workflow_runs.map((r) => ({
    id: r.id,
    htmlUrl: r.html_url,
    createdAt: r.created_at,
    event: r.event,
    headBranch: r.head_branch,
    conclusion: r.conclusion,
  }));
}

/**
 * Fetches the run metadata and artifact list for a specific run ID.
 * Returns null if the run cannot be found.
 */
export async function getRunById(token: string, runId: number): Promise<NightlyRun | null> {
  const runRes = await ghFetch(`/actions/runs/${runId}`, token);
  if (!runRes.ok) return null;
  const run = await runRes.json() as WorkflowRun;
  const artifacts = await listRunArtifacts(runId, token);
  return { run, artifacts };
}

/**
 * Loads test results for a playbook from GitHub artifacts.
 * Prefers Windows results; falls back to Linux.
 * Returns null if no token is configured or no results are available.
 *
 * @param runId  Optional specific run ID. If omitted, the latest nightly run is used.
 */
export async function loadGitHubTestResults(
  playbookId: string,
  token: string,
  runId?: number,
): Promise<LoadedTestResults | null> {
  const nightly = runId
    ? await getRunById(token, runId)
    : await getLatestNightlyRun(token);
  if (!nightly) return null;

  const { windows: winArtifact, linux: linuxArtifact } = findPlaybookArtifacts(
    nightly.artifacts,
    playbookId
  );
  const artifact = winArtifact ?? linuxArtifact;
  if (!artifact) return null;

  const summary = await extractFullSummary(artifact, token);
  if (!summary) return null;

  const resultsMap: LoadedTestResults["resultsMap"] = {};
  for (const r of summary.results ?? []) {
    resultsMap[r.test_id] = {
      success: r.success,
      skipped: r.skipped ?? false,
      duration: r.duration ?? 0,
      error: r.error_message ?? "",
    };
  }

  return {
    resultsMap,
    summary: {
      passed: summary.passed ?? 0,
      failed: summary.failed ?? 0,
      skipped: summary.skipped ?? 0,
    },
  };
}

/**
 * Loads test results from ALL artifacts for a playbook (all devices/archs).
 * Returns merged results plus per-device breakdowns.
 */
export async function loadAllGitHubTestResults(
  playbookId: string,
  token: string,
  runId?: number,
): Promise<LoadedAllTestResults | null> {
  const nightly = runId
    ? await getRunById(token, runId)
    : await getLatestNightlyRun(token);
  if (!nightly) return null;

  const allArtifacts = findAllPlaybookArtifacts(nightly.artifacts, playbookId);
  if (allArtifacts.length === 0) return null;

  const deviceResults: DeviceTestResult[] = [];
  const mergedResultsMap: LoadedAllTestResults["resultsMap"] = {};
  let totalPassed = 0, totalFailed = 0, totalSkipped = 0;

  await Promise.all(allArtifacts.map(async ({ artifact, platform, arch }) => {
    const summary = await extractFullSummary(artifact, token);
    if (!summary) return;

    const deviceMap: DeviceTestResult["resultsMap"] = {};
    for (const r of summary.results ?? []) {
      const entry = {
        success: r.success,
        skipped: r.skipped ?? false,
        duration: r.duration ?? 0,
        error: r.error_message ?? "",
      };
      deviceMap[r.test_id] = entry;
      mergedResultsMap[r.test_id] = entry;
    }

    deviceResults.push({
      device: arch,
      platform,
      resultsMap: deviceMap,
      summary: {
        passed: summary.passed ?? 0,
        failed: summary.failed ?? 0,
        skipped: summary.skipped ?? 0,
      },
    });

    totalPassed += summary.passed ?? 0;
    totalFailed += summary.failed ?? 0;
    totalSkipped += summary.skipped ?? 0;
  }));

  if (deviceResults.length === 0) return null;

  return {
    resultsMap: mergedResultsMap,
    summary: { passed: totalPassed, failed: totalFailed, skipped: totalSkipped },
    deviceResults,
  };
}
