interface PlaybookHelpBoxProps {
  playbookTitle?: string;
}

const REPO_URL = "https://github.com/amd/playbooks";

export default function PlaybookHelpBox({ playbookTitle }: PlaybookHelpBoxProps) {
  const issueTitle = playbookTitle ? `Help with: ${playbookTitle}` : "";
  const newIssueHref = issueTitle
    ? `${REPO_URL}/issues/new?title=${encodeURIComponent(issueTitle)}`
    : `${REPO_URL}/issues/new`;
  const browseIssuesHref = `${REPO_URL}/issues`;

  return (
    <div className="mt-6 bg-gradient-to-r from-[#2a1f1a] via-[#1e1e1e] to-[#1e1e1e] border border-[#333333] rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-5">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-[#D4915D]/10 border border-[#D4915D]/30 flex items-center justify-center text-[#D4915D]">
          <svg
            className="w-5 h-5"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56 0-.27-.01-1.16-.02-2.11-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.27-1.69-1.27-1.69-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.75 2.69 1.24 3.34.95.1-.74.4-1.24.73-1.53-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.04 0 0 .96-.31 3.16 1.18a10.94 10.94 0 0 1 5.76 0c2.2-1.49 3.16-1.18 3.16-1.18.62 1.58.23 2.75.11 3.04.74.81 1.18 1.83 1.18 3.09 0 4.42-2.69 5.4-5.25 5.68.41.36.78 1.05.78 2.12 0 1.53-.01 2.76-.01 3.14 0 .31.21.68.8.56C20.21 21.39 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5Z" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">
            Need help with this playbook?
          </h3>
          <p className="text-sm text-[#a0a0a0] leading-relaxed">
            Run into an issue or have a question? Open a GitHub issue and our
            team will take a look.
          </p>
        </div>
      </div>
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 md:flex-shrink-0">
        <a
          href={browseIssuesHref}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm bg-[#242424] hover:bg-[#2f2f2f] text-[#d0d0d0] font-medium rounded-lg border border-[#333333] hover:border-[#444] transition-colors whitespace-nowrap"
        >
          Browse Issues
        </a>
        <a
          href={newIssueHref}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm bg-[#D4915D] hover:bg-[#B8784A] text-black font-medium rounded-lg transition-colors whitespace-nowrap"
        >
          Open an Issue
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M14 5l7 7m0 0l-7 7m7-7H3"
            />
          </svg>
        </a>
      </div>
    </div>
  );
}
