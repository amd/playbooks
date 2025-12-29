"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import DependencySankey from "@/components/DependencySankey";

interface GitHubIssue {
  title: string;
  labels: Array<{ name: string }>;
  number: number;
}

interface ProcessedData {
  core: SankeyData;
  supplemental: SankeyData;
}

interface SankeyData {
  nodes: Array<{ name: string }>;
  links: Array<{ source: string; target: string; value: number }>;
}

export default function DependenciesPage() {
  const [data, setData] = useState<ProcessedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGitHubIssues();
  }, []);

  async function fetchGitHubIssues() {
    try {
      setLoading(true);
      setError(null);

      // Use our server-side API route to fetch GitHub issues
      const response = await fetch("/api/github-issues");
      const data = await response.json();
      
      const { issues, error: apiError } = data;
      
      if (!issues || issues.length === 0) {
        setError(
          "No playbook issues found. " +
          (apiError || "Please ensure the GitHub repository has issues with appropriate labels (track::core/supplemental, os::*, app::*, framework::*, model::*). ") +
          "To access private repositories, set the GITHUB_TOKEN environment variable."
        );
        console.warn(
          "To fetch issues from the GitHub repository:\n" +
          "1. Create a .env.local file in the project root\n" +
          "2. Add: GITHUB_TOKEN=your_github_personal_access_token\n" +
          "3. Create a token at: https://github.com/settings/tokens\n" +
          "4. Grant 'repo' scope for private repositories\n" +
          "5. Restart the dev server"
        );
        return;
      }

      const processedData = processIssues(issues);
      setData(processedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      console.error("Error fetching GitHub issues:", err);
    } finally {
      setLoading(false);
    }
  }

  function processIssues(issues: GitHubIssue[]): ProcessedData {
    const coreIssues = issues.filter((issue) =>
      issue.labels.some((label) => label.name === "track::core")
    );
    const supplementalIssues = issues.filter((issue) =>
      issue.labels.some((label) => label.name === "track::supplemental")
    );

    return {
      core: buildSankeyData(coreIssues, "Core"),
      supplemental: buildSankeyData(supplementalIssues, "Supplemental"),
    };
  }

  function buildSankeyData(issues: GitHubIssue[], trackName: string): SankeyData {
    const nodes = new Set<string>();
    const linksMap = new Map<string, number>();

    // Helper function to truncate playbook names
    const truncatePlaybookName = (name: string, maxLength: number = 40): string => {
      if (name.length <= maxLength) return name;
      return name.substring(0, maxLength) + "...";
    };

    // Add track root node
    nodes.add(trackName);

    issues.forEach((issue) => {
      const labels = issue.labels.map((l) => l.name);
      
      const oses = labels.filter((l) => l.startsWith("os::"));
      const apps = labels.filter((l) => l.startsWith("app::"));
      const frameworks = labels.filter((l) => l.startsWith("framework::"));
      const models = labels.filter((l) => l.startsWith("model::"));

      const playbook = truncatePlaybookName(issue.title);
      nodes.add(playbook);

      // Link track to playbook
      const trackLink = `${trackName}→${playbook}`;
      linksMap.set(trackLink, (linksMap.get(trackLink) || 0) + 1);

      // For each OS, link playbook to OS, then OS to dependencies
      if (oses.length === 0) {
        // If no OS specified, treat as general (could be either)
        oses.push("os::any");
      }

      oses.forEach((os) => {
        const osDisplay = os.replace("os::", "").toUpperCase();
        nodes.add(osDisplay);

        // Link playbook to OS
        const osLink = `${playbook}→${osDisplay}`;
        linksMap.set(osLink, (linksMap.get(osLink) || 0) + 1);

        // Add dependency type grouping nodes for this OS
        const appsGroupNode = `Apps (${osDisplay})`;
        const frameworksGroupNode = `Frameworks (${osDisplay})`;
        const modelsGroupNode = `Models (${osDisplay})`;

        // Link OS to apps through Apps group
        if (apps.length > 0) {
          nodes.add(appsGroupNode);
          const osToAppsLink = `${osDisplay}→${appsGroupNode}`;
          linksMap.set(osToAppsLink, (linksMap.get(osToAppsLink) || 0) + 1);

          apps.forEach((app) => {
            const appName = app.replace("app::", "");
            const appDisplay = `${appName} (${osDisplay})`;
            nodes.add(appDisplay);
            const link = `${appsGroupNode}→${appDisplay}`;
            linksMap.set(link, (linksMap.get(link) || 0) + 1);
          });
        }

        // Link OS to frameworks through Frameworks group
        if (frameworks.length > 0) {
          nodes.add(frameworksGroupNode);
          const osToFrameworksLink = `${osDisplay}→${frameworksGroupNode}`;
          linksMap.set(osToFrameworksLink, (linksMap.get(osToFrameworksLink) || 0) + 1);

          frameworks.forEach((framework) => {
            const fwName = framework.replace("framework::", "");
            const fwDisplay = `${fwName} (${osDisplay})`;
            nodes.add(fwDisplay);
            const link = `${frameworksGroupNode}→${fwDisplay}`;
            linksMap.set(link, (linksMap.get(link) || 0) + 1);
          });
        }

        // Link OS to models through Models group
        if (models.length > 0) {
          nodes.add(modelsGroupNode);
          const osToModelsLink = `${osDisplay}→${modelsGroupNode}`;
          linksMap.set(osToModelsLink, (linksMap.get(osToModelsLink) || 0) + 1);

          models.forEach((model) => {
            const modelName = model.replace("model::", "");
            const modelDisplay = `${modelName} (${osDisplay})`;
            nodes.add(modelDisplay);
            const link = `${modelsGroupNode}→${modelDisplay}`;
            linksMap.set(link, (linksMap.get(link) || 0) + 1);
          });
        }
      });
    });

    const links = Array.from(linksMap.entries()).map(([key, value]) => {
      const [source, target] = key.split("→");
      return { source, target, value };
    });

    return {
      nodes: Array.from(nodes).map((name) => ({ name })),
      links,
    };
  }

  return (
    <main className="min-h-screen bg-[#0d0d0d] grid-pattern">
      <Header />
      
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl md:text-5xl font-bold text-white text-center mb-4">
          Playbook Dependencies
        </h1>
        <p className="text-gray-400 text-center mb-12 max-w-3xl mx-auto">
          Visualization of playbook dependencies showing apps, frameworks, and models
          required for each operating system, organized by track.
        </p>

        {loading && (
          <div className="text-center text-white py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            <p className="mt-4">Loading GitHub issues...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-900/20 border border-red-500 text-red-300 px-6 py-4 rounded-lg max-w-3xl mx-auto mb-8">
            <h3 className="font-bold mb-2">⚠️ Error</h3>
            <p className="mb-3">{error}</p>
            <details className="text-sm text-red-300/80">
              <summary className="cursor-pointer font-semibold mb-2">Setup Instructions</summary>
              <ol className="list-decimal list-inside space-y-1 ml-2">
                <li>Create a <code className="bg-black/30 px-1 py-0.5 rounded">.env.local</code> file in the project root</li>
                <li>Add: <code className="bg-black/30 px-1 py-0.5 rounded">GITHUB_TOKEN=your_token_here</code></li>
                <li>Create a token at <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="underline text-red-200">github.com/settings/tokens</a></li>
                <li>Grant <code className="bg-black/30 px-1 py-0.5 rounded">repo</code> scope for private repositories</li>
                <li>Restart the development server</li>
              </ol>
            </details>
            <button
              onClick={fetchGitHubIssues}
              className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {data && !loading && (
          <div className="space-y-16">
            <div>
              <h2 className="text-3xl font-bold text-white mb-6 text-center">
                Core Track Dependencies
              </h2>
              <DependencySankey data={data.core} title="Core Track" />
            </div>

            <div>
              <h2 className="text-3xl font-bold text-white mb-6 text-center">
                Supplemental Track Dependencies
              </h2>
              <DependencySankey data={data.supplemental} title="Supplemental Track" />
            </div>
          </div>
        )}
      </div>

      <Footer />
    </main>
  );
}

