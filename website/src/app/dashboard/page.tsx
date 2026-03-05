"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

interface RunnerInfo {
  runner_id: number;
  runner_name: string;
  os: string;
  status: string;
  busy: boolean;
  labels: string[];
}

interface CellData {
  runners: RunnerInfo[];
}

type MatrixData = Record<string, Record<string, CellData>>;

const HARDWARE_LABELS: Record<string, string> = {
  halo: "STX Halo",
  stx: "STX Point",
  krk: "Krackan Point",
  rx7900xt: "Radeon RX 7900 XT",
  rx9070xt: "Radeon RX 9070 XT",
};

const OS_LABELS = ["Windows", "Linux"];

function classifyRunner(runner: RunnerInfo): { hardware: string; os: string } {
  const searchable = [
    runner.runner_name.toLowerCase(),
    ...runner.labels.map((l) => l.toLowerCase()),
  ].join(" ");

  let hardware = "Other";
  for (const [key, display] of Object.entries(HARDWARE_LABELS)) {
    if (searchable.includes(key.toLowerCase())) {
      hardware = display;
      break;
    }
  }

  let os = "Other";
  const runnerOs = runner.os.toLowerCase();
  for (const osName of OS_LABELS) {
    if (runnerOs.includes(osName.toLowerCase())) {
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

function RunnerStatus({ runner }: { runner: RunnerInfo }) {
  if (runner.status !== "online") {
    return (
      <div className="flex items-center gap-1.5">
        <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#6b6b6b]" />
        <span className="text-[#6b6b6b] text-xs font-medium">Offline</span>
      </div>
    );
  }

  if (runner.busy) {
    return (
      <div className="flex items-center gap-1.5">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-yellow-400" />
        </span>
        <span className="text-yellow-400 text-xs font-medium">Busy</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5">
      <span className="inline-block w-2.5 h-2.5 rounded-full bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.4)]" />
      <span className="text-green-400 text-xs font-medium">Idle</span>
    </div>
  );
}

const REQUIRED_RUNNERS = 2;

function cellOnlineCount(cell: CellData): number {
  return cell.runners.filter((r) => r.status === "online").length;
}

function CellContent({ cell }: { cell: CellData }) {
  const online = cellOnlineCount(cell);
  const sufficient = online >= REQUIRED_RUNNERS;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span
          className={`text-lg font-bold tabular-nums ${
            sufficient ? "text-green-400" : "text-[#a0a0a0]"
          }`}
        >
          {online}/{REQUIRED_RUNNERS}
        </span>
        {!sufficient && (
          <span className="text-[10px] font-semibold uppercase tracking-wide text-yellow-500/80">
            needs {REQUIRED_RUNNERS - online} more
          </span>
        )}
      </div>

      {cell.runners.map((runner) => (
        <div
          key={runner.runner_id}
          className="px-3.5 py-3 rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] hover:border-[#444] transition-colors"
        >
          <div className="flex items-center justify-between gap-2 mb-2">
            <span className="text-sm font-medium text-white truncate">{runner.runner_name}</span>
            <RunnerStatus runner={runner} />
          </div>
          <div className="flex flex-wrap gap-1.5">
            {runner.labels
              .filter((l) => l !== "self-hosted")
              .map((label) => (
                <span
                  key={label}
                  className="px-2 py-0.5 text-[10px] rounded-full bg-[#242424] border border-[#333] text-[#a0a0a0]"
                >
                  {label}
                </span>
              ))}
          </div>
        </div>
      ))}
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
            This dashboard reads the registered self-hosted runners via the GitHub API using a{" "}
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
              <code className="bg-[#242424] px-1.5 py-0.5 rounded text-[#D4915D] text-xs">Administration</code>{" "}
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

type DashboardTab = "ci" | "playbooks";

const TABS: { id: DashboardTab; label: string }[] = [
  { id: "ci", label: "CI Status" },
  { id: "playbooks", label: "Playbook Status" },
];

type PlaybookCellStatus = "pass" | "fail" | "partial" | "no-tests";

interface PlaybookMatrixColumn {
  id: string;
  hardware: string;
  os: string;
  arch: string;
  platform: string;
}

interface PlaybookMatrixCell {
  passed: number;
  failed: number;
  skipped: number;
  totalTests: number;
  status: PlaybookCellStatus;
}

interface PlaybookMatrixRow {
  playbookId: string;
  title: string;
  category: string;
  developed: boolean;
  cells: Record<string, PlaybookMatrixCell>;
}

interface PlaybookTestMatrixResponse {
  run: {
    id: number;
    htmlUrl: string;
    createdAt: string;
    event: string;
  } | null;
  columns: PlaybookMatrixColumn[];
  rows: PlaybookMatrixRow[];
}

function CIStatusDashboard() {
  const [runners, setRunners] = useState<RunnerInfo[]>([]);
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
  const onlineCount = runners.filter((r) => r.status === "online").length;
  const busyCount = runners.filter((r) => r.busy).length;
  const offlineCount = totalRunners - onlineCount;

  const totalCombinations = hardwareRows.length * OS_LABELS.length;
  const sufficientCells = Object.values(matrix).reduce(
    (acc, osMap) =>
      acc + Object.values(osMap).filter((cell) => cellOnlineCount(cell) >= REQUIRED_RUNNERS).length,
    0
  );
  const insufficientCells = totalCombinations - sufficientCells;

  return (
    <div className="space-y-6">
      {!loading && runners.length > 0 && (
        <div className="flex flex-wrap items-center gap-4 animate-fade-in">
          <div className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] border border-[#333] rounded-lg">
            <span className="text-sm text-[#6b6b6b]">Total runners:</span>
            <span className="text-sm font-semibold text-white">{totalRunners}</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-green-900/15 border border-green-800/30 rounded-lg">
            <span className="inline-block w-2 h-2 rounded-full bg-green-400" />
            <span className="text-sm text-green-400 font-medium">{onlineCount} online</span>
          </div>
          {busyCount > 0 && (
            <div className="flex items-center gap-2 px-4 py-2 bg-yellow-900/15 border border-yellow-800/30 rounded-lg">
              <span className="inline-block w-2 h-2 rounded-full bg-yellow-400" />
              <span className="text-sm text-yellow-400 font-medium">{busyCount} busy</span>
            </div>
          )}
          {offlineCount > 0 && (
            <div className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] border border-[#333] rounded-lg">
              <span className="inline-block w-2 h-2 rounded-full bg-[#6b6b6b]" />
              <span className="text-sm text-[#6b6b6b] font-medium">{offlineCount} offline</span>
            </div>
          )}
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            insufficientCells === 0
              ? "bg-green-900/15 border border-green-800/30"
              : "bg-red-900/15 border border-red-800/30"
          }`}>
            <span className={`text-sm font-medium ${insufficientCells === 0 ? "text-green-400" : "text-red-400"}`}>
              {sufficientCells}/{totalCombinations} combos covered
            </span>
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

      {loading && (
        <div className="flex items-center justify-center py-16">
          <div className="flex items-center gap-3 text-[#a0a0a0]">
            <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span className="text-sm">Fetching runners...</span>
          </div>
        </div>
      )}

      {!loading && error && (
        <div className="max-w-2xl mx-auto animate-fade-in">
          <div className="px-4 py-3 rounded-xl bg-red-900/15 border border-red-800/30 text-red-400 text-sm">
            {error}
          </div>
        </div>
      )}

      {!loading && runners.length > 0 && (
        <div className="space-y-3 animate-fade-in">
          <div className="overflow-x-auto rounded-xl border border-[#333]">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-[#1a1a1a]">
                  <th className="text-left px-6 py-4 text-sm font-semibold text-[#D4915D] border-b border-r border-[#333] w-55">
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
          {insufficientCells > 0 && (
            <div className="flex items-center gap-2.5 px-4 py-3 rounded-lg bg-[#1a1a1a] border border-[#333] text-xs text-[#a0a0a0]">
              <svg className="w-4 h-4 text-yellow-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>
                <strong className="text-white font-medium">{insufficientCells} combination{insufficientCells > 1 ? "s" : ""}</strong>{" "}
                {insufficientCells > 1 ? "have" : "has"} fewer than {REQUIRED_RUNNERS} runners.
                Each device + OS pair requires {REQUIRED_RUNNERS} machines for redundancy against maintenance, failures, and provisioning delays.
              </span>
            </div>
          )}
        </div>
      )}

      {!loading && !error && runners.length === 0 && (
        <div className="text-center py-16 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#1a1a1a] border border-[#333] mb-4">
            <svg className="w-8 h-8 text-[#6b6b6b]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-white mb-1">No runners found</h3>
          <p className="text-sm text-[#6b6b6b]">
            No self-hosted runners are registered for this repository.
          </p>
        </div>
      )}

      {error && <SetupGuide />}
    </div>
  );
}

interface RunOption {
  id: number;
  htmlUrl: string;
  createdAt: string;
  event: string;
  headBranch: string;
  conclusion: string | null;
}

function eventBadge(event: string) {
  if (event === "schedule") return { label: "Nightly", cls: "bg-blue-900/30 text-blue-400 border-blue-800/30" };
  if (event === "workflow_dispatch") return { label: "Manual", cls: "bg-purple-900/30 text-purple-400 border-purple-800/30" };
  return { label: event, cls: "bg-[#242424] text-[#6b6b6b] border-[#333]" };
}

function RunSelector({
  runs,
  selectedId,
  onChange,
}: {
  runs: RunOption[];
  selectedId: number | null;
  onChange: (id: number | null) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useCallback((node: HTMLDivElement | null) => {
    if (!node) return;
    const handler = (e: MouseEvent) => {
      if (!node.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const selected = selectedId != null ? runs.find((r) => r.id === selectedId) : null;
  const label = selected
    ? new Date(selected.createdAt).toLocaleString()
    : "Latest nightly";

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 px-3 py-1.5 bg-[#1a1a1a] border border-[#333] rounded-lg text-sm text-[#a0a0a0] hover:border-[#555] hover:text-white transition-colors"
      >
        <svg className="w-3.5 h-3.5 text-[#D4915D] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span>Run: <span className="text-white font-medium">{label}</span></span>
        <svg className={`w-3.5 h-3.5 transition-transform ${open ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute left-0 top-full mt-1 z-50 w-80 bg-[#1a1a1a] border border-[#333] rounded-xl shadow-2xl overflow-hidden">
          <div className="max-h-72 overflow-y-auto">
            <button
              onClick={() => { onChange(null); setOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-[#242424] transition-colors ${selectedId == null ? "bg-[#242424]" : ""}`}
            >
              <span className="flex-1 text-left text-white font-medium">Latest nightly</span>
              {selectedId == null && <svg className="w-3.5 h-3.5 text-[#D4915D]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>}
            </button>
            <div className="border-t border-[#2a2a2a]" />
            {runs.map((run) => {
              const badge = eventBadge(run.event);
              const isSelected = selectedId === run.id;
              return (
                <button
                  key={run.id}
                  onClick={() => { onChange(run.id); setOpen(false); }}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-[#242424] transition-colors ${isSelected ? "bg-[#242424]" : ""}`}
                >
                  <div className="flex-1 min-w-0 text-left">
                    <div className="text-[#a0a0a0]">{new Date(run.createdAt).toLocaleString()}</div>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span className={`px-1.5 py-0.5 text-[10px] font-semibold rounded border ${badge.cls}`}>{badge.label}</span>
                      <span className="text-[11px] text-[#555] truncate">{run.headBranch}</span>
                    </div>
                  </div>
                  {isSelected && <svg className="w-3.5 h-3.5 text-[#D4915D] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function PlaybookStatusDashboard() {
  const [matrix, setMatrix] = useState<PlaybookTestMatrixResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [availableRuns, setAvailableRuns] = useState<RunOption[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);

  const fetchMatrix = useCallback(async (runId: number | null = null) => {
    setLoading(true);
    setError(null);
    try {
      const url = runId
        ? `/api/dashboard/playbook-test-matrix?run_id=${runId}`
        : "/api/dashboard/playbook-test-matrix";
      const res = await fetch(url);
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || `API error: ${res.status}`);
      }
      setMatrix(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch playbook test matrix");
      setMatrix(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch the list of available runs once on mount
  useEffect(() => {
    fetch("/api/dashboard/playbook-runs?per_page=20")
      .then((r) => r.json())
      .then((d) => { if (d.runs) setAvailableRuns(d.runs); })
      .catch(() => {/* non-critical — run selector just stays empty */});
  }, []);

  useEffect(() => {
    fetchMatrix(selectedRunId);
  }, [fetchMatrix, selectedRunId]);

  type CellStyle = {
    label: string;
    dot: string | null;
    text: string;
    bg: string;
    border: string;
  };

  const getCellStyle = (cell: PlaybookMatrixCell | undefined, developed: boolean, testsAdded: boolean): CellStyle => {
    if (!developed || !testsAdded) {
      return { label: "—", dot: null, text: "text-[#2e2e2e]", bg: "bg-transparent", border: "border-[#1e1e1e]" };
    }
    if (!cell || cell.status === "no-tests") {
      return { label: "Not tested", dot: null, text: "text-[#555]", bg: "bg-transparent", border: "border-[#2a2a2a]" };
    }
    switch (cell.status) {
      case "pass":
        return { label: "All passing", dot: "bg-green-400", text: "text-green-300", bg: "bg-green-900/10", border: "border-green-800/25" };
      case "fail":
        return { label: "Failing", dot: "bg-red-400", text: "text-red-300", bg: "bg-red-900/10", border: "border-red-800/25" };
      case "partial":
        return { label: "Some passing", dot: "bg-yellow-400", text: "text-yellow-300", bg: "bg-yellow-900/10", border: "border-yellow-800/25" };
      default:
        return { label: "Not tested", dot: null, text: "text-[#555]", bg: "bg-transparent", border: "border-[#2a2a2a]" };
    }
  };

  const runDate = matrix?.run?.createdAt ? new Date(matrix.run.createdAt) : null;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="flex items-center gap-3 text-[#a0a0a0]">
          <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span className="text-sm">Loading nightly playbook results...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto animate-fade-in">
        <div className="px-4 py-3 rounded-xl bg-red-900/15 border border-red-800/30 text-red-400 text-sm">
          {error}
        </div>
      </div>
    );
  }

  if (!matrix || matrix.rows.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 animate-fade-in">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#1a1a1a] border border-[#333] mb-5">
          <svg className="w-8 h-8 text-[#D4915D]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-white mb-2">No playbooks found</h3>
        <p className="text-sm text-[#6b6b6b] max-w-md text-center">
          No playbooks could be loaded.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4 animate-fade-in">
      {!matrix.run && (
        <div className="flex items-center gap-2.5 px-4 py-3 rounded-lg bg-[#1a1a1a] border border-[#333] text-xs text-[#a0a0a0]">
          <svg className="w-4 h-4 text-[#6b6b6b] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>No nightly test artifacts found — all combinations are shown but no results are available yet.</span>
        </div>
      )}
      <div className="flex flex-wrap items-center gap-3">
        {availableRuns.length > 0 && (
          <RunSelector
            runs={availableRuns}
            selectedId={selectedRunId}
            onChange={(id) => setSelectedRunId(id)}
          />
        )}
        <div className="px-4 py-2 rounded-lg bg-[#1a1a1a] border border-[#333] text-sm text-[#a0a0a0]">
          <span className="text-white font-medium">{matrix.rows.length}</span> playbooks ×{" "}
          <span className="text-white font-medium">{matrix.columns.length}</span> combinations
        </div>
        <div className="px-4 py-2 rounded-lg bg-green-900/15 border border-green-800/30 text-sm text-[#a0a0a0]">
          <span className="text-green-400 font-medium">{matrix.rows.filter((r) => r.developed).length}</span>
          <span> developed</span>
        </div>
        {matrix.rows.some((r) => !r.developed) && (
          <div className="px-4 py-2 rounded-lg bg-[#1a1a1a] border border-[#333] text-sm text-[#a0a0a0]">
            <span className="text-[#6b6b6b] font-medium">{matrix.rows.filter((r) => !r.developed).length}</span>
            <span> not yet developed</span>
          </div>
        )}
        {runDate && (
          <div className="px-4 py-2 rounded-lg bg-[#1a1a1a] border border-[#333] text-sm text-[#a0a0a0]">
            Run date: <span className="text-white font-medium">{runDate.toLocaleString()}</span>
          </div>
        )}
        {matrix.run?.htmlUrl && (
          <a
            href={matrix.run.htmlUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 rounded-lg border border-[#D4915D]/40 text-[#D4915D] text-sm font-medium hover:bg-[#D4915D]/10 transition-colors"
          >
            View workflow run
          </a>
        )}
        <button
          onClick={() => fetchMatrix(selectedRunId)}
          disabled={loading}
          className="px-4 py-2 rounded-lg border border-[#333] text-[#a0a0a0] text-sm hover:text-white hover:border-[#555] transition-colors disabled:opacity-50"
        >
          Refresh
        </button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-[#333]">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-[#1a1a1a]">
              <th className="text-left px-4 py-3 text-sm font-semibold text-[#D4915D] border-b border-r border-[#333] min-w-[420px]">
                Playbook
              </th>
              <th className="px-3 py-3 text-xs font-semibold text-[#D4915D] border-b border-r border-[#333] w-[80px] text-center">
                Developed
              </th>
              <th className="px-3 py-3 text-xs font-semibold text-[#D4915D] border-b border-r border-[#333] w-[100px] text-center">
                Tests Added
              </th>
              {matrix.columns.map((column) => (
                <th
                  key={column.id}
                  className="px-3 py-3 text-xs font-semibold text-[#D4915D] border-b border-[#333] min-w-[110px] text-center"
                >
                  <div className="flex flex-col items-center leading-tight gap-0.5">
                    <span className="text-[11px] font-semibold text-[#a0a0a0]">{column.hardware}</span>
                    <span className="text-[10px] font-normal text-[#555]">{column.os}</span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(() => {
              const elements: React.ReactNode[] = [];
              let lastCategory = "";
              let categoryRowIdx = 0;
              matrix.rows.forEach((row) => {
                if (row.category !== lastCategory) {
                  lastCategory = row.category;
                  categoryRowIdx = 0;
                  elements.push(
                    <tr key={`cat-${row.category}`} className="bg-[#111]">
                      <td
                        colSpan={matrix.columns.length + 3}
                        className="px-4 py-1.5 border-t border-b border-[#2a2a2a]"
                      >
                        <span className="text-[11px] font-semibold uppercase tracking-widest text-[#555]">
                          {row.category}
                        </span>
                      </td>
                    </tr>
                  );
                }
                const idx = categoryRowIdx++;
                elements.push(
                  <tr key={row.playbookId} className={idx % 2 === 0 ? "bg-[#0d0d0d]" : "bg-[#141414]"}>
                    <td className="px-4 py-3 border-r border-[#333] align-middle">
                      <Link
                        href={`/playbooks/${row.playbookId}`}
                        className="text-sm font-medium text-white hover:text-[#D4915D] transition-colors"
                      >
                        {row.title}
                      </Link>
                    </td>
                    <td className="px-3 py-3 border-r border-[#333] align-middle text-center">
                      {row.developed ? (
                        <svg className="w-4 h-4 text-green-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4 text-[#444] mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      )}
                    </td>
                    <td className="px-3 py-3 border-r border-[#333] align-middle text-center">
                      {Object.values(row.cells).some((c) => c.totalTests > 0) ? (
                        <svg className="w-4 h-4 text-green-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4 text-[#444] mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      )}
                    </td>
                    {matrix.columns.map((column) => {
                      const cell = row.cells[column.id];
                      const testsAdded = Object.values(row.cells).some((c) => c.totalTests > 0);
                      const style = getCellStyle(cell, row.developed, testsAdded);
                      const isClickable = !!(cell && cell.totalTests > 0);
                      const runId = selectedRunId ?? matrix?.run?.id ?? null;

                      const cellBadge = (
                        <div className={`inline-flex items-center justify-center gap-1.5 rounded border ${style.border} ${style.bg} px-2 py-1 w-full ${isClickable ? "hover:border-[#D4915D]/50 hover:bg-[#D4915D]/5 transition-colors" : ""}`}>
                          {style.dot && (
                            <span className={`inline-block w-1.5 h-1.5 rounded-full shrink-0 ${style.dot}`} />
                          )}
                          <span className={`text-[11px] font-medium whitespace-nowrap ${style.text}`}>{style.label}</span>
                        </div>
                      );

                      return (
                        <td key={column.id} className={`px-2 py-2 align-middle text-center${isClickable ? " cursor-pointer" : ""}`}>
                          {isClickable ? (
                            <Link
                              href={`/playbooks/${row.playbookId}?coverage=true&test_device=${column.arch}&platform=${column.platform}${runId ? `&run_id=${runId}` : ""}`}
                            >
                              {cellBadge}
                            </Link>
                          ) : (
                            cellBadge
                          )}
                        </td>
                      );
                    })}
                  </tr>
                );
              });
              return elements;
            })()}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<DashboardTab>("ci");

  return (
    <main className="min-h-screen bg-[#0d0d0d] grid-pattern">
      <Header />

      <section className="pt-28 pb-6 px-6 gradient-hero relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#D4915D]/5 rounded-full blur-3xl" />
        <div className="max-w-[1400px] mx-auto relative z-10">
          <div className="text-center max-w-4xl mx-auto animate-fade-in mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-3 leading-tight">
              Playbooks {" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#D4915D] to-[#E8B896]">
                CI Dashboard
              </span>
            </h1>
            <p className="text-lg text-[#a0a0a0] max-w-2xl mx-auto">
              CI runner status and playbook execution overview
            </p>
          </div>
        </div>
      </section>

      <section className="px-4">
        <div className="max-w-[1800px] mx-auto">
          <div className="flex gap-1 border-b border-[#333]">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-5 py-3 text-sm font-medium transition-colors relative ${
                  activeTab === tab.id
                    ? "text-[#D4915D]"
                    : "text-[#6b6b6b] hover:text-[#a0a0a0]"
                }`}
              >
                {tab.label}
                {activeTab === tab.id && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#D4915D] rounded-t" />
                )}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="px-4 pb-6 pt-6">
        <div className="max-w-[1800px] mx-auto">
          {activeTab === "ci" && <CIStatusDashboard />}
          {activeTab === "playbooks" && <PlaybookStatusDashboard />}
        </div>
      </section>

      <Footer />
    </main>
  );
}
