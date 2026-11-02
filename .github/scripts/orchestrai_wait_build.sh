#!/usr/bin/env bash
# Wait until one OrchestrAI pipeline build finishes (STARTED_BUILD_URL, BATCH_ID).
# Writes build_url to $GITHUB_OUTPUT. Used for a batch's build and for its retry.
set -e
BUILD_URL="${STARTED_BUILD_URL}"
if [ -z "$BUILD_URL" ]; then
  echo "::error::No OrchestrAI pipeline build URL for batch ${BATCH_ID}"; exit 1
fi
echo "build_url=${BUILD_URL}" >> "$GITHUB_OUTPUT"
echo "Waiting for OrchestrAI pipeline build ..."
# SECURITY: pass credentials via a 0600 netrc file, never as `curl -u
# user:token` — argv is world-readable (/proc/<pid>/cmdline, ps) for the
# life of each curl, which would leak the pipeline token to any other
# process on a shared/persistent self-hosted runner. mktemp creates the
# file 0600; printf is a shell builtin, so the token never hits argv.
NETRC="$(mktemp)"
trap 'rm -f "$NETRC"' EXIT
NETRC_HOST=$(printf '%s' "$BUILD_URL" | sed -E 's#^[a-zA-Z][a-zA-Z0-9+.-]*://##; s#[:/].*$##')
printf 'machine %s login %s password %s\n' \
  "$NETRC_HOST" "$ORCHESTRAI_PIPELINE_USER" "$ORCHESTRAI_PIPELINE_TOKEN" > "$NETRC"
# Bounded poll: 330 min of wall-clock time (not a count of polls, which
# each take 15s plus the request) — max_duration (300m) plus 30 min for
# the build to wind down, and under GitHub's 360-minute job timeout.
DEADLINE=$((SECONDS + 330 * 60))
FAIL_MAX=20       # ~5min of consecutive unreachable polls -> give up
finished=""; fails=0
while [ "$SECONDS" -lt "$DEADLINE" ]; do
  if data=$(curl -sf --connect-timeout 10 --max-time 30 --netrc-file "$NETRC" "${BUILD_URL}api/json?tree=result,building" 2>/dev/null); then
    fails=0
    building=$(echo "$data" | python3 -c "import sys,json;print(json.load(sys.stdin).get('building',True))" 2>/dev/null || echo "True")
    result=$(echo "$data" | python3 -c "import sys,json;print(json.load(sys.stdin).get('result') or '')" 2>/dev/null || echo "")
    # The batch result reflects ALL its playbooks; this job's verdict is
    # resolved per-playbook in the next step from summary.json.
    if [ "$building" = "False" ] && [ -n "$result" ]; then
      echo "Batch build finished: $result (per-playbook verdict resolved next)"; finished=1; break
    fi
  else
    fails=$((fails + 1))
    if [ "$fails" -ge "$FAIL_MAX" ]; then
      echo "::error::OrchestrAI pipeline unreachable ($FAIL_MAX consecutive failures)"; exit 1
    fi
  fi
  sleep 15
done
if [ -z "$finished" ]; then
  echo "::error::Timed out waiting for OrchestrAI pipeline build"; exit 1
fi
