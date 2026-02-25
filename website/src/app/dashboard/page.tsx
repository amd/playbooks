"use client";

import { useState, useEffect, useCallback } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

interface JobInfo {
  id: number;
  run_id: number;
  name: string;
  status: string;
  conclusion: string | null;
  started_at: string | null;
  completed_at: string | null;
  html_url: string;
}

interface RunnerInfo {
  runner_id: number;
  runner_name: string;
  labels: string[];
  jobs: JobInfo[];
}

interface CellData {
  runners: RunnerInfo[];
}

type MatrixData = Record<string, Record<string, CellData>>;

const HARDWARE_LABELS: Record<string, string> = {
  halo: "STX Halo",
  krackan: "Krackan Point",
};

const OS_LABELS = ["Windows", "Linux"];

function classifyRunner(runner: RunnerInfo): { hardware: string; os: string } {
  const labelNames = runner.labels.map((l) => l.toLowerCase());

  let hardware = "Other";
  for (const [key, display] of Object.entries(HARDWARE_LABELS)) {
    if (labelNames.includes(key.toLowerCase())) {
      hardware = display;
      break;
    }
  }

  let os = "Other";
  for (const osName of OS_LABELS) {
    if (labelNames.includes(osName.toLowerCase())) {
      os = osName;
      break;
    }
  }

  return { hardware, os };
}

function buildMatrix(runners: RunnerInfo[]): MatrixData {
  const matrix: MatrixData = {};
  for (const hw of Object.values(HARDWARE_LABELS)) {
    matrix[hw] = {};
    for (const os of OS_LABELS) {
      matrix[hw][os] = { runners: [] };
    }
  }

  for (const runner of runners) {
    const { hardware, os } = classifyRunner(runner);
    if (matrix[hardware]?.[os]) {
      matrix[hardware][os].runners.push(runner);
    }
  }

  return matrix;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function RunnerStatus({ runner }: { runner: RunnerInfo }) {
  const latestJob = runner.jobs[0];
  if (!latestJob) return null;

  const isRunning = latestJob.status === "in_progress" || latestJob.status === "queued";

  if (isRunning) {
    return (
      <div className="flex items-center gap-1.5">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-yellow-400" />
        </span>
        <span className="text-yellow-400 text-xs font-medium">Running</span>
      </div>
    );
  }

  const conclusion = latestJob.conclusion;
  if (conclusion === "success") {
    return (
      <div className="flex items-center gap-1.5">
        <span className="inline-block w-2.5 h-2.5 rounded-full bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.4)]" />
        <span className="text-green-400 text-xs font-medium">Idle</span>
      </div>
    );
  }
  if (conclusion === "failure") {
    return (
      <div className="flex items-center gap-1.5">
        <span className="inline-block w-2.5 h-2.5 rounded-full bg-red-400 shadow-[0_0_6px_rgba(248,113,113,0.4)]" />
        <span className="text-red-400 text-xs font-medium">Last run failed</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5">
      <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#6b6b6b]" />
      <span className="text-[#6b6b6b] text-xs font-medium">{conclusion ?? "Unknown"}</span>
    </div>
  );
}

function CellContent({ cell }: { cell: CellData }) {
  if (cell.runners.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-[#6b6b6b] text-sm italic py-3">
        No runners
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {cell.runners.map((runner) => {
        const latestJob = runner.jobs[0];
        const recentJobs = runner.jobs.slice(0, 5);
        return (
          <div
            key={runner.runner_id}
            className="px-3.5 py-3 rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] hover:border-[#444] transition-colors"
          >
            <div className="flex items-center justify-between gap-2 mb-2">
              <span className="text-sm font-medium text-white truncate">{runner.runner_name}</span>
              <RunnerStatus runner={runner} />
            </div>

            {latestJob && (
              <div className="text-xs text-[#6b6b6b] mb-2.5">
                Last active {latestJob.completed_at ? timeAgo(latestJob.completed_at) : latestJob.started_at ? timeAgo(latestJob.started_at) : "—"}
              </div>
            )}

            {/* Recent job results */}
            <div className="flex items-center gap-1">
              <span className="text-[10px] text-[#6b6b6b] mr-1.5 uppercase tracking-wide">Recent</span>
              {recentJobs.map((job) => (
                <a
                  key={job.id}
                  href={job.html_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  title={`${job.name}\n${job.conclusion ?? job.status}`}
                  className={`w-4 h-4 rounded-sm flex items-center justify-center text-[9px] font-bold transition-transform hover:scale-125 ${
                    job.status === "in_progress"
                      ? "bg-yellow-400/20 text-yellow-400 border border-yellow-400/30"
                      : job.conclusion === "success"
                        ? "bg-green-400/15 text-green-400 border border-green-400/20"
                        : job.conclusion === "failure"
                          ? "bg-red-400/15 text-red-400 border border-red-400/20"
                          : job.conclusion === "skipped"
                            ? "bg-[#333] text-[#6b6b6b] border border-[#444]"
                            : "bg-[#242424] text-[#6b6b6b] border border-[#333]"
                  }`}
                >
                  {job.status === "in_progress"
                    ? "~"
                    : job.conclusion === "success"
                      ? "\u2713"
                      : job.conclusion === "failure"
                        ? "\u2717"
                        : job.conclusion === "skipped"
                          ? "-"
                          : "?"}
                </a>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function SetupGuide() {
  const [open, setOpen] = useState(false);

  return (
    <div className="bg-[#1a1a1a] border border-[#333] rounded-xl overflow-hidden max-w-2xl mx-auto">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-6 py-4 hover:bg-[#242424] transition-colors"
      >
        <span className="flex items-center gap-2 text-sm font-semibold text-[#a0a0a0]">
          <svg className="w-4 h-4 text-[#D4915D]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          How to configure the GITHUB_TOKEN for this dashboard
        </span>
        <svg
          className={`w-4 h-4 text-[#6b6b6b] transition-transform ${open ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="px-6 pb-5 border-t border-[#333] pt-4 text-sm text-[#a0a0a0] space-y-3 animate-fade-in">
          <p>
            This dashboard reads runner activity via the GitHub Workflow Runs API using a{" "}
            <code className="bg-[#242424] px-1.5 py-0.5 rounded text-[#D4915D] text-xs">DASHBOARD_GITHUB_TOKEN</code>{" "}
            environment variable set on the server.
          </p>
          <h4 className="text-white font-semibold pt-1">Setting the token</h4>
          <p>
            Create a{" "}
            <code className="bg-[#242424] px-1.5 py-0.5 rounded text-[#D4915D] text-xs">.env.local</code>{" "}
            file in the <code className="bg-[#242424] px-1.5 py-0.5 rounded text-[#D4915D] text-xs">website/</code> directory:
          </p>
          <pre className="bg-[#0a0a0a] border border-[#333] rounded-lg p-4 text-xs font-mono text-[#e0e0e0] overflow-x-auto">
            DASHBOARD_GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
          </pre>
          <h4 className="text-white font-semibold pt-1">Creating the token</h4>
          <ol className="list-decimal list-inside space-y-2">
            <li>
              Go to{" "}
              <a
                href="https://github.com/settings/tokens?type=beta"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#D4915D] hover:underline"
              >
                GitHub Settings &rarr; Fine-grained tokens
              </a>
            </li>
            <li>Click <strong className="text-white">Generate new token</strong></li>
            <li>
              Set <strong className="text-white">Repository access</strong> to{" "}
              <code className="bg-[#242424] px-1.5 py-0.5 rounded text-[#D4915D] text-xs">Only select repositories</code>{" "}
              and pick <code className="bg-[#242424] px-1.5 py-0.5 rounded text-[#D4915D] text-xs">amd/halo_playbooks</code>
            </li>
            <li>
              Under <strong className="text-white">Repository permissions</strong>, set{" "}
              <code className="bg-[#242424] px-1.5 py-0.5 rounded text-[#D4915D] text-xs">Actions</code>{" "}
              to <strong className="text-white">Read-only</strong>
            </li>
            <li>Click <strong className="text-white">Generate token</strong> and paste it into your <code className="bg-[#242424] px-1.5 py-0.5 rounded text-[#D4915D] text-xs">.env.local</code></li>
          </ol>
          <div className="mt-3 px-3 py-2 rounded-lg bg-[#242424] border border-[#333] text-xs text-[#6b6b6b]">
            <strong className="text-[#a0a0a0]">Note:</strong> The token never leaves the server.
            The dashboard fetches from <code className="text-[#D4915D]">/api/runners</code> which
            calls the GitHub API server-side.
          </div>
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const [runners, setRunners] = useState<RunnerInfo[]>([]);
  const [runsChecked, setRunsChecked] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastFetched, setLastFetched] = useState<Date | null>(null);

  const fetchRunners = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/runners");
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || `API error: ${res.status}`);
      }
      setRunners(data.runners || []);
      setRunsChecked(data.runs_checked || 0);
      setLastFetched(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch runners");
      setRunners([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRunners();
  }, [fetchRunners]);

  const matrix = buildMatrix(runners);
  const hardwareRows = Object.values(HARDWARE_LABELS);

  const totalRunners = runners.length;
  const runningCount = runners.filter((r) => r.jobs[0]?.status === "in_progress").length;
  const idleCount = totalRunners - runningCount;

  return (
    <main className="min-h-screen bg-[#0d0d0d] grid-pattern">
      <Header />

      <section className="pt-28 pb-6 px-6 gradient-hero relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#D4915D]/5 rounded-full blur-3xl" />
        <div className="max-w-[1400px] mx-auto relative z-10">
          <div className="text-center max-w-4xl mx-auto animate-fade-in mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-3 leading-tight">
              CI Runner{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#D4915D] to-[#E8B896]">
                Dashboard
              </span>
            </h1>
            <p className="text-lg text-[#a0a0a0] max-w-2xl mx-auto">
              Self-hosted runner activity from recent workflow runs
            </p>
          </div>
        </div>
      </section>

      <section className="px-6 pb-6">
        <div className="max-w-[1400px] mx-auto space-y-6">
          {/* Summary bar */}
          {!loading && runners.length > 0 && (
            <div className="flex flex-wrap items-center gap-4 animate-fade-in">
              <div className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] border border-[#333] rounded-lg">
                <span className="text-sm text-[#6b6b6b]">Runners seen:</span>
                <span className="text-sm font-semibold text-white">{totalRunners}</span>
              </div>
              {runningCount > 0 && (
                <div className="flex items-center gap-2 px-4 py-2 bg-yellow-900/15 border border-yellow-800/30 rounded-lg">
                  <span className="inline-block w-2 h-2 rounded-full bg-yellow-400" />
                  <span className="text-sm text-yellow-400 font-medium">{runningCount} running</span>
                </div>
              )}
              {idleCount > 0 && (
                <div className="flex items-center gap-2 px-4 py-2 bg-green-900/15 border border-green-800/30 rounded-lg">
                  <span className="inline-block w-2 h-2 rounded-full bg-green-400" />
                  <span className="text-sm text-green-400 font-medium">{idleCount} idle</span>
                </div>
              )}
              <div className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] border border-[#333] rounded-lg">
                <span className="text-sm text-[#6b6b6b]">Based on last</span>
                <span className="text-sm font-semibold text-white">{runsChecked} runs</span>
              </div>
              {lastFetched && (
                <div className="ml-auto flex items-center gap-2">
                  <span className="text-xs text-[#6b6b6b]">
                    Updated {lastFetched.toLocaleTimeString()}
                  </span>
                  <button
                    onClick={fetchRunners}
                    disabled={loading}
                    className="px-3 py-1.5 text-xs font-medium text-[#D4915D] border border-[#D4915D]/30 rounded-lg hover:bg-[#D4915D]/10 transition-colors disabled:opacity-50"
                  >
                    {loading ? "Refreshing..." : "Refresh"}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="flex items-center justify-center py-16">
              <div className="flex items-center gap-3 text-[#a0a0a0]">
                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span className="text-sm">Fetching runner activity...</span>
              </div>
            </div>
          )}

          {/* Error state */}
          {!loading && error && (
            <div className="max-w-2xl mx-auto animate-fade-in">
              <div className="px-4 py-3 rounded-xl bg-red-900/15 border border-red-800/30 text-red-400 text-sm">
                {error}
              </div>
            </div>
          )}

          {/* Matrix table */}
          {!loading && runners.length > 0 && (
            <div className="overflow-x-auto rounded-xl border border-[#333] animate-fade-in">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-[#1a1a1a]">
                    <th className="text-left px-6 py-4 text-sm font-semibold text-[#D4915D] border-b border-r border-[#333] w-48">
                      Hardware
                    </th>
                    {OS_LABELS.map((os) => (
                      <th
                        key={os}
                        className="text-left px-6 py-4 text-sm font-semibold text-[#D4915D] border-b border-[#333]"
                      >
                        <div className="flex items-center gap-2">
                          {os === "Windows" ? (
                            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801" />
                            </svg>
                          ) : (
                            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M12.504 0c-.155 0-.311.003-.466.009a11.978 11.978 0 00-4.653 1.11c-.635.296-1.24.656-1.804 1.07a12.062 12.062 0 00-3.667 4.6A11.953 11.953 0 00.834 12c0 1.742.372 3.397 1.044 4.888a12.015 12.015 0 002.108 3.2 12.05 12.05 0 003.159 2.437A11.937 11.937 0 0012 24a11.94 11.94 0 004.855-1.025 12.043 12.043 0 003.159-2.437 12.01 12.01 0 002.108-3.2A11.928 11.928 0 0023.166 12a11.95 11.95 0 00-1.08-5.211 12.056 12.056 0 00-3.667-4.6 11.93 11.93 0 00-1.804-1.07A11.978 11.978 0 0012.504 0z" />
                            </svg>
                          )}
                          {os}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {hardwareRows.map((hw, idx) => (
                    <tr key={hw} className={idx % 2 === 0 ? "bg-[#0d0d0d]" : "bg-[#141414]"}>
                      <td className="px-6 py-5 text-sm font-semibold text-white border-r border-[#333] align-top">
                        <div className="flex items-center gap-2">
                          <span className="inline-block w-2 h-2 rounded-full bg-[#D4915D]" />
                          {hw}
                        </div>
                      </td>
                      {OS_LABELS.map((os) => (
                        <td key={os} className="px-6 py-5 border-[#333] align-top min-w-[300px]">
                          <CellContent cell={matrix[hw]?.[os] ?? { runners: [] }} />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && runners.length === 0 && (
            <div className="text-center py-16 animate-fade-in">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#1a1a1a] border border-[#333] mb-4">
                <svg className="w-8 h-8 text-[#6b6b6b]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-white mb-1">No runner activity found</h3>
              <p className="text-sm text-[#6b6b6b]">
                No self-hosted runner jobs were found in recent workflow runs.
              </p>
            </div>
          )}

          {/* Setup guide */}
          <SetupGuide />
        </div>
      </section>

      <Footer />
    </main>
  );
}
